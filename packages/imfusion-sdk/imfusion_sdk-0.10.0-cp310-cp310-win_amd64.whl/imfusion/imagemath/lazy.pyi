"""
Lazy evaluation (imagemath.lazy)
"""
from __future__ import annotations
import imfusion
import numpy
import typing
__all__ = ['Expression', 'absolute', 'add', 'arctan2', 'argmax', 'argmin', 'channel_swizzle', 'cos', 'divide', 'equal', 'exp', 'greater', 'greater_equal', 'less', 'less_equal', 'log', 'max', 'maximum', 'mean', 'min', 'minimum', 'multiply', 'negative', 'norm', 'not_equal', 'power', 'prod', 'sign', 'sin', 'sqrt', 'square', 'subtract', 'sum']
class Expression:
    """
    
    Expressions to be used for lazy evaluation.
    
    This class serves as a wrapper for :class:`~imfusion.SharedImage`, :class:`~imfusion.SharedImageSet`, and scalar values to be used for lazy evaluation. Lazy evaluation approach delays the actual evaluation until the point that the result is needed. If you prefer the eager evaluation approach, you can directly invoke operations on :class:`~imfusion.SharedImage` and :class:`~imfusion.SharedImageSet` objects.
    
    Here is an example how to use lazy evaluation approach:
    
    >>> from imfusion import imagemath
    
    Create expressions from :class:`~imfusion.SharedImage` instances:
    
    >>> expr1 = imagemath.lazy.Expression(si1)
    >>> expr2 = imagemath.lazy.Expression(si2)
    
    Any operation with the expressions will return another expression. Expressions are stored in the expression tree and not evaluated yet without any evaluation. 
    
    >>> expr3 = expr1 + expr2
    
    Expressions must be explicitly evaluated to get results. Use the :meth:`~imfusion.imagemath.lazy.evaluate` method for this purpose:
    
    >>> res = expr3.evaluate()
    
    Here, result is a :class:`~imfusion.SharedImage` instance:
    
    >>> print(res)
    imfusion.SharedImage(FLOAT width: 512 height: 512)
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __abs__(self) -> Expression:
        """
        Expression for absolute value, element-wise.
        """
    @typing.overload
    def __add__(self, x: Expression) -> Expression:
        """
        Addition, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
        """
    @typing.overload
    def __add__(self, x: imfusion.SharedImage) -> Expression:
        """
        Addition, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
        """
    @typing.overload
    def __add__(self, x: imfusion.SharedImageSet) -> Expression:
        """
        Addition, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
        """
    @typing.overload
    def __add__(self, x: float) -> Expression:
        """
        Addition, element-wise.
        
        Args:
        
        	x (float): scalar value.
        """
    @typing.overload
    def __eq__(self, x: Expression) -> Expression:
        """
        Return the truth value of (x1 == x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
        """
    @typing.overload
    def __eq__(self, x: imfusion.SharedImage) -> Expression:
        """
        Return the truth value of (x1 == x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
        """
    @typing.overload
    def __eq__(self, x: imfusion.SharedImageSet) -> Expression:
        """
        Return the truth value of (x1 == x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
        """
    @typing.overload
    def __eq__(self, x: float) -> Expression:
        """
        Return the truth value of (x1 == x2), element-wise.
        
        Args:
        
        	x (float): scalar value.
        """
    @typing.overload
    def __ge__(self, x: Expression) -> Expression:
        """
        Return the truth value of (x1 >= x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
        """
    @typing.overload
    def __ge__(self, x: imfusion.SharedImage) -> Expression:
        """
        Return the truth value of (x1 >= x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
        """
    @typing.overload
    def __ge__(self, x: imfusion.SharedImageSet) -> Expression:
        """
        Return the truth value of (x1 >= x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
        """
    @typing.overload
    def __ge__(self, x: float) -> Expression:
        """
        Return the truth value of (x1 >= x2), element-wise.
        
        Args:
        
        	x (float): scalar value.
        """
    def __getitem__(self, index: int) -> Expression:
        """
        This method only works with :class:`~imfusion.SharedImageSet` :class:`~imfusion.imagemath.lazy.Expression` instances.
        Returns a :class:`~imfusion.SharedImage` :class:`~imfusion.imagemath.lazy.Expression` from a :class:`~imfusion.SharedImageSet` :class:`~imfusion.imagemath.lazy.Expression`.
        
        Args:
        
        	index (int): The index of :class:`~imfusion.SharedImage` :class:`~imfusion.imagemath.lazy.Expression`.
        """
    @typing.overload
    def __gt__(self, x: Expression) -> Expression:
        """
        Return the truth value of (x1 > x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
        """
    @typing.overload
    def __gt__(self, x: imfusion.SharedImage) -> Expression:
        """
        Return the truth value of (x1 > x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
        """
    @typing.overload
    def __gt__(self, x: imfusion.SharedImageSet) -> Expression:
        """
        Return the truth value of (x1 > x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
        """
    @typing.overload
    def __gt__(self, x: float) -> Expression:
        """
        Return the truth value of (x1 > x2), element-wise.
        
        Args:
        
        	x (float): scalar value.
        """
    @typing.overload
    def __init__(self, shared_image_set: imfusion.SharedImageSet) -> None:
        """
        Creates an expression wrapping :class:`~imfusion.SharedImageSet` instance.
        
        Args:
        
        	shared_image_set (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance to be wrapped by :class:`~imfusion.imagemath.lazy.Expression`.
        """
    @typing.overload
    def __init__(self, shared_image: imfusion.SharedImage) -> None:
        """
        Creates an expression wrapping :class:`~imfusion.SharedImage` instance.
        
        Args:
        
        	shared_image (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance to be wrapped by :class:`~imfusion.imagemath.lazy.Expression`.
        """
    @typing.overload
    def __init__(self, value: float) -> None:
        """
        Creates an expression wrapping a scalar value.
        
        Args:
        
        	value (float): Scalar value to be wrapped by :class:`~imfusion.imagemath.lazy.Expression`.
        """
    @typing.overload
    def __init__(self, channel: int) -> None:
        """
        Creates an expression wrapping a variable, e.g. a result of another computation which is not yet available during creation of the expr. Currently, only one per expression is allowed.
        
        Args:
        
        	channel (int): The channel of the variable wrapped by :class:`~imfusion.imagemath.lazy.Expression`.
        """
    @typing.overload
    def __le__(self, x: Expression) -> Expression:
        """
        Return the truth value of (x1 <= x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
        """
    @typing.overload
    def __le__(self, x: imfusion.SharedImage) -> Expression:
        """
        Return the truth value of (x1 <= x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
        """
    @typing.overload
    def __le__(self, x: imfusion.SharedImageSet) -> Expression:
        """
        Return the truth value of (x1 <= x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
        """
    @typing.overload
    def __le__(self, x: float) -> Expression:
        """
        Return the truth value of (x1 <= x2), element-wise.
        
        Args:
        
        	x (float): scalar value.
        """
    @typing.overload
    def __lt__(self, x: Expression) -> Expression:
        """
        Return the truth value of (x1 < x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
        """
    @typing.overload
    def __lt__(self, x: imfusion.SharedImage) -> Expression:
        """
        Return the truth value of (x1 < x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
        """
    @typing.overload
    def __lt__(self, x: imfusion.SharedImageSet) -> Expression:
        """
        Return the truth value of (x1 < x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
        """
    @typing.overload
    def __lt__(self, x: float) -> Expression:
        """
        Return the truth value of (x1 < x2), element-wise.
        
        Args:
        
        	x (float): scalar value.
        """
    @typing.overload
    def __mul__(self, x: Expression) -> Expression:
        """
        Multiplication, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
        """
    @typing.overload
    def __mul__(self, x: imfusion.SharedImage) -> Expression:
        """
        Multiplication, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
        """
    @typing.overload
    def __mul__(self, x: imfusion.SharedImageSet) -> Expression:
        """
        Multiplication, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
        """
    @typing.overload
    def __mul__(self, x: float) -> Expression:
        """
        Multiplication, element-wise.
        
        Args:
        
        	x (float): scalar value.
        """
    @typing.overload
    def __ne__(self, x: Expression) -> Expression:
        """
        Return the truth value of (x1 != x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
        """
    @typing.overload
    def __ne__(self, x: imfusion.SharedImage) -> Expression:
        """
        Return the truth value of (x1 != x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
        """
    @typing.overload
    def __ne__(self, x: imfusion.SharedImageSet) -> Expression:
        """
        Return the truth value of (x1 != x2), element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
        """
    @typing.overload
    def __ne__(self, x: float) -> Expression:
        """
        Return the truth value of (x1 != x2), element-wise.
        
        Args:
        
        	x (float): scalar value.
        """
    def __neg__(self) -> Expression:
        """
        Expression for numerical negative, element-wise.
        """
    @typing.overload
    def __pow__(self, x: Expression) -> Expression:
        """
        The first argument is raised to powers of the second argument, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
        """
    @typing.overload
    def __pow__(self, x: imfusion.SharedImage) -> Expression:
        """
        The first argument is raised to powers of the second argument, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
        """
    @typing.overload
    def __pow__(self, x: imfusion.SharedImageSet) -> Expression:
        """
        The first argument is raised to powers of the second argument, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
        """
    @typing.overload
    def __pow__(self, x: float) -> Expression:
        """
        The first argument is raised to powers of the second argument, element-wise.
        
        Args:
        
        	x (float): scalar value.
        """
    @typing.overload
    def __radd__(self, arg0: imfusion.SharedImage) -> Expression:
        ...
    @typing.overload
    def __radd__(self, arg0: imfusion.SharedImageSet) -> Expression:
        ...
    @typing.overload
    def __radd__(self, arg0: float) -> Expression:
        ...
    @typing.overload
    def __req__(self, arg0: imfusion.SharedImage) -> Expression:
        ...
    @typing.overload
    def __req__(self, arg0: imfusion.SharedImageSet) -> Expression:
        ...
    @typing.overload
    def __req__(self, arg0: float) -> Expression:
        ...
    @typing.overload
    def __rge__(self, arg0: imfusion.SharedImage) -> Expression:
        ...
    @typing.overload
    def __rge__(self, arg0: imfusion.SharedImageSet) -> Expression:
        ...
    @typing.overload
    def __rge__(self, arg0: float) -> Expression:
        ...
    @typing.overload
    def __rgt__(self, arg0: imfusion.SharedImage) -> Expression:
        ...
    @typing.overload
    def __rgt__(self, arg0: imfusion.SharedImageSet) -> Expression:
        ...
    @typing.overload
    def __rgt__(self, arg0: float) -> Expression:
        ...
    @typing.overload
    def __rle__(self, arg0: imfusion.SharedImage) -> Expression:
        ...
    @typing.overload
    def __rle__(self, arg0: imfusion.SharedImageSet) -> Expression:
        ...
    @typing.overload
    def __rle__(self, arg0: float) -> Expression:
        ...
    @typing.overload
    def __rlt__(self, arg0: imfusion.SharedImage) -> Expression:
        ...
    @typing.overload
    def __rlt__(self, arg0: imfusion.SharedImageSet) -> Expression:
        ...
    @typing.overload
    def __rlt__(self, arg0: float) -> Expression:
        ...
    @typing.overload
    def __rmul__(self, arg0: imfusion.SharedImage) -> Expression:
        ...
    @typing.overload
    def __rmul__(self, arg0: imfusion.SharedImageSet) -> Expression:
        ...
    @typing.overload
    def __rmul__(self, arg0: float) -> Expression:
        ...
    @typing.overload
    def __rne__(self, arg0: imfusion.SharedImage) -> Expression:
        ...
    @typing.overload
    def __rne__(self, arg0: imfusion.SharedImageSet) -> Expression:
        ...
    @typing.overload
    def __rne__(self, arg0: float) -> Expression:
        ...
    @typing.overload
    def __rpow__(self, arg0: imfusion.SharedImage) -> Expression:
        ...
    @typing.overload
    def __rpow__(self, arg0: imfusion.SharedImageSet) -> Expression:
        ...
    @typing.overload
    def __rpow__(self, arg0: float) -> Expression:
        ...
    @typing.overload
    def __rsub__(self, arg0: imfusion.SharedImage) -> Expression:
        ...
    @typing.overload
    def __rsub__(self, arg0: imfusion.SharedImageSet) -> Expression:
        ...
    @typing.overload
    def __rsub__(self, arg0: float) -> Expression:
        ...
    @typing.overload
    def __rtruediv__(self, arg0: imfusion.SharedImage) -> Expression:
        ...
    @typing.overload
    def __rtruediv__(self, arg0: imfusion.SharedImageSet) -> Expression:
        ...
    @typing.overload
    def __rtruediv__(self, arg0: float) -> Expression:
        ...
    @typing.overload
    def __sub__(self, x: Expression) -> Expression:
        """
        Addition, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
        """
    @typing.overload
    def __sub__(self, x: imfusion.SharedImage) -> Expression:
        """
        Addition, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
        """
    @typing.overload
    def __sub__(self, x: imfusion.SharedImageSet) -> Expression:
        """
        Addition, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
        """
    @typing.overload
    def __sub__(self, x: float) -> Expression:
        """
        Addition, element-wise.
        
        Args:
        
        	x (float): scalar value.
        """
    @typing.overload
    def __truediv__(self, x: Expression) -> Expression:
        """
        Division, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
        """
    @typing.overload
    def __truediv__(self, x: imfusion.SharedImage) -> Expression:
        """
        Division, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
        """
    @typing.overload
    def __truediv__(self, x: imfusion.SharedImageSet) -> Expression:
        """
        Division, element-wise.
        
        Args:
        
        	x (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
        """
    @typing.overload
    def __truediv__(self, x: float) -> Expression:
        """
        Division, element-wise.
        
        Args:
        
        	x (float): scalar value.
        """
    def argmax(self) -> list[numpy.ndarray[numpy.int32[4, 1]]]:
        """
        Return the expression for computing a list of the indices of maximum values, channel-wise. The indices are represented as (x, y, z, image index).
        """
    def argmin(self) -> list[numpy.ndarray[numpy.int32[4, 1]]]:
        """
        Return the expression for computing a list of the indices of minimum values, channel-wise. The indices are represented as (x, y, z, image index).
        """
    def channel_swizzle(self, indices: list[int]) -> Expression:
        """
        Returns the expression which reorders the channels of an image based on the input indices, e.g. indices[0] will correspond to the first channel of the output image.
        
        Args:
        
        	indices (List[int]): List of channels indices to swizzle the channels of the :class:`~imfusion.SharedImage` or :class:`~imfusion.SharedImageSet` expressions.
        """
    def evaluate(self) -> typing.Any:
        """
        Evalute the expression into an image object, which is :class:`~imfusion.SharedImage` or :class:`~imfusion.SharedImageSet` instance. Scalar expressions return None when evaluated.
        Until this method is called, the operands and operations are stored in an expression tree but not evaluated yet. 
        		
        Returns: :class:`~imfusion.SharedImage` or :class:`~imfusion.SharedImageSet` instance depending on the end result of the expression tree.
        """
    def max(self) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
        Return the expression for computing the list of the maximum elements of images, channel-wise.
        """
    def mean(self) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
        Return the expression for computing a list of channel-wise average of image elements.
        """
    def min(self) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
        Return the expression for computing the list of the minimum elements of images, channel-wise.
        """
    def norm(self, order: typing.Any = 2) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
        Returns the expression for computing the norm of an image, channel-wise.
        
        Args:
        
        	order (int, float, 'inf'): Order of the norm. Default is L2 norm.
        """
    def prod(self) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
        Return the expression for computing a list of channel-wise production of image elements.
        """
    def sum(self) -> numpy.ndarray[numpy.float64[m, 1]]:
        """
        Return the expression for computing a list of channel-wise sum of image elements.
        """
def absolute(x: Expression) -> Expression:
    """
    Expression for absolute value, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def add(x1: Expression, x2: Expression) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def add(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def add(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def add(x1: Expression, x2: float) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def add(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def add(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def add(x1: float, x2: Expression) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def arctan2(x1: Expression, x2: Expression) -> Expression:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def arctan2(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def arctan2(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def arctan2(x1: Expression, x2: float) -> Expression:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def arctan2(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def arctan2(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def arctan2(x1: float, x2: Expression) -> Expression:
    """
    Trigonometric inverse tangent, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def argmax(x: Expression) -> list[numpy.ndarray[numpy.int32[4, 1]]]:
    """
    Return the expression for computing a list of the indices of maximum values, channel-wise. The indices are represented as (x, y, z, image index).
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def argmin(x: Expression) -> list[numpy.ndarray[numpy.int32[4, 1]]]:
    """
    Return the expression for computing a list of the indices of minimum values, channel-wise. The indices are represented as (x, y, z, image index).
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def channel_swizzle(x: Expression, indices: list[int]) -> Expression:
    """
    Returns the expression which reorders the channels of an image based on the input indices, e.g. indices[0] will correspond to the first channel of the output image.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	indices (List[int]): List of channels indices to swizzle the channels of the :class:`~imfusion.SharedImage` or :class:`~imfusion.SharedImageSet` expressions.
    """
def cos(x: Expression) -> Expression:
    """
    Expression for cosine, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def divide(x1: Expression, x2: Expression) -> Expression:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def divide(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def divide(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def divide(x1: Expression, x2: float) -> Expression:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def divide(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def divide(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def divide(x1: float, x2: Expression) -> Expression:
    """
    Division, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def equal(x1: Expression, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def equal(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def equal(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def equal(x1: Expression, x2: float) -> Expression:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def equal(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def equal(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def equal(x1: float, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 == x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def exp(x: Expression) -> Expression:
    """
    Expression for exponential operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def greater(x1: Expression, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def greater(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater(x1: Expression, x2: float) -> Expression:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def greater(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def greater(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def greater(x1: float, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 > x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def greater_equal(x1: Expression, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def greater_equal(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def greater_equal(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def greater_equal(x1: Expression, x2: float) -> Expression:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def greater_equal(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def greater_equal(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def greater_equal(x1: float, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 >= x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def less(x1: Expression, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def less(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less(x1: Expression, x2: float) -> Expression:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def less(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def less(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def less(x1: float, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 < x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def less_equal(x1: Expression, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def less_equal(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def less_equal(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def less_equal(x1: Expression, x2: float) -> Expression:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def less_equal(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def less_equal(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def less_equal(x1: float, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 <= x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def log(x: Expression) -> Expression:
    """
    Expression for natural logarithm, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def max(x: Expression) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the expression for computing the list of the maximum elements of images, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def maximum(x1: Expression, x2: Expression) -> Expression:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def maximum(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def maximum(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def maximum(x1: Expression, x2: float) -> Expression:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def maximum(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def maximum(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def maximum(x1: float, x2: Expression) -> Expression:
    """
    Return element-wise maximum of arguments.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def mean(x: Expression) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the expression for computing a list of channel-wise average of image elements.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def min(x: Expression) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the expression for computing the list of the minimum elements of images, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def minimum(x1: Expression, x2: Expression) -> Expression:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def minimum(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def minimum(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def minimum(x1: Expression, x2: float) -> Expression:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def minimum(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def minimum(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def minimum(x1: float, x2: Expression) -> Expression:
    """
    Return element-wise minimum of arguments.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def multiply(x1: Expression, x2: Expression) -> Expression:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def multiply(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def multiply(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def multiply(x1: Expression, x2: float) -> Expression:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def multiply(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def multiply(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def multiply(x1: float, x2: Expression) -> Expression:
    """
    Multiplication, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def negative(x: Expression) -> Expression:
    """
    Expression for numerical negative, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def norm(x: Expression, order: typing.Any = 2) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Returns the expression for computing the norm of an image, channel-wise.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	order (int, float, 'inf'): Order of the norm. Default is L2 norm.
    """
@typing.overload
def not_equal(x1: Expression, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def not_equal(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def not_equal(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def not_equal(x1: Expression, x2: float) -> Expression:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def not_equal(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def not_equal(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def not_equal(x1: float, x2: Expression) -> Expression:
    """
    Return the truth value of (x1 != x2), element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def power(x1: Expression, x2: Expression) -> Expression:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def power(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def power(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def power(x1: Expression, x2: float) -> Expression:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def power(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def power(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def power(x1: float, x2: Expression) -> Expression:
    """
    The first argument is raised to powers of the second argument, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def prod(x: Expression) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the expression for computing a list of channel-wise production of image elements.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def sign(x: Expression) -> Expression:
    """
    Expression for element-wise indication of the sign of image elements.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def sin(x: Expression) -> Expression:
    """
    Expression for sine, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def sqrt(x: Expression) -> Expression:
    """
    Expression for the square-root operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def square(x: Expression) -> Expression:
    """
    Expression for the square operation, element-wise.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def subtract(x1: Expression, x2: Expression) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def subtract(x1: Expression, x2: imfusion.SharedImage) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    """
@typing.overload
def subtract(x1: Expression, x2: imfusion.SharedImageSet) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    """
@typing.overload
def subtract(x1: Expression, x2: float) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    	x2 (float): scalar value.
    """
@typing.overload
def subtract(x1: imfusion.SharedImage, x2: Expression) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImage`): :class:`~imfusion.SharedImage` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def subtract(x1: imfusion.SharedImageSet, x2: Expression) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (:class:`~imfusion.SharedImageSet`): :class:`~imfusion.SharedImageSet` instance.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
@typing.overload
def subtract(x1: float, x2: Expression) -> Expression:
    """
    Addition, element-wise.
    
    Args:
    
    	x1 (float): scalar value.
    	x2 (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
def sum(x: Expression) -> numpy.ndarray[numpy.float64[m, 1]]:
    """
    Return the expression for computing a list of channel-wise sum of image elements.
    
    Args:
    
    	x (:class:`~imfusion.imagemath.lazy.Expression`): :class:`~imfusion.imagemath.lazy.Expression` instance wrapping :class:`~imfusion.SharedImage` instance, :class:`~imfusion.SharedImageSet` instance, or scalar value.
    """
