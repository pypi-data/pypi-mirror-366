"""
This module offers a way of interacting with Labels projects from python.
		The central class in this module is the :class:`Project` class. It allow you to either create a new local project or load an existing local project:

		.. code-block:: python

		    import imfusion
		    from imfusion import labels
		    new_project = labels.Project('New Project', 'path/to/new/project/folder')
		    existing_project = labels.Project.load('path/to/existing/project')
		    remote_project = labels.Project.load('http://example.com', '1', 'username', 'password123')

		From there you can add new tag definitions, annotation definitions and data to the project:

		.. code-block:: python

			project.add_tag('NewTag', labels.TagKind.Bool)
			project.add_labelmap_layer('NewLabelmap')
			project.add_descriptor(imfusion.io.open('/path/to/image')[0])

		The :class:`Project` instance is also the central way to access this kind of data:

		.. code-block:: python

			new_tag = project.tags['NewTag']  # can also be indexed with an integer, i.e. tags[0]
			new_labelmap = project.labelmap_layers['NewLabelmap']  # can also be indexed with an interger, i.e. labelmap_layers[0]
			new_descriptor = project.descriptors[0]

		The :class:`DataDescriptor` class represents an entry in the project's database and can be used to access the the entry's metadata, tags and annotations.
		The interface for accessing tags and annotations is the same as in :class:`Project` but also offers the additional :attr:`value` attribute to get the value of the tag / annotation:

		.. code-block:: python

			name = descriptor.name
			shape = (descriptor.n_images, descriptor.n_channels, descriptor.n_slices, descriptor.height, descriptor.width)
			new_tag = descriptor.tags['NewTag']
			tag_value = descriptor.tags['NewTag'].value
			labelmap = descriptor.labelmap_layers['NewLabelmap'].load()
			roi = descriptor.roi
			image = descriptor.load_image(crop_to_roi=True)

		.. note::

			Keep in mind that all modifications made to a local project are stored in memory and will only be saved to disk if you call :obj:`Project.save() <imfusion.labels.Project.save>`.
			Modifications to remote projects are applied immediately.
			Alternatively, you can also use the :class:`Project` as a context manager:

			.. code-block:: python

				with Project('SomeName', /some/path) as project:
					...  # will automatically save the project when exiting the context if there was no exception

			.. warning::
				Changing annotation data is the only exception to this rule. It is written immediately to disk
				(see :meth:LabelMapLayer.save_new_data`, :meth:LandmarkLayer.save_new_data`, :meth:BoundingBoxLayer.save_new_data`)
"""
from __future__ import annotations
import imfusion
import imfusion.labels
import numpy
import typing
__all__ = ['BoundingBox', 'BoundingBoxAccessor', 'BoundingBoxLayer', 'BoundingBoxLayersAccessor', 'BoxSet', 'DataType', 'Descriptor', 'GeometryKind', 'Label', 'LabelLegacy', 'LabelMapLayer', 'LabelMapsAccessor', 'LabelsAccessor', 'LabelsAccessorLegacy', 'Landmark', 'LandmarkLayer', 'LandmarkLayersAccessor', 'LandmarkSet', 'LandmarksAccessor', 'Layer', 'LayerKind', 'LayersAccessor', 'LockToken', 'Project', 'ProjectSettings', 'Tag', 'TagKind', 'TagLegacy', 'TagsAccessor', 'TagsAccessorLegacy']
class BoundingBox:
    __hash__: typing.ClassVar[None] = None
    color: tuple[int, int, int]
    name: str
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __bool__(self) -> bool:
        ...
    @typing.overload
    def __eq__(self, other: BoundingBox) -> bool:
        ...
    @typing.overload
    def __eq__(self, other: typing.Any) -> typing.Any:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def descriptor(self) -> Descriptor:
        ...
    @property
    def index(self) -> int:
        ...
    @property
    def project(self) -> Project:
        ...
class BoundingBoxAccessor:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __contains__(self, name: str) -> bool:
        ...
    @typing.overload
    def __getitem__(self, index: int) -> BoundingBox:
        """
        Retrieve an entry from this :class:`~imfusion.labels.BoundingBoxAccessor` by its index.
        
        Args:
        	index: Integer index of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, name: str) -> BoundingBox:
        """
        Retrieve an entry from this :class:`~imfusion.labels.BoundingBoxAccessor` by its name.
        
        Args:
        	name: Name of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, slice: slice) -> BoundingBoxAccessor:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.BoundingBoxAccessor` using Python's slice notation (``[start:stop:step]``).
        
        Args:
        	slice: :class:`slice` instance that specifies the indices of entries to be retrieved. Can be implicitly constructed using Python's slice notation.
        """
    @typing.overload
    def __getitem__(self, selection: list[int]) -> BoundingBoxAccessor:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.BoundingBoxAccessor` by using a list of indices.
        
        Args:
        	selection: List of integer indices of the entries to be retrieved.
        """
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    @typing.overload
    def __setitem__(self, index: int, value: typing.Any) -> None:
        """
        Change an existing entry by index.
        
        Args:
        	index: Index of the entry to be changed.
        	value: Value to set at ``index``.
        """
    @typing.overload
    def __setitem__(self, name: str, value: typing.Any) -> None:
        """
        Change an existing entry by name.
        
        Args:
        	name: Name of the entry to be changed.
        	value: Value to set at ``name``.
        """
    @typing.overload
    def __setitem__(self, index: slice, value: list) -> None:
        """
        Change multiple entries denoted using Python's slice notation (``[start:stop:step]``).
        
        Args:
        	slice: :class:`slice` instance that specifies the indices of entries to be changed. Can be implicitly constructed from Python's slice notation or created explicitly with :class:`slice`.
        	value: Value to set at indices specified by``slice``.
        """
    def size(self) -> int:
        ...
    @property
    def names(self) -> list[str]:
        """
        List of the names of :class:`~imfusion.labels.BoundingBox`\s available through this :class:`~imfusion.labels.BoundingBoxAccessor`
        """
class BoundingBoxLayer:
    name: str
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @staticmethod
    def add_boundingbox(*args, **kwargs):
        """
        add_annotation(self: imfusion.labels._bindings.BoundingBoxLayer, name: str, color: tuple[int, int, int] = (255, 255, 255)) -> imfusion.labels._bindings.BoundingBox
        
        
        					Define a new entry in this boundingbox layer. The definition consists of only the name, the actual coordinates for it are stored in the BoxSet.
        
        					Args:
        						name (str): Name of the new boundingbox.
        						color (tuple[int, int, int]): Color for displaying this boundingbox in the UI.
        """
    def __repr__(self) -> str:
        ...
    def add_annotation(self, name: str, color: tuple[int, int, int] = (255, 255, 255)) -> BoundingBox:
        """
        					Define a new entry in this boundingbox layer. The definition consists of only the name, the actual coordinates for it are stored in the BoxSet.
        
        					Args:
        						name (str): Name of the new boundingbox.
        						color (tuple[int, int, int]): Color for displaying this boundingbox in the UI.
        """
    def load(self) -> typing.Any:
        ...
    def save_new_data(self, value: typing.Any, lock_token: LockToken = ...) -> None:
        """
        						Change the data of this layer.
        
        						.. warning::
        
        							Beware that, unlike other modifications, new layer data is immediately written to disk, regardless of calls to :obj:`Project.save() <imfusion.labels.Project.save>`.
        """
    @property
    def annotations(self) -> typing.Any:
        ...
    @property
    def boundingboxes(*args, **kwargs):
        """
        """
    @property
    def descriptor(self) -> Descriptor:
        ...
    @property
    def folder(self) -> str:
        ...
    @property
    def id(self) -> str:
        ...
    @property
    def index(self) -> int:
        ...
    @property
    def project(self) -> Project:
        ...
class BoundingBoxLayersAccessor:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __contains__(self, name: str) -> bool:
        ...
    @typing.overload
    def __getitem__(self, index: int) -> BoundingBoxLayer:
        """
        Retrieve an entry from this :class:`~imfusion.labels.BoundingBoxLayersAccessor` by its index.
        
        Args:
        	index: Integer index of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, name: str) -> BoundingBoxLayer:
        """
        Retrieve an entry from this :class:`~imfusion.labels.BoundingBoxLayersAccessor` by its name.
        
        Args:
        	name: Name of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, slice: slice) -> BoundingBoxLayersAccessor:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.BoundingBoxLayersAccessor` using Python's slice notation (``[start:stop:step]``).
        
        Args:
        	slice: :class:`slice` instance that specifies the indices of entries to be retrieved. Can be implicitly constructed using Python's slice notation.
        """
    @typing.overload
    def __getitem__(self, selection: list[int]) -> BoundingBoxLayersAccessor:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.BoundingBoxLayersAccessor` by using a list of indices.
        
        Args:
        	selection: List of integer indices of the entries to be retrieved.
        """
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def size(self) -> int:
        ...
    @property
    def active(self) -> BoundingBoxLayer | None:
        """
        					Return the currently active layer or None if no layer is active.
        
        					The active layer is usually only relevant when using Python inside the application.
        					It can be set by the user to defined the layer that can be modified with e.g. the brush tool.
        
        					It's currently not possible to change the active layer through the Python API but only in the UI.
        """
    @property
    def names(self) -> list[str]:
        """
        List of the names of :class:`~imfusion.labels.BoundingBoxLayer`\s available through this :class:`~imfusion.labels.BoundingBoxLayersAccessor`
        """
class BoxSet:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @staticmethod
    def from_descriptor(descriptor: Descriptor, layer_name: str) -> BoxSet:
        """
        					Create a BoxSet tailored to a specific annotation layer in a descriptor.
        """
    def __bool__(self) -> bool:
        ...
    def __init__(self, names: list[str], n_frames: int) -> None:
        ...
    def add(self, type: str, frame: int, top_left: numpy.ndarray[numpy.float64[3, 1]], lower_right: numpy.ndarray[numpy.float64[3, 1]]) -> None:
        """
        					Add a box to the set.
        
        					Args:
        						type (str): Type of box that should be added.
        						frame (int): Frame for which this box should be added.
        						top_left (tuple[int, int, int]): Coordinates of the top left corner of the box.
        						lower_right (tuple[int, int, int]): Coordinates of the lower right corner of the box.
        """
    def asdict(self) -> dict:
        """
        Convert this AnnotationSet into a dict. Modifying the dict does not reflect on the AnnotationSet.
        """
    def frame(self, which: int) -> BoxSet:
        """
        Select only the points that belong to the specified frame.
        """
    @typing.overload
    def type(self, type: str) -> BoxSet:
        """
        Select only the points that belong to the specified type.
        """
    @typing.overload
    def type(self, type: int) -> BoxSet:
        """
        Select only the points that belong to the specified type.
        """
class DataType:
    """
    Enum for specifying what is considered valid data in the project.
    
    Members:
    
      SingleChannelImages : Consider 2D greyscale images as valid data.
    
      MultiChannelImages : Consider 2D color images as valid data.
    
      SingleChannelVolumes : Consider 3D greyscale images as valid data.
    
      MultiChannelVolumes : Consider 3D color images as valid data.
    
      AnyDataType : Consider any kind of image data as valid data.
    """
    AnyDataType: typing.ClassVar[DataType]  # value = DataType.AnyDataType
    MultiChannelImages: typing.ClassVar[DataType]  # value = DataType.MultiChannelImages
    MultiChannelVolumes: typing.ClassVar[DataType]  # value = DataType.MultiChannelVolumes
    SingleChannelImages: typing.ClassVar[DataType]  # value = DataType.SingleChannelImages
    SingleChannelVolumes: typing.ClassVar[DataType]  # value = DataType.SingleChannelVolumes
    __members__: typing.ClassVar[dict[str, DataType]]  # value = {'SingleChannelImages': DataType.SingleChannelImages, 'MultiChannelImages': DataType.MultiChannelImages, 'SingleChannelVolumes': DataType.SingleChannelVolumes, 'MultiChannelVolumes': DataType.MultiChannelVolumes, 'AnyDataType': DataType.AnyDataType}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __and__(self, arg0: DataType) -> DataType:
        ...
    @typing.overload
    def __eq__(self, other: typing.Any) -> bool:
        ...
    @typing.overload
    def __eq__(self, arg0: DataType) -> bool:
        ...
    def __ge__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __gt__(self, other: typing.Any) -> bool:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __invert__(self) -> DataType:
        ...
    def __le__(self, other: typing.Any) -> bool:
        ...
    def __lt__(self, other: typing.Any) -> bool:
        ...
    @typing.overload
    def __ne__(self, other: typing.Any) -> bool:
        ...
    @typing.overload
    def __ne__(self, arg0: DataType) -> bool:
        ...
    def __or__(self, arg0: DataType) -> DataType:
        ...
    def __repr__(self):
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    def __xor__(self, arg0: DataType) -> DataType:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Descriptor:
    """
    
    				Class representing an entry in the project's database.
    				It holds, amongst other things, meta data about the image, annotations and the location of the image.
    """
    comments: str
    grouping: list[str]
    name: str
    region_of_interest: tuple[numpy.ndarray[numpy.int32[3, 1]], numpy.ndarray[numpy.int32[3, 1]]]
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __repr__(self):
        ...
    def _export_labelmaps(self, path: str, all_layers: bool = True) -> None:
        """
        					Export the labelmap(s) of this dataset as DicomSeg.
        
        					Args:
        						path (str): File path where the resulting DicomSeg will be saved.
        						all_layers (bool): Whether to export all layers or just the current one.
        """
    def consider_frame_annotated(self, frame: int, annotated: bool) -> None:
        ...
    def is_considered_annotated(self, frame: typing.Any = None) -> bool:
        ...
    def load_image(self, crop_to_roi: bool) -> imfusion.SharedImageSet:
        ...
    def load_thumbnail(self, generate: bool = True) -> imfusion.SharedImageSet:
        """
        					Return the image thumbnail as a SharedImageSet.
        
        					Args:
        						generate (bool): Whether to generate the thumbnail if it's missing. If this is False, the method will return None for missing thumbnails.
        """
    def lock(self) -> LockToken:
        ...
    @property
    def boundingbox_layers(self) -> BoundingBoxLayersAccessor:
        ...
    @property
    def byte_size(self) -> int:
        ...
    @property
    def has_data(self) -> bool:
        ...
    @property
    def height(self) -> int:
        ...
    @property
    def identifier(self) -> str:
        ...
    @property
    def import_time(self) -> int:
        ...
    @property
    def is_locked(self) -> bool:
        ...
    @property
    def labelmap_layers(self) -> LabelMapsAccessor:
        ...
    @property
    def landmark_layers(self) -> LandmarkLayersAccessor:
        ...
    @property
    def latest_edit_time(self) -> int:
        ...
    @property
    def load_path(self) -> tuple[str, str]:
        ...
    @property
    def modality(self) -> imfusion.Data.Modality:
        ...
    @property
    def n_channels(self) -> int:
        ...
    @property
    def n_images(self) -> int:
        ...
    @property
    def n_slices(self) -> int:
        ...
    @property
    def original_data_path(self) -> str:
        ...
    @property
    def own_copy(self) -> bool:
        ...
    @property
    def patient_name(self) -> str:
        ...
    @property
    def project(self) -> Project:
        ...
    @property
    def roi(self) -> typing.Any:
        ...
    @roi.setter
    def roi(self, arg1: tuple[numpy.ndarray[numpy.int32[3, 1]], numpy.ndarray[numpy.int32[3, 1]]]) -> None:
        ...
    @property
    def scale(self) -> float:
        ...
    @property
    def series_instance_uid(self) -> str:
        ...
    @property
    def shift(self) -> float:
        ...
    @property
    def spacing(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        ...
    @property
    def sub_file_id(self) -> str:
        ...
    @property
    def tags(self) -> TagsAccessorLegacy:
        ...
    @property
    def thumbnail_path(self) -> str:
        ...
    @property
    def top_down(self) -> bool:
        ...
    @property
    def type(self) -> imfusion.PixelType:
        ...
    @property
    def width(self) -> int:
        ...
class GeometryKind:
    """
    The kind of geometry that can be used for annotating inside a GEOMETRIC_ANNOTATION layer.
    
    Members:
    
      LANDMARK
    
      BOUNDING_BOX
    """
    BOUNDING_BOX: typing.ClassVar[GeometryKind]  # value = <GeometryKind.BOUNDING_BOX: 1>
    LANDMARK: typing.ClassVar[GeometryKind]  # value = <GeometryKind.LANDMARK: 0>
    __members__: typing.ClassVar[dict[str, GeometryKind]]  # value = {'LANDMARK': <GeometryKind.LANDMARK: 0>, 'BOUNDING_BOX': <GeometryKind.BOUNDING_BOX: 1>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Label:
    """
    A single Label of :class:`~imfusion.labels.Layer` that defines its name and color among other things.
    """
    __hash__: typing.ClassVar[None] = None
    color: tuple[int, int, int]
    geometry: GeometryKind | None
    id: str
    kind: LayerKind
    name: str
    value: int | None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, arg0: Label) -> bool:
        ...
    def __init__(self, name: str, kind: LayerKind, color: tuple[int, int, int] | None = None, value: int | None = None) -> None:
        ...
    def __ne__(self, arg0: Label) -> bool:
        ...
    def __repr__(self) -> str:
        ...
class LabelLegacy:
    __hash__: typing.ClassVar[None] = None
    color: tuple[int, int, int]
    name: str
    value: typing.Any
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __bool__(self) -> bool:
        ...
    @typing.overload
    def __eq__(self, other: LabelLegacy) -> bool:
        ...
    @typing.overload
    def __eq__(self, other: typing.Any) -> typing.Any:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def descriptor(self) -> Descriptor:
        ...
    @property
    def index(self) -> int:
        ...
    @property
    def project(self) -> Project:
        ...
class LabelMapLayer:
    name: str
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @staticmethod
    def add_label(*args, **kwargs):
        """
        add_annotation(self: imfusion.labels._bindings.LabelMapLayer, name: str, value: int, color: Optional[tuple[int, int, int]] = None) -> imfusion.labels._bindings.LabelLegacy
        
        
        					Define a new entry in this labelmap layer. A label is represented by a name and a corresponding integer value for designating voxels in the labelmap.
        
        					Args:
        						name (str): Name of the new label.
        						value (int): Value for encoding this label in the labelmap.
        						color (tuple[int, int, int]): Color for displaying this label in the UI. Int need to be in the range [0 255]. Default colors are picked if not provided.
        """
    def __repr__(self) -> str:
        ...
    def add_annotation(self, name: str, value: int, color: tuple[int, int, int] | None = None) -> LabelLegacy:
        """
        					Define a new entry in this labelmap layer. A label is represented by a name and a corresponding integer value for designating voxels in the labelmap.
        
        					Args:
        						name (str): Name of the new label.
        						value (int): Value for encoding this label in the labelmap.
        						color (tuple[int, int, int]): Color for displaying this label in the UI. Int need to be in the range [0 255]. Default colors are picked if not provided.
        """
    def create_empty_labelmap(self) -> typing.Any:
        """
        					Create an empty labelmap that is compatible with this layer.
        					The labelmap will have the same size and meta data as the image.
        					The labelmap is completely independent of the layer and does not replace the existing labelmap of the layer!
        					To use this labelmap for the layer, call :meth:`LabelMapLayer.save_new_data`.
        """
    def has_data(self) -> bool:
        """
        Return whether the labelmap exists and is not empty.
        """
    def load(self) -> typing.Any:
        """
        				Load the labelmap as a SharedImagetSet.
        				If the labelmap is completely empty, None is returned.
        				To create a new labelmap use :meth:`LabelMapLayer.create_empty_labelmap`.
        """
    def path(self) -> str:
        """
        Returns the path where the labelmap is stored on disk. Empty for remote projects.
        """
    def save_new_data(self, value: typing.Any, lock_token: LockToken = ...) -> None:
        """
        						Change the data of this layer.
        
        						.. warning::
        
        							Beware that, unlike other modifications, new layer data is immediately written to disk, regardless of calls to :obj:`Project.save() <imfusion.labels.Project.save>`.
        """
    def thumbnail_path(self) -> str:
        """
        Returns the path where the labelmap thumbnail is stored on disk. Empty for remote projects.
        """
    @property
    def annotations(self) -> typing.Any:
        ...
    @property
    def descriptor(self) -> Descriptor:
        ...
    @property
    def folder(self) -> str:
        ...
    @property
    def id(self) -> str:
        ...
    @property
    def index(self) -> int:
        ...
    @property
    def labels(*args, **kwargs):
        """
        """
    @property
    def project(self) -> Project:
        ...
class LabelMapsAccessor:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __contains__(self, name: str) -> bool:
        ...
    @typing.overload
    def __getitem__(self, index: int) -> LabelMapLayer:
        """
        Retrieve an entry from this :class:`~imfusion.labels.LabelMapsAccessor` by its index.
        
        Args:
        	index: Integer index of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, name: str) -> LabelMapLayer:
        """
        Retrieve an entry from this :class:`~imfusion.labels.LabelMapsAccessor` by its name.
        
        Args:
        	name: Name of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, slice: slice) -> LabelMapsAccessor:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.LabelMapsAccessor` using Python's slice notation (``[start:stop:step]``).
        
        Args:
        	slice: :class:`slice` instance that specifies the indices of entries to be retrieved. Can be implicitly constructed using Python's slice notation.
        """
    @typing.overload
    def __getitem__(self, selection: list[int]) -> LabelMapsAccessor:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.LabelMapsAccessor` by using a list of indices.
        
        Args:
        	selection: List of integer indices of the entries to be retrieved.
        """
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def size(self) -> int:
        ...
    @property
    def active(self) -> LabelMapLayer | None:
        """
        					Return the currently active layer or None if no layer is active.
        
        					The active layer is usually only relevant when using Python inside the application.
        					It can be set by the user to defined the layer that can be modified with e.g. the brush tool.
        
        					It's currently not possible to change the active layer through the Python API but only in the UI.
        """
    @property
    def names(self) -> list[str]:
        """
        List of the names of :class:`~imfusion.labels.LabelMap`\s available through this :class:`~imfusion.labels.LabelMapsAccessor`
        """
class LabelsAccessor:
    """
    Like a ``list`` of :class:`~imfusion.labels.Label`, but allows indexing by index or name.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __contains__(self, name: str) -> bool:
        ...
    def __eq__(self, arg0: LabelsAccessor) -> bool:
        ...
    @typing.overload
    def __getitem__(self, index: int) -> Label:
        """
        	Retrieve an entry from this :class:`~imfusion.labels.LabelsAccessor` by its index.
        	
        	Args:
        		index: Integer index of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, name: str) -> Label:
        """
        	Retrieve an entry from this :class:`~imfusion.labels.LabelsAccessor` by its name.
        	
        	Args:
        		name: Name of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, slice: slice) -> LabelsAccessor:
        """
        				Retrieve multiple entries from this :class:`~imfusion.labels.LabelsAccessor` using Python's slice notation (``[start:stop:step]``).
        	
        				Args:
        					slice: :class:`slice` instance that specifies the indices of entries to be retrieved. Can be implicitly constructed using Python's slice notation.
        """
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: LabelsAccessor) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def names(self) -> list[str]:
        """
        List of the names of :class:`~imfusion.labels.Label`\s available through this :class:`~imfusion.labels.LabelsAccessor`
        """
class LabelsAccessorLegacy:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __contains__(self, name: str) -> bool:
        ...
    @typing.overload
    def __getitem__(self, index: int) -> LabelLegacy:
        """
        Retrieve an entry from this :class:`~imfusion.labels.LabelsAccessorLegacy` by its index.
        
        Args:
        	index: Integer index of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, name: str) -> LabelLegacy:
        """
        Retrieve an entry from this :class:`~imfusion.labels.LabelsAccessorLegacy` by its name.
        
        Args:
        	name: Name of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, slice: slice) -> LabelsAccessorLegacy:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.LabelsAccessorLegacy` using Python's slice notation (``[start:stop:step]``).
        
        Args:
        	slice: :class:`slice` instance that specifies the indices of entries to be retrieved. Can be implicitly constructed using Python's slice notation.
        """
    @typing.overload
    def __getitem__(self, selection: list[int]) -> LabelsAccessorLegacy:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.LabelsAccessorLegacy` by using a list of indices.
        
        Args:
        	selection: List of integer indices of the entries to be retrieved.
        """
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    @typing.overload
    def __setitem__(self, index: int, value: typing.Any) -> None:
        """
        Change an existing entry by index.
        
        Args:
        	index: Index of the entry to be changed.
        	value: Value to set at ``index``.
        """
    @typing.overload
    def __setitem__(self, name: str, value: typing.Any) -> None:
        """
        Change an existing entry by name.
        
        Args:
        	name: Name of the entry to be changed.
        	value: Value to set at ``name``.
        """
    @typing.overload
    def __setitem__(self, index: slice, value: list) -> None:
        """
        Change multiple entries denoted using Python's slice notation (``[start:stop:step]``).
        
        Args:
        	slice: :class:`slice` instance that specifies the indices of entries to be changed. Can be implicitly constructed from Python's slice notation or created explicitly with :class:`slice`.
        	value: Value to set at indices specified by``slice``.
        """
    def size(self) -> int:
        ...
    @property
    def names(self) -> list[str]:
        """
        List of the names of :class:`~imfusion.labels.LabelLegacy`\s available through this :class:`~imfusion.labels.LabelsAccessorLegacy`
        """
class Landmark:
    __hash__: typing.ClassVar[None] = None
    color: tuple[int, int, int]
    name: str
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __bool__(self) -> bool:
        ...
    @typing.overload
    def __eq__(self, other: Landmark) -> bool:
        ...
    @typing.overload
    def __eq__(self, other: typing.Any) -> typing.Any:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def descriptor(self) -> Descriptor:
        ...
    @property
    def index(self) -> int:
        ...
    @property
    def project(self) -> Project:
        ...
class LandmarkLayer:
    name: str
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @staticmethod
    def add_landmark(*args, **kwargs):
        """
        add_annotation(self: imfusion.labels._bindings.LandmarkLayer, name: str, color: tuple[int, int, int] = (255, 255, 255)) -> imfusion.labels._bindings.Landmark
        
        
        					Define a new entry in this landmark layer. The definition consists of only the name, the actual coordinates for it are stored in the LandmarkSet.
        
        					Args:
        						name (str): Name of the new landmark.
        						color (tuple[int, int, int]): Color for displaying this annotation in the UI.
        """
    def __repr__(self) -> str:
        ...
    def add_annotation(self, name: str, color: tuple[int, int, int] = (255, 255, 255)) -> Landmark:
        """
        					Define a new entry in this landmark layer. The definition consists of only the name, the actual coordinates for it are stored in the LandmarkSet.
        
        					Args:
        						name (str): Name of the new landmark.
        						color (tuple[int, int, int]): Color for displaying this annotation in the UI.
        """
    def load(self) -> typing.Any:
        ...
    def save_new_data(self, value: typing.Any, lock_token: LockToken = ...) -> None:
        """
        						Change the data of this layer.
        
        						.. warning::
        
        							Beware that, unlike other modifications, new layer data is immediately written to disk, regardless of calls to :obj:`Project.save() <imfusion.labels.Project.save>`.
        """
    @property
    def annotations(self) -> typing.Any:
        ...
    @property
    def descriptor(self) -> Descriptor:
        ...
    @property
    def folder(self) -> str:
        ...
    @property
    def id(self) -> str:
        ...
    @property
    def index(self) -> int:
        ...
    @property
    def landmarks(*args, **kwargs):
        """
        """
    @property
    def project(self) -> Project:
        ...
class LandmarkLayersAccessor:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __contains__(self, name: str) -> bool:
        ...
    @typing.overload
    def __getitem__(self, index: int) -> LandmarkLayer:
        """
        Retrieve an entry from this :class:`~imfusion.labels.LandmarkLayersAccessor` by its index.
        
        Args:
        	index: Integer index of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, name: str) -> LandmarkLayer:
        """
        Retrieve an entry from this :class:`~imfusion.labels.LandmarkLayersAccessor` by its name.
        
        Args:
        	name: Name of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, slice: slice) -> LandmarkLayersAccessor:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.LandmarkLayersAccessor` using Python's slice notation (``[start:stop:step]``).
        
        Args:
        	slice: :class:`slice` instance that specifies the indices of entries to be retrieved. Can be implicitly constructed using Python's slice notation.
        """
    @typing.overload
    def __getitem__(self, selection: list[int]) -> LandmarkLayersAccessor:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.LandmarkLayersAccessor` by using a list of indices.
        
        Args:
        	selection: List of integer indices of the entries to be retrieved.
        """
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def size(self) -> int:
        ...
    @property
    def active(self) -> LandmarkLayer | None:
        """
        					Return the currently active layer or None if no layer is active.
        
        					The active layer is usually only relevant when using Python inside the application.
        					It can be set by the user to defined the layer that can be modified with e.g. the brush tool.
        
        					It's currently not possible to change the active layer through the Python API but only in the UI.
        """
    @property
    def names(self) -> list[str]:
        """
        List of the names of :class:`~imfusion.labels.LandmarkLayer`\s available through this :class:`~imfusion.labels.LandmarkLayersAccessor`
        """
class LandmarkSet:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @staticmethod
    def from_descriptor(descriptor: Descriptor, layer_name: str) -> LandmarkSet:
        """
        					Create a LandmarkSet tailored to a specific annotation layer in a descriptor.
        """
    def __bool__(self) -> bool:
        ...
    def __init__(self, names: list[str], n_frames: int) -> None:
        ...
    def add(self, type: str, frame: int, world: numpy.ndarray[numpy.float64[3, 1]]) -> None:
        """
        					Add a keypoint to the set.
        
        					Args:
        						type (str): Type of keypoint that should be added.
        						frame (int): Frame for which this keypoint should be added.
        						world (tuple[int, int, int]): Coordinates of the point.
        """
    def asdict(self) -> dict:
        """
        Convert this AnnotationSet into a dict. Modifying the dict does not reflect on the AnnotationSet.
        """
    def frame(self, which: int) -> LandmarkSet:
        """
        Select only the points that belong to the specified frame.
        """
    @typing.overload
    def type(self, type: str) -> LandmarkSet:
        """
        Select only the points that belong to the specified type.
        """
    @typing.overload
    def type(self, type: int) -> LandmarkSet:
        """
        Select only the points that belong to the specified type.
        """
class LandmarksAccessor:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __contains__(self, name: str) -> bool:
        ...
    @typing.overload
    def __getitem__(self, index: int) -> Landmark:
        """
        Retrieve an entry from this :class:`~imfusion.labels.LandmarksAccessor` by its index.
        
        Args:
        	index: Integer index of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, name: str) -> Landmark:
        """
        Retrieve an entry from this :class:`~imfusion.labels.LandmarksAccessor` by its name.
        
        Args:
        	name: Name of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, slice: slice) -> LandmarksAccessor:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.LandmarksAccessor` using Python's slice notation (``[start:stop:step]``).
        
        Args:
        	slice: :class:`slice` instance that specifies the indices of entries to be retrieved. Can be implicitly constructed using Python's slice notation.
        """
    @typing.overload
    def __getitem__(self, selection: list[int]) -> LandmarksAccessor:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.LandmarksAccessor` by using a list of indices.
        
        Args:
        	selection: List of integer indices of the entries to be retrieved.
        """
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    @typing.overload
    def __setitem__(self, index: int, value: typing.Any) -> None:
        """
        Change an existing entry by index.
        
        Args:
        	index: Index of the entry to be changed.
        	value: Value to set at ``index``.
        """
    @typing.overload
    def __setitem__(self, name: str, value: typing.Any) -> None:
        """
        Change an existing entry by name.
        
        Args:
        	name: Name of the entry to be changed.
        	value: Value to set at ``name``.
        """
    @typing.overload
    def __setitem__(self, index: slice, value: list) -> None:
        """
        Change multiple entries denoted using Python's slice notation (``[start:stop:step]``).
        
        Args:
        	slice: :class:`slice` instance that specifies the indices of entries to be changed. Can be implicitly constructed from Python's slice notation or created explicitly with :class:`slice`.
        	value: Value to set at indices specified by``slice``.
        """
    def size(self) -> int:
        ...
    @property
    def names(self) -> list[str]:
        """
        List of the names of :class:`~imfusion.labels.Landmark`\s available through this :class:`~imfusion.labels.LandmarksAccessor`
        """
class Layer:
    """
    A single layer that defines which labels can be annotated for each :class:`~imfusion.labels.Descriptor`.
    """
    __hash__: typing.ClassVar[None] = None
    id: str
    kind: LayerKind
    name: str
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, arg0: Layer) -> bool:
        ...
    def __init__(self, name: str, kind: LayerKind, labels: list[Label] = []) -> None:
        ...
    def __ne__(self, arg0: Layer) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def add_label(self, arg0: Label) -> None:
        ...
    @property
    def labels(self) -> LabelsAccessor:
        ...
    @labels.setter
    def labels(self, arg1: list[Label]) -> None:
        ...
class LayerKind:
    """
    The kind of a layer defines what can be labelled in that layer.
    
    Members:
    
      PIXELWISE
    
      BOUNDINGBOX
    
      LANDMARK
    
      GEOMETRIC_ANNOTATION
    """
    BOUNDINGBOX: typing.ClassVar[LayerKind]  # value = <LayerKind.BOUNDINGBOX: 1>
    GEOMETRIC_ANNOTATION: typing.ClassVar[LayerKind]  # value = <LayerKind.GEOMETRIC_ANNOTATION: 3>
    LANDMARK: typing.ClassVar[LayerKind]  # value = <LayerKind.LANDMARK: 2>
    PIXELWISE: typing.ClassVar[LayerKind]  # value = <LayerKind.PIXELWISE: 0>
    __members__: typing.ClassVar[dict[str, LayerKind]]  # value = {'PIXELWISE': <LayerKind.PIXELWISE: 0>, 'BOUNDINGBOX': <LayerKind.BOUNDINGBOX: 1>, 'LANDMARK': <LayerKind.LANDMARK: 2>, 'GEOMETRIC_ANNOTATION': <LayerKind.GEOMETRIC_ANNOTATION: 3>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class LayersAccessor:
    """
    Like a ``list`` of :class:`~imfusion.labels.Layer`, but allows indexing by index or name.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __contains__(self, name: str) -> bool:
        ...
    def __eq__(self, arg0: LayersAccessor) -> bool:
        ...
    @typing.overload
    def __getitem__(self, index: int) -> Layer:
        """
        	Retrieve an entry from this :class:`~imfusion.labels.LayersAccessor` by its index.
        	
        	Args:
        		index: Integer index of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, name: str) -> Layer:
        """
        	Retrieve an entry from this :class:`~imfusion.labels.LayersAccessor` by its name.
        	
        	Args:
        		name: Name of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, slice: slice) -> LayersAccessor:
        """
        				Retrieve multiple entries from this :class:`~imfusion.labels.LayersAccessor` using Python's slice notation (``[start:stop:step]``).
        	
        				Args:
        					slice: :class:`slice` instance that specifies the indices of entries to be retrieved. Can be implicitly constructed using Python's slice notation.
        """
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: LayersAccessor) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def names(self) -> list[str]:
        """
        List of the names of :class:`~imfusion.labels.Layer`\s available through this :class:`~imfusion.labels.LayersAccessor`
        """
class LockToken:
    """
    
    				A token representing a lock of a DataDescriptor.
    
    				Only the holder of the token can modify the layers of a locked :class:`~imfusion.labels.Descriptor`.
    				Locking is only supported in remote projects. Local projects ignore the locking mechanism.
    				A LockToken can be acquired through :meth:`~imfusion.labels.Descriptor.lock`.
    				It can be used as a context manager so that it is unlocked automatically, when exiting the context.
    				Tokens expire automatically after a certain time depending on the server (default: after 5 minutes).
    
    				.. code-block:: python
    					
    					descriptor = project.descriptors[0]
    					with descriptor.lock() as lock:
    						...
    	
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __enter__(self) -> LockToken:
        ...
    def __exit__(self, arg0: typing.Any, arg1: typing.Any, arg2: typing.Any) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def unlock(self) -> None:
        """
        Releases the lock. The token will become invalid afters and should not be used anymore.
        """
class Project:
    """
    Class that represents a Labels project. A project holds all information regarding defined annotations and data samples
    """
    data_type: DataType
    grouping_hierachy: list[str]
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @staticmethod
    def create(settings: ProjectSettings, path: str = '', username: str = '', password: str = '') -> Project:
        """
        				Create a new project with the given settings.
        
        				:code:`path` can be either a path or URL.
        
        				Passing a folder will create a local project.
        				The folder must be empty otherwise an exception is raised.
        
        				When passing a http(s) URL, it must point to the base URL of a Labels server (e.g. https://example.com and **not** https://example.com/api/v1/projects).
        				Additionally, a valid username and password must be specified.
        				The server might reject a project, e.g. because a project with the same name already exists.
        				In this case, an exception is raised.
        """
    @staticmethod
    def load(path: str, project_id: str | None = None, username: str | None = None, password: str | None = None) -> Project:
        """
        					Load an existing project from disk or from a remote server.
        
        					Args:
        						path (str): Either a folder containing a local project or an URL to a remote project.
        						project_id (str): the ID of the project to load
        						username (str): the username with which to authenticate
        						password (str): the password with which to authenticate
        """
    def __enter__(self) -> Project:
        ...
    def __exit__(self, arg0: typing.Any, arg1: typing.Any, arg2: typing.Any) -> None:
        ...
    def __init__(self, name: str, project_path: str, data_type: DataType = imfusion.labels.DataType.AnyDataType) -> None:
        """
        					Create a new local project. Doing so will also create a new project folder on disk.
        
        					Args:
        						name (str): Name of the project.
        						project_path (str): Folder that should contain all the project's files.
        						data_type (imfusion.labels.DataType): Type of data, which is allowed to be added to this project. By default, there are no restrictions on the type of data.
        """
    def _import_pixelwise_layers(self, path: str, current_layer_only: bool = False) -> bool:
        """
        					Import the given file as pixelwise layers.
        
        					Only works with DicomSeg files.
        					The dataset will be determined according to the Referenced Instance Sequence.
        
        					By default, imports and modifies all layers of the referenced dataset.
        					If current_layer_only is true, only the currently active pixelwise layer is modified.
        """
    def add_boundingbox_layer(self, name: str) -> BoundingBoxLayer:
        """
        					Define a new boundingbox layer for this project.
        
        					Args:
        						name (str): Name of the new boundingbox layer.
        """
    @typing.overload
    def add_descriptor(self, shared_image_set: imfusion.SharedImageSet, name: str = '', own_copy: bool = False) -> typing.Any:
        """
        Create a new entry in the project's database from a given image.
        For local project, the descriptor to the dataset is returned immediately.
        For remote project, only the identifier of the descriptor is returned.
        The actual dataset will only become available after a call to sync().
        
        Args:
        	name (str): Name of the new database entry.
        	shared_image_set (imfusion.SharedImageSet): Image for which the new entry will be created.
        	own_copy (bool): If True, Labels will save a copy of the image in the project folder.
        		Automatically set to True if the image does not have a DataSourceComponent, as this implies that is was created rather then loaded.
        """
    @typing.overload
    def add_descriptor(self, name: str, shared_image_set: imfusion.SharedImageSet, own_copy: bool = False) -> typing.Any:
        """
        Create a new entry in the project's database from a given image.
        For local project, the descriptor to the dataset is returned immediately.
        For remote project, only the identifier of the descriptor is returned.
        The actual dataset will only become available after a call to sync().
        
        Args:
        	name (str): Name of the new database entry.
        	shared_image_set (imfusion.SharedImageSet): Image for which the new entry will be created.
        	own_copy (bool): If True, Labels will save a copy of the image in the project folder.
        		Automatically set to True if the image does not have a DataSourceComponent, as this implies that is was created rather then loaded.
        """
    def add_labelmap_layer(self, name: str) -> LabelMapLayer:
        """
        					Define a new labelmap layer for this project.
        
        					Args:
        						name (str): Name of the new labelmap layer.
        """
    def add_landmark_layer(self, name: str) -> LandmarkLayer:
        """
        					Define a new landmark layer for this project.
        
        					Args:
        						name (str): Name of the new landmark layer.
        """
    def add_tag(self, name: str, kind: TagKind, color: tuple[int, int, int] = (255, 255, 255), options: list[str] = []) -> TagLegacy:
        """
        					Define a new tag for this project.
        
        					Args:
        						name (str): Name of the new tag.
        						kind (imfusion.labels.TagKind): Type of the new tag (Bool, Float or Enum).
        						color (tuple[int, int, int]): Color of the tag in the UI.
        						options (list[str]): Options that the user can choose from. Only applies to Enum tags.
        """
    def delete_descriptors(self, descriptors: list[Descriptor]) -> None:
        """
        					"Remove the given descriptors from the project.
        
        					Args:
        						descriptors (list[Descriptors]): list of descriptors that should be deleted from the project.
        """
    def edit(self, arg0: ProjectSettings) -> None:
        """
        					Edit the project settings by applying the given settings.
        
        					Editing a project is a potentially destructive action that cannot be reverted.
        
        					When adding new tags, layers or label their "id" field should be empty (an id
        					will be automatically assigned).
        
        					.. warning::
        
        						Remote project are not edited in-place at the moment.
        						After calling this method, you need to reload the project from
        						the server. Otherwise, the project settings will be out of sync
        						with the server.
        """
    def refresh_access_token(self) -> None:
        """
        					Refresh the access token of a remote project.
        					Access tokens expire after a predefined period of time, and need to be refreshed
        					in order to make further requests.
        """
    def save(self) -> None:
        """
        					Save the modifications performed in memory to disk.
        """
    def settings(self) -> ProjectSettings:
        """
        					Return the current settings of a project.
        
        					The settings are not connected to the project,
        					so changing the settings object does not change the project.
        					Use :meth:`~imfusion.labels.Project.edit` to apply new settings.
        """
    def sync(self) -> int:
        """
        					Synchronize the local state of a remote project.
        					Any "event" that occured between the last sync() call and this one are replayed locally,
        					such that the local Project reflects the last known state of the project on the server.
        					An "event" refers to any change being made on the project data by any client (including
        					this one), such as a dataset being added or deleted, a new label map being uploaded,
        					a tag value being changed, etc.
        
        					Returns the number of events applied to the project.
        """
    @property
    def boundingbox_layers(self) -> BoundingBoxLayersAccessor:
        """
        					Returns an :class:`~imfusion.labels.BoundingBoxLayersAccessor` to the boundingbox layers defined in the project.
        """
    @property
    def configuration(self) -> imfusion.Properties:
        ...
    @property
    def descriptors(self) -> list:
        ...
    @property
    def id(self) -> typing.Any:
        """
        Return the unique id of a remote project.
        """
    @property
    def is_local(self) -> bool:
        """
        Returns whether the project is local
        """
    @property
    def is_remote(self) -> bool:
        """
        Returns whether the project is remote
        """
    @property
    def labelmap_layers(self) -> LabelMapsAccessor:
        """
        					Returns an Accessor to the labelmap layers defined in the project.
        """
    @property
    def landmark_layers(self) -> LandmarkLayersAccessor:
        """
        					Returns an :class:`~imfusion.labels.LandmarkLayerAccessor` to the landmark layers defined in the project.
        """
    @property
    def path(self) -> str:
        ...
    @property
    def tags(self) -> TagsAccessorLegacy:
        """
        										Returns an Accessor to the tags defined in the project.
        """
class ProjectSettings:
    """
    Contains the invididual elements that make up a project definition.
    """
    __hash__: typing.ClassVar[None] = None
    name: str
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, arg0: ProjectSettings) -> bool:
        ...
    def __init__(self, name: str, tags: list[Tag] = [], layers: list[Layer] = []) -> None:
        ...
    def __ne__(self, arg0: ProjectSettings) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def add_layer(self, arg0: Layer) -> None:
        """
        Add a new layer to the settings.
        """
    def add_tag(self, arg0: Tag) -> None:
        """
        Add a new tag to the settings.
        """
    def remove_layer(self, arg0: Layer) -> None:
        ...
    def remove_tag(self, arg0: Tag) -> None:
        ...
    @property
    def layers(self) -> LayersAccessor:
        ...
    @layers.setter
    def layers(self, arg1: list[Layer]) -> None:
        ...
    @property
    def tags(self) -> TagsAccessor:
        ...
    @tags.setter
    def tags(self, arg1: list[Tag]) -> None:
        ...
class Tag:
    """
    A Tag definition. Tag values can be set on a :class:`~imfusion.labels.Descriptor` according to this definition.
    """
    __hash__: typing.ClassVar[None] = None
    color: tuple[int, int, int]
    id: str
    kind: TagKind
    name: str
    options: list
    readonly: bool
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, arg0: Tag) -> bool:
        ...
    def __init__(self, name: str, kind: TagKind, color: tuple[int, int, int] | None = None, options: list = [], readonly: bool = False) -> None:
        ...
    def __ne__(self, arg0: Tag) -> bool:
        ...
    def __repr__(self) -> str:
        ...
class TagKind:
    """
    Enum for differentiating different kinds of tags.
    
    Members:
    
      Bool : Tag that stores a single boolean value.
    
      Enum : Tag that stores a list of string options.
    
      Float : Tag that stores a single float value.
    """
    Bool: typing.ClassVar[TagKind]  # value = <TagKind.Bool: 0>
    Enum: typing.ClassVar[TagKind]  # value = <TagKind.Enum: 1>
    Float: typing.ClassVar[TagKind]  # value = <TagKind.Float: 2>
    __members__: typing.ClassVar[dict[str, TagKind]]  # value = {'Bool': <TagKind.Bool: 0>, 'Enum': <TagKind.Enum: 1>, 'Float': <TagKind.Float: 2>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class TagLegacy:
    __hash__: typing.ClassVar[None] = None
    color: tuple[int, int, int]
    locked: bool
    name: str
    value: typing.Any
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __bool__(self) -> bool:
        ...
    @typing.overload
    def __eq__(self, other: TagLegacy) -> bool:
        ...
    @typing.overload
    def __eq__(self, other: typing.Any) -> typing.Any:
        ...
    def __repr__(self) -> str:
        ...
    def add_option(self, option: str) -> None:
        """
        					Add a new value option for this tag (only works with enum tags).
        
        					Args:
        						option: New option to be added to this tag.
        """
    @property
    def descriptor(self) -> Descriptor:
        ...
    @property
    def id(self) -> str:
        ...
    @property
    def index(self) -> int:
        ...
    @property
    def kind(self) -> TagKind:
        ...
    @property
    def options(self) -> list[str]:
        ...
    @property
    def project(self) -> Project:
        ...
class TagsAccessor:
    """
    Like a ``list`` of :class:`~imfusion.labels.Tag`, but allows indexing by index or name.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __contains__(self, name: str) -> bool:
        ...
    def __eq__(self, arg0: TagsAccessor) -> bool:
        ...
    @typing.overload
    def __getitem__(self, index: int) -> Tag:
        """
        	Retrieve an entry from this :class:`~imfusion.labels.TagsAccessor` by its index.
        	
        	Args:
        		index: Integer index of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, name: str) -> Tag:
        """
        	Retrieve an entry from this :class:`~imfusion.labels.TagsAccessor` by its name.
        	
        	Args:
        		name: Name of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, slice: slice) -> TagsAccessor:
        """
        				Retrieve multiple entries from this :class:`~imfusion.labels.TagsAccessor` using Python's slice notation (``[start:stop:step]``).
        	
        				Args:
        					slice: :class:`slice` instance that specifies the indices of entries to be retrieved. Can be implicitly constructed using Python's slice notation.
        """
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: TagsAccessor) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def names(self) -> list[str]:
        """
        List of the names of :class:`~imfusion.labels.Tag`\s available through this :class:`~imfusion.labels.TagsAccessor`
        """
class TagsAccessorLegacy:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __contains__(self, name: str) -> bool:
        ...
    @typing.overload
    def __getitem__(self, index: int) -> TagLegacy:
        """
        Retrieve an entry from this :class:`~imfusion.labels.TagsAccessorLegacy` by its index.
        
        Args:
        	index: Integer index of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, name: str) -> TagLegacy:
        """
        Retrieve an entry from this :class:`~imfusion.labels.TagsAccessorLegacy` by its name.
        
        Args:
        	name: Name of the entry to be retrieved.
        """
    @typing.overload
    def __getitem__(self, slice: slice) -> TagsAccessorLegacy:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.TagsAccessorLegacy` using Python's slice notation (``[start:stop:step]``).
        
        Args:
        	slice: :class:`slice` instance that specifies the indices of entries to be retrieved. Can be implicitly constructed using Python's slice notation.
        """
    @typing.overload
    def __getitem__(self, selection: list[int]) -> TagsAccessorLegacy:
        """
        Retrieve multiple entries from this :class:`~imfusion.labels.TagsAccessorLegacy` by using a list of indices.
        
        Args:
        	selection: List of integer indices of the entries to be retrieved.
        """
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    @typing.overload
    def __setitem__(self, index: int, value: typing.Any) -> None:
        """
        Change an existing entry by index.
        
        Args:
        	index: Index of the entry to be changed.
        	value: Value to set at ``index``.
        """
    @typing.overload
    def __setitem__(self, name: str, value: typing.Any) -> None:
        """
        Change an existing entry by name.
        
        Args:
        	name: Name of the entry to be changed.
        	value: Value to set at ``name``.
        """
    @typing.overload
    def __setitem__(self, index: slice, value: list) -> None:
        """
        Change multiple entries denoted using Python's slice notation (``[start:stop:step]``).
        
        Args:
        	slice: :class:`slice` instance that specifies the indices of entries to be changed. Can be implicitly constructed from Python's slice notation or created explicitly with :class:`slice`.
        	value: Value to set at indices specified by``slice``.
        """
    def size(self) -> int:
        ...
    @property
    def names(self) -> list[str]:
        """
        List of the names of :class:`~imfusion.labels.TagLegacy`\s available through this :class:`~imfusion.labels.TagsAccessorLegacy`
        """
def _init_thread() -> None:
    """
    			Internal function that initializes some global objects that are bound to the current thread.
    
    			Automatically called when importing the module.
    			Needs to be called again when the bindings should be called from another thread.
    
    			.. warning::
    				Note that the bindings are generally not thread-safe!
    				Do not modify the same local project from multiple threads.
    				Also don't pass object between threads.
    """
