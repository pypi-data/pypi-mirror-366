"""

This module contains functionality for all kinds of registration tasks.
You can find a demonstration of how to perform image registration on our `GitHub <https://github.com/ImFusionGmbH/public-python-demos/blob/master/imfusion_sdk/5_image_registration.ipynb>`_.
"""
from __future__ import annotations
import imfusion
import numpy
import os
import typing
__all__ = ['AbstractImageRegistration', 'DescriptorsRegistrationAlgorithm', 'ImageRegistrationAlgorithm', 'ParametricImageRegistration', 'RegistrationInitAlgorithm', 'RegistrationResults', 'RegistrationResultsAlgorithm', 'VolumeBasedMeshRegistrationAlgorithm', 'apply_deformation', 'load_registration_results', 'scan_for_registration_results']
class AbstractImageRegistration(imfusion.BaseAlgorithm):
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
class DescriptorsRegistrationAlgorithm:
    """
    
    Class for performing image registration using local feature descriptors.
    
    This algorithm performs the following steps:
    1) Preprocess the fixed and moving images to prepare them for feature extraction. This consists of resampling to :attr:`~imfusion.reg.DescriptorsRegistrationAlgorithm.spacing` and baking-in the rotation.
    2) Extract feature descriptors using either DISAFeaturesAlgorithm or MINDDescriptorAlgorithm depending on :attr:`~imfusion.reg.DescriptorsRegistrationAlgorithm.descriptor_type`\.
    3) Computes the weight for the moving image features.
    4) Instantiates and uses :class:`~imfusion.reg.FeatureMapsRegistrationAlgorithm` to register the feature descriptors images. The computed registration is then applied to the moving image.
    """
    class DescriptorType:
        """
        Members:
        
          DISA : Use the DISA descriptors defined in the paper "DISA: DIfferentiable Similarity Approximation for Universal Multimodal Registration", Ronchetti et al. 2023
        
          MIND
        """
        DISA: typing.ClassVar[DescriptorsRegistrationAlgorithm.DescriptorType]  # value = <DescriptorType.DISA: 0>
        MIND: typing.ClassVar[DescriptorsRegistrationAlgorithm.DescriptorType]  # value = <DescriptorType.MIND: 1>
        __members__: typing.ClassVar[dict[str, DescriptorsRegistrationAlgorithm.DescriptorType]]  # value = {'DISA': <DescriptorType.DISA: 0>, 'MIND': <DescriptorType.MIND: 1>}
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
    DISA: typing.ClassVar[DescriptorsRegistrationAlgorithm.DescriptorType]  # value = <DescriptorType.DISA: 0>
    MIND: typing.ClassVar[DescriptorsRegistrationAlgorithm.DescriptorType]  # value = <DescriptorType.MIND: 1>
    spacing: float
    type: DescriptorsRegistrationAlgorithm.DescriptorType
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, arg0: imfusion.SharedImageSet, arg1: imfusion.SharedImageSet) -> None:
        ...
    def globalRegistration(self) -> None:
        ...
    def heatmap(self, point: numpy.ndarray[numpy.float64[3, 1]]) -> imfusion.SharedImageSet:
        ...
    def initialize_pose(self) -> None:
        ...
    def localRegistration(self) -> None:
        ...
    def processed_fixed(self) -> imfusion.SharedImageSet:
        ...
    def processed_moving(self) -> imfusion.SharedImageSet:
        ...
    @property
    def weight(self) -> imfusion.SharedImageSet:
        ...
class ImageRegistrationAlgorithm(imfusion.BaseAlgorithm):
    """
    
    High-level interface for image registration.
    The image registration algorithm wraps several concrete image registration algorithms (e.g. linear and deformable) and extends them with
    pre-processing techniques. Available pre-processing options include downsampling and gradient-magnitude used for LC2. On creation, the
    algorithm tries to find the best settings for the registration problem depending on the modality, size and other properties of the input
    images. The image registration comes with a default set of different transformation models.
    """
    class PreprocessingOptions:
        """
        
        Flags to enable/disable certain preprocessing options.
        
        Members:
        
          NO_PREPROCESSING : Disable preprocessing completely (this cannot be ORed with other options)
        
          RESTRICT_MEMORY : Downsamples the images so that the registration will not use more than a given maximum of (video) memory
        
          ADJUST_SPACING : if the spacing difference of both images is large, the spacing of the adjusted to the smaller one
        
          IGNORE_FILTERING : Ignore any PreProcessingFilter required by the AbstractImageRegistration object
        
          CACHE_RESULTS : Store PreProcessing results and only re-compute if necessary
        
          NORMALIZE : Normalize images to float range [0.0, 1.0]
        """
        ADJUST_SPACING: typing.ClassVar[ImageRegistrationAlgorithm.PreprocessingOptions]  # value = <PreprocessingOptions.ADJUST_SPACING: 2>
        CACHE_RESULTS: typing.ClassVar[ImageRegistrationAlgorithm.PreprocessingOptions]  # value = <PreprocessingOptions.CACHE_RESULTS: 16>
        IGNORE_FILTERING: typing.ClassVar[ImageRegistrationAlgorithm.PreprocessingOptions]  # value = <PreprocessingOptions.IGNORE_FILTERING: 4>
        NORMALIZE: typing.ClassVar[ImageRegistrationAlgorithm.PreprocessingOptions]  # value = <PreprocessingOptions.NORMALIZE: 32>
        NO_PREPROCESSING: typing.ClassVar[ImageRegistrationAlgorithm.PreprocessingOptions]  # value = <PreprocessingOptions.NO_PREPROCESSING: 0>
        RESTRICT_MEMORY: typing.ClassVar[ImageRegistrationAlgorithm.PreprocessingOptions]  # value = <PreprocessingOptions.RESTRICT_MEMORY: 1>
        __members__: typing.ClassVar[dict[str, ImageRegistrationAlgorithm.PreprocessingOptions]]  # value = {'NO_PREPROCESSING': <PreprocessingOptions.NO_PREPROCESSING: 0>, 'RESTRICT_MEMORY': <PreprocessingOptions.RESTRICT_MEMORY: 1>, 'ADJUST_SPACING': <PreprocessingOptions.ADJUST_SPACING: 2>, 'IGNORE_FILTERING': <PreprocessingOptions.IGNORE_FILTERING: 4>, 'CACHE_RESULTS': <PreprocessingOptions.CACHE_RESULTS: 16>, 'NORMALIZE': <PreprocessingOptions.NORMALIZE: 32>}
        @staticmethod
        def _pybind11_conduit_v1_(*args, **kwargs):
            ...
        def __and__(self, other: typing.Any) -> typing.Any:
            ...
        def __eq__(self, other: typing.Any) -> bool:
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
        def __invert__(self) -> typing.Any:
            ...
        def __le__(self, other: typing.Any) -> bool:
            ...
        def __lt__(self, other: typing.Any) -> bool:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __or__(self, other: typing.Any) -> typing.Any:
            ...
        def __rand__(self, other: typing.Any) -> typing.Any:
            ...
        def __repr__(self) -> str:
            ...
        def __ror__(self, other: typing.Any) -> typing.Any:
            ...
        def __rxor__(self, other: typing.Any) -> typing.Any:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        def __xor__(self, other: typing.Any) -> typing.Any:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class TransformationModel:
        """
        
        Available transformation models. Each one represents a specific registration approach.
        
        Members:
        
          LINEAR : Rigid or affine DOF registration
        
          FFD : Registration with non-linear Free-Form deformations
        
          TPS : Registration with non-linear Thin-Plate-Splines deformations
        
          DEMONS : Registration with non-linear dense (per-pixel) deformations
        
          GREEDY_DEMONS : Registration with non-linear dense (per-pixel) deformations using patch-based SimilarityMeasures
        
          POLY_RIGID : Registration with poly-rigid (i.e. partially piecewise rigid) deformations.
        
          USER_DEFINED
        """
        DEMONS: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.DEMONS: 3>
        FFD: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.FFD: 1>
        GREEDY_DEMONS: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.GREEDY_DEMONS: 4>
        LINEAR: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.LINEAR: 0>
        POLY_RIGID: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.POLY_RIGID: 5>
        TPS: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.TPS: 2>
        USER_DEFINED: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.USER_DEFINED: 100>
        __members__: typing.ClassVar[dict[str, ImageRegistrationAlgorithm.TransformationModel]]  # value = {'LINEAR': <TransformationModel.LINEAR: 0>, 'FFD': <TransformationModel.FFD: 1>, 'TPS': <TransformationModel.TPS: 2>, 'DEMONS': <TransformationModel.DEMONS: 3>, 'GREEDY_DEMONS': <TransformationModel.GREEDY_DEMONS: 4>, 'POLY_RIGID': <TransformationModel.POLY_RIGID: 5>, 'USER_DEFINED': <TransformationModel.USER_DEFINED: 100>}
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
    ADJUST_SPACING: typing.ClassVar[ImageRegistrationAlgorithm.PreprocessingOptions]  # value = <PreprocessingOptions.ADJUST_SPACING: 2>
    CACHE_RESULTS: typing.ClassVar[ImageRegistrationAlgorithm.PreprocessingOptions]  # value = <PreprocessingOptions.CACHE_RESULTS: 16>
    DEMONS: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.DEMONS: 3>
    FFD: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.FFD: 1>
    GREEDY_DEMONS: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.GREEDY_DEMONS: 4>
    IGNORE_FILTERING: typing.ClassVar[ImageRegistrationAlgorithm.PreprocessingOptions]  # value = <PreprocessingOptions.IGNORE_FILTERING: 4>
    LINEAR: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.LINEAR: 0>
    NORMALIZE: typing.ClassVar[ImageRegistrationAlgorithm.PreprocessingOptions]  # value = <PreprocessingOptions.NORMALIZE: 32>
    NO_PREPROCESSING: typing.ClassVar[ImageRegistrationAlgorithm.PreprocessingOptions]  # value = <PreprocessingOptions.NO_PREPROCESSING: 0>
    POLY_RIGID: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.POLY_RIGID: 5>
    RESTRICT_MEMORY: typing.ClassVar[ImageRegistrationAlgorithm.PreprocessingOptions]  # value = <PreprocessingOptions.RESTRICT_MEMORY: 1>
    TPS: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.TPS: 2>
    USER_DEFINED: typing.ClassVar[ImageRegistrationAlgorithm.TransformationModel]  # value = <TransformationModel.USER_DEFINED: 100>
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, fixed: imfusion.SharedImageSet, moving: imfusion.SharedImageSet, model: ImageRegistrationAlgorithm.TransformationModel = ImageRegistrationAlgorithm.TransformationModel.LINEAR) -> None:
        """
        Args:
        	fixed: Input image that stays fixed during the registration.
        	moving: Input image that will be moving registration.
        	model: Defines the registration approach to use. Defaults to rigid / affine registration.
        """
    def compute_preprocessing(self) -> bool:
        """
        Applies the pre-processing options on the input images.
        Results are cached so this is a no-op if the preprocessing options have not changed.
        This function is automatically called by the `compute` method, and therefore does not have to be explicitly called in most cases.
        """
    def reset(self) -> None:
        """
        Resets the transformation of moving to its initial transformation.
        """
    def swap_fixed_and_moving(self) -> None:
        """
        Swaps which image is considered fixed and moving.
        """
    @property
    def best_similarity(self) -> float:
        """
        Returns the best value of the similarity measure after optimization.
        """
    @property
    def fixed(self) -> imfusion.SharedImageSet:
        """
        Returns input image that is currently considered to be fixed.
        """
    @property
    def is_deformable(self) -> bool:
        """
        Indicates whether the current configuration uses a deformable registration
        """
    @property
    def max_memory(self) -> int:
        """
        Restrict the memory used by the registration to the given amount in mebibyte.
        The value can be set in any case but will only have an effect if the RestrictMemory option is enabled.
        This will restrict video memory as well.
        The minimum size is 64 MB (the value will be clamped).
        """
    @max_memory.setter
    def max_memory(self, arg1: int) -> None:
        ...
    @property
    def moving(self) -> imfusion.SharedImageSet:
        """
        Returns input image that is currently considered to be moving.
        """
    @property
    def optimizer(self) -> imfusion.Optimizer:
        """
        Reference to the underlying optimizer.
        """
    @optimizer.setter
    def optimizer(self, arg1: imfusion.Optimizer) -> None:
        ...
    @property
    def param_registration(self) -> ParametricImageRegistration:
        """
        Reference to the underlying parametric registration object that actually performs the computation (e.g. parametric registration, deformable registration, etc.).
        Will return None if the transformation model is not parametric.
        """
    @property
    def preprocessing_options(self) -> ImageRegistrationAlgorithm.PreprocessingOptions:
        """
        Which options should be enabled for preprocessing.
        The options are bitwise OR combination of PreprocessingOptions.
        """
    @preprocessing_options.setter
    def preprocessing_options(self, arg1: ImageRegistrationAlgorithm.PreprocessingOptions) -> None:
        ...
    @property
    def registration(self) -> AbstractImageRegistration:
        """
        Reference to the underlying registration object that actually performs the computation (e.g. parametric registration, deformable registration, etc.)
        """
    @property
    def transformation_model(self) -> ImageRegistrationAlgorithm.TransformationModel:
        """
        Transformation model to be used for the registration.
        If the transformation model changes, internal objects will be deleted and recreated.
        The configuration of the current model will be saved and the new model will be configured with any previously saved configuration for that model.
        Any attached identity deformations are removed from both images.
        """
    @transformation_model.setter
    def transformation_model(self, arg1: ImageRegistrationAlgorithm.TransformationModel) -> None:
        ...
    @property
    def verbose(self) -> bool:
        """
        Indicates whether the algorithm is going to print additional and detailed info messages.
        """
    @verbose.setter
    def verbose(self, arg1: bool) -> None:
        ...
class ParametricImageRegistration(imfusion.BaseAlgorithm):
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
class RegistrationInitAlgorithm(imfusion.BaseAlgorithm):
    """
    Initialize the registration of two volumes by moving the second one.
    """
    class Mode:
        """
        Specifies how the distance between images should be computed.
        
        Members:
        
          BOUNDING_BOX
        
          CENTER_OF_MASS
        """
        BOUNDING_BOX: typing.ClassVar[RegistrationInitAlgorithm.Mode]  # value = <Mode.BOUNDING_BOX: 0>
        CENTER_OF_MASS: typing.ClassVar[RegistrationInitAlgorithm.Mode]  # value = <Mode.CENTER_OF_MASS: 1>
        __members__: typing.ClassVar[dict[str, RegistrationInitAlgorithm.Mode]]  # value = {'BOUNDING_BOX': <Mode.BOUNDING_BOX: 0>, 'CENTER_OF_MASS': <Mode.CENTER_OF_MASS: 1>}
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
    BOUNDING_BOX: typing.ClassVar[RegistrationInitAlgorithm.Mode]  # value = <Mode.BOUNDING_BOX: 0>
    CENTER_OF_MASS: typing.ClassVar[RegistrationInitAlgorithm.Mode]  # value = <Mode.CENTER_OF_MASS: 1>
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, image1: imfusion.SharedImageSet, image2: imfusion.SharedImageSet) -> None:
        ...
    @property
    def mode(self) -> RegistrationInitAlgorithm.Mode:
        """
        Initialization mode (align bounding box centers, or center of mass).
        """
    @mode.setter
    def mode(self, arg1: RegistrationInitAlgorithm.Mode) -> None:
        ...
class RegistrationResults:
    """
    
    Class responsible for handling and storing results of data registration.
    Provides functionality to add, remove, apply and manage registration results and their related data.
    `RegistrationResults` can be saved and loaded into ImFusion Registration Results (irr) files, potentially including data source information.
    When data source information is available this class can load the missing data to be able to apply the results.
    Each result contains a registration matrix and (when applicable) a deformation.
    """
    class Result:
        ground_truth: bool
        name: str
        @staticmethod
        def _pybind11_conduit_v1_(*args, **kwargs):
            ...
        def __repr__(self) -> str:
            ...
        def apply(self) -> imfusion.DataList:
            """
            Applies the current result.
            Return: the list of affected data.
            """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __delitem__(self, index: int) -> None:
        """
        Removes the result at the given index.
        """
    def __getitem__(self, index: int) -> RegistrationResults.Result:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> typing.Iterator[RegistrationResults.Result]:
        ...
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def add(self, datalist: list[imfusion.Data], name: str = '', ground_truth: bool = False) -> None:
        ...
    def clear(self) -> None:
        """
        Clears all results.
        """
    def load_missing_data(self) -> list[imfusion.Data]:
        ...
    def remove(self, index: int) -> bool:
        """
        Removes the result at the given index.
        """
    def resolve_data(self, datalist: list[imfusion.Data]) -> None:
        ...
    def save(self, path: str | os.PathLike) -> None:
        ...
    @property
    def has_ground_truth(self) -> bool:
        ...
    @property
    def some_data_missing(self) -> bool:
        ...
    @property
    def source_path(self) -> str | None:
        """
        Returns the number of results.
        """
class RegistrationResultsAlgorithm(imfusion.BaseAlgorithm):
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @property
    def results(self) -> RegistrationResults:
        ...
class VolumeBasedMeshRegistrationAlgorithm(imfusion.BaseAlgorithm):
    """
    
    Calculates a deformable registration between two meshes by calculating a deformable registration between distance volumes.
    Internally, an instance of the DemonsImageRegistration algorithm is used to register the "fixed" distance volume to the "moving" distance volume.
    As this registration computes the **inverse** of the mapping from the fixed to the moving volume, this directly yields a registration of the "moving" Mesh
    to the "fixed" Mesh.
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, fixed: imfusion.Mesh, moving: imfusion.Mesh, pointcloud: imfusion.PointCloud = None) -> None:
        ...
def apply_deformation(image: imfusion.SharedImageSet, adjust_size: bool = True, nearest_interpolation: bool = False) -> imfusion.SharedImageSet:
    """
    Creates a deformed image from the input image and its deformation.
    
    Args:
    	image (SharedImageSet): Input image assumed to have a deformation.
    	adjust_size (bool): Whether the resulting image should adjust its size to encompass the deformation.
    	nearest_interpolation (bool): Whether nearest or linear interpolation is used.
    """
def load_registration_results(path: str) -> RegistrationResults:
    ...
def scan_for_registration_results(directory: str) -> list[RegistrationResults]:
    ...
