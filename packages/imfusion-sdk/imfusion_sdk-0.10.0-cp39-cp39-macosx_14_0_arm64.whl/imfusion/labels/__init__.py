import types
import warnings
from functools import wraps

from imfusion.labels import _bindings
from imfusion.labels._bindings import *

__doc__ = _bindings.__doc__

from typing import Callable

_bindings._init_thread()

def __DataType_repr(self):
    def test_flag(lhs: DataType, rhs: DataType):
        return (lhs & rhs) == rhs and ((rhs is not None) or (lhs == rhs))

    if test_flag(self, DataType.AnyDataType):
        return "DataType.AnyDataType"

    found_types = []
    for entry in DataType.__entries:
        if test_flag(self, getattr(DataType, entry)):
            found_types.append(f'DataType.{entry}')

    if not found_types:
        return "None"

    return ' | '.join(found_types)


DataType.__repr__ = __DataType_repr


# Patch Descriptor class
def __Descriptor_repr(self):
    desc_repr = 'Descriptor('

    # we have to use dir here instead of vars because the __dict__ of objects created by pybind is often empty
    # (only attributes bound with def_readwrite end up in the dict, and we almost never use this)
    for name in dir(self):
        if name.startswith('__'):
            continue
        value = getattr(self, name)
        if isinstance(value, types.MethodType):
            continue
        value_repr = '\n\t'.join(line for line in repr(value).split('\n'))
        desc_repr += f'\n\t{name}={value_repr}'

    desc_repr += ')'

    return desc_repr


Descriptor.__repr__ = __Descriptor_repr


def deprecate(old: str, new: str, owner: object, is_property=False):
    @wraps(getattr(owner, new))
    def wrapped(*args, **kwargs):
        warnings.warn(f'{old} is deprecated. Use {new} instead.', category=DeprecationWarning)
        return getattr(args[0], new) if is_property else getattr(owner, new)(*args, **kwargs)

    if is_property:
        wrapped = property(wrapped)

    setattr(owner, old, wrapped)


deprecate('labels', 'annotations', LabelMapLayer, True)
deprecate('add_label', 'add_annotation', LabelMapLayer)
deprecate('landmarks', 'annotations', LandmarkLayer, True)
deprecate('add_landmark', 'add_annotation', LandmarkLayer)
deprecate('boundingboxes', 'annotations', BoundingBoxLayer, True)
deprecate('add_boundingbox', 'add_annotation', BoundingBoxLayer)
