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
from functools import wraps
from imfusion.labels._bindings import BoundingBox
from imfusion.labels._bindings import BoundingBoxAccessor
from imfusion.labels._bindings import BoundingBoxLayer
from imfusion.labels._bindings import BoundingBoxLayersAccessor
from imfusion.labels._bindings import BoxSet
from imfusion.labels._bindings import DataType
from imfusion.labels._bindings import Descriptor
from imfusion.labels._bindings import GeometryKind
from imfusion.labels._bindings import Label
from imfusion.labels._bindings import LabelLegacy
from imfusion.labels._bindings import LabelMapLayer
from imfusion.labels._bindings import LabelMapsAccessor
from imfusion.labels._bindings import LabelsAccessor
from imfusion.labels._bindings import LabelsAccessorLegacy
from imfusion.labels._bindings import Landmark
from imfusion.labels._bindings import LandmarkLayer
from imfusion.labels._bindings import LandmarkLayersAccessor
from imfusion.labels._bindings import LandmarkSet
from imfusion.labels._bindings import LandmarksAccessor
from imfusion.labels._bindings import Layer
from imfusion.labels._bindings import LayerKind
from imfusion.labels._bindings import LayersAccessor
from imfusion.labels._bindings import LockToken
from imfusion.labels._bindings import Project
from imfusion.labels._bindings import ProjectSettings
from imfusion.labels._bindings import Tag
from imfusion.labels._bindings import TagKind
from imfusion.labels._bindings import TagLegacy
from imfusion.labels._bindings import TagsAccessor
from imfusion.labels._bindings import TagsAccessorLegacy
import types as types
import warnings as warnings
from . import _bindings
__all__ = ['BoundingBox', 'BoundingBoxAccessor', 'BoundingBoxLayer', 'BoundingBoxLayersAccessor', 'BoxSet', 'DataType', 'Descriptor', 'GeometryKind', 'Label', 'LabelLegacy', 'LabelMapLayer', 'LabelMapsAccessor', 'LabelsAccessor', 'LabelsAccessorLegacy', 'Landmark', 'LandmarkLayer', 'LandmarkLayersAccessor', 'LandmarkSet', 'LandmarksAccessor', 'Layer', 'LayerKind', 'LayersAccessor', 'LockToken', 'Project', 'ProjectSettings', 'Tag', 'TagKind', 'TagLegacy', 'TagsAccessor', 'TagsAccessorLegacy', 'deprecate', 'types', 'warnings', 'wraps']
def __DataType_repr(self):
    ...
def __Descriptor_repr(self):
    ...
def deprecate(old: str, new: str, owner: object, is_property = False):
    ...
