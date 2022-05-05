
import onnxscript
from onnxscript import script
from onnxscript.onnx import opset15 as op
from onnxscript.onnx_types import INT64
from typing import List

# TODO: Need to verify definitions below.
# Behavior for integral types is not explicitly described in ONNX spec.
# Need to verify if any issues exist with numeric precision.


@script()
def ReduceSumSquare(data, axes: List[int],  keepdims: int):
    # Note: attribute input is promoted to input when calling ReduceSum
    return op.ReduceSum(data * data, axes, keepdims=keepdims)


@script()
def ReduceL1(data, axes: List[int],  keepdims: int):
    return op.ReduceSum(op.Abs(data), axes, keepdims=keepdims)


@script()
def ReduceL2(data, axes: List[int],  keepdims: int):
    # TODO: ONNX spec is unclear about behavior for integral types!
    sum_square = op.ReduceSum(data * data, axes, keepdims=keepdims)
    # TODO: must cast for integral types
    return op.Sqrt(sum_square)


@script()
def ReduceLogSum(data, axes: List[int],  keepdims: int):
    return op.Log(op.ReduceSum(data, axes, keepdims=keepdims))


@script()
def ReduceLogSumExp(data, axes: List[int],  keepdims: int):
    return op.Log(op.ReduceSum(op.Exp(data), axes, keepdims=keepdims))


@script()
def Hardmax(X, axis: int):
    '''
    Hardmax is similar to ArgMax, with the result being encoded OneHot style.
    '''
    argmax = op.ArgMax(X, axis=axis, keepdims=False)
    # Get the size of input X along specified axis
    # Unfortunately, we cannot say `end=axis+1`.
    # No computation possible on attributes.
    xshape = op.Shape(X, start=axis)
    zero = op.Constant(value_ints=[0])
    depth = op.GatherElements(xshape, zero)
    empty_shape = op.Constant(value_ints=[0])
    depth = op.Reshape(depth, empty_shape)
    values = op.Constant(value_ints=[0, 1])
    cast_values = op.CastLike(values, X)
    return op.OneHot(argmax, depth, cast_values, axis=axis)


# TODO: find a way to replace the name 'Hardmax2' with 'Hardmax'
# TODO: if uncommented, fails at converter.eval_attr()
# @script()
# def Hardmax2(X, axis: int):
#     '''
#     This is an alternative encoding of Hardmax using ReduceMax.
#     Unfortunately, this is hard to encode in ONNX because Hardmax has a single
#     axis attribute, while ReduceMax has a list of axes as attribute.
#     ONNX has no mechanism to transform the axis parameter to axes,
#     thas is, to translate the `axes=[axis]` code below.
#     '''
#     # axes=[axis] is not working yet
#     maxval = op.ReduceMax(X, axes=[axis], keepdims=True)
#     ismaxval = op.Equal(X, maxval)
#     # Must select only the first occurrence of maxval
#     ismaxval_int = op.Cast(ismaxval, to=INT64.dtype)
#     cumsum = op.Cumsum(ismaxval_int, axis, exclusive=True)
#     no_earlier_maxval = op.Equal(cumsum, 0)
#     return (ismaxval and no_earlier_maxval)


@script()
def DepthToSpace(input, blocksize: int, mode: str):
    # Get dimensions of input
    b, c, h, w = op.Split(op.Shape(input), [1, 1, 1, 1])
    # Create a 1D tensor representing blocksize
    size_0 = op.Constant(value_int=blocksize)
    size = op.Reshape(size_0, [1])
    if (mode == 'DCR'):
        tmpshape = op.Concat(b, size, size, c / (size*size), h, w, axis=0)
        reshaped = op.Reshape(input, tmpshape)
        transposed = op.Transpose(reshaped, perm=[0, 3, 4, 1, 5, 2])
    else:
        # assert mode == "CRD"
        tmpshape = op.Concat(b, c / (size * size), size, size, h, w, axis=0)
        reshaped = op.Reshape(input, tmpshape)
        transposed = op.Transpose(reshaped, perm=[0, 1, 4, 2, 5, 3])
    finalshape = op.Concat(b, c / (size*size), h * size, w * size, axis=0)
    y = op.Reshape(transposed, finalshape)
    return y


@script()
def SpaceToDepth(input, blocksize: int):
    # Inverse of DepthToSpace (mode 'DCR')
    b, C, H, W = op.Split(op.Shape(input), [1, 1, 1, 1], axis=0)
    size_0 = op.Constant(value_int=blocksize)
    # size = op.Reshape(size_0, onnxscript.make_tensor('one', 7, [1], [1])) # TensorProto.INT64: 7
    size = op.Reshape(size_0, [1])
    # Reshape to [b, C, H/size, size, W/size, size]
    tmpshape = op.Concat(b, C, H/size, size, W/size, size, axis=0)
    reshaped = op.Reshape(input, tmpshape)
    transposed = op.Transpose(reshaped, perm=[0, 3, 5, 1, 2, 4])
    finalshape = op.Concat(b, C * size * size, H/size, W/size, axis=0)
    y = op.Reshape(transposed, finalshape)
    return y
