from typing import Callable, Mapping, Sequence, Set, Tuple

import torch
import torch._decomp
from torch._dynamo.utils import deepcopy_to_fake_tensor, detect_fake_mode
from torch._subclasses.fake_tensor import FakeTensorMode
from torch.fx import Graph, Node
from torch.fx.experimental.proxy_tensor import make_fx
from torch.fx.graph_module import GraphModule
from torch.fx.node import has_side_effect, map_aggregate
from torch.fx.passes.shape_prop import _extract_tensor_metadata


def std_decompositions():
    return {
        **torch._decomp.core_aten_decompositions(),
        **torch._decomp.get_decompositions(
            [
                torch.ops.aten.addmm,
                torch.ops.aten.gelu,
                torch.ops.aten.native_layer_norm,
                torch.ops.aten.split.Tensor,
                torch.ops.aten.split_with_sizes,
                torch.ops.aten.embedding,
                torch.ops.aten._unsafe_view,
                torch.ops.aten.upsample_nearest2d,
                torch.ops.aten.clamp_min,
                torch.ops.aten.clamp_max,
                torch.ops.aten.relu_,
                torch.ops.aten.roll,
                torch.ops.aten.linalg_vector_norm,
                torch.ops.aten._native_batch_norm_legit,
                torch.ops.aten._native_batch_norm_legit_no_training,
                torch.ops.aten.relu,
                torch.ops.aten.repeat,
                torch.ops.aten._log_softmax,
                torch.ops.aten.hardtanh,
                ## ops those are not decomposed anymore
                # torch.ops.aten.split_copy,
                # torch.ops.aten.split_copy.Tensor,
                # torch.ops.aten.split_with_sizes_copy,
                # torch.ops.aten.unbind_copy.int,
                # torch.ops.aten.copy_,
                # torch.ops.aten.copy,
                # torch.ops.aten.lift_fresh_copy,
                # torch.ops.aten.index.Tensor,
                # torch.ops.aten.max.default,
                # torch.ops.aten.min.default,
                # torch.ops.aten.select_scatter,
                ## ops those are decomposed to prims.xx
                # torch.ops.aten.add_.Tensor,  # prims.add + aten.copy_
                # torch.ops.aten.arange.default,  # prims.iota
                # torch.ops.aten.arange.start,  # prims.iota
                # torch.ops.aten.var_mean,  # prims.{var+sum+div}
                # torch.ops.aten.log2, # prims.log2
                # torch.ops.aten.ceil, # prims.ceil
            ]
        ),
    }


STD_DECOMPOSITIONS = std_decompositions()


def _is_parent_of_lift_fresh_copy(node: Node) -> bool:
    if any(child.target == torch.ops.aten.lift_fresh_copy.default for child in node.users):
        assert len(node.users) == 1
        return True
    return False


# Copy of https://github.com/furiosa-ai/npu-tools/blob/2d9194c0/crates/furiosa-torch/furiosa/torch/preprocess.py#L10, just with different function name.
def do_make_fx(gm, inputs, decomposition_table):
    from torch.func import functionalize

    gm = functionalize(gm, remove="mutations_and_views")

    # tracing with real mode is ok because all tensors are FakeTensor
    gm = make_fx(gm, decomposition_table=decomposition_table)(*inputs)

    eliminate_dead_code(gm.graph)
    gm.graph.lint()
    return gm


def replace_fake_tensor_to_origin_tensor(fake_gm, traced_gm, origin_state_dict):
    # make mapping FakeTensor to parameter name
    param_mapping = {fake_t: key for key, fake_t in dict(fake_gm.named_parameters()).items()}
    buffer_mapping = {fake_t: key for key, fake_t in dict(fake_gm.named_buffers()).items()}

    # replace FakeTensor parameters to original tensors for later execution
    param_dict = {}
    for key, fake_t in traced_gm._parameters.items():
        origin_key = param_mapping[fake_t]
        origin_t = origin_state_dict[origin_key]
        param_dict[key] = origin_t
    traced_gm._parameters = param_dict

    buffer_dict = {}
    for key, fake_t in traced_gm._buffers.items():
        if fake_t in buffer_mapping:
            origin_key = buffer_mapping[fake_t]
            origin_t = origin_state_dict[origin_key]
            buffer_dict[key] = origin_t
        # there are some cases that new constant buffers are created through make_fx
        # refer test_index_tensor_* tests in tests/python/test_aten_ops.py
        else:
            buffer_dict[key] = fake_t
    traced_gm._buffers = buffer_dict


def fill_tensor_metas(gm):
    for node in gm.graph.nodes:
        if 'tensor_meta' in node.meta:
            continue
        elif node.name == 'output':
            continue
        elif 'constant' in node.name:
            if node.name.startswith('_param'):
                tensor = gm._parameters[node.target]
            else:
                tensor = gm._buffers[node.target]

            meta = _extract_tensor_metadata(tensor)
            node.meta['tensor_meta'] = meta
        else:
            # copy code from https://github.com/pytorch/pytorch/blob/v2.1.0/torch/fx/passes/shape_prop.py#L161-L173
            found_tensor = False

            def extract_tensor_meta(obj):
                if isinstance(obj, torch.Tensor):
                    nonlocal found_tensor
                    found_tensor = True
                    return _extract_tensor_metadata(obj)
                else:
                    return obj

            result = node.meta['val']  # example fake tensors
            meta = map_aggregate(result, extract_tensor_meta)
            if found_tensor:
                node.meta['tensor_meta'] = meta


# make tensor as contiguous tensor
def to_contiguous(tensor):
    return tensor.clone(memory_format=torch.contiguous_format)


# Copied from https://github.com/furiosa-ai/npu-tools/blob/fb569c46f27bcf8905e772c27abf277b9e79d653/crates/furiosa-torch/furiosa/torch/preprocess.py#L14-L17
def make_named_buffer_to_contiguous(gm):
    for key, t in gm.named_buffers():
        if not t.is_contiguous() and len(t.shape) > 1:
            gm.register_buffer(key, to_contiguous(t))


# Copied from https://github.com/furiosa-ai/npu-tools/blob/2d9194c0/crates/furiosa-torch/furiosa/torch/preprocess.py#L80,
# but with some modification. This function should result in same GraphModule as one generated by `preprocess` in npu-tools for consistent compilation result.
def preprocess(gm: GraphModule, inputs: Sequence, decomposition_table=STD_DECOMPOSITIONS):
    make_named_buffer_to_contiguous(gm)

    origin_state_dict = {
        **dict(gm.named_parameters()),
        **dict(gm.named_buffers()),
    }

    fake_mode = detect_fake_mode(inputs) or FakeTensorMode()
    fake_gm = deepcopy_to_fake_tensor(gm, fake_mode)

    ##################################
    # Start of Furiosa-rt only Section
    # This code only exists in furiosa-runtime's preprocess code. This code should be kept not to affect final result graph.
    ##################################

    # Fake tensors which is parent of lift_fresh_copy causes error during execution.
    # So convert them into real tensors.
    # https://github.com/pytorch/pytorch/blob/7bcf7da3a268b435777fe87c7794c382f444e86d/torch/_subclasses/fake_tensor.py#L1326
    for node in fake_gm.graph.nodes:
        if node.op != "get_attr":
            continue
        if _is_parent_of_lift_fresh_copy(node):
            setattr(fake_gm, node.target, getattr(gm, node.target))

    # Save original allow_non_fake_inputs value of FakeTensorMode
    original_val = fake_mode.allow_non_fake_inputs
    fake_mode.allow_non_fake_inputs = True

    # Some constant tensors might have been converted to input tensor. In this case, those also should not be fake tensor.
    to_be_real_tensor_input = [
        _is_parent_of_lift_fresh_copy(node) for node in gm.graph.nodes if node.op == "placeholder"
    ]
    assert len(to_be_real_tensor_input) == len(inputs)

    ##################################
    # End of Furiosa-rt only Section
    ##################################

    fake_inputs = [
        t if to_be_real else fake_mode.from_tensor(t, static_shapes=True)
        for t, to_be_real in zip(inputs, to_be_real_tensor_input)
    ]

    # Trace module with fake inputs. Operation between normal tensor and fake tensors does not incur
    # actual computation, so this may not cause much overhead.
    #
    # Why don't copy original model into fake model that only contains fake tensor and trace it?
    # Because some constants in FX graph might cause error if it is fake tensor, it should be a real tensor (e.g., constant tensor produced by torch.tensor).
    traced_gm = do_make_fx(fake_gm, fake_inputs, decomposition_table)

    # replace all fake tensors to original tensors
    replace_fake_tensor_to_origin_tensor(fake_gm, traced_gm, origin_state_dict)

    # Fill tensor_meta of several nodes including constant nodes
    fill_tensor_metas(traced_gm)

    # Restore allow_non_fake_inputs value of FakeTensorMode
    fake_mode.allow_non_fake_inputs = original_val

    return traced_gm


class GmCapturer:
    def __call__(self, gm, inputs):
        self.traced_gm = preprocess(gm, inputs)
        return self.traced_gm


def custom_compiler(model) -> Tuple[GmCapturer, Callable]:
    gm_capturer = GmCapturer()
    return gm_capturer, torch.compile(model, backend=gm_capturer, dynamic=False, fullgraph=True)


def trace_module(gm, args: Sequence, kwargs: Mapping = {}):
    with torch._dynamo.config.patch(cache_size_limit=1024):
        torch._dynamo.reset()
        original_inline_config = torch._dynamo.config.inline_inbuilt_nn_modules
        # To prevent constant tensors from becoming placeholder (input) nodes.
        torch._dynamo.config.inline_inbuilt_nn_modules = False

        try:
            gm_capturer, traced_callable = custom_compiler(gm)
            traced_callable(*args, **kwargs)
            return gm_capturer.traced_gm
        finally:
            torch._dynamo.config.inline_inbuilt_nn_modules = original_inline_config


# TODO: add more in-place ops here or find way to get list of in-place ops from torch.
SIDE_EFFECT_OPS: Set[Callable] = {
    torch.ops.aten.index_put_.default,
    torch.ops.aten.index_put.default,
    torch.ops.aten.copy_.default,
}
# To avoid ``Graph.eliminate_dead_code`` not to remove in-place ops with no user.
for op in SIDE_EFFECT_OPS:
    has_side_effect(op)


def eliminate_dead_code(graph: Graph) -> None:
    for node in reversed(graph.nodes):
        if len(node.users) > 0:
            continue
        if not node.is_impure():
            graph.erase_node(node)
