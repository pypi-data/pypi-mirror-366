"""
imfusion - ImFusion SDK for Medical Imaging
===========================================

This module provides Python bindings for the C++ ImFusion libraries.
"""

import os
import re
import sys
import sysconfig
from pathlib import Path

# Because the bindings from Suite installers are not installed (the user is expected to set up PYTHONPATH instead) the python version compat is not checked
# We need to do a manual check for the contained _bindings versions here
# This fixes PYSDK-342

EXT_SUFFIX = sysconfig.get_config_vars()["EXT_SUFFIX"]
PY_VERSION_NODOT = sysconfig.get_config_vars()["py_version_nodot"]
V_MAJOR, *V_MINOR = PY_VERSION_NODOT
V_MINOR = "".join(V_MINOR)
shared_lib_pattern = EXT_SUFFIX.replace(PY_VERSION_NODOT, r"(\d{2,3})")
available_versions = [re.search(shared_lib_pattern, bindings_module).groups(1)[0] for bindings_module in os.listdir(Path(__file__).parent) if bindings_module.startswith("_bindings.")]
if PY_VERSION_NODOT not in available_versions:
    raise ImportError(f"The ImFusion Python SDK was not compiled for the currently used Python version ({V_MAJOR}.{V_MINOR}).\n"
                      f"Compatible versions are: {[major + '.' + ''.join(minor) for major, *minor in available_versions]}")

del EXT_SUFFIX, PY_VERSION_NODOT, V_MAJOR, V_MINOR, Path, sysconfig, re

# For Python 3.8+ on Windows, we need to explicitly add some folders to the DLL directory
if sys.platform == "win32" and (sys.version_info.major, sys.version_info.minor) >= (3, 8):
    imfusionlib_dir = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(os.path.join(imfusionlib_dir, "ImFusionLib.dll")):
        # In the wheel the dlls are directly in the module directory, while in
        # the msi installer they are one directory up
        imfusionlib_dir = os.path.dirname(imfusionlib_dir)
    for extra_dir in ["", "plugins", "plugins/Release"]:
        cur_dir = os.path.join(imfusionlib_dir, extra_dir)
        if os.path.isdir(cur_dir):
            os.add_dll_directory(cur_dir)
    del imfusionlib_dir, extra_dir, cur_dir

try:
    from ._devenv import *
except ImportError:
    pass

try:
    import numpy
except ImportError as e:
    raise ImportError(
        "The imfusion package requires numpy to be installed in the current environment"
    ) from e

# We pass the already constructed module from sys.modules into the `bind` function of our bindings dll to define everything on the `imfusion` module directly.
from ._bindings import bind
imfusion = sys.modules["imfusion"]
bind(imfusion)

_register_algorithm = imfusion._register_algorithm
del bind
del _bindings
del imfusion

def try_import_imfusion_plugin(plugin: str) -> None:
    import importlib
    import sysconfig
    from pathlib import Path

    expected_python_tag = sysconfig.get_config_var("EXT_SUFFIX")
    potential_hits = [
        path
        for path in Path(__file__).parent.glob(f"{plugin}*")
        if path.name == plugin or expected_python_tag in path.name
    ]
    if not potential_hits:
        return
    importlib.import_module(f".{plugin}", __package__)


try_import_imfusion_plugin("imagemath")
try_import_imfusion_plugin("dicom")
try_import_imfusion_plugin("computed_tomography")
try_import_imfusion_plugin("machinelearning")
try_import_imfusion_plugin("stream")
try_import_imfusion_plugin("igtl")
try_import_imfusion_plugin("registration")
try_import_imfusion_plugin("ultrasound")
try_import_imfusion_plugin("anatomy")
try_import_imfusion_plugin("spine")

from .Algorithm import *


def keep_data_alive(cls):
    import functools
    import itertools

    def init_wrapper(init):
        """
        Decorator intended to wrap the __init__ of a class that requires instances of Data.
        The decorator will store references of the Data instances in a protected list attribute.
        This is needed in case the Data instance was a temporary object (constructed in the class type's  __call__),
        otherwise we would encounter crashes as python would hold references to already deleted objects.
        """

        @functools.wraps(init)
        def init_with_save(self, *args, **kwargs):
            self._stored_data = []
            for arg in itertools.chain(args, kwargs.values()):
                if isinstance(arg, Data):
                    self._stored_data.append(arg)
            init(self, *args, **kwargs)

        return init_with_save

    @functools.wraps(cls.__init_subclass__)
    def init_subclass(cls, *args, **kwargs):
        """Automatically applies the init_wrapper decorator on the __init__ of any derived class."""
        super(cls).__init_subclass__(*args, **kwargs)
        cls.__init__ = init_wrapper(cls.__init__)

    # Perform the actual wrapping
    cls.__init__ = init_wrapper(cls.__init__)
    cls.__init_subclass__ = classmethod(init_subclass)

    return cls


to_wrap = [
    name
    for name, cls in locals().items()
    if name.endswith("Algorithm") and isinstance(cls, type)
]
for name in to_wrap:
    exec(f"{name} = keep_data_alive({name})")

app = None

import atexit


@atexit.register
def __cleanup():
    """
    Deletes the ApplicationController on exit and calls deinit().
    This assures the OpenGL context is cleaned-up correctly.
    """
    global app
    if app is not None:
        del app
    deinit()


del atexit


def register_algorithm(id, name, cls):
    """
    Register an Algorithm to the framework.

    The Algorithm will be accessible through the given id.
    If the id is already used, the registration will fail.

    cls must derive from Algorithm otherwise a TypeError is
    raised.
    """
    if not issubclass(cls, Algorithm):
        raise TypeError("cls does not derive from Algorithm")

    def create_compatible(data, create):
        try:
            input = cls.convert_input(data)
            if type(input) is not dict:
                # if input is a generator, this evaluates it
                input = list(input)
                if not create:
                    return (True, None)

            try:
                # convert list of tuples to dict (e.g. from a generator)
                input_dict = dict(input)
                # only use dicts that contain named parameters
                if all(type(k) == str for k in input_dict.keys()):
                    input = input_dict
            except (TypeError, ValueError):
                pass

            # create an instance with the input as arguments
            if type(input) is dict:
                return (True, cls(**input))
            else:
                return (True, cls(*input))
        except IncompatibleError as e:
            if create and app and str(e):
                log_error("The algorithm could not be created: " + str(e))
            return (False, None)

    _register_algorithm(id, name, create_compatible)


def __apply_shift_and_scale(self, arr):
    """
    Return a copy of the array with storage values converted to original values.
    The dtype of the returned array is always DOUBLE.
    """
    return (arr / self.scale) - self.shift


MemImage.apply_shift_and_scale = __apply_shift_and_scale
SharedImage.apply_shift_and_scale = __apply_shift_and_scale


def __best_dtype(dtype_list: List[numpy.dtype]) -> numpy.dtype:
    """
    Helper function that returns a dtype that allows to represent the values in the range defined
    by the union of the ranges determined by the input dtypes.

    The max integer returned by this function has 32 bits: any integer with more bits will determine
    a double dtype.

    :param dtype_list: a list of numpy.dtypes, it must have size at least 1 as it is not checked.
    :return: the dtype that allows to represent all the values represented by the input dtypes.
    """
    np_type = numpy.result_type(*dtype_list) if len(dtype_list) > 1 else dtype_list[0]
    try:
        # Basically we don't support 64-bit integers, in fact this:
        # `SharedImage(numpy.array([[1]], dtype=numpy.uint64))`
        # leads to:
        # `imfusion.SharedImage(DOUBLE width: 1)`
        # Hence here for consistency >=64-bit integers are converted into doubles.
        if numpy.iinfo(np_type).bits >= 64:
            np_type = numpy.double
    except ValueError:
        pass
    return np_type


def __convert_image_into_numpy_array(self):
    """
    Convenience method for converting a MemImage or a SharedImage into a newly created numpy array with scale and shift
    already applied.

    Shift and scale may determine a complex change of pixel type prior the conversion into numpy array:

    - as a first rule, even if the type of shift and scale is float, they will still be considered as integers if
      they are representing integers (e.g. a shift of 2.000 will be treated as 2);
    - if shift and scale are such that the pixel values range (determined by the pixel_type) would not be fitting into
      the pixel_type, e.g. a negative pixel value but the type is unsigned, then the pixel_type will be promoted into
      a signed type if possible, otherwise into a single precision floating point type;
    - if shift and scale are such that the pixel values range (determined by the pixel_type) would be fitting into a
      demoted pixel_type, e.g. the type is signed but the range of pixel values is unsigned, then the pixel_type
      will be demoted;
    - if shift and scale do not certainly determine that all the possible pixel values (in the range determined by the
      pixel_type) would become integers, then the pixel_type will be promoted into a single precision floating point
      type.
    - in any case, the returned numpy array will be returned with type up to 32-bit integers. If the integer type
      would require more bits, then the resulting pixel_type will be DOUBLE.

    :param self: instance of a MemImage or of a SharedImage
    :return: numpy.ndarray
    """
    if isinstance(self, MemImage):
        imf_type = self.type
    elif isinstance(self, SharedImage):
        imf_type = self.descriptor.pixel_type
    else:
        raise TypeError("Unknown image argument cannot be converted into a numpy array")

    if imf_type == PixelType.BYTE:
        np_type = numpy.byte
    elif imf_type == PixelType.UBYTE:
        np_type = numpy.ubyte
    elif imf_type == PixelType.SHORT:
        np_type = numpy.short
    elif imf_type == PixelType.USHORT:
        np_type = numpy.ushort
    elif imf_type == PixelType.INT:
        np_type = numpy.int32
    elif imf_type == PixelType.UINT:
        np_type = numpy.uint32
    elif imf_type == PixelType.FLOAT:
        np_type = numpy.single
    elif imf_type == PixelType.DOUBLE:
        np_type = numpy.double
    elif imf_type == PixelType.HFLOAT:
        np_type = numpy.single
    else:
        np_type = numpy.single

    # This entire logic takes care of auto-conversions when shift and scale are meaningful (also see the docstring).
    if (
            (not numpy.isclose(self.shift, 0.0) or not numpy.isclose(self.scale, 1.0))
            and np_type != numpy.single
            and np_type != numpy.double
    ):
        if not self.shift.is_integer() or not (1 / self.scale).is_integer():
            np_type = numpy.single
        else:
            # Shift and scale are such that we remain in the integers domain
            val_min = round(__apply_shift_and_scale(self, numpy.iinfo(np_type).min))
            val_max = round(__apply_shift_and_scale(self, numpy.iinfo(np_type).max))
            # The min type that "can hold the value after applying shift and scale" may have changed
            dtype_min = numpy.min_scalar_type(val_min)
            dtype_max = numpy.min_scalar_type(val_max)
            # val_max may now be in the range defined by the dtype of val_min (i.e. after applying shift and scale)
            if numpy.iinfo(dtype_min).min <= val_max <= numpy.iinfo(dtype_min).max:
                np_type = __best_dtype([dtype_min])
            # Otherwise, val_min may now be in the range defined by the dtype of val_max (i.e. after applying shift
            # and scale)
            elif numpy.iinfo(dtype_max).min <= val_min <= numpy.iinfo(dtype_max).max:
                np_type = __best_dtype([dtype_max])
            # If both val_max and val_min are not within the range of the dtype of the other, then we can only get the
            # best dtype from their combination.
            else:
                np_type = __best_dtype([dtype_min, dtype_max])

    return __apply_shift_and_scale(self, numpy.array(self)).astype(np_type)


MemImage.numpy = __convert_image_into_numpy_array
SharedImage.numpy = __convert_image_into_numpy_array


def __SI_assign_array(self, arr, casting="same_kind"):
    """
    Copies the contents of arr to the SharedImage.
    Automatically calls setDirtyMem.

    The casting parameters behaves like numpy.copyto.
    """
    mem = numpy.array(self, copy=False)
    numpy.copyto(mem, arr, casting=casting)
    self.set_dirty_mem()


SharedImage.assign_array = __SI_assign_array


def __SIS_apply_shift_and_scale(self, arr):
    """
    Return a copy of the array with storage values converted to original values.

    :param self: instance of a SharedImageSet which provides shift and scale
    :param arr: array to be converted from storage values into original values
    :return: numpy.ndarray
    """
    arrays = [si.apply_shift_and_scale(arr[i]) for (i, si) in enumerate(self)]
    np_type = __best_dtype([a.dtype for a in arrays])
    return numpy.array(arrays, dtype=np_type)


SharedImageSet.apply_shift_and_scale = __SIS_apply_shift_and_scale


def __SIS_array(self, **kwargs):
    """
    Convenience method for reading a SharedImageSet as storage values, without shift and scale considered.

    :param self: instance of a SharedImageSet
    :return: numpy.ndarray
    """
    # this is much easier than doing that in C++
    arrays = [numpy.array(self.get(i), copy=False) for i in range(len(self))]
    return numpy.stack(arrays, axis=0)


SharedImageSet.__array__ = __SIS_array


def __SIS_convert_images_into_numpy_array(self):
    """
    Convenience method for reading a SharedImageSet as original values, with shift and scale already applied.

    :param self: instance of a SharedImageSet
    :return: numpy.ndarray
    """
    arrays = [self.get(i).numpy() for i in range(len(self))]
    np_type = __best_dtype([a.dtype for a in arrays])
    return numpy.array(arrays, dtype=np_type)


SharedImageSet.numpy = __SIS_convert_images_into_numpy_array


def __SIS_assign_array(self, arr):
    """
    Copies the contents of arr to the MemImage.
    Automatically calls setDirtyMem.
    """
    num_frames = arr.shape[0]

    for i in range(num_frames):
        if i < self.size:
            mem = numpy.array(self[i], copy=False)
            numpy.copyto(mem, arr[i])
        else:
            self.add(SharedImage(arr[i]))
        self[i].set_dirty_mem()

    while num_frames < self.size:
        self.remove(self[-1])


SharedImageSet.assign_array = __SIS_assign_array

del sys, os
