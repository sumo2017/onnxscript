"""
Test data for aten operators which don't exist in PyTorch file:
pytorch/torch/testing/_internal/common_methods_invocations.py.
"""

import functools
import itertools
from typing import Any, List

import torch
from torch import testing as torch_testing
from torch.testing._internal import common_dtype, common_methods_invocations
from torch.testing._internal.opinfo import core as opinfo_core

S = 5
M = 10


def sample_inputs__local_scalar_dense(op_info, device, dtype, requires_grad, **kwargs):
    del op_info

    shapes = (
        (),
        (1,),
        (3,),
        (1, 1),
        (1, 2),
        (2, 1),
        (1, 1, 1),
        (2, 2, 2),
    )

    for shape in shapes:
        t = torch_testing.make_tensor(
            shape,
            low=0,
            high=1,
            device=device,
            dtype=dtype,
            requires_grad=requires_grad,
            **kwargs,
        )
        yield opinfo_core.SampleInput(t)


def sample_inputs_conv3d(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    make_arg = functools.partial(
        torch_testing.make_tensor, device=device, dtype=dtype, requires_grad=requires_grad
    )

    # Ordered as shapes for input, weight, bias,
    # and a dict of values of (stride, padding, dilation, groups)
    cases: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...], dict[str, Any]] = (  # type: ignore[assignment]
        (
            (1, 3, 3, 224, 224),
            (32, 3, 3, 3, 3),
            None,
            {
                "stride": (2, 2, 2),
                "padding": (1, 1, 1),
                "dilation": (1, 1, 1),
                "groups": 1,
            },
        ),
        (
            (2, 4, 3, 56, 56),
            (32, 4, 3, 3, 3),
            (32,),
            {
                "stride": (3, 3, 3),
                "padding": 2,
                "dilation": (1, 1, 1),
                "groups": 1,
            },
        ),
    )

    for input_shape, weight, bias, kwargs in cases:  # type: ignore[assignment]
        # Batched
        yield opinfo_core.SampleInput(
            make_arg(input_shape),
            args=(make_arg(weight), make_arg(bias) if bias is not None else bias),
            kwargs=kwargs,
        )
        # Unbatched
        yield opinfo_core.SampleInput(
            make_arg(input_shape[1:]),  # type: ignore[index]
            args=(make_arg(weight), make_arg(bias) if bias is not None else bias),
            kwargs=kwargs,
        )


def sample_inputs_convolution(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    make_arg = functools.partial(
        torch_testing.make_tensor, device=device, dtype=dtype, requires_grad=requires_grad
    )

    # Ordered as shapes for input, weight, bias,
    # and a dict of values of (stride, padding, dilation, groups)
    cases: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...], dict[str, Any]] = (  # type: ignore[assignment]
        (
            (1, 3, 4),
            (3, 3, 3),
            (3,),
            {
                "stride": (2,),
                "padding": (2,),
                "dilation": (1,),
                "transposed": False,
                "output_padding": (0,),
                "groups": 1,
            },
        ),
        (
            (1, 3, 4),
            (3, 3, 3),
            None,
            {
                "stride": (2,),
                "padding": (2,),
                "dilation": (1,),
                "transposed": True,
                "output_padding": (0,),
                "groups": 1,
            },
        ),
        (
            (1, 3, 224, 224),
            (32, 3, 3, 3),
            None,
            {
                "stride": (2, 2),
                "padding": (1, 1),
                "dilation": (1, 1),
                "transposed": False,
                "output_padding": (0, 0),
                "groups": 1,
            },
        ),
        (
            (1, 3, 3, 224, 224),
            (32, 3, 3, 3, 3),
            (32,),
            {
                "stride": (2, 2, 2),
                "padding": (1, 1, 1),
                "dilation": (1, 1, 1),
                "transposed": False,
                "output_padding": (0, 0, 0),
                "groups": 1,
            },
        ),
        # FIXME(jiz): Uncomment out these test data once
        # torch 2.0 is released.
        # (
        #     (1, 3, 224, 224, 224),
        #     (32, 3, 3, 3, 3),
        #     (32,),
        #     {
        #         "stride": (2, 2, 2),
        #         "padding": (1, 1, 1),
        #         "dilation": (1, 1, 1),
        #         "transposed": False,
        #         "output_padding": (0, 0, 0),
        #         "groups": 1,
        #     },
        # ),
        (
            (2, 4, 6, 6),
            (4, 1, 3, 3),
            (4,),
            {
                "stride": (3, 2),
                "padding": (1, 1),
                "dilation": (1, 1),
                "transposed": True,
                "output_padding": (0, 0),
                "groups": 4,
            },
        ),
    )

    for input_shape, weight, bias, kwargs in cases:  # type: ignore[assignment]
        yield opinfo_core.SampleInput(
            make_arg(input_shape),
            args=(make_arg(weight), make_arg(bias) if bias is not None else bias),
            kwargs=kwargs,
        )


def sample_inputs_layer_norm(op_info, device, dtype, requires_grad, **kwargs):
    del op_info  # unused
    del kwargs
    make_arg = functools.partial(
        torch_testing.make_tensor, device=device, dtype=dtype, requires_grad=requires_grad
    )

    # Ordered as input shape, normalized_shape, eps
    cases: tuple[tuple[int], tuple[int], float] = (  # type: ignore[assignment]
        ((1, 2, 3), (1, 2, 3), 0.5),
        ((2, 2, 3), (2, 3), -0.5),
        ((1,), (1,), 1e-5),
        ((1, 2), (2,), 1e-5),
        ((0, 1), (1,), 1e-5),
    )

    for input_shape, normalized_shape, eps in cases:  # type: ignore[misc]
        # Shape of weight and bias should be the same as normalized_shape
        weight = make_arg(normalized_shape)  # type: ignore[has-type]
        bias = make_arg(normalized_shape)  # type: ignore[has-type]
        yield opinfo_core.SampleInput(
            make_arg(input_shape),  # type: ignore[has-type]
            args=(normalized_shape, weight, bias, eps),  # type: ignore[has-type]
        )
        yield opinfo_core.SampleInput(
            make_arg(input_shape),  # type: ignore[has-type]
            args=(normalized_shape, None, bias, eps),  # type: ignore[has-type]
        )
        yield opinfo_core.SampleInput(
            make_arg(input_shape),  # type: ignore[has-type]
            args=(normalized_shape, weight, None, eps),  # type: ignore[has-type]
        )
        yield opinfo_core.SampleInput(
            make_arg(input_shape),  # type: ignore[has-type]
            args=(normalized_shape, None, None, eps),  # type: ignore[has-type]
        )


class _TestParamsMaxPoolEmptyStrideBase:
    # Adapted from https://github.com/pytorch/pytorch/blob/d6d55f8590eab05d2536756fb4efcfb2d07eb81a/torch/testing/_internal/common_methods_invocations.py#L3203
    def __init__(self):
        self.kwargs = {
            "kernel_size": [3],
            "stride": [()],
            "ceil_mode": [True, False],
            "padding": [0, 1],
            "dilation": [1],
        }

        # fmt: off
        self.shapes = [
            [1, 2, None],  # batch
            [2],  # channels
            [3, 6]  # signal
        ]
        # fmt: on

    def _gen_shape(self):
        for shape in itertools.product(*self.shapes):
            # shape[0] is None indicates missing batch dimension
            if shape[0] is None:
                shape = shape[1:]

            yield shape, torch.contiguous_format
            # only 2d (N, C, H, W) rank 4 tensors support channels_last memory format
            if len(self.shapes) == 4 and len(shape) == 4:
                yield shape, torch.channels_last

    def _gen_kwargs(self):
        keys = self.kwargs.keys()
        for values in itertools.product(*self.kwargs.values()):
            yield dict(zip(keys, values))

    def gen_input_params(self):
        yield from itertools.product(self._gen_shape(), self._gen_kwargs())


class _TestParamsMaxPool1dEmptyStride(_TestParamsMaxPoolEmptyStrideBase):
    def __init__(self):
        super().__init__()
        self.kwargs["kernel_size"] += [(3,)]
        self.kwargs["stride"] += [(2,)]
        self.kwargs["padding"] += [(1,)]
        self.kwargs["dilation"] += [(1,)]


class _TestParamsMaxPool2dEmptyStride(_TestParamsMaxPoolEmptyStrideBase):
    def __init__(self):
        super().__init__()
        self.kwargs["kernel_size"] += [(3, 2)]
        self.kwargs["stride"] += [(2, 1)]
        self.kwargs["padding"] += [(1, 1)]
        self.kwargs["dilation"] += [(1, 2)]

        self.shapes.append([6])


class _TestParamsMaxPool3dEmptyStride(_TestParamsMaxPoolEmptyStrideBase):
    def __init__(self):
        super().__init__()
        self.kwargs["kernel_size"] += [(3, 2, 3)]
        self.kwargs["stride"] += [(2, 1, 2)]
        self.kwargs["dilation"] += [(1, 2, 1)]

        self.shapes.append([6])
        self.shapes.append([5])


def sample_inputs_max_pool_empty_strides(op_info, device, dtype, requires_grad, **kwargs):
    make_arg = functools.partial(
        torch_testing.make_tensor, device=device, dtype=dtype, requires_grad=False
    )

    # FIXME: (RuntimeError: non-empty 3D or 4D (batch mode) tensor expected for input)

    params_generator_type_dict = {
        "ops.aten.max_pool1d": _TestParamsMaxPool1dEmptyStride,
        "ops.aten.max_pool2d": _TestParamsMaxPool2dEmptyStride,
        "ops.aten.max_pool3d": _TestParamsMaxPool3dEmptyStride,
    }

    params_generator = params_generator_type_dict[op_info.name]()
    for (shape, memory_format), kwargs in params_generator.gen_input_params():
        arg = make_arg(shape).to(memory_format=memory_format).requires_grad_(requires_grad)
        yield opinfo_core.SampleInput(arg, kwargs=kwargs)


def sample_inputs_max_pool1d_with_indices(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    make_arg = functools.partial(
        torch_testing.make_tensor, device=device, dtype=dtype, requires_grad=False
    )
    params_generator = (
        common_methods_invocations._TestParamsMaxPool1d()  # pylint: disable=protected-access
    )
    for (shape, memory_format), kwargs in params_generator.gen_input_params():
        arg = make_arg(shape).to(memory_format=memory_format).requires_grad_(requires_grad)
        yield opinfo_core.SampleInput(arg, kwargs=kwargs)


def sample_inputs_max_pool2d_with_indices(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    make_arg = functools.partial(
        torch_testing.make_tensor, device=device, dtype=dtype, requires_grad=False
    )
    params_generator = (
        common_methods_invocations._TestParamsMaxPool2d()  # pylint: disable=protected-access
    )
    for (shape, memory_format), kwargs in params_generator.gen_input_params():
        arg = make_arg(shape).to(memory_format=memory_format).requires_grad_(requires_grad)
        yield opinfo_core.SampleInput(arg, kwargs=kwargs)


def sample_inputs_max_pool3d_with_indices(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    make_arg = functools.partial(
        torch_testing.make_tensor, device=device, dtype=dtype, requires_grad=False
    )
    params_generator = (
        common_methods_invocations._TestParamsMaxPool3d()  # pylint: disable=protected-access
    )
    for (shape, memory_format), kwargs in params_generator.gen_input_params():
        arg = make_arg(shape).to(memory_format=memory_format).requires_grad_(requires_grad)
        yield opinfo_core.SampleInput(arg, kwargs=kwargs)


def sample_inputs_native_group_norm(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    make_arg = functools.partial(
        torch_testing.make_tensor, device=device, dtype=dtype, requires_grad=requires_grad
    )

    # Ordered as input shape, C,N,HxW, and kwargs for group and eps
    cases = (
        ((1, 6, 3), (6,), (6,), 1, 6, 3, {"group": 2, "eps": 0.5}),
        ((2, 6, 3), (6,), (6,), 2, 6, 3, {"group": 3, "eps": -0.5}),
        ((5, 5, 5), (5,), (5,), 5, 5, 5, {"group": 1, "eps": 1e-5}),
        ((5, 8, 10), (8,), (8,), 5, 8, 10, {"group": 4, "eps": 1e-5}),
    )

    for input_shape, weight, bias, N, C, HxW, kwargs in cases:
        # args: running mean, running var, weight and bias should necessarily be of shape: (channels,)
        channels = input_shape[1] if len(input_shape) > 1 else 0
        weight = make_arg(channels) if channels > 0 else None
        bias = make_arg(channels) if channels > 0 else None

        yield opinfo_core.SampleInput(
            make_arg(input_shape),
            args=(
                weight,
                bias,
                N,
                C,
                HxW,
            ),
            kwargs=kwargs,
        )


def sample_inputs_col2im(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    # input_shape, output_size, kernal, dilation, padding, stride
    cases = (
        (
            (1, 12, 12),
            (4, 5),
            (2, 2),
            {"dilation": (1, 1), "padding": (0, 0), "stride": (1, 1)},
        ),
        (
            (1, 8, 30),
            (4, 5),
            (2, 2),
            {"dilation": (1, 1), "padding": (1, 1), "stride": (1, 1)},
        ),
        (
            (1, 8, 9),
            (4, 4),
            (2, 2),
            {"dilation": (1, 1), "padding": (0, 0), "stride": (1, 1)},
        ),
        (
            (1, 8, 25),
            (4, 4),
            (2, 2),
            {"dilation": (1, 1), "padding": (1, 1), "stride": (1, 1)},
        ),
        (
            (1, 8, 9),
            (4, 4),
            (2, 2),
            {"dilation": (1, 1), "padding": (1, 1), "stride": (2, 2)},
        ),
        (
            (1, 9, 4),
            (4, 4),
            (3, 3),
            {"dilation": (1, 1), "padding": (1, 1), "stride": (2, 2)},
        ),
        (
            (1, 18, 16),
            (2, 2),
            (1, 1),
            {"dilation": (2, 2), "padding": (3, 3), "stride": (2, 2)},
        ),
    )

    make_arg = functools.partial(
        torch_testing.make_tensor, device=device, dtype=dtype, requires_grad=requires_grad
    )
    for shape, output_size, kernel_size, kwargs in cases:
        tensor = make_arg(shape)
        yield opinfo_core.SampleInput(tensor, args=(output_size, kernel_size), kwargs=kwargs)


def sample_inputs_index(op_info, device, dtype, requires_grad, **kwargs):
    del op_info  # Unused
    del kwargs  # Unused
    make_arg = functools.partial(
        torch_testing.make_tensor, dtype=dtype, device=device, requires_grad=requires_grad
    )
    s = 5
    index_1d = common_methods_invocations.index_variable(2, s, device=device)
    index_2d = common_methods_invocations.index_variable((s + 1, 2), s, device=device)
    index_3d = common_methods_invocations.index_variable((s + 2, s + 1, 2), s, device=device)
    test_args = [
        ([index_1d],),
        ([None, index_1d],),
        ([None, None, None, index_1d],),
        ([index_1d, None],),
        ([index_1d, None, None],),
        # Extra index
        ([None, index_1d, None, index_1d],),
        ([index_1d, None, index_1d, None],),
        ([None, index_1d, index_1d, None],),
        ([index_2d],),
        ([None, index_2d],),
        ([None, None, None, index_2d],),
        ([index_2d, None],),
        ([index_2d, None, None],),
        # Extra index
        ([None, index_2d, None, index_2d],),
        ([index_2d, None, index_2d, None],),
        ([None, index_2d, index_2d, None],),
        ([index_3d],),
        ([None, index_3d],),
        ([None, None, None, index_3d],),
        ([index_3d, None],),
        ([index_3d, None, None],),
        # Extra index
        ([None, index_3d, None, index_3d],),
        ([index_3d, None, index_3d, None],),
        ([None, index_3d, index_3d, None],),
        # Mixed indices
        ([None, index_3d, index_1d, index_2d],),
        # All indices are not None
        ([index_2d, index_3d, index_1d],),
        ([index_2d, index_3d, index_1d, index_2d],),
    ]

    for args in test_args:
        yield opinfo_core.SampleInput(make_arg((s, s, s, s)), args=args)


def sample_inputs_native_dropout(
    op_info, device, dtype, requires_grad, *, valid_input_dim=None, **kwargs
):
    del op_info  # Unused
    del kwargs  # Unused
    make_arg = functools.partial(
        torch_testing.make_tensor, device=device, dtype=dtype, requires_grad=requires_grad
    )

    if valid_input_dim:
        cases = ((S,) * i for i in valid_input_dim)
    else:
        cases = ((S, S), (S,), ())
    # ONNX requires 0 <= p < 1
    p_vals = [0.0]

    training_vals = [True, False]

    for case, p, training in itertools.product(cases, p_vals, training_vals):
        yield opinfo_core.SampleInput(make_arg(case), p=p, train=training)


def sample_inputs_stft(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    del kwargs

    def mt(shape, **kwargs):
        return torch_testing.make_tensor(
            shape, device=device, dtype=dtype, requires_grad=requires_grad, **kwargs
        )

    yield opinfo_core.SampleInput(mt(100), n_fft=10, return_complex=True)
    yield opinfo_core.SampleInput(mt(100), n_fft=10, return_complex=False)
    if dtype.is_complex:
        yield opinfo_core.SampleInput(mt(100), n_fft=10)

    yield opinfo_core.SampleInput(mt(10), n_fft=7, return_complex=True)
    yield opinfo_core.SampleInput(mt((10, 100)), n_fft=16, hop_length=4, return_complex=True)

    window = mt(16, low=0.5, high=2.0)
    yield opinfo_core.SampleInput(
        mt((2, 100)), kwargs=dict(n_fft=16, window=window, return_complex=True)
    )
    yield opinfo_core.SampleInput(
        mt((3, 100)), kwargs=dict(n_fft=16, window=window, return_complex=True)
    )
    if not dtype.is_complex:
        yield opinfo_core.SampleInput(
            mt((10, 100)), n_fft=16, window=window, onesided=False, return_complex=True
        )


def sample_inputs_tensor_bool(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    del device
    del requires_grad
    del kwargs
    yield opinfo_core.SampleInput(True, dtype=dtype)
    yield opinfo_core.SampleInput(False, dtype=dtype)


def sample_inputs_tensor_float(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    del device
    del requires_grad
    del kwargs
    yield opinfo_core.SampleInput(3.0, dtype=dtype)
    yield opinfo_core.SampleInput(-1.0, dtype=dtype)


def sample_inputs_tensor_int(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    del device
    del requires_grad
    del kwargs
    yield opinfo_core.SampleInput(2, dtype=dtype)
    yield opinfo_core.SampleInput(-5, dtype=dtype)


def sample_inputs_bernoulli_p(op_info, device, dtype, requires_grad, **kwargs):
    del op_info

    shapes = [
        [3],
        [],
        [3, 2],
        [2, 3, 2],
    ]

    for shape in shapes:
        for p in (0, 0.5, 1):
            t = torch_testing.make_tensor(
                shape,
                low=0,
                high=1,
                device=device,
                dtype=dtype,
                requires_grad=requires_grad,
                **kwargs,
            )
            yield opinfo_core.SampleInput(t, args=(p,))
            yield opinfo_core.SampleInput(t, kwargs={"p": p})


def sample_inputs_bernoulli_p_deterministic(op_info, device, dtype, requires_grad, **kwargs):
    del op_info

    shapes = [
        [3],
        [],
        [3, 2],
        [2, 3, 2],
    ]

    for shape in shapes:
        for p in (0, 1):
            t = torch_testing.make_tensor(
                shape,
                low=0,
                high=1,
                device=device,
                dtype=dtype,
                requires_grad=requires_grad,
                **kwargs,
            )
            yield opinfo_core.SampleInput(t, args=(p,))
            yield opinfo_core.SampleInput(t, kwargs={"p": p})


def sample_inputs_embedding_bag(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    del kwargs

    def make_input(shape):
        return common_methods_invocations.make_tensor(
            shape, device=device, dtype=dtype, requires_grad=requires_grad
        )

    def make_long_input(shape, *, low, high, noncontiguous=False):
        return common_methods_invocations.make_tensor(
            shape,
            device=device,
            dtype=torch.long,
            low=low,
            high=high,
            noncontiguous=noncontiguous,
        )

    def make_per_sample_weight(flag, idx):
        # a tensor of float / double weights, or None
        # to indicate all weights should be taken to be 1
        if flag:
            return make_input(idx.reshape(-1).shape)
        return None

    offsets = [
        torch.tensor([0, 2, 3], device=device, dtype=torch.long),
        torch.tensor([0, 0, 2], device=device, dtype=torch.long),
        torch.tensor([0, 2, 2, 4], device=device, dtype=torch.long),
    ]
    for offset in offsets:
        for include_last_offset in (True, False):
            for generate_per_sample_weight in (True, False):
                for mode in (
                    0,
                    1,
                    2,
                ):  # ('sum', 'mean', 'max')
                    # per_sample_weights only support mode='sum'
                    if generate_per_sample_weight and mode in (1, 2):  # ('mean', 'max'):
                        continue

                    # 1-D index tensor
                    indices = make_long_input((S,), low=0, high=M)
                    per_sample_weights = make_per_sample_weight(
                        generate_per_sample_weight, indices
                    )
                    # 0
                    yield common_methods_invocations.SampleInput(
                        make_input((M, S)),
                        args=(indices,),
                        kwargs={
                            "offsets": offset,
                            "mode": mode,
                            "per_sample_weights": per_sample_weights,
                            "include_last_offset": include_last_offset,
                        },
                    )

                    indices = make_long_input((S,), low=0, high=M, noncontiguous=True)
                    per_sample_weights = make_per_sample_weight(
                        generate_per_sample_weight, indices
                    )
                    # 1
                    yield common_methods_invocations.SampleInput(
                        make_input((M, S)),
                        args=(indices,),
                        kwargs={
                            "offsets": offset,
                            "mode": mode,
                            "per_sample_weights": per_sample_weights,
                            "include_last_offset": include_last_offset,
                        },
                    )

                    if mode != 2:  # "max" mode in 2-D index tensor make aten func crash
                        # 2-D index tensor
                        indices = make_long_input((S, S), low=0, high=M)
                        per_sample_weights = make_per_sample_weight(
                            generate_per_sample_weight, indices
                        )
                        # 2
                        yield common_methods_invocations.SampleInput(
                            make_input((M, S)),
                            args=(indices,),
                            kwargs={
                                "offsets": offset,
                                "mode": mode,
                                "per_sample_weights": per_sample_weights,
                                "include_last_offset": include_last_offset,
                            },
                        )

                        indices = make_long_input((S, S), low=0, high=M, noncontiguous=True)
                        per_sample_weights = make_per_sample_weight(
                            generate_per_sample_weight, indices
                        )
                        # 3
                        yield common_methods_invocations.SampleInput(
                            make_input((M, S)),
                            args=(indices,),
                            kwargs={
                                "offsets": offset,
                                "mode": mode,
                                "per_sample_weights": per_sample_weights,
                                "include_last_offset": include_last_offset,
                            },
                        )


def sample_inputs_embedding_bag_padding_idx(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    del kwargs

    def make_input(shape):
        return common_methods_invocations.make_tensor(
            shape, device=device, dtype=dtype, requires_grad=requires_grad
        )

    def make_long_input(shape, *, low, high, noncontiguous=False):
        return common_methods_invocations.make_tensor(
            shape,
            device=device,
            dtype=torch.long,
            low=low,
            high=high,
            noncontiguous=noncontiguous,
        )

    def make_per_sample_weight(flag, idx):
        # a tensor of float / double weights, or None
        # to indicate all weights should be taken to be 1
        if flag:
            return make_input(idx.reshape(-1).shape)
        return None

    offsets = [
        torch.tensor([0, 2, 3], device=device, dtype=torch.long),
        # Below case not work for FullGraph mode, guess due to op.While() bug:
        # when the initial condition is False, it still excute the loop body once.
        # torch.tensor([0, 0, 2], device=device, dtype=torch.long),
        # torch.tensor([0, 2, 2, 4], device=device, dtype=torch.long),
    ]
    for offset in offsets:
        for include_last_offset in (True, False):
            for generate_per_sample_weight in (True, False):
                for mode in (
                    0,
                    1,
                    2,
                ):  # ('sum', 'mean', 'max')
                    # per_sample_weights only support mode='sum'
                    if generate_per_sample_weight and mode in (1, 2):  # ('mean', 'max'):
                        continue

                    for padding_idx in (-1, 0, 1, 2, 3):
                        # 1-D index tensor
                        indices = make_long_input((S,), low=0, high=M)
                        per_sample_weights = make_per_sample_weight(
                            generate_per_sample_weight, indices
                        )
                        # 0
                        yield common_methods_invocations.SampleInput(
                            make_input((M, S)),
                            args=(indices,),
                            kwargs={
                                "offsets": offset,
                                "scale_grad_by_freq": False,
                                "mode": mode,
                                "sparse": False,
                                "per_sample_weights": per_sample_weights,
                                "include_last_offset": include_last_offset,
                                "padding_idx": padding_idx,
                            },
                        )

                        indices = make_long_input((S,), low=0, high=M, noncontiguous=True)
                        per_sample_weights = make_per_sample_weight(
                            generate_per_sample_weight, indices
                        )
                        # 1
                        yield common_methods_invocations.SampleInput(
                            make_input((M, S)),
                            args=(indices,),
                            kwargs={
                                "offsets": offset,
                                "scale_grad_by_freq": False,
                                "mode": mode,
                                "sparse": False,
                                "per_sample_weights": per_sample_weights,
                                "include_last_offset": include_last_offset,
                                "padding_idx": padding_idx,
                            },
                        )

                        # if mode != 2:  # "max" mode in 2-D index tensor make aten func crash
                        #     # 2-D index tensor
                        #     indices = make_long_input((S, S), low=0, high=M)
                        #     per_sample_weights = make_per_sample_weight(
                        #         generate_per_sample_weight, indices
                        #     )
                        #     # 2
                        #     yield common_methods_invocations.SampleInput(
                        #         make_input((M, S)),
                        #         args=(indices,),
                        #         kwargs={
                        #             "offsets": offset,
                        #             "mode": mode,
                        #             "per_sample_weights": per_sample_weights,
                        #             "include_last_offset": include_last_offset,
                        #             "padding_idx": padding_idx,
                        #         },
                        #     )

                        #     indices = make_long_input((S, S), low=0, high=M, noncontiguous=True)
                        #     per_sample_weights = make_per_sample_weight(
                        #         generate_per_sample_weight, indices
                        #     )
                        #     # 3
                        #     yield common_methods_invocations.SampleInput(
                        #         make_input((M, S)),
                        #         args=(indices,),
                        #         kwargs={
                        #             "offsets": offset,
                        #             "mode": mode,
                        #             "per_sample_weights": per_sample_weights,
                        #             "include_last_offset": include_last_offset,
                        #             "padding_idx": padding_idx,
                        #         },
                        #     )


def sample_inputs_unfold(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    # Case `target_end == 1`, where `target_end = (input.size(dimension) - size) // step + 1`.
    t = torch_testing.make_tensor(
        (2, 3, 4),
        device=device,
        dtype=dtype,
        requires_grad=requires_grad,
        **kwargs,
    )
    dimension = 1
    size = 2
    step = 2
    # target_end = (3 - 2) // 2 + 1 = 1
    yield opinfo_core.SampleInput(t, args=(dimension, size, step))


def sample_inputs_slice_scatter(op_info, device, dtype, requires_grad, **kwargs):
    del op_info
    del kwargs
    make_arg = functools.partial(
        torch_testing.make_tensor, dtype=dtype, device=device, requires_grad=requires_grad
    )

    L = 20
    cases = (
        ((L, L, L), (L, L, L), (0, 0, L, 1)),
        ((L, L, L), (L // 2, L, L), (0, L // 2, L, 1)),
        ((L, L, L), (L // 4, L, L), (0, L // 2, L, 2)),
        ((L, L, L), (L, L, L), (1, 0, L, 1)),
        ((L, L, L), (L, L // 2, L), (1, L // 2, L, 1)),
        ((L, L, L), (L, L // 4, L), (1, L // 2, L, 2)),
        ((L, L, L), (L, L, L), (2, 0, L, 1)),
        ((L, L, L), (L, L, L // 2), (2, L // 2, L, 1)),
        ((L, L, L), (L, L, L // 4), (2, L // 2, L, 2)),
        ((L, L, L), (L, L // 2, L), (1, L // 2, L * 2, 1)),  # end > L
        ((L, L, L), (L, L, L), (-2, 0, L, 1)),  # negative dim
        ((L, L, L), (L, L, L // 4), (-1, L // 2, L * 2, 2)),  # end > L and negative dim
    )

    for input_shape, src_shape, args in cases:
        input_ = make_arg(input_shape)
        src = make_arg(src_shape)
        yield opinfo_core.SampleInput(input_, args=(src, *args))


def sample_inputs__softmax(
    op_info,
    device,
    dtype,
    requires_grad,
    **kwargs,
):
    del op_info  # Unused

    make_arg = functools.partial(
        torch_testing.make_tensor, device=device, dtype=dtype, requires_grad=requires_grad
    )
    cases = [
        ((S,), (0,)),
        ((S, S), (0,)),
        ((S, S), (1,)),
        ((S, S), (-1,)),
        ((S, M, S), (2,)),
        ((S, 0, 0), (-1,)),
    ]

    for (shape, dim), half_to_float in itertools.product(cases, (False,)):
        # NOTE: softmax with half to float conversion is not supported on CPU
        # So we don't test it here
        kwargs = dict(half_to_float=half_to_float)
        yield opinfo_core.SampleInput(make_arg(shape), args=dim, kwargs=kwargs)


def sample_inputs_scaled_dot_product_flash_attention(
    op_info, device, dtype, requires_grad, **kwargs
):
    del op_info
    del kwargs

    make = opinfo_core.partial(
        opinfo_core.make_tensor, device=device, dtype=dtype, requires_grad=requires_grad
    )
    batch, seq_q, seq_kv, num_heads, head_dim = 4, 3, 6, 4, 8

    dim_4_q_shape = (batch, num_heads, seq_q, head_dim)
    dim_4_kv_shape = (batch, num_heads, seq_kv, head_dim)

    qkv_shapes = [(dim_4_q_shape, dim_4_kv_shape)]
    samples = []
    for qkv_shape, is_causal, dropout_p in opinfo_core.product(
        qkv_shapes, [True, False], [0.0]
    ):
        shape_q, shape_kv = qkv_shape
        samples.append(
            opinfo_core.SampleInput(
                make(shape_q),
                make(shape_kv),
                make(shape_kv),
                is_causal=is_causal,
                dropout_p=dropout_p,
            )
        )

    # Add an attn_mask
    samples.append(
        opinfo_core.SampleInput(
            make((batch, num_heads, seq_q, head_dim)),
            make((batch, num_heads, seq_kv, head_dim)),
            make((batch, num_heads, seq_kv, head_dim)),
            is_causal=False,
            dropout_p=0.0,
        )
    )

    yield from samples


# NOTE: How to create an OpInfo:
# 1. Create a function that generates sample inputs for the op.
#    This function should yield SampleInputs.
#    Use `sample_inputs_col2im` as an example.
# 2. Specify dtypes that the op supports.
# 3. Use how you would call the op in PyTorch as the name of the OpInfo.
#    For example, `torch.ops.aten.col2im` should be named "ops.aten.col2im".
#    This way OpInfo knows to use `torch.ops.aten.col2im` as the op.
#    See the docstring of OpInfo for more details.
#
#    This name is used as the unique ID to connect `TorchLibOpInfo("unique_name", ...)``
#    in ops_test_data.py and opinfo_core.OpInfo("unique_name", ...)
#    To avoid name duplication, it is possible to rename the OpInfo and specify
#    the `op` field explicitly.
OP_DB: List[opinfo_core.OpInfo] = [
    opinfo_core.OpInfo(
        "ops.aten._local_scalar_dense",
        aten_name="_local_scalar_dense",
        dtypes=common_dtype.all_types(),
        sample_inputs_func=sample_inputs__local_scalar_dense,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.col2im",
        aten_name="col2im",
        dtypes=common_dtype.floating_and_complex_types_and(torch.half, torch.bfloat16),
        sample_inputs_func=sample_inputs_col2im,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.embedding_bag",
        aten_name="embedding_bag",
        dtypes=common_dtype.floating_types_and_half(),
        sample_inputs_func=sample_inputs_embedding_bag,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.embedding_bag.padding_idx",
        aten_name="embedding_bag.padding_idx",
        dtypes=common_dtype.floating_types_and_half(),
        sample_inputs_func=sample_inputs_embedding_bag_padding_idx,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "nn.functional.conv3d",
        aten_name="conv3d",
        dtypes=common_dtype.floating_and_complex_types_and(torch.int64, torch.bfloat16),
        sample_inputs_func=sample_inputs_conv3d,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.convolution",
        aten_name="convolution",
        dtypes=common_dtype.floating_and_complex_types_and(torch.int64, torch.bfloat16),
        sample_inputs_func=sample_inputs_convolution,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.index.Tensor",
        aten_name="index.Tensor",
        dtypes=common_dtype.all_types_and_complex_and(
            torch.bool, torch.float16, torch.bfloat16, torch.chalf
        ),
        sample_inputs_func=sample_inputs_index,
    ),
    opinfo_core.OpInfo(
        "ops.aten.layer_norm",
        aten_name="layer_norm",
        dtypes=common_dtype.floating_and_complex_types_and(torch.int64, torch.bfloat16),
        sample_inputs_func=sample_inputs_layer_norm,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.max_pool1d",
        variant_test_name="empty_strides",
        aten_name="max_pool1d",
        dtypes=common_dtype.floating_types_and(torch.bfloat16),
        sample_inputs_func=sample_inputs_max_pool_empty_strides,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.max_pool2d",
        variant_test_name="empty_strides",
        aten_name="max_pool2d",
        dtypes=common_dtype.floating_types_and(torch.bfloat16),
        sample_inputs_func=sample_inputs_max_pool_empty_strides,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.max_pool3d",
        variant_test_name="empty_strides",
        aten_name="max_pool3d",
        dtypes=common_dtype.floating_types_and(torch.bfloat16),
        sample_inputs_func=sample_inputs_max_pool_empty_strides,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.native_dropout",
        aten_name="native_dropout",
        dtypes=common_dtype.all_types_and_half(),
        sample_inputs_func=sample_inputs_native_dropout,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.native_group_norm",
        aten_name="native_group_norm",
        dtypes=common_dtype.floating_and_complex_types_and(torch.half, torch.bfloat16),
        sample_inputs_func=sample_inputs_native_group_norm,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "nn.functional.max_pool1d_with_indices",
        aten_name="max_pool1d_with_indices",
        dtypes=common_dtype.floating_types_and(torch.bfloat16),
        sample_inputs_func=sample_inputs_max_pool1d_with_indices,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "nn.functional.max_pool2d_with_indices",
        aten_name="max_pool2d_with_indices",
        dtypes=common_dtype.floating_types_and(torch.bfloat16),
        sample_inputs_func=sample_inputs_max_pool2d_with_indices,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "nn.functional.max_pool3d_with_indices",
        aten_name="max_pool3d_with_indices",
        dtypes=common_dtype.floating_types_and(torch.bfloat16),
        sample_inputs_func=sample_inputs_max_pool3d_with_indices,
        supports_out=False,
    ),
    # NOTE: torch.STFT has pre-padding and it's not supported by aten::stft
    # This custom OpInfo uses aten::stft directly.
    opinfo_core.OpInfo(
        "ops.aten.stft",
        aten_name="stft",
        dtypes=common_dtype.floating_and_complex_types_and(torch.half, torch.bfloat16),
        sample_inputs_func=sample_inputs_stft,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.tensor.bool",
        aten_name="tensor.bool",
        dtypes=common_dtype.all_types_and(torch.half, torch.bfloat16),
        sample_inputs_func=sample_inputs_tensor_bool,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.tensor.float",
        aten_name="tensor.float",
        dtypes=common_dtype.all_types_and(torch.half, torch.bfloat16),
        sample_inputs_func=sample_inputs_tensor_float,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.tensor.int",
        aten_name="tensor.int",
        dtypes=common_dtype.all_types_and(torch.half, torch.bfloat16),
        sample_inputs_func=sample_inputs_tensor_int,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.bernoulli.p",
        aten_name="bernoulli.p",
        # dtypes can be a tuple of (torch.float, torch.double).
        dtypes=common_dtype.all_types(),
        sample_inputs_func=sample_inputs_bernoulli_p,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        # Deterministic bernoulli sampling where p is either 0 or 1
        "ops.aten.bernoulli.p_deterministic",
        op=torch.ops.aten.bernoulli.p,
        aten_name="bernoulli.p",
        dtypes=common_dtype.all_types(),
        sample_inputs_func=sample_inputs_bernoulli_p_deterministic,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "unfold_extra",
        op=lambda x, *args: x.unfold(*args),
        aten_name="unfold",
        dtypes=common_dtype.all_types(),
        sample_inputs_func=sample_inputs_unfold,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten.slice_scatter",
        aten_name="slice_scatter",
        dtypes=common_dtype.all_types_and(torch.bfloat16, torch.half, torch.bool),
        sample_inputs_func=sample_inputs_slice_scatter,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten._softmax",
        aten_name="_softmax",
        dtypes=common_dtype.floating_types_and_half(),
        sample_inputs_func=sample_inputs__softmax,
        supports_out=False,
    ),
    opinfo_core.OpInfo(
        "ops.aten._scaled_dot_product_flash_attention",
        aten_name="_scaled_dot_product_flash_attention",
        dtypes=common_dtype.floating_types_and(torch.bfloat16),
        # NOTE: Different from aten::scaled_dot_product_attention, this op doesn't support
        #       dim<=3 input.
        sample_inputs_func=sample_inputs_scaled_dot_product_flash_attention,
        supports_out=False,
        supports_forward_ad=False,
        supports_fwgrad_bwgrad=True,
        check_batched_forward_grad=False,
    ),
]
