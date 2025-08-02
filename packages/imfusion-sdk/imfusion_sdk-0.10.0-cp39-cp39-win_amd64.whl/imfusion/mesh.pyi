"""

Submodules containing routines for pre- and post-processing meshes.
"""
from __future__ import annotations
import imfusion
import numpy
import typing
__all__ = ['PointDistanceResult', 'Primitive', 'create', 'point_distance']
class PointDistanceResult:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, mean_distance: float, median_distance: float, standard_deviation: float, min_distance: float, max_distance: float, distances: numpy.ndarray[numpy.float64[m, 1]]) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def distances(self) -> numpy.ndarray[numpy.float64[m, 1]]:
        ...
    @property
    def max_distance(self) -> float:
        ...
    @property
    def mean_distance(self) -> float:
        ...
    @property
    def median_distance(self) -> float:
        ...
    @property
    def min_distance(self) -> float:
        ...
    @property
    def standard_deviation(self) -> float:
        ...
class Primitive:
    """
    Enumeration of supported mesh primitives.
    
    Members:
    
      SPHERE
    
      CYLINDER
    
      PYRAMID
    
      CUBE
    
      ICOSAHEDRON_SPHERE
    
      CONE
    
      GRID
    """
    CONE: typing.ClassVar[Primitive]  # value = <Primitive.CONE: 5>
    CUBE: typing.ClassVar[Primitive]  # value = <Primitive.CUBE: 3>
    CYLINDER: typing.ClassVar[Primitive]  # value = <Primitive.CYLINDER: 1>
    GRID: typing.ClassVar[Primitive]  # value = <Primitive.GRID: 6>
    ICOSAHEDRON_SPHERE: typing.ClassVar[Primitive]  # value = <Primitive.ICOSAHEDRON_SPHERE: 4>
    PYRAMID: typing.ClassVar[Primitive]  # value = <Primitive.PYRAMID: 2>
    SPHERE: typing.ClassVar[Primitive]  # value = <Primitive.SPHERE: 0>
    __members__: typing.ClassVar[dict[str, Primitive]]  # value = {'SPHERE': <Primitive.SPHERE: 0>, 'CYLINDER': <Primitive.CYLINDER: 1>, 'PYRAMID': <Primitive.PYRAMID: 2>, 'CUBE': <Primitive.CUBE: 3>, 'ICOSAHEDRON_SPHERE': <Primitive.ICOSAHEDRON_SPHERE: 4>, 'CONE': <Primitive.CONE: 5>, 'GRID': <Primitive.GRID: 6>}
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
def create(shape: Primitive) -> imfusion.Mesh:
    """
    Create a mesh primitive.
    
    		Args:
    			shape: The shape of the primitive to create.
    """
@typing.overload
def point_distance(target: imfusion.Mesh, source: imfusion.Mesh, signed_distance: bool = False, range_of_interest: tuple[int, int] | None = None) -> PointDistanceResult:
    """
    	Compute point-wise distances between: 1. source mesh vertices and target mesh surface, 2. source point cloud and target mesh surface, 3. source mesh vertices and target point cloud vertices, 4. source point cloud and the target point cloud
    
    	Args:
    		target: Target data, defining the locations to estimate the distance to.
    		source: Source data, defining the locations to estimate the distance from.
    		signed_distance: Whether to compute signed distances (applicable to meshes only). Defaults to False.
    		range_of_interest: Optional range of distances to consider (min, max) in percentage (integer-valued). Distances outside of this range will be set to NaN. Statistics are computed only over non-NaN distances. Defaults to None.
    
    	Returns:
    		A PointDistanceResult object containing the computed statistics and distances.
    """
@typing.overload
def point_distance(target: imfusion.PointCloud, source: imfusion.Mesh, signed_distance: bool = False, range_of_interest: tuple[int, int] | None = None) -> PointDistanceResult:
    ...
@typing.overload
def point_distance(target: imfusion.PointCloud, source: imfusion.PointCloud, signed_distance: bool = False, range_of_interest: tuple[int, int] | None = None) -> PointDistanceResult:
    ...
@typing.overload
def point_distance(target: imfusion.Mesh, source: imfusion.PointCloud, signed_distance: bool = False, range_of_interest: tuple[int, int] | None = None) -> PointDistanceResult:
    ...
