"""
imfusion.machinelearning - Bindings for Machine Learning
==========================================================

This submodule provides Python bindings for the C++ ImFusion classes that can be used during the training of machine learning models.
"""
# import all the actual bindings before doing anything else
import sys
from ._bindings import bind
bind(sys.modules["imfusion.machinelearning"])
del _bindings, bind

import abc
from typing import Iterator
from .engines import *

if sys.version_info[0] <= 3 and sys.version_info[1] < 6:
    import warnings

    warnings.warn('imfusion.machinelearning requires python >= 3.6, older versions might not work as expected',
                  UserWarning, stacklevel=2)


# deprecation layer
class AbstractOperation(Operation):
    @abc.abstractmethod
    def __init__(self, name='', processing_policy=Operation.ProcessingPolicy.EVERYTHING_BUT_LABELS):
        Operation.__init__(self, name, processing_policy)

    def __init_subclass__(self, *args, **kwargs):
        import warnings
        warnings.warn("'AbstractOperation' has been renamed 'Operation'", DeprecationWarning, 2)
        super().__init_subclass__(*args, **kwargs)


# numpy conversion for DataElement
def __DataElement_array(self: DataElement, copy=False):
    import numpy as np
    if isinstance(self, TensorSetElement):
        if len(self) == 1: # avoid stacking if possible
            return np.array(content, copy=copy)
    return np.stack([np.array(content, copy=copy) for content in self.content])


# implementing this in C++ was always giving me SEGFAULTs
def __DataElement_iter(self) -> Iterator:
    return iter(self.content)


DataElement.__array__ = __DataElement_array
DataElement.__iter__ = __DataElement_iter
DataElement.numpy = __DataElement_array

# import torch_utils
from .torch_utils import *

# NOTE: this is commented out for now as the factories need to be initialized for this to work
# TODO: When init() is moved inside the bindings this can be uncommented
# try:
#     import openvino_engine
# except ModuleNotFoundError:
#     import warnings
#     warnings.warn('openvino_engine requires the openvino module, please install it if you want to use this engine.',
#                    UserWarning, stacklevel=2)
