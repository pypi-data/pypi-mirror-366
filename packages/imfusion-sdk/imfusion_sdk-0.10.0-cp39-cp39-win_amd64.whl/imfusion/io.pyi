"""
IO
"""
from __future__ import annotations
import imfusion
import os
import typing
__all__ = ['open', 'write']
def open(path: str | os.PathLike) -> list:
    """
    Load the content of a file or folder as a list of :class:`~imfusion.Data`.
    
    The list can contain instances of any class deriving from `Data`, i.e. :class:`~imfusion.SharedImage`, :class:`~imfusion.Mesh`, :class:`~imfusion.PointCloud`, etc...
    
    Args:
    	path: can be path to a file containing a supported file formats, or a folder containing Dicom data, if the imfusion package was built with Dicom support.
    
    Note:
    	An IOError is raised if the file cannot be opened or a ValueError if the filetype is not supported. Some filetypes (like workspaces) cannot be opened by this function, but must be opened with :meth:`imfusion.ApplicationController.open`.
    
    Example:
    	>>> imfusion.load('ct_image.png')  # doctest: +SKIP
    	[imfusion.SharedImageSet(size: 1, [imfusion.SharedImage(USHORT width: 512 height: 512 spacing: 0.661813x0.661813x1 mm)])]  # doctest: +SKIP
    	>>> imfusion.load('multi_label_segmentation.nii.gz')  # doctest: +SKIP
    	[imfusion.SharedImageSet(size: 1, [imfusion.SharedImage(UBYTE width: 128 height: 128 slices: 128 channels: 3 spacing: 1x1x1 mm)])]  # doctest: +SKIP
    	>>> imfusion.load('ultrasound_sweep.imf')  # doctest: +SKIP
    	[imfusion.SharedImageSet(size: 159, [  # doctest: +SKIP
    		imfusion.SharedImage(UBYTE width: 457 height: 320 spacing: 0.4x0.4x1 mm),  # doctest: +SKIP
    		imfusion.SharedImage(UBYTE width: 457 height: 320 spacing: 0.4x0.4x1 mm),  # doctest: +SKIP
    		...  # doctest: +SKIP
    		imfusion.SharedImage(UBYTE width: 457 height: 320 spacing: 0.4x0.4x1 mm)  # doctest: +SKIP
    	>>> imfusion.load('path_to_folder_containing_multiple_dcm_datasets')  # doctest: +SKIP
    	[imfusion.SharedImageSet(size: 1, [imfusion.SharedImage(FLOAT width: 400 height: 400 slices: 300 spacing: 2.03642x2.03642x3 mm)])]  # doctest: +SKIP
    """
def write(data_list: list[imfusion.Data], file_path: str | os.PathLike) -> None:
    """
    Save a :class:`~imfusion.Data` instance to the specified file path as an ImFusion file.
    
    :param data: any instance of class deriving from :class:`~imfusion.Data` can be saved with this methods, examples are :class:`~imfusion.SharedImageSet`, :class:`~imfusion.Mesh` and :class:`~imfusion.PointCloud`.
    :param file_path: Path to ImFusion file. The data is saved in a single file. File path must end with `.imf`.
    
    Note:
    	Raises a RuntimeError on failure or if `file_path` doesn't end with `.imf` extension.
    
    Example:
    	>>> mesh = Mesh(...)
    	>>> imfusion.save(mesh, 'path/to/imf/file.imf')
    """
