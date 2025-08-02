"""

imfusion.imagemath - Bindings for ImageMath Operations  
======================================================

This module provides element-wise arithmetic operations for :class:`~imfusion.SharedImage` and :class:`~imfusion.SharedImageSet`. You can apply these :mod:`~imfusion.imagemath` functionalities directly to objects of :class:`~imfusion.SharedImage` and :class:`~imfusion.SharedImageSet` with eager evaluation. Alternatively, the module offers lazy evaluation functionality through the submodule :mod:`~imfusion.imagemath.lazy`. You can create wrapper expressions using the :class:`~imfusion.imagemath.lazy.Expression` provided by :mod:`~imfusion.imagemath.lazy`.

See :class:`~imfusion.imagemath.lazy.Expression` for details.

*Example for eager evaluation:*

>>> from imfusion import imagemath

Add `si1` and `si2`, which are :class:`~imfusion.SharedImage` instances:

>>> res = si1 + si2

`res` is a :class:`~imfusion.SharedImage` instance.

>>> print(res)
imfusion.SharedImage(FLOAT width: 512 height: 512)

*Example for lazy evaluation:*

>>> from imfusion import imagemath

Create expressions from :class:`~imfusion.SharedImage` instances:

>>> expr1 = imagemath.lazy.Expression(si1)
>>> expr2 = imagemath.lazy.Expression(si2)

Add `expr1` and `expr2`:

>>> expr3 = expr1 + expr2

Alternatively, you could add `expr1` and `si2` or `si1` and `expr2`. Any expression containing an instance of :class:`~imagemath.lazy.Expression` will be converted to lazy evaluation expression. 

>>> expr3 = expr1 + si2

Find the result with lazy evaluation: 

>>> res = expr3.evaluate()

`res` is a :class:`~imfusion.SharedImage` instance similar to eager evaluation case.

>>> print(res)
imfusion.SharedImage(FLOAT width: 512 height: 512)
"""
from __future__ import annotations
import imfusion
import numpy
import typing
from . import lazy
__all__ = ['absolute', 'add', 'arctan2', 'argmax', 'argmin', 'channel_swizzle', 'cos', 'divide', 'equal', 'exp', 'greater', 'greater_equal', 'lazy', 'less', 'less_equal', 'log', 'max', 'maximum', 'mean', 'min', 'minimum', 'multiply', 'negative', 'norm', 'not_equal', 'power', 'prod', 'sign', 'sin', 'sqrt', 'square', 'subtract', 'sum']
@typing.overload
def absolute(x: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Absolute value, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def absolute(x: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Absolute value, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def add(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def add(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def add(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def add(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def add(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def add(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def add(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def add(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def arctan2(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def arctan2(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def arctan2(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def arctan2(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def arctan2(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def arctan2(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def arctan2(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def arctan2(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def argmax(x: imfusion.SharedImage) -> list[numpy.ndarray[numpy.int32[4, 1]]]:
    """
    Return a list of the indices of maximum values, channel-wise. The indices are represented as (x, y, z, image index).
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def argmax(x: imfusion.SharedImageSet) -> list[numpy.ndarray[numpy.int32[4, 1]]]:
    """
    Return a list of the indices of maximum values, channel-wise. The indices are represented as (x, y, z, image index).
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def argmin(x: imfusion.SharedImage) -> list[numpy.ndarray[numpy.int32[4, 1]]]:
    """
    Return a list of the indices of minimum values, channel-wise. The indices are represented as (x, y, z, image index).
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def argmin(x: imfusion.SharedImageSet) -> list[numpy.ndarray[numpy.int32[4, 1]]]:
    """
    Return a list of the indices of minimum values, channel-wise. The indices are represented as (x, y, z, image index).
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def channel_swizzle(x: imfusion.SharedImage, indices: list[int]) -> imfusion.SharedImage:
    """
    Reorders the channels of an image based on the input indices, e.g. indices[0] will correspond to the first channel of the output image.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	indices (List[int]): List of channels indices to swizzle the channels of :class:`~imfusion.SharedImage`.
    """
@typing.overload
def channel_swizzle(x: imfusion.SharedImageSet, indices: list[int]) -> imfusion.SharedImageSet:
    """
    Reorders the channels of an image based on the input indices, e.g. indices[0] will correspond to the first channel of the output image.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	indices (List[int]): List of channels indices to swizzle the channels of :class:`~imfusion.SharedImageSet`.
    """
@typing.overload
def cos(x: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Cosine, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def cos(x: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Cosine, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def divide(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def divide(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def divide(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def divide(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def divide(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def divide(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def divide(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def divide(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def equal(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def equal(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def equal(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def equal(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def equal(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def equal(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def equal(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def equal(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def exp(x: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Exponential operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def exp(x: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Exponential operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def greater(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def greater(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater_equal(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater_equal(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater_equal(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def greater_equal(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater_equal(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater_equal(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def greater_equal(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater_equal(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def less(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def less(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less_equal(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less_equal(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less_equal(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def less_equal(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less_equal(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less_equal(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def less_equal(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less_equal(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def log(x: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Natural logarithm, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def log(x: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Natural logarithm, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def max(x: imfusion.SharedImage) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the list of the maximum elements of images, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def max(x: imfusion.SharedImageSet) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the list of the maximum elements of images, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def maximum(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def maximum(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def maximum(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def maximum(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def maximum(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def maximum(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def maximum(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def maximum(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def mean(x: imfusion.SharedImage) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return a list of channel-wise average of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def mean(x: imfusion.SharedImageSet) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return a list of channel-wise average of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def min(x: imfusion.SharedImage) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the list of the minimum elements of images, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def min(x: imfusion.SharedImageSet) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the list of the minimum elements of images, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def minimum(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def minimum(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def minimum(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def minimum(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def minimum(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def minimum(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def minimum(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def minimum(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def multiply(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def multiply(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def multiply(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def multiply(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def multiply(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def multiply(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def multiply(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def multiply(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def negative(x: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Numerical negative, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def negative(x: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Numerical negative, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def norm(x: imfusion.SharedImage, order: typing.Any = 2) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Returns the norm of an image instance, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	order (int, float, 'inf'): Order of the norm. Default is L2 norm.
    """
@typing.overload
def norm(x: imfusion.SharedImageSet, order: typing.Any = 2) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Returns the norm of an image instance, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	order (int, float, 'inf'): Order of the norm. Default is L2 norm.
    """
@typing.overload
def not_equal(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def not_equal(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def not_equal(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def not_equal(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def not_equal(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def not_equal(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def not_equal(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def not_equal(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def power(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def power(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def power(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def power(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def power(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def power(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def power(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def power(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def prod(x: imfusion.SharedImage) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return a list of channel-wise production of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def prod(x: imfusion.SharedImageSet) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return a list of channel-wise production of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def sign(x: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Element-wise indication of the sign of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def sign(x: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Element-wise indication of the sign of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def sin(x: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Sine, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def sin(x: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Sine, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def sqrt(x: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Square-root operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def sqrt(x: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Square-root operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def square(x: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Square operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def square(x: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Square operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def subtract(x1: imfusion.SharedImage, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def subtract(x1: imfusion.SharedImage, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def subtract(x1: imfusion.SharedImage, x2: float) -> imfusion.SharedImage:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def subtract(x1: imfusion.SharedImageSet, x2: imfusion.SharedImage) -> imfusion.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def subtract(x1: imfusion.SharedImageSet, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def subtract(x1: imfusion.SharedImageSet, x2: float) -> imfusion.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (float): scalar value.
    """
@typing.overload
def subtract(x1: float, x2: imfusion.SharedImage) -> imfusion.SharedImage:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def subtract(x1: float, x2: imfusion.SharedImageSet) -> imfusion.SharedImageSet:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def sum(x: imfusion.SharedImage) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return a list of channel-wise sum of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def sum(x: imfusion.SharedImageSet) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return a list of channel-wise sum of image elements.
    
    Args:
    
    	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
