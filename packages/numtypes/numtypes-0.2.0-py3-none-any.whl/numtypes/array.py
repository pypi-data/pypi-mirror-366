from typing import Sequence, Type, TypeGuard, overload
from types import EllipsisType

from numtypes.types import Shape, AnyShape, UnknownShape, ArrayType, Array, Dim1, Dim2
from numtypes.debug import config

import numpy as np


def array[S: Shape, T: ArrayType](
    elements: Sequence, *, dtype: Type[T] = np.float64, shape: S
) -> Array[S, T]:
    """Creates a numpy array with the given shape and type.

    Args:
        elements: The elements to create the array from.
        dtype: The type of the array. Defaults to np.float64.
        shape: The shape of the array. Use -1 if you don't want to check the size of a specific dimension.

    Returns:
        A numpy array with the given shape and type. The advantage of this function is that it
        tells the type checker what the shape of the array is.
    """

    result = np.array(elements, dtype=dtype)

    assert shape_of(result, matches=shape)

    return result


@overload
def array_1d[T: ArrayType](
    elements: Sequence, *, dtype: Type[T] = np.float64
) -> Array[Dim1, T]:
    """Creates a 1D numpy array with the given elements and type.

    Args:
        elements: The elements to create the array from.
        dtype: The type of the array. Defaults to np.float64.

    Returns:
        A 1D numpy array with the given elements and type. The advantage of this function is that
        it tells the type checker what the shape of the array is.
    """
    ...


@overload
def array_1d[T: ArrayType, L: tuple[int]](
    elements: Sequence, *, dtype: Type[T] = np.float64, length: L
) -> Array[L, T]:
    """Creates a 1D numpy array with the given elements and type.

    Args:
        elements: The elements to create the array from.
        dtype: The type of the array. Defaults to np.float64.
        length: The length of the array (as a tuple of one integer). This is used to specify the exact
            length of the array.

    Returns:
        A 1D numpy array with the given elements and type. The advantage of this function is that
        it tells the type checker what the shape of the array is.
    """
    ...


def array_1d[T: ArrayType, L: tuple[int]](
    elements: Sequence, *, dtype: Type[T] = np.float64, length: L | None = None
) -> Array[Dim1 | L, T]:
    result = np.array(elements, dtype=dtype)

    assert shape_of(result, matches=(len(elements),) if length is None else length)

    return result


@overload
def array_2d[T: ArrayType](
    elements: Sequence[Sequence], *, dtype: Type[T] = np.float64
) -> Array[Dim2, T]:
    """Creates a 2D numpy array with the given elements and type.

    Args:
        elements: The elements to create the array from. Each element should be a sequence
            representing a row of the 2D array.
        dtype: The type of the array. Defaults to np.float64.

    Returns:
        A 2D numpy array with the given elements and type. The advantage of this function is that
        it tells the type checker what the shape of the array is.
    """


@overload
def array_2d[T: ArrayType, S: tuple[int, int]](
    elements: Sequence[Sequence], *, dtype: Type[T] = np.float64, shape: S
) -> Array[S, T]:
    """Creates a 2D numpy array with the given elements and type.

    Args:
        elements: The elements to create the array from. Each element should be a sequence
            representing a row of the 2D array.
        dtype: The type of the array. Defaults to np.float64.
        shape: The shape of the array (as a tuple of two integers). This is used to specify the exact
            shape of the array.

    Returns:
        A 2D numpy array with the given elements and type. The advantage of this function is that
        it tells the type checker what the shape of the array is.
    """


def array_2d[T: ArrayType, S: tuple[int, int]](
    elements: Sequence[Sequence], *, dtype: Type[T] = np.float64, shape: S | None = None
) -> Array[Dim2 | S, T]:
    result = np.array(elements, dtype=dtype)

    assert shape_of(
        result, matches=(len(elements), len(elements[0])) if shape is None else shape
    )

    return result


@overload
def shape_of[ShapeT: Shape, DataT: ArrayType](
    array: Array[UnknownShape, DataT],
    /,
    *,
    matches: ShapeT,
    name: str = "array",
) -> TypeGuard[Array[ShapeT, DataT]]:
    """Verifies that the shape of the given array matches the expected shape.

    Args:
        array: The array to check. If used together with an assert, the type of the
            array will be inferred by the type checker.
        matches: The expected shape. Use -1 if you don't want to check the size of a
            specific dimension.
        name: The name of the array. Used in the error message.

    Returns:
        True, which indicates that the shape of the array match the expected shape. If
        the shape does not match, an AssertionError is raised instead.
    """
    ...


@overload
def shape_of[DataT: ArrayType](
    array: Array[UnknownShape, DataT],
    /,
    *,
    matches: tuple[int | EllipsisType, ...],
    name: str = "array",
) -> TypeGuard[Array[AnyShape, DataT]]:
    """Verifies that the shape of the given array matches the expected shape.

    Args:
        array: The array to check. If used together with an assert, the type of the
            array will be inferred by the type checker.
        matches: The expected shape. Use -1 if you don't want to check the size of a
            specific dimension. Use `...` to skip checking the remaining dimensions.
        name: The name of the array. Used in the error message.

    Returns:
        True, which indicates that the shape of the array matches the expected shape. If
        the shape does not match, an AssertionError is raised instead.

    Note:
        If the `matches` parameter contains an ellipsis (`...`), it is only allowed as the last element.
        In addition, calling this function will no longer provide type information about the shape of the array.
    """
    ...


def shape_of[ShapeT: Shape, DataT: ArrayType](
    array: Array[UnknownShape, DataT],
    /,
    *,
    matches: ShapeT | tuple[int | EllipsisType, ...],
    name: str = "array",
) -> TypeGuard[Array[ShapeT, DataT]]:
    ellipsis_indices = tuple(
        i for i, expected in enumerate(matches) if expected is Ellipsis
    )

    assert len(ellipsis_indices) == 0 or (
        len(ellipsis_indices) == 1 and ellipsis_indices[0] == len(matches) - 1
    ), (
        "You can place `...` in the shape only as the last element. This means that you "
        "don't want to check the size and number of the remaining dimensions. "
        f"Got {len(ellipsis_indices)} occurrences of `...` in {matches} at indices {ellipsis_indices}."
    )

    if len(ellipsis_indices) == 1:
        matches = matches[:-1] + (-1,) * max(0, len(array.shape) - len(matches) + 1)

    _verify(
        all(
            actual == expected
            for actual, expected in zip(array.shape, matches)
            if expected != -1
        )
        and len(array.shape) == len(matches),
        f"Expected the {name} to have shape {matches}, but got {array.shape}.",
    )

    return True


def _verify(condition: bool, message: str) -> None:
    if condition:
        return

    config.debugger()
    config.logger(message)

    assert condition, message
