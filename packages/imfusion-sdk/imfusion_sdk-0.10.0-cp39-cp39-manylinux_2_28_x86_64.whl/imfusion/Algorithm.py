from functools import wraps
import inspect
from typing import List, Optional, Callable
import warnings

from imfusion import BaseAlgorithm, Data, IncompatibleError, Properties


class Algorithm(BaseAlgorithm):
    """
    Base class for Algorithms.

    An Algorithm accepts certain Data as input and performs some
    computation on it.

    Example for an algorithm that takes exactly one image and prints
    its name:

    >>> class MyAlgorithm(Algorithm):
    ...     def __init__(self, image):
    ...         super().__init__()
    ...         self.image = image
    ...
    ...     @classmethod
    ...     def convert_input(cls, data):
    ...         images = data.images()
    ...         if len(images) == 1 and len(data) == 1:
    ...             return [images[0]]
    ...         raise IncompatibleError('Requires exactly one image')
    ...
    ...     def compute(self):
    ...         print(self.image.name)

    In order to make an Algorithm available to the ImFusion Suite (i.e. the
    context menu when right-clicking on selected data), it has to be registered to the
    ApplicationController:

    >>> imfusion.register_algorithm('Python.MyAlgorithm','My Algorithm', MyAlgorithm)  # DOCTEST: +skip

    If the Algorithm is created through the ImFusion Suite, the
    :meth:`convert_input` method is called to determine if the Algorithm
    is compatible with the desired input data.
    If this method does not raise an exception, the Algorithm is initialized
    with the data returned by :meth:`convert_input`. The implementation is
    similar to this:

    .. code-block:: python

       try:
           input = MyAlgorithm.convert_input(some_data)
           return MyAlgorithm(*input)
       except IncompatibleError:
           return None

    The Algorithm class also provides default implementations for the
    :meth:`configuration` and :meth:`configure` methods that automatically
    serialize attributes created with :meth:`add_param`.
    """

    class action:
        """
        Decorator to demarcate a method as an "action".
        Actions are displayed as additional buttons when creating an AlgorithmController in the Suite
        and can be run generically, using their id, through :meth:`~imfusion.Algorithm.run_action`.

        Args:
            display_name: Text that should be shown on the Controller button.
        """

        @staticmethod
        def action_wrapper(
            func: Callable[[BaseAlgorithm], Optional[BaseAlgorithm.Status]]
        ) -> Callable[[BaseAlgorithm], BaseAlgorithm.Status]:
            """Helper that returns :attr:`~imfusion.Algorithm.UNKNOWN` automatically if the wrapped method did not return a status."""

            @wraps(func)
            def wrapper(self_algo: BaseAlgorithm):
                status = func(self_algo)
                if status is None:
                    return BaseAlgorithm.Status.UNKNOWN
                return status

            return wrapper

        def __init__(self, display_name: str):
            self.display_name = display_name

        def __call__(self, method):
            # Check that the method does not take any argument
            if not list(inspect.signature(method).parameters.keys()) == ["self"]:
                warnings.warn(
                    f"Cannot register {method.__name__} as an action because it should not take any argument"
                )
                return
            method._is_action = True
            method.display_name = self.display_name or method.__name__
            return self.action_wrapper(method)

    def __init__(self):

        # First, we have to filter out the methods of the base class because they are not initialized until we call super().__init__()
        base_methods = set(dir(Algorithm))
        own_methods = set(dir(self)) - base_methods
        # Now we filter out only the methods with the "_is_action" flag
        actions = [
            meth
            for meth_name in own_methods
            if getattr((meth := getattr(self, meth_name)), "_is_action", False)
        ]

        BaseAlgorithm.__init__(self, actions)  # important to initialize the C++ backend
        self._params = []

    @classmethod
    def convert_input(cls, data: List[Data]) -> List[Data]:
        """
        Convert the given DataList to a valid input for the algorithm.

        Must be overridden in derived classes.
        Raise an :exc:`IncompatibleError` if the given data does not exactly
        match the required input of the algorithm.
        Should return a list, a dict or a generator.
        """
        raise NotImplementedError(
            "The algorithm did not implement its convert_input class method."
        )

    def add_param(self, name, value, attributes=""):
        """
        Add a new parameter to the object.

        The parameter is available as a new attribute with the given name
        and value. The attribute will be configured automatically.

        >>> class MyAlgorithm(Algorithm):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self.add_param('x', 5)
        >>> a = MyAlgorithm()
        >>> a.x
        5
        """
        setattr(self, name, value)
        self._params.append((name, attributes))

    def output(self):
        """
        Return the output generated by the previous call to :meth:`compute`.
        The returned type must be a list of Data objects!
        The default implementation returns an empty list.
        """
        return []

    def configuration(self):
        """
        Returns a copy of the current algorithm configuration.
        """
        p = Properties()
        for name, attributes in self._params:
            p[name] = getattr(self, name)
            if attributes:
                existing_attributes = ", ".join(f"{attr}: {value!r}" for attr, value in p.param_attributes(name))
                if existing_attributes:
                    attributes = f"{existing_attributes}, {attributes}"
                p.set_param_attributes(name, attributes)
        return p

    def configure(self, p):
        """
        Sets the current algorithm configuration with the given Properties.
        """
        if not p:
            return

        for name, _ in self._params:
            value = p.param(name, getattr(self, name))
            if value is not None:
                setattr(self, name, value)


Algorithm.__module__ = "imfusion"
Algorithm.__qualname__ = "Algorithm"
