"""The `sfcgal` module is the main module of PySFCGAL.

It contains the definition of every geometry classes, plus some I/O functions.
"""

from __future__ import annotations

import functools
import platform
import typing
from enum import Enum
from typing import Optional, Tuple, Union, cast

if typing.TYPE_CHECKING:
    from typing_extensions import TypeAlias

from ._sfcgal import ffi, lib

# Required until Alpha Shapes bug is not fixed on MSVC
compiler = platform.python_compiler()

try:
    import icontract

    has_icontract = True
except ImportError:
    has_icontract = False


def cond_icontract(lambda_func, contract_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            icontract_decorator = getattr(icontract, contract_name)
            decorated_func = icontract_decorator(lambda_func)(func)
            return decorated_func(*args, **kwargs)
        if not has_icontract:
            return func
        return wrapper
    return decorator


# this must be called before anything else
lib.sfcgal_init()


class BufferType(Enum):
    SFCGAL_BUFFER3D_ROUND = 0
    SFCGAL_BUFFER3D_CYLSPHERE = 1
    SFCGAL_BUFFER3D_FLAT = 2


class DimensionError(Exception):
    """Indicates a dimension error, e.g. requesting for the Z coordinates in
    a 2D-point."""

    pass


def sfcgal_version():
    """Returns the version string of SFCGAL"""
    version = ffi.string(lib.sfcgal_version()).decode("utf-8")
    return version


def sfcgal_full_version():
    """Returns the full version string of SFCGAL"""
    version = ffi.string(lib.sfcgal_full_version()).decode("utf-8")
    return version


class Geometry:
    """Geometry mother class, from which every other geometry class inheritates.

    It defines a large bunch of methods that are shared along every geometries.

    Attributes
    ----------
    _owned : bool, default True
        If True, the Python geometry owns the low-level SFCGAL geometry, which is
        removed when the Python structure is cleaned by the garbage collector.

    _geom : _cffi_backend._CDatabase
        SFCGAL geometry associated to the Python Geometry. The operations on the
        geometry are done at the SFCGAL lower level.

    """
    _geom: ffi.CData
    _owned = True

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def distance(self, other: Geometry) -> float:
        """
        Compute the 2D Euclidean distance between this geometry and another geometry.

        Parameters
        ----------
        other : Geometry
            The other geometry object to compute the distance to.

        Returns
        -------
        float
            The 2D Euclidean distance between the two geometries.
        """
        return lib.sfcgal_geometry_distance(self._geom, other._geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def distance_3d(self, other: Geometry) -> float:
        """
        Compute the 3D Euclidean distance between this geometry and another geometry.

        Parameters
        ----------
        other : Geometry
            The other geometry object to compute the 3D distance to.

        Returns
        -------
        float
            The 3D Euclidean distance between the two geometries.
        """
        return lib.sfcgal_geometry_distance_3d(self._geom, other._geom)

    @property
    @cond_icontract(lambda self: self.is_valid(), "require")
    def area(self) -> float:
        """
        Return the area of the geometry.

        This property returns the area of the geometry, applicable
        for surfaces like polygons.

        Returns
        -------
        float
            The area of the geometry.
        """
        return lib.sfcgal_geometry_area(self._geom)

    @property
    def is_empty(self) -> bool:
        """
        Check if the geometry is empty.

        Returns
        -------
        bool
            True if the geometry is empty, False otherwise.
        """
        return lib.sfcgal_geometry_is_empty(self._geom)

    @property
    def has_z(self) -> bool:
        """
        Check if the geometry has a Z component (3D geometry).

        Returns
        -------
        bool
            True if the geometry has a Z component, False otherwise.
        """
        return lib.sfcgal_geometry_is_3d(self._geom) == 1

    @property
    def has_m(self) -> bool:
        """
        Check if the geometry is measured (has an 'M' value).

        Returns
        -------
        bool
            True if the geometry is measured, False otherwise.
        """
        return lib.sfcgal_geometry_is_measured(self._geom) == 1

    @property
    def geom_type(self) -> str:
        """
        Return the type of the geometry as a string.

        Returns
        -------
        str
            The geometry type as a string (e.g., 'Point', 'Polygon').
        """
        return geom_types_r[lib.sfcgal_geometry_type_id(self._geom)]

    @cond_icontract(lambda self: self.is_valid(), "require")
    def area_3d(self) -> float:
        """
        Return the 3D area of the geometry.

        Returns
        -------
        float
            The 3D area of the geometry.
        """
        return lib.sfcgal_geometry_area_3d(self._geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def volume(self) -> float:
        """
        Return the volume of the geometry.

        Returns
        -------
        float
            The volume of the geometry.
        """
        return lib.sfcgal_geometry_volume(self._geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def convexhull(self) -> Optional[Geometry]:
        """
        Compute the 2D convex hull of the geometry.

        Returns
        -------
        Geometry
            The convex hull of the geometry.
        """
        geom = lib.sfcgal_geometry_convexhull(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def convexhull_3d(self) -> Optional[Geometry]:
        """
        Compute the 3D convex hull of the geometry.

        Returns
        -------
        Geometry
            The 3D convex hull of the geometry.
        """
        geom = lib.sfcgal_geometry_convexhull_3d(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def difference(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the difference between this geometry and another in 2D.

        Parameters
        ----------
        other : Geometry
            The other geometry to compute the difference with.

        Returns
        -------
        Geometry
            The resulting geometry after computing the difference.
        """
        geom = lib.sfcgal_geometry_difference(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def difference_3d(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the difference between this geometry and another in 3D.

        Parameters
        ----------
        other : Geometry
            The other geometry to compute the 3D difference with.

        Returns
        -------
        Geometry
            The resulting 3D geometry after computing the difference.
        """
        geom = lib.sfcgal_geometry_difference_3d(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid(), "require")
    def intersects(self, other: Geometry) -> bool:
        """
        Check if this geometry intersects with another geometry in 2D.

        Parameters
        ----------
        other : Geometry
            The other geometry to check intersection with.

        Returns
        -------
        bool
            True if the geometries intersect, False otherwise.
        """
        return lib.sfcgal_geometry_intersects(self._geom, other._geom) == 1

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def intersects_3d(self, other: Geometry) -> bool:
        """
        Check if this geometry intersects with another geometry in 3D.

        Parameters
        ----------
        other : Geometry
            The other geometry to check intersection with.

        Returns
        -------
        bool
            True if the geometries intersect in 3D, False otherwise.
        """
        return lib.sfcgal_geometry_intersects_3d(self._geom, other._geom) == 1

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def intersection(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the intersection of this geometry and another in 2D.

        Parameters
        ----------
        other : Geometry
            The other geometry to compute the intersection with.

        Returns
        -------
        Geometry
            The resulting geometry after the intersection operation.
        """
        geom = lib.sfcgal_geometry_intersection(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def intersection_3d(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the intersection of this geometry and another in 3D.

        Parameters
        ----------
        other : Geometry
            The other geometry to compute the 3D intersection with.

        Returns
        -------
        Geometry
            The resulting geometry after the 3D intersection operation.
        """
        geom = lib.sfcgal_geometry_intersection_3d(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def union(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the union of this geometry and another in 2D.

        Parameters
        ----------
        other : Geometry
            The other geometry to compute the union with.

        Returns
        -------
        Geometry
            The resulting geometry after the union operation.
        """
        geom = lib.sfcgal_geometry_union(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def union_3d(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the union of this geometry and another in 3D.

        Parameters
        ----------
        other : Geometry
            The other geometry to compute the 3D union with.

        Returns
        -------
        Geometry
            The resulting 3D geometry after the union operation.
        """
        geom = lib.sfcgal_geometry_union_3d(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def covers(self, other: Geometry) -> bool:
        """
        Check if this geometry covers another geometry in 2D.

        Parameters
        ----------
        other : Geometry
            The other geometry to check coverage with.

        Returns
        -------
        bool
            True if this geometry covers the other geometry, False otherwise.
        """
        return lib.sfcgal_geometry_covers(self._geom, other._geom) == 1

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def covers_3d(self, other: Geometry) -> bool:
        """
        Check if this geometry covers another geometry in 3D.

        Parameters
        ----------
        other : Geometry
            The other geometry to check 3D coverage with.

        Returns
        -------
        bool
            True if this geometry covers the other geometry in 3D, False otherwise.
        """
        return lib.sfcgal_geometry_covers_3d(self._geom, other._geom) == 1

    @cond_icontract(lambda self: self.is_valid(), "require")
    def triangulate_2dz(self) -> Optional[Geometry]:
        """
        Compute the 2D triangulation of the geometry with Z values.

        Returns
        -------
        Geometry
            The resulting triangulated geometry with Z values.
        """
        geom = lib.sfcgal_geometry_triangulate_2dz(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def tessellate_3d(self) -> Optional[Geometry]:
        """
        Perform tessellation on the geometry.

        Returns
        -------
        Geometry
            The tessellated geometry.
        """
        tessellation = lib.sfcgal_geometry_tesselate(self._geom)
        return Geometry.from_sfcgal_geometry(tessellation)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def tessellate(self) -> Optional[Geometry]:
        """
        Perform tessellation on the geometry.

        Returns
        -------
        Geometry
            The tessellated geometry.
        """
        tri = lib.sfcgal_geometry_triangulate_2dz(self._geom)
        geom = lib.sfcgal_geometry_intersection(self._geom, tri)

        return Geometry.from_sfcgal_geometry(geom)

    def force_lhr(self) -> Optional[Geometry]:
        """
        Force the geometry to have a left-hand rule (LHR) orientation.

        Returns
        -------
        Geometry
            The resulting geometry with LHR orientation.
        """
        geom = lib.sfcgal_geometry_force_lhr(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    def force_rhr(self) -> Optional[Geometry]:
        """
        Force the geometry to have a right-hand rule (RHR) orientation.

        Returns
        -------
        Geometry
            The resulting geometry with RHR orientation.
        """
        geom = lib.sfcgal_geometry_force_rhr(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    def is_valid(self) -> bool:
        """
        Check if the geometry is valid.

        Returns
        -------
        bool
            True if the geometry is valid, False otherwise.
        """
        return lib.sfcgal_geometry_is_valid(self._geom) != 0

    def is_valid_detail(self) -> Tuple[Optional[str], None]:
        """
        Provide detailed information about the validity of the geometry.

        Returns
        -------
        str
            A string describing the reason if the geometry is invalid.
            If valid, returns None.
        """
        invalidity_reason = ffi.new("char **")
        invalidity_location = ffi.new("sfcgal_geometry_t **")
        lib.sfcgal_geometry_is_valid_detail(
            self._geom, invalidity_reason, invalidity_location
        )
        ffi_invalidity_reason = invalidity_reason[0]

        # If ffi_invalidity_reason is Null, the geometry is valid.
        if ffi_invalidity_reason == ffi.NULL:
            return (None, None)

        return (ffi.string(ffi_invalidity_reason).decode("utf-8"), None)

    def is_planar(self) -> bool:
        """
        Check if the geometry is planar.

        Returns
        -------
        bool
            True if the geometry is planar, False otherwise.
        """
        return lib.sfcgal_geometry_is_planar(self._geom) == 1

    @cond_icontract(lambda self: self.is_valid(), "require")
    def orientation(self) -> int:
        """
        Get the orientation of the geometry.

        Returns
        -------
        int
            The orientation of the geometry.
        """
        return lib.sfcgal_geometry_orientation(self._geom)

    @cond_icontract(lambda self, r: self.is_valid(), "require")
    def round(self, r: int) -> Optional[Geometry]:
        """
        Round the geometry to a specified precision.

        Parameters
        ----------
        r : float
            The precision to which to round the geometry.

        Returns
        -------
        float
            The rounded geometry.
        """
        geom = lib.sfcgal_geometry_round(self._geom, r)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, other: self.is_valid() and other.is_valid(), "require")
    def minkowski_sum(self, other: Geometry) -> Optional[Geometry]:
        """
        Calculate the Minkowski sum of this geometry and another geometry.

        Parameters
        ----------
        other : Geometry
            The other geometry to calculate the Minkowski sum with.

        Returns
        -------
        Geometry
            The resulting Minkowski sum geometry.
        """
        geom = lib.sfcgal_geometry_minkowski_sum(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, radius: self.is_valid(), "require")
    def offset_polygon(self, radius: float) -> Optional[Geometry]:
        """
        Create an offset polygon from the geometry.

        Parameters
        ----------
        radius : float
            The radius of the offset.

        Returns
        -------
        Geometry
            The resulting offset polygon geometry.
        """
        geom = lib.sfcgal_geometry_offset_polygon(self._geom, radius)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, extrude_x, extrude_y, extrude_z: self.is_valid(), "require"
    )
    def extrude(
            self, extrude_x: float, extrude_y: float, extrude_z: float
    ) -> Optional[Geometry]:
        """
        Extrude the geometry in the specified direction.

        Parameters
        ----------
        extrude_x : float
            The distance to extrude in the x direction.
        extrude_y : float
            The distance to extrude in the y direction.
        extrude_z : float
            The distance to extrude in the z direction.

        Returns
        -------
        Geometry
            The resulting extruded geometry.
        """
        geom = lib.sfcgal_geometry_extrude(self._geom, extrude_x, extrude_y, extrude_z)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def straight_skeleton(self) -> Optional[Geometry]:
        """
        Compute the straight skeleton of the geometry.

        Returns
        -------
        Geometry
            The resulting straight skeleton geometry.
        """
        geom = lib.sfcgal_geometry_straight_skeleton(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def straight_skeleton_distance_in_m(self) -> Optional[Geometry]:
        """
        Compute the straight skeleton distance in meters.

        Returns
        -------
        Geometry
            The resulting geometry representing the straight skeleton distance.
        """
        geom = lib.sfcgal_geometry_straight_skeleton_distance_in_m(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, height: (
            self.is_valid() and self.geom_type == "Polygon" and height != 0
        ),
        "require",
    )
    def extrude_straight_skeleton(self, height: float) -> Optional[Geometry]:
        """
        Extrude the geometry along its straight skeleton.

        Parameters
        ----------
        height : float
            The height to which the geometry will be extruded.

        Returns
        -------
        Geometry
            The resulting extruded geometry along the straight skeleton.
        """
        geom = lib.sfcgal_geometry_extrude_straight_skeleton(self._geom, height)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, building_height, roof_height: (
            self.is_valid() and self.geom_type == "Polygon" and roof_height != 0
        ),
        "require",
    )
    def extrude_polygon_straight_skeleton(
        self, building_height: float, roof_height: float
    ) -> Optional[Geometry]:
        """
        Extrude a polygon along its straight skeleton with specified building
        and roof heights.

        Parameters
        ----------
        building_height : float
            The height of the building.
        roof_height : float
            The height of the roof.

        Returns
        -------
        Geometry
            The resulting geometry with the specified building and roof heights.
        """
        geom = lib.sfcgal_geometry_extrude_polygon_straight_skeleton(
            self._geom, building_height, roof_height
        )
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self: (
            self.is_valid()
            and self.geom_type in ("MultiPolygon", "Polygon", "Triangle")
        ),
        "require",
    )
    def straight_skeleton_partition(self):
        """Returns the straight skeleton partition for the given Polygon

        Returns
        -------
        Geometry
            Partition of the Polygon straight skeleton
        """
        geom = lib.sfcgal_geometry_straight_skeleton_partition(self._geom, True)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self: self.is_valid(), "require")
    def approximate_medial_axis(self) -> Optional[Geometry]:
        """
        Compute the approximate medial axis of the geometry.

        Returns
        -------
        Geometry
            The resulting geometry representing the approximate medial axis.
        """
        geom = lib.sfcgal_geometry_approximate_medial_axis(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, start, end: (
            self.is_valid() and -1. <= start <= 1. and -1. <= end <= 1.
        ),
        "require",
    )
    @cond_icontract(lambda result: result.is_valid(), "ensure")
    def line_sub_string(self, start: float, end: float) -> Optional[Geometry]:
        """
        Extract a substring from the geometry represented as a line segment.

        Parameters
        ----------
        start : float
            The start parameter of the substring.
        end : float
            The end parameter of the substring.

        Returns
        -------
        Geometry
            The resulting substring geometry.
        """
        geom = lib.sfcgal_geometry_line_sub_string(self._geom, start, end)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, alpha=1.0, allow_holes=False: (
            self.is_valid() and alpha >= 0
        ),
        "require",
    )
    def alpha_shapes(
            self, alpha: float = 1.0, allow_holes: bool = False) -> Optional[Geometry]:
        """
        Compute the alpha shapes of the geometry.

        Parameters
        ----------
        alpha : float, optional
            The alpha parameter (default is 1.0).
        allow_holes : bool, optional
            Whether to allow holes in the alpha shapes (default is False).

        Returns
        -------
        Geometry
            The resulting alpha shapes geometry.
        """
        if "MSC" in compiler:
            raise NotImplementedError(
                "Alpha shapes methods is not available on Python versions using MSVC "
                "compiler. See: https://github.com/CGAL/cgal/issues/7667"
            )
        geom = lib.sfcgal_geometry_alpha_shapes(self._geom, alpha, allow_holes)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, allow_holes=False, nb_components=1: (
            self.is_valid() and nb_components >= 0
        ),
        "require",
    )
    def optimal_alpha_shapes(
        self, allow_holes: bool = False, nb_components: int = 1
    ) -> Optional[Geometry]:
        """
        Compute the optimal alpha shapes of the geometry.

        Parameters
        ----------
        allow_holes : bool, optional
            Whether to allow holes in the optimal alpha shapes (default is False).
        nb_components : int, optional
            The number of components to consider (default is 1).

        Returns
        -------
        Geometry
            The resulting optimal alpha shapes geometry.
        """
        if "MSC" in compiler:
            raise NotImplementedError(
                "Alpha shapes methods is not available on Python versions using MSVC "
                "compiler. See: https://github.com/CGAL/cgal/issues/7667"
            )
        geom = lib.sfcgal_geometry_optimal_alpha_shapes(
            self._geom, allow_holes, nb_components
        )
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, relative_alpha, relative_offset=0: (
            self.is_valid() and relative_alpha > 0 and relative_offset >= 0
        ),
        "require",
    )
    def alpha_wrapping_3d(
            self, relative_alpha: int, relative_offset: int = 0) -> Optional[Geometry]:
        """
        Compute the 3D alpha wrapping of a geometry

        Parameters
        ----------
        relative_alpha : int
            The relative_alpha parameter
        relative_offset : int, optional
            The alpha parameter (default is 0).
            If relative_offset is equal, it is automatically computed
            from the relative_alpha parameter.

        Returns
        -------
        Geometry
            The resulting 3D alpha wrapping geometry as a PolyhedralSurface.
        """
        geom = lib.sfcgal_geometry_alpha_wrapping_3d(
            self._geom, relative_alpha, relative_offset)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, allow_holes, nb_components: self.is_valid(), "require")
    def y_monotone_partition_2(
        self, allow_holes: bool = False, nb_components: int = 1
    ) -> Optional[Geometry]:
        """
        Compute the Y-monotone partition of the geometry in 2D.

        Parameters
        ----------
        allow_holes : bool, optional
            Whether to allow holes in the partition (default is False).
        nb_components : int, optional
            The number of components to consider (default is 1).

        Returns
        -------
        Geometry
            The resulting Y-monotone partition geometry.
        """
        geom = lib.sfcgal_y_monotone_partition_2(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, allow_holes, nb_components: self.is_valid(), "require")
    def approx_convex_partition_2(
        self, allow_holes: bool = False, nb_components: int = 1
    ) -> Optional[Geometry]:
        """
        Compute the approximate convex partition of the geometry in 2D.

        Parameters
        ----------
        allow_holes : bool, optional
            Whether to allow holes in the partition (default is False).
        nb_components : int, optional
            The number of components to consider (default is 1).

        Returns
        -------
        Geometry
            The resulting approximate convex partition geometry.
        """
        geom = lib.sfcgal_approx_convex_partition_2(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, allow_holes, nb_components: self.is_valid(), "require")
    def greene_approx_convex_partition_2(
        self, allow_holes: bool = False, nb_components: int = 1
    ) -> Optional[Geometry]:
        """
        Compute the Greene's approximate convex partition of the geometry in 2D.

        Parameters
        ----------
        allow_holes : bool, optional
            Whether to allow holes in the partition (default is False).
        nb_components : int, optional
            The number of components to consider (default is 1).

        Returns
        -------
        Geometry
            The resulting Greene's approximate convex partition geometry.
        """
        geom = lib.sfcgal_greene_approx_convex_partition_2(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, allow_holes, nb_components: self.is_valid(), "require")
    def optimal_convex_partition_2(
        self, allow_holes: bool = False, nb_components: int = 1
    ) -> Optional[Geometry]:
        """
        Compute the optimal convex partition of the geometry in 2D.

        Parameters
        ----------
        allow_holes : bool, optional
            Whether to allow holes in the partition (default is False).
        nb_components : int, optional
            The number of components to consider (default is 1).

        Returns
        -------
        Geometry
            The resulting optimal convex partition geometry.
        """
        geom = lib.sfcgal_optimal_convex_partition_2(self._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, other: (
            self.is_valid()
            and self.geom_type == "Polygon"
            and other.is_valid()
            and other.geom_type == "Point"
            and self.intersects(other)
        ),
        "require",
    )
    def point_visibility(self, other: Geometry) -> Optional[Geometry]:
        """
        Compute the visibility of a point from a polygon geometry.

        Parameters
        ----------
        other : Geometry
            A point geometry from which the visibility is computed.

        Returns
        -------
        Geometry
            The resulting geometry representing the visibility from the point to
            the polygon.
        """
        geom = lib.sfcgal_geometry_visibility_point(self._geom, other._geom)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(
        lambda self, other_a, other_b: (
            self.is_valid()
            and self.geom_type == "Polygon"
            and other_a.is_valid()
            and other_a.geom_type == "Point"
            and other_b.is_valid()
            and other_b.geom_type == "Point"
            and self.has_exterior_edge(other_a, other_b)
        ),
        "require",
    )
    def segment_visibility(
            self, other_a: Geometry, other_b: Geometry) -> Optional[Geometry]:
        """
        Compute the visibility of a segment between two points from a polygon geometry.

        Parameters
        ----------
        other_a : Geometry
            The first point geometry defining one endpoint of the segment.
        other_b : Geometry
            The second point geometry defining the other endpoint of the segment.

        Returns
        -------
        Geometry
            The resulting geometry representing the visibility along the segment between
            the two points.
        """
        geom = lib.sfcgal_geometry_visibility_segment(
            self._geom, other_a._geom, other_b._geom
        )
        return Geometry.from_sfcgal_geometry(geom)

    def translate_2d(self, dx: float = 0, dy: float = 0) -> Optional[Geometry]:
        """
        This method is an alias for the `translate` function.

        .. deprecated:: 2.0.0
                `translate_2d` will be removed in v3.0.0, it is replaced by
                `translate` in order to be consistent in the function naming.

        Parameters
        ----------
        dx : float, optional
            x component of the translation vector
        dy : float, optional
            y component of the translation vector

        Returns
        -------
        Geometry
            A 2D geometry translated from the current geometry
        """
        return self.translate(dx, dy)

    def translate(self, dx: float = 0, dy: float = 0) -> Optional[Geometry]:
        """Translate a geometry by a 2D vector, hence producing a
        2D-geometry as an output.

        Parameters
        ----------
        dx : float, optional
            x component of the translation vector
        dy : float, optional
            y component of the translation vector

        Returns
        -------
        Geometry
            A 2D geometry translated from the current geometry
        """
        translated_geom = lib.sfcgal_geometry_translate_2d(self._geom, dx, dy)
        return Geometry.from_sfcgal_geometry(translated_geom)

    def translate_3d(
            self, dx: float = 0, dy: float = 0, dz: float = 0) -> Optional[Geometry]:
        """
        Translate a geometry by a 3D vector, hence producing a 3D-geometry as an output.

        If the current geometry is 2D, the starting Z coordinates is assumed to be 0.

        Parameters
        ----------
        dx : float, optional
            x component of the translation vector
        dy : float, optional
            y component of the translation vector
        dz : float, optional
            z component of the translation vector

        Returns
        -------
        Geometry
            A 3D geometry translated from the current geometry
        """
        translated_geom = lib.sfcgal_geometry_translate_3d(self._geom, dx, dy, dz)
        return Geometry.from_sfcgal_geometry(translated_geom)

    def scale_uniform(self, factor: float = 1.) -> Optional[Geometry]:
        """Scale a geometry by a given factor

        Parameters
        ----------
        factor : float, optional
            Scaling factor, 1. by default (identity scale)

        Returns
        -------
        Geometry
            Scaled geometry
        """
        return self.scale(factor, factor, factor)

    def scale(
            self, fx: float = 1., fy: float = 1., fz: float = 1.) -> Optional[Geometry]:
        """Scale a geometry by different factors for each dimension

        Parameters
        ----------
        fx : float, optional
            Scaling factor for x dimension, 1. by default (identity scale)
        fy : float, optional
            Scaling factor for y dimension, 1. by default (identity scale)
        fz : float, optional
            Scaling factor for z dimension, 1. by default (identity scale)

        Returns
        -------
        Geometry
            Scaled geometry
        """
        geom = lib.sfcgal_geometry_scale_3d(self._geom, fx, fy, fz)
        return Geometry.from_sfcgal_geometry(geom)

    def scale_around_center(
            self, fx: float, fy: float, fz: float, cx: float, cy: float, cz: float
    ) -> Optional[Geometry]:
        """
        Scale a geometry by different factors for each dimension around a center point

        Parameters
        ----------
        fx : float
            Scaling factor for x dimension
        fy : float
            Scaling factor for y dimension
        fz : float
            Scaling factor for z dimension
        cx : float
            X-coordinate of the center point
        cy : float
            Y-coordinate of the center point
        cz : float
            Z-coordinate of the center point

        """
        geom = lib.sfcgal_geometry_scale_3d_around_center(
            self._geom, fx, fy, fz, cx, cy, cz
        )
        return Geometry.from_sfcgal_geometry(geom)

    def rotate(self, angle: float = 0.) -> Optional[Geometry]:
        """
        Rotates a geometry around the origin (0,0,0) by a given angle

        Parameters
        ----------
        angle : float, optional
            Rotation angle in radians

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate(self._geom, angle)
        return Geometry.from_sfcgal_geometry(geom)

    def rotate_around_2d_point(
        self, angle: float, cx: float, cy: float
    ) -> Optional[Geometry]:
        """
        Rotates a geometry around a specified point by a given angle

        Parameters
        ----------
        angle : float
            Rotation angle in radians
        cx : float
            X-coordinate of the center point
        cy : float
            Y-coordinate of the center point

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate_2d(self._geom, angle, cx, cy)
        return Geometry.from_sfcgal_geometry(geom)

    def rotate_around_3d_axis(
        self, angle: float, ax: float, ay: float, az: float
    ) -> Optional[Geometry]:
        """
        Rotates a 3D geometry around a specified axis by a given angle

        Parameters
        ----------
        angle : float
            Rotation angle in radians
        ax : float
            X-coordinate of the axis vector
        ay : float
            Y-coordinate of the axis vector
        az : float
            Z-coordinate of the axis vector

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate_3d(self._geom, angle, ax, ay, az)
        return Geometry.from_sfcgal_geometry(geom)

    def rotate_3d_around_center(
        self,
        angle: float,
        ax: float,
        ay: float,
        az: float,
        cx: float,
        cy: float,
        cz: float,
    ) -> Optional[Geometry]:
        """
        Rotates a 3D geometry around a specified axis and center point by a given

        Parameters
        ----------
        angle : float
            Rotation angle in radians
        ax : float
            X-coordinate of the axis vector
        ay : float
            Y-coordinate of the axis vector
        az : float
            Z-coordinate of the axis vector
        cx : float
            X-coordinate of the center point
        cy : float
            Y-coordinate of the center point
        cz : float
            Z-coordinate of the center point

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate_3d_around_center(
            self._geom, angle, ax, ay, az, cx, cy, cz
        )
        return Geometry.from_sfcgal_geometry(geom)

    def rotate_x(self, angle: float = 0.) -> Optional[Geometry]:
        """
        Rotates a geometry around the X axis by a given angle

        Parameters
        ----------
        angle : float, optional
            Rotation angle in radians

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate_x(self._geom, angle)
        return Geometry.from_sfcgal_geometry(geom)

    def rotate_y(self, angle: float = 0.) -> Optional[Geometry]:
        """
        Rotates a geometry around the Y axis by a given angle

        Parameters
        ----------
        angle : float, optional
            Rotation angle in radians

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate_y(self._geom, angle)
        return Geometry.from_sfcgal_geometry(geom)

    def rotate_z(self, angle: float = 0.) -> Optional[Geometry]:
        """
        Rotates a geometry around the Z axis by a given angle

        Parameters
        ----------
        angle : float, optional
            Rotation angle in radians

        Returns
        -------
        Geometry
            The rotated geometry
        """
        geom = lib.sfcgal_geometry_rotate_z(self._geom, angle)
        return Geometry.from_sfcgal_geometry(geom)

    @cond_icontract(lambda self, tolerance: (self.is_valid() and tolerance > 0),
                    "require")
    def simplify(self, tolerance: float, preserveTopology: bool) -> Optional[Geometry]:
        """
        Compute the simplication of the geometry.

        Parameters
        ----------
        tolerance : float
            The simplification threshold.
        preserveTopology : bool
            Preserve topology or not.

        Returns
        -------
        Geometry
            The simplified geometry.
        """
        geom = lib.sfcgal_geometry_simplify(self._geom, tolerance, preserveTopology)
        return Geometry.from_sfcgal_geometry(geom)

    def write_vtk(self, filename: str) -> None:
        """
        Export the geometry to a VTK file.

        Parameters
        ----------
        filename : str
            The name of the file to which the geometry will be exported.

        """
        return lib.sfcgal_geometry_as_vtk_file(self._geom, bytes(filename, 'utf-8'))

    def to_vtk(self) -> str:
        """
        Export the geometry to a VTK string, i.e. basically the content of a VTK file.

        Returns
        -------
        str
            VTK representation of the geometry
        """
        try:
            buf = ffi.new("char**")
            length = ffi.new("size_t*")
            lib.sfcgal_geometry_as_vtk(self._geom, buf, length)
            vtk_string = ffi.string(buf[0], length[0]).decode("utf-8")
        finally:
            # we're responsible for free'ing the memory
            if not buf[0] == ffi.NULL:
                lib.free(buf[0])
        return vtk_string

    def write_obj(self, filename: str) -> None:
        """
        Export the geometry to a OBJ file.

        Parameters
        ----------
        filename : str
            The name of the file to which the geometry will be exported.

        """
        return lib.sfcgal_geometry_as_obj_file(self._geom, bytes(filename, 'utf-8'))

    def to_obj(self) -> str:
        """
        Export the geometry to a OBJ string, i.e. basically the content of a OBJ file.

        Returns
        -------
        str
            OBJ representation of the geometry
        """
        try:
            buf = ffi.new("char**")
            length = ffi.new("size_t*")
            lib.sfcgal_geometry_as_obj(self._geom, buf, length)
            obj_string = ffi.string(buf[0], length[0]).decode("utf-8")
        finally:
            # we're responsible for free'ing the memory
            if not buf[0] == ffi.NULL:
                lib.free(buf[0])
        return obj_string

    def write_stl(self, filename: str) -> None:
        """
        Export the geometry to a STL file.

        Parameters
        ----------
        filename : str
            The name of the file to which the geometry will be exported.

        """
        return lib.sfcgal_geometry_as_stl_file(self._geom, bytes(filename, 'utf-8'))

    def to_stl(self) -> str:
        """
        Export the geometry to a STL string, i.e. basically the content of a STL file.

        Returns
        -------
        str
            STL representation of the geometry
        """
        try:
            buf = ffi.new("char**")
            length = ffi.new("size_t*")
            lib.sfcgal_geometry_as_stl(self._geom, buf, length)
            stl_string = ffi.string(buf[0], length[0]).decode("utf-8")
        finally:
            # we're responsible for free'ing the memory
            if not buf[0] == ffi.NULL:
                lib.free(buf[0])
        return stl_string

    def __del__(self):
        if self._owned and hasattr(self, "_geom"):
            # only free geometries owned by the class
            # this isn't the case when working with geometries contained by
            # a collection (e.g. a GeometryCollection)
            lib.sfcgal_geometry_delete(self._geom)

    def __str__(self):
        return self.to_wkt(8)

    def wrap(self) -> Optional[Geometry]:
        """Wrap the SFCGAL geometry attribute of the current instance in a new geometry
        instance. This method produces a deep copy of the geometry instance.

        Returns
        -------
        Geometry
            A cloned Geometry of the current instance

        """
        return Geometry.from_sfcgal_geometry(lib.sfcgal_geometry_clone(self._geom))

    @staticmethod
    def from_sfcgal_geometry(geom: ffi.CData, owned: bool = True) -> Optional[Geometry]:
        """Wrap the SFCGAL geometry passed as a parameter in a new geometry instance.

        This method allows to build a new Python object from a SFCGAL geometry (which
        is basically a C pointer).

        Parameters
        ----------
        geom : _cffi_backend._CDatabase
            SFCGAL geometry that will be used as an attribute in the new geometry
            instance
        owned : bool
            If True, the new Geometry owns the SFCGAL pointer. Be careful, if a SFCGAL
            pointer is owned by several Geometry instances, there might be some trouble
            after removing one of them (or after the garbage collector action).

        Returns
        -------
        Geometry
            A Geometry instance built from the SFCGAL geometry parameter.

        """
        if geom == ffi.NULL:
            return None
        geom_type_id = lib.sfcgal_geometry_type_id(geom)
        if geom_type_id not in geom_type_to_cls:
            return None
        cls = geom_type_to_cls[geom_type_id]
        geometry: Geometry = object.__new__(cls)
        geometry._geom = geom
        geometry._owned = owned
        return geometry

    def to_coordinates(self):
        """Generates the coordinates of the Geometry.

        Raises
        ------
        NotImplementedError
            The method must be implemented only in child classes.
        """
        raise NotImplementedError(
            "to_coordinates is implemented only for child classes!"
        )

    def to_dict(self) -> dict:
        """Generates a geojson-like dictionary that represents the Geometry.

        This dictionary contains a 'type' key which depicts the geometry type
        (e.g. Point, MultiLineString, Tin, ...) and a 'coordinates' key that contains
        the geometry point coordinates.

        """
        return {"type": self.geom_type, "coordinates": self.to_coordinates()}

    @classmethod
    def from_coordinates(cls, coordinates: list) -> Optional[Geometry]:
        """Instantiates a Geometry starting from a list of coordinates.

        The geometry class may be Point, LineString, Polygon, ...

        Parameters
        ----------
        coordinates : list
            Geometry coordinates, the list structure depends on the geometry type.

        Returns
        -------
        Geometry
            An instance of the corresponding geometry type
        """
        return cls(coordinates)  # type: ignore

    @classmethod
    def from_dict(cls, geojson_data: dict) -> Optional[Geometry]:
        """Instantiates a Geometry starting from a geojson-like dictionnary.

        The dictionary must contain 'type' and 'coordinates' keys; the 'type' value
        should be a valid geometry descriptor.

        The geometry class with which the method is called may be Point, LineString,
        Polygon, ...

        Parameters
        ----------
        geojson_data : dict
            Geometry description, in a geojson-like format

        Returns
        -------
        Geometry
            An instance of the corresponding geometry type
        """
        if geojson_data.get("type") is None:
            raise KeyError("There is no 'type' key in the provided data.")
        if geojson_data.get("coordinates") is None:
            raise KeyError("There is no 'coordinates' key in the provided data.")
        return cls.from_coordinates(geojson_data["coordinates"])

    @staticmethod
    def from_wkt(wkt: str) -> Optional[Geometry]:
        """Parse a Well-Known Text (WKT) representation into a Geometry object.

        This function takes a WKT string and converts it into a `Geometry` object
        by utilizing the SFCGAL library's WKT parsing capabilities.

        Parameters
        ----------
        wkt : str
            The Well-Known Text (WKT) string representing the geometry.

        Returns
        -------
        Geometry
            A `Geometry` object parsed from the WKT string.

        """
        sfcgal_geom = Geometry.sfcgal_geom_from_wkt(wkt)
        return Geometry.from_sfcgal_geometry(sfcgal_geom)

    @staticmethod
    def sfcgal_geom_from_wkt(wkt: str) -> ffi.CData:
        """
        Internal function to read Well-Known Text (WKT) and return the
        SFCGAL geometry object.

        This function converts the WKT string into a UTF-8 encoded byte string,
        and uses the SFCGAL library to create a geometry object from the WKT.

        Parameters
        ----------
        wkt : str
            The Well-Known Text (WKT) string representing the geometry.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Point

        """
        wkt_bytes = bytes(wkt, encoding="utf-8")
        return lib.sfcgal_io_read_wkt(wkt_bytes, len(wkt_bytes))

    @staticmethod
    def from_wkb(wkb: Union[bytes, bytearray]) -> Optional[Geometry]:
        """
        Parse a Well-Known Binary (WKB) representation into a Geometry object.

        This function takes a WKB byte string and converts it into a `Geometry` object
        by utilizing the SFCGAL library's WKB parsing capabilities.

        Parameters
        ----------
        wkb : bytes
            The Well-Known Binary (WKB) byte string representing the geometry.

        Returns
        -------
        Geometry
            A `Geometry` object parsed from the WKB byte string.
        """
        sfcgal_geom = Geometry.sfcgal_geom_from_wkb(wkb)
        return Geometry.from_sfcgal_geometry(sfcgal_geom)

    @staticmethod
    def sfcgal_geom_from_wkb(wkb: Union[str, bytes, bytearray]) -> ffi.CData:
        """Internal function to read a Well-Known Binary (WKB) representation
        and return the SFCGAL geometry object.

        This function accepts a WKB representation in either binary format
        (bytes or bytearray) or hexadecimal string format,
        converts it into a UTF-8 encoded byte string, and uses the SFCGAL
        library to generate the corresponding geometry object.

        Parameters
        ----------
        wkb : bytes, bytearray, or str
            The Well-Known Binary (WKB) data representing the geometry.
            - If a `bytes` or `bytearray` object is provided, it is automatically
            converted to a hexadecimal string.
            - If a `str` is provided, it must already be a hexadecimal string.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Point

        """
        if isinstance(wkb, (bytes, bytearray)):
            wkb = wkb.hex()
        elif not isinstance(wkb, str):
            raise TypeError("WKB must be a hexadecimal str or data binary")
        wkb = bytes(wkb, encoding="utf-8")
        return lib.sfcgal_io_read_wkb(wkb, len(wkb))

    def to_wkt(self, decim: int = -1) -> str:
        """Convert a geometry object into its Well-Known Text (WKT) representation.

        This function takes a geometry object and returns its WKT representation as a
        string.
        If the `decim` parameter is provided and is non-negative, the WKT will include
        a specific number of decimal places.

        Parameters
        ----------
        decim : int, optional
            The number of decimal places to include in the WKT output.
            If `decim` is negative (default), the WKT is returned without a specific
            decimal precision.

        Returns
        -------
        str
            The Well-Known Text (WKT) representation of the geometry.

        """
        wkt = ""
        try:
            buf = ffi.new("char**")
            length = ffi.new("size_t*")
            if decim >= 0:
                lib.sfcgal_geometry_as_text_decim(self._geom, decim, buf, length)
            else:
                lib.sfcgal_geometry_as_text(self._geom, buf, length)
            wkt = ffi.string(buf[0], length[0]).decode("utf-8")
        finally:
            # we're responsible for free'ing the memory
            if not buf[0] == ffi.NULL:
                lib.free(buf[0])
        return wkt

    def to_wkb(self, as_hex: bool = False) -> str:
        """Convert a geometry object into its Well-Known Binary (WKB) or Hexadecimal WKB
        representation.

        This function takes a geometry object and returns its WKB representation as a
        binary string, or as a hexadecimal string if `as_hex` is set to True. It handles
        memory allocation for the generated WKB and ensures that memory is properly
        freed after use.

        Parameters
        ----------
        as_hex : bool, optional
            If True, the function returns the geometry's WKB as a hexadecimal string.
            If False (default), the WKB is returned as a binary string.

        Returns
        -------
        Union[str, bytes]
            WKB representation of the geometry

        """
        try:
            buf = ffi.new("char**")
            length = ffi.new("size_t*")
            if as_hex:
                lib.sfcgal_geometry_as_hexwkb(self._geom, buf, length)
            else:
                lib.sfcgal_geometry_as_wkb(self._geom, buf, length)

            wkb = ffi.buffer(buf[0], length[0])[:]
        finally:
            # we're responsible for free'ing the memory
            if not buf[0] == ffi.NULL:
                lib.free(buf[0])
        return wkb.decode("utf-8") if as_hex else wkb


class Point(Geometry):
    """Point

    Attributes
    ----------
    _owned : bool, default True
        If True, the Python geometry owns the low-level SFCGAL geometry, which is
        removed when the Python structure is cleaned by the garbage collector.
    _geom : _cffi_backend._CDatabase
        SFCGAL point associated to the Point instance. The operations on the geometry
        are done at the SFCGAL lower level.
    """

    Coord: TypeAlias = Optional[Union[int, float]]

    def __init__(
        self, x: Coord = None, y: Coord = None, z: Coord = None, m: Coord = None
    ):
        self._geom = self.sfcgal_geom_from_coordinates([x, y, z, m])

    def __eq__(self, other: object) -> bool:
        """Two points are equals if their dimension and coordinates are equals
        (x, y, z and m).
        """
        if not isinstance(other, Point):
            return False
        are_point_equal = self.x == other.x and self.y == other.y
        if self.has_z and other.has_z:
            are_point_equal &= self.z == other.z
        elif self.has_z ^ other.has_z:
            return False
        if self.has_m and other.has_m:
            are_point_equal &= self.m == other.m
        elif self.has_m ^ other.has_m:
            return False
        return are_point_equal

    @property
    def x(self) -> Coord:
        """Get the x-coordinate of the point.

        Returns
        -------
        float
            The x-coordinate of the point.
        """
        return lib.sfcgal_point_x(self._geom)

    @property
    def y(self) -> Coord:
        """Get the y-coordinate of the point.

        Returns
        -------
        float
            The y-coordinate of the point.
        """
        return lib.sfcgal_point_y(self._geom)

    @property
    def z(self) -> Coord:
        """Get the z-coordinate of the point.

        Raises
        ------
        DimensionError
            If the point has no z coordinate.

        Returns
        -------
        float
            The z-coordinate of the point.
        """
        if lib.sfcgal_geometry_is_3d(self._geom):
            return lib.sfcgal_point_z(self._geom)
        else:
            raise DimensionError("This point has no z coordinate.")

    @property
    def m(self) -> Coord:
        """Get the m-coordinate of the point.

        Raises
        ------
        DimensionError
            If the point has no m coordinate.

        Returns
        -------
        float
            The m-coordinate of the point.
        """
        if lib.sfcgal_geometry_is_measured(self._geom):
            return lib.sfcgal_point_m(self._geom)
        else:
            raise DimensionError("This point has no m coordinate.")

    @cond_icontract(
        lambda self, radius, segments: (
            self.is_valid() and radius > 0 and segments > 3
        ),
        "require",
    )
    def buffer_3d(self, radius: float, segments: int) -> Optional[Geometry]:
        """
        Computes a 3D buffer around a Point

        Parameters
        ----------
        radius : float
            The buffer radius
        segments : int
            The number of segments to use for approximating curved surfaces

        Returns
        -------
        Geometry
            The buffered geometry

        """
        geom = lib.sfcgal_geometry_buffer3d(self._geom, radius, segments, 0)
        return Geometry.from_sfcgal_geometry(geom)

    def to_coordinates(self) -> Tuple[Coord, ...]:
        """Generates the coordinates of the Point.

        Returns
        -------
        tuple
            Two, three or four floating points depending on the point nature.
        """
        coords: Tuple[Point.Coord, ...] = (self.x, self.y)
        if self.has_m:
            coords += (self.z if self.has_z else None, self.m)
        elif self.has_z:
            coords = (*coords, self.z)
        return coords

    @classmethod
    def from_coordinates(cls, coordinates: list) -> Point:
        """Instantiates a Point starting from a list of coordinates.

        Parameters
        ----------
        coordinates : list
            Point coordinates.

        Returns
        -------
        Point
            The Point that corresponds to the provided coordinates

        """
        return cls(*coordinates)

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: list) -> ffi.CData:
        """Instantiates a SFCGAL Point starting from a list of coordinates.
        If the coordinates are None or if the list is empty, an empty point is returned.

        Parameters
        ----------
        coordinates : list
            Point coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Point

        """
        length_coordinates = len(coordinates)
        if length_coordinates == 0:
            return lib.sfcgal_point_create()
        elif length_coordinates < 2 or length_coordinates > 4:
            raise DimensionError("Coordinates length must be 2, 3 or 4.")

        if all(coord is None for coord in coordinates):
            return lib.sfcgal_point_create()
        elif any(coord is None for coord in coordinates[:2]):
            raise ValueError(
                f"These coordinate set is unvalid ({coordinates}), "
                "X and Y must be defined."
            )

        if length_coordinates == 2:
            return lib.sfcgal_point_create_from_xy(*coordinates)
        elif length_coordinates == 3:
            return lib.sfcgal_point_create_from_xyz(*coordinates)
        elif length_coordinates == 4:
            has_z = coordinates[2] is not None
            has_m = coordinates[3] is not None
            if not has_z and not has_m:
                return lib.sfcgal_point_create_from_xy(coordinates[0], coordinates[1])
            elif has_z and not has_m:
                return lib.sfcgal_point_create_from_xyz(
                    coordinates[0], coordinates[1], coordinates[2]
                )
            elif not has_z and has_m:
                return lib.sfcgal_point_create_from_xym(
                    coordinates[0], coordinates[1], coordinates[3]
                )
            else:
                return lib.sfcgal_point_create_from_xyzm(*coordinates)


class LineString(Geometry):
    def __init__(self, coords: Tuple = ()):
        """Initialize a LineString with a tuple of point coordinates.

        Parameters
        ----------
        coords : list of tuples
            A list of tuples where each tuple represents the coordinates of a point in
            the LineString.
        """
        self._geom = self.sfcgal_geom_from_coordinates(list(coords))

    def __eq__(self, other: object) -> bool:
        """Two LineStrings are equals if they contain the same points in the same
        order."""
        if not isinstance(other, LineString):
            return False
        if len(self) != len(other):
            return False
        for p, other_p in zip(self, other):
            if not p == other_p:
                return False
        return True

    def __len__(self):
        """Return the number of points in the LineString.

        Returns
        -------
        int
            The number of points in the LineString.
        """
        return lib.sfcgal_linestring_num_points(self._geom)

    def __iter__(self):
        """Iterate over the points in the LineString.

        Yields
        ------
        Point
            The points in the LineString.
        """
        for n in range(len(self)):
            yield Geometry.from_sfcgal_geometry(
                lib.sfcgal_linestring_point_n(self._geom, n),
                owned=False,
            )

    def __get_point_n(self, n):
        """Returns the n-th point within a linestring. This method is internal and makes
        the assumption that the index is valid for the geometry.

        Parameters
        ----------
        n : int
            Index of the point to recover.

        Returns
        -------
        Point
            Point at the index n.
        """
        return Geometry.from_sfcgal_geometry(
            lib.sfcgal_linestring_point_n(self._geom, n), owned=False
        )

    def __getitem__(self, key):
        """Get a point (or several) within a linestring, identified through an index or
        a slice.

        Raises an IndexError if the key is invalid for the geometry.

        Raises a TypeError if the key is neither an integer or a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the point(s) to recover.

        Returns
        -------
        Point or list of Points
            The Point(s) at the specified index or indices.
        """
        length = self.__len__()
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_point_n(index)
        elif isinstance(key, slice):
            geoms = [self.__get_point_n(index) for index in range(*key.indices(length))]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    @property
    def coords(self):
        """Return the coordinates of the LineString as a CoordinateSequence.

        Returns
        -------
        CoordinateSequence
            A sequence of coordinates representing the points in the LineString.
        """
        return CoordinateSequence(self)

    def has_edge(self, point_a: Point, point_b: Point) -> bool:
        """Check if the LineString contains the edge between two points.

        Parameters
        ----------
        point_a : Point
            The first point of the edge.
        point_b : Point
            The second point of the edge.

        Returns
        -------
        bool
            True if the edge exists in the LineString, False otherwise.
        """
        return is_segment_in_coordsequence(self.to_coordinates(), point_a, point_b)

    @cond_icontract(
        lambda self, radius, segments, buffer_type: (
            self.is_valid() and radius > 0 and segments > 3 and (
                isinstance(buffer_type, BufferType)
                or (isinstance(buffer_type, int) and buffer_type in (0, 1, 2))
            )
        ),
        "require",
    )
    def buffer_3d(
        self, radius: float, segments: int, buffer_type: Union[BufferType, int]
    ) -> Optional[Geometry]:
        """
        Computes a 3D buffer around a LineString

        Parameters
        ----------
        radius : float
            The buffer radius
        segments : int
            The number of segments to use for approximating curved surfaces
        buffer_type : BufferType|int
            Either 0 (SFCGAL_BUFFER3D_ROUND, Minkowski sum with a sphere),
            1 (SFCGAL_BUFFER3D_CYLSPHERE: Union of cylinders and spheres) or
            2 (SFCGAL_BUFFER3D_FLAT: Construction of a disk on the bisector plane)

        Returns
        -------
        Geometry
            The buffered geometry

        """
        if isinstance(buffer_type, BufferType):
            buffer_type = buffer_type.value
        geom = lib.sfcgal_geometry_buffer3d(self._geom, radius, segments, buffer_type)
        return Geometry.from_sfcgal_geometry(geom)

    def to_coordinates(self) -> list:
        """Generates the coordinates of the LineString.

        Uses the __iter__ property of the LineString to iterate over points.

        Returns
        -------
        list
            List of point coordinates.
        """
        return [point.to_coordinates() for point in self]

    @staticmethod
    def sfcgal_geom_from_coordinates(
            coordinates: list, close: bool = False) -> ffi.CData:
        """Instantiates a SFCGAL LineString starting from a list of coordinates.

        Parameters
        ----------
        coordinates : list
            LineString coordinates.
        close : bool
            If True, the LineString is built as closed even if the coordinates are not,
            i.e. the first point is replicated at the last position.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL LineString

        """
        linestring = lib.sfcgal_linestring_create()
        for coordinate in coordinates:
            cpoint = Point.sfcgal_geom_from_coordinates(coordinate)
            lib.sfcgal_linestring_add_point(linestring, cpoint)
        if close and coordinates[0] != coordinates[-1]:
            cpoint = Point.sfcgal_geom_from_coordinates(coordinates[0])
            lib.sfcgal_linestring_add_point(linestring, cpoint)
        return linestring


class Polygon(Geometry):
    """Polygon

    Attributes
    ----------
    _geom : _cffi_backend._CDatabase
        SFCGAL polygon associated to the Polygon instance. The operations on the
        geometry are done at the SFCGAL lower level.
    """

    def __init__(self, exterior: Tuple = (), interiors: Optional[Tuple] = None):
        """Initialize a Polygon with given exterior and optional interior rings.

        Parameters
        ----------
        exterior : tuples of tuples
            A list of coordinates defining the exterior ring of the polygon.
        interiors : tuple of tuple of tuples, optional
            A list of interior rings, where each interior is defined by a list of
            coordinates. Default is None, which initializes to an empty list.
        """
        if interiors is None:
            interiors = ()
        self._geom = self.sfcgal_geom_from_coordinates(
            [
                exterior,
                *interiors,
            ]
        )

    def __iter__(self):
        """Iterate over the rings of the Polygon.

        Yields
        ------
        Geometry
            The exterior and interior rings of the Polygon.
        """
        for n in range(1 + self.n_interiors):
            yield self.__get_ring_n(n)

    def __getitem__(self, key):
        """Get a ring (or several) within a polygon, identified through an index or a
        slice. The first ring is always the exterior ring, the next ones are the
        interior rings (optional).

        Raises an IndexError if the key is unvalid for the geometry.

        Raises a TypeError if the key is neither an integer or a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the ring(s) to recover.

        Returns
        -------
        Geometry or list of Geometry
            The specified ring or a list of rings if a slice is provided.
        """
        length = 1 + self.n_interiors
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_ring_n(index)
        elif isinstance(key, slice):
            geoms = [self.__get_ring_n(index) for index in range(*key.indices(length))]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    def __eq__(self, other: object) -> bool:
        """Two Polygons are equal if their rings (exterior and interior) are equal.

        Parameters
        ----------
        other : Polygon
            The Polygon to compare against.

        Returns
        -------
        bool
            True if the Polygons are equal, False otherwise.
        """
        if not isinstance(other, Polygon):
            return False
        if self.exterior != other.exterior:
            return False
        if self.n_interiors != other.n_interiors:
            return False
        for p, other_p in zip(self.interiors, other.interiors):
            if p != other_p:
                return False
        return True

    @property
    def exterior(self):
        """Get the exterior ring of the Polygon.

        Returns
        -------
        Geometry
            The exterior ring of the Polygon.
        """
        return Geometry.from_sfcgal_geometry(
            lib.sfcgal_polygon_exterior_ring(self._geom), owned=False
        )

    @property
    def n_interiors(self):
        """Get the number of interior rings in the Polygon.

        Returns
        -------
        int
            The number of interior rings.
        """
        return lib.sfcgal_polygon_num_interior_rings(self._geom)

    @property
    def interiors(self):
        """Get a list of the interior rings of the Polygon.

        Returns
        -------
        list of Geometry
            A list of interior rings.
        """
        interior_rings = []
        for idx in range(self.n_interiors):
            interior_rings.append(
                Geometry.from_sfcgal_geometry(
                    lib.sfcgal_polygon_interior_ring_n(self._geom, idx), owned=False
                )
            )
        return interior_rings

    @property
    def rings(self):
        """Get all the rings of the Polygon, including the exterior and interior rings.

        Returns
        -------
        list of Geometry
            A list containing the exterior ring followed by the interior rings.
        """
        return [self.exterior] + self.interiors

    def __get_ring_n(self, n):
        """Returns the n-th ring within a polygon. This method is internal and makes the
        assumption that the index is valid for the geometry. The 0 index refers to the
        exterior ring.

        Parameters
        ----------
        n : int
            Index of the ring to recover.

        Returns
        -------
        Geometry
            The ring at the specified index.
        """
        return self.rings[n]

    def has_exterior_edge(self, point_a: Point, point_b: Point) -> bool:
        """Check if the polygon has an edge defined by the two given points.

        This method verifies whether the line segment between point_a and point_b lies
        within the exterior ring of the polygon.

        Parameters
        ----------
        point_a : Point
            The first point defining the edge.
        point_b : Point
            The second point defining the edge.

        Returns
        -------
        bool
            True if the edge is part of the exterior ring, False otherwise.
        """
        poly_coordinates = self.to_coordinates()
        exterior_coordinates = poly_coordinates[0]
        return is_segment_in_coordsequence(exterior_coordinates, point_a, point_b)

    def to_coordinates(self) -> list:
        """Generates the coordinates of the Polygon.

        Returns
        -------
        list
            List of the polygon ring coordinates
        """
        return [ring.to_coordinates() for ring in self.rings]

    @classmethod
    def from_coordinates(cls, coordinates: list) -> Optional[Polygon]:
        """Instantiates a Polygon starting from a list of coordinates.

        Parameters
        ----------
        coordinates : list
            Polygon coordinates. The first item corresponds to the coordinates of the
            exterior ring, whilst the following items are the coordinates of the
            interior rings, if they exist.

        Returns
        -------
        Polygon
            The Polygon that corresponds to the provided coordinates

        """
        return cls(
            tuple(coordinates[0]),
            tuple(coordinates[1:]) if len(coordinates) > 0 else None,
        )

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: list) -> ffi.CData:
        """Instantiates a SFCGAL Polygon starting from a list of coordinates.

        Parameters
        ----------
        coordinates : list
            Polygon coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Polygon

        """
        if len(coordinates) == 0 or len(coordinates[0]) == 0:
            return lib.sfcgal_polygon_create()
        exterior = LineString.sfcgal_geom_from_coordinates(coordinates[0], True)
        polygon = lib.sfcgal_polygon_create_from_exterior_ring(exterior)
        for n in range(1, len(coordinates)):
            interior = LineString.sfcgal_geom_from_coordinates(coordinates[n], True)
            lib.sfcgal_polygon_add_interior_ring(polygon, interior)
        return polygon


class CoordinateSequence:
    def __init__(self, parent):
        """Initialize the CoordinateSequence with a parent geometry.

        Parameters
        ----------
        parent : Geometry
            The parent geometry object that this sequence is associated with.
        """
        # keep reference to parent to avoid garbage collection
        self._parent = parent

    def __len__(self):
        """Return the number of coordinates in the sequence.

        Returns
        -------
        int
            The number of coordinates in the sequence.
        """
        return self._parent.__len__()

    def __iter__(self):
        """Iterate over the coordinates in the sequence.

        Yields
        ------
        tuple
            A tuple representing the coordinates of each point.
        """
        length = self.__len__()
        for n in range(0, length):
            yield self.__get_coord_n(n)

    def __get_coord_n(self, n):
        """Returns the n-th coordinate within the sequence.

        This method makes the assumption that the index is valid for the geometry.

        Parameters
        ----------
        n : int
            Index of the coordinate to recover.

        Returns
        -------
        tuple
            A tuple representing the coordinates of the point at index n.
        """
        point_n = lib.sfcgal_linestring_point_n(self._parent._geom, n)
        return Point.from_sfcgal_geometry(point_n, owned=False).to_coordinates()

    def __getitem__(self, key):
        """Get a coordinate (or several) within the sequence, identified through an
        index or a slice.

        Raises an IndexError if the key is invalid for the geometry.

        Raises a TypeError if the key is neither an integer nor a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the coordinate(s) to recover.

        Returns
        -------
        tuple or list of tuples
            The coordinate(s) at the specified index or slice.
        """
        length = self.__len__()
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_coord_n(index)
        elif isinstance(key, slice):
            geoms = [self.__get_coord_n(index) for index in range(*key.indices(length))]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )


class GeometryCollectionBase(Geometry):
    @property
    def geoms(self):
        """Return the geometries in the collection.

        Returns
        -------
        GeometrySequence
            A sequence of geometries contained in this collection.
        """
        return GeometrySequence(self)

    def __len__(self):
        """Return the number of geometries in the collection.

        Returns
        -------
        int
            The number of geometries in the collection.
        """
        return len(self.geoms)

    def __iter__(self):
        """Iterate over the geometries in the collection.

        Yields
        ------
        Geometry
            Each geometry in the collection.
        """
        return self.geoms.__iter__()

    def __getitem__(self, index):
        """Get a geometry (or several) within the collection, identified through an
        index.

        Raises an IndexError if the index is invalid for the geometry collection.

        Parameters
        ----------
        index : int
            Index of the geometry to recover.

        Returns
        -------
        Geometry
            The geometry at the specified index.
        """
        return self.geoms[index]

    def __eq__(self, other: object) -> bool:
        """Check if two geometry collections are equal based on their geometries.

        Parameters
        ----------
        other : GeometryCollectionBase
            The other geometry collection to compare.

        Returns
        -------
        bool
            True if both collections contain the same geometries, False otherwise.
        """
        if not isinstance(other, GeometryCollectionBase):
            return False
        return self.geoms == other.geoms

    def to_coordinates(self):
        """Generates the coordinates for every geometry collection.

        Uses the __iter__ property of the class to iterate over the geometries.

        Returns
        -------
        list
            List of the coordinates of each geometry in the collection
        """
        return [geom.to_coordinates() for geom in self]

    def _add_geometry(self, geometry: Geometry) -> None:
        """Add a geometry to the collection.

        This should not directly be called by a Geometry:
        - A Geometry which inherits from `GeometryCollectionBase` has
            a specialized method. For example, `MultiPoint` has `add_point`.
        - A `GeometryCollection` has `add_geometry`.

        Parameters
        ----------
        geometry: Geometry
            The geometry to add.
        """
        clone = lib.sfcgal_geometry_clone(geometry._geom)
        lib.sfcgal_geometry_collection_add_geometry(self._geom, clone)


class MultiPoint(GeometryCollectionBase):
    def __init__(self, coords: Tuple = ()):
        """Initialize the MultiPoint with a tuple of coordinates.

        Parameters
        ----------
        coords : Tuple
            MultiPoint coordinates.
            If coords is empty, an empty MultiPoint is created.

        Returns
        -------
        MultiPoint
            A MultiPoint with coordinates coords

        """
        self._geom = MultiPoint.sfcgal_geom_from_coordinates(coords)

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: Tuple) -> ffi.CData:
        """Instantiates a SFCGAL MultiPoint starting from a tuple of coordinates.

        Parameters
        ----------
        coordinates : Tuple
            MultiPoint coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL MultiPoint

        """
        multipoint = lib.sfcgal_multi_point_create()
        for coords in coordinates:
            point = Point.sfcgal_geom_from_coordinates(coords)
            lib.sfcgal_geometry_collection_add_geometry(multipoint, point)
        return multipoint

    @cond_icontract(lambda self, point: point.geom_type == "Point", "require")
    def add_point(self, point: Point) -> None:
        """Add a point to the multipoint.

        Parameters
        ----------
        point: Point
            The point to add.
        """
        self._add_geometry(point)


class MultiLineString(GeometryCollectionBase):
    def __init__(self, coords: Tuple = ()):
        """Initialize the MultiLineString with a tuple of coordinates.

        Parameters
        ----------
        coords : Tuple
            MultiLineString coordinates.
            If coords is empty, an empty MultiLineString is created.

        Returns
        -------
        MultiLineString
            A MultiLineString with coordinates coords

        """
        self._geom = MultiLineString.sfcgal_geom_from_coordinates(coords)

    @staticmethod
    def sfcgal_geom_from_coordinates(
            coordinates: Tuple, close: bool = False) -> ffi.CData:
        """Instantiates a SFCGAL MultiLineString starting from a tuple of coordinates.

        Parameters
        ----------
        coordinates : Tuple
            MultiLineString coordinates.
        close : bool
            If True, the linestrings are built as closed even if their coordinates are
            not, i.e. their first point is replicated at the last position.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL MultiLineString

        """
        multilinestring = lib.sfcgal_multi_linestring_create()
        for coords in coordinates:
            linestring = LineString.sfcgal_geom_from_coordinates(coords, close=close)
            lib.sfcgal_geometry_collection_add_geometry(multilinestring, linestring)
        return multilinestring

    @cond_icontract(
        lambda self, linestring: linestring.geom_type == "LineString", "require")
    def add_linestring(self, linestring: LineString) -> None:
        """Add a linestring to the multilinestring.

        Parameters
        ----------
        linestring: LineString
            The linestring to add.
        """
        self._add_geometry(linestring)


class MultiPolygon(GeometryCollectionBase):
    def __init__(self, coords: Tuple = ()):
        """Initialize the MultiPolygon with a tuple of coordinates.

        Parameters
        ----------
        coords : Tuple
            MultiPolygon coordinates.
            If coords is empty, an empty MultiPolygon is created.

        Returns
        -------
        MultiPolygon
            A MultiPolygon with coordinates coords

        """
        self._geom = MultiPolygon.sfcgal_geom_from_coordinates(coords)

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: Tuple) -> ffi.CData:
        """Instantiates a SFCGAL MultiPolygon starting from a tuple of coordinates.

        Parameters
        ----------
        coordinates : Tuple
            MultiPolygon coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL MultiPolygon

        """
        multipolygon = lib.sfcgal_multi_polygon_create()
        if coordinates:
            for coords in coordinates:
                polygon = Polygon.sfcgal_geom_from_coordinates(coords)
                lib.sfcgal_geometry_collection_add_geometry(multipolygon, polygon)
        return multipolygon

    @cond_icontract(
        lambda self, polygon: polygon.geom_type == "Polygon", "require")
    def add_polygon(self, polygon: Polygon) -> None:
        """Add a polygon to the multipolygon.

        Parameters
        ----------
        polygon: Polygon
            The polygon to add.
        """
        self._add_geometry(polygon)


class Tin(Geometry):
    def __init__(self, coords: Tuple = ()):
        """Initialize the Tin with a tuple of coordinates.

        Parameters
        ----------
        coords : Tuple
            A list of coordinate tuples that define the vertices of the TIN.
            If None, initializes an empty TIN.
        """
        self._geom = Tin.sfcgal_geom_from_coordinates(list(coords))

    def __len__(self):
        """Return the number of patches in the TIN.

        Returns
        -------
        int
            The number of patches that comprise the TIN.
        """
        return lib.sfcgal_triangulated_surface_num_patches(self._geom)

    def __iter__(self):
        """Iterate over the patches in the TIN.

        Yields
        ------
        Geometry
            Each patch in the TIN as a Geometry object.
        """
        for n in range(0, len(self)):
            yield Geometry.from_sfcgal_geometry(
                lib.sfcgal_triangulated_surface_patch_n(self._geom, n),
                owned=False,
            )

    def __get_geometry_n(self, n):
        """Returns the n-th patch within the TIN.

        This method assumes that the index is valid for the TIN.

        Parameters
        ----------
        n : int
            Index of the triangle to recover.

        Returns
        -------
        Geometry
            The patch at the specified index as a Geometry object.
        """
        return Geometry.from_sfcgal_geometry(
            lib.sfcgal_triangulated_surface_patch_n(self._geom, n),
            owned=False,
        )

    def __getitem__(self, key):
        """Get a patch (or several) within the TIN, identified through an index or a
        slice.

        Raises an IndexError if the key is invalid for the TIN.

        Raises a TypeError if the key is neither an integer nor a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the patch(es) to recover.

        Returns
        -------
        Geometry or list of Geometry
            The patch(es) at the specified index or slice.
        """
        length = self.__len__()
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_geometry_n(index)
        elif isinstance(key, slice):
            geoms = [
                self.__get_geometry_n(index) for index in range(*key.indices(length))
            ]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    def __eq__(self, other: object) -> bool:
        """Check if two TINs are equal based on their patches.

        Parameters
        ----------
        other : Tin
            The other TIN to compare.

        Returns
        -------
        bool
            True if both TINs contain the same patches, False otherwise.
        """
        if not isinstance(other, Tin):
            return False
        return self[:] == other[:]

    def to_multipolygon(self, wrapped: bool = False) -> Union[MultiPolygon, ffi.CData]:
        """Convert the TIN to a MultiPolygon.

        Parameters
        ----------
        wrapped : bool, optional
            If True, wrap the result in a Geometry object. Defaults to False.

        Returns
        -------
        MultiPolygon
            A MultiPolygon representation of the TIN.
        """
        multipolygon = lib.sfcgal_multi_polygon_create()
        num_geoms = lib.sfcgal_triangulated_surface_num_patches(self._geom)
        for geom_idx in range(num_geoms):
            triangle_geom = lib.sfcgal_triangulated_surface_patch_n(
                self._geom, geom_idx
            )
            triangle_clone = lib.sfcgal_geometry_clone(triangle_geom)
            triangle_clone_wrap = cast(
                Triangle, Geometry.from_sfcgal_geometry(triangle_clone))
            polygon = triangle_clone_wrap.to_polygon(wrapped=False)
            lib.sfcgal_geometry_collection_add_geometry(multipolygon, polygon)
        return Geometry.from_sfcgal_geometry(multipolygon) if wrapped else multipolygon

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: list) -> ffi.CData:
        """Instantiates a SFCGAL Tin starting from a list of coordinates.

        Parameters
        ----------
        coordinates : list
            Tin coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Tin

        """
        tin = lib.sfcgal_triangulated_surface_create()
        for coords in coordinates:
            triangle = Triangle.sfcgal_geom_from_coordinates(coords)
            lib.sfcgal_triangulated_surface_add_patch(tin, triangle)
        return tin

    @cond_icontract(lambda self, patch: patch.geom_type == "Triangle", "require")
    def add_patch(self, patch: Triangle) -> None:
        """Add a triangle to the Tin.

        Parameters
        ----------
        patch: Triangle
            The patch to add.
        """
        patch_clone = lib.sfcgal_geometry_clone(patch._geom)
        lib.sfcgal_triangulated_surface_add_patch(self._geom, patch_clone)

    def to_coordinates(self) -> list:
        """Generates the coordinates of the TIN

        Uses the __iter__ property of the TIN to iterate over patches.

        Returns
        -------
        list
            List of patches' coordinates.
        """
        return [patch.to_coordinates() for patch in self]


class Triangle(Geometry):
    def __init__(self, coords=None):
        """Initialize the Triangle with the given coordinates.

        Parameters
        ----------
        coords : list of tuples, optional
            A list of coordinate tuples that define the vertices of the triangle.
            If None, initializes an empty triangle.
        """
        self._geom = Triangle.sfcgal_geom_from_coordinates(coords)

    @property
    def coords(self):
        """Get the coordinates of the triangle.

        Returns
        -------
        list of tuples
            The coordinates of the triangle's vertices.
        """
        return self.to_coordinates()

    def __iter__(self):
        """Iterate over the vertices of the triangle.

        Yields
        ------
        Geometry
            Each vertex of the triangle as a Geometry object.
        """
        for n in range(3):
            yield Geometry.from_sfcgal_geometry(
                lib.sfcgal_triangle_vertex(self._geom, n),
                owned=False,
            )

    def __get_geometry_n(self, n):
        """Returns the n-th vertex of the triangle.

        This method assumes that the index is valid for the triangle.

        Parameters
        ----------
        n : int
            Index of the vertex to recover.

        Returns
        -------
        Geometry
            The vertex at the specified index as a Geometry object.
        """
        return Geometry.from_sfcgal_geometry(
            lib.sfcgal_triangle_vertex(self._geom, n),
            owned=False,
        )

    def __getitem__(self, key):
        """Get a vertex (or several) within the triangle, identified through an index
        or a slice.

        Raises an IndexError if the key is invalid for the triangle.

        Raises a TypeError if the key is neither an integer nor a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the vertex(es) to recover.

        Returns
        -------
        Geometry or list of Geometry
            The vertex(es) at the specified index or slice.
        """
        length = 3
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_geometry_n(index)
        elif isinstance(key, slice):
            geoms = [
                self.__get_geometry_n(index) for index in range(*key.indices(length))
            ]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    def __eq__(self, other: object) -> bool:
        """Check if two triangles are equal based on their vertices.

        Parameters
        ----------
        other : Triangle
            The other triangle to compare.

        Returns
        -------
        bool
            True if both triangles contain the same vertices, False otherwise.
        """
        if not isinstance(other, Triangle):
            return False
        return all(vertex == other_vertex for vertex, other_vertex in zip(self, other))

    def to_polygon(self, wrapped: bool = True) -> Union[Polygon, ffi.CData]:
        """Convert the triangle to a Polygon.

        Parameters
        ----------
        wrapped : bool, optional
            If True, wrap the result in a Geometry object. Defaults to True.

        Returns
        -------
        Polygon
            A Polygon representation of the triangle.
        """
        exterior = lib.sfcgal_linestring_create()
        for point_idx in range(4):
            point = lib.sfcgal_triangle_vertex(self._geom, point_idx)
            lib.sfcgal_linestring_add_point(exterior, lib.sfcgal_geometry_clone(point))
        polygon = lib.sfcgal_polygon_create_from_exterior_ring(exterior)
        return Geometry.from_sfcgal_geometry(polygon) if wrapped else polygon

    def to_coordinates(self):
        """Generates the coordinates of the Triangle.

        Uses the __iter__ property of the Triangle to iterate over vertices.

        Returns
        -------
        list
            List of the vertex coordinates
        """
        return [vertex.to_coordinates() for vertex in self]

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: list) -> ffi.CData:
        """Instantiates a SFCGAL Triangle starting from a list of coordinates.

        If the coordinates does not contain three items, an empty Triangle is returned

        Parameters
        ----------
        coordinates : list
            Triangle coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Triangle
        """
        triangle = None
        if coordinates and len(coordinates) == 3:
            triangle = lib.sfcgal_triangle_create_from_points(
                Point.sfcgal_geom_from_coordinates(coordinates[0]),
                Point.sfcgal_geom_from_coordinates(coordinates[1]),
                Point.sfcgal_geom_from_coordinates(coordinates[2]),
            )
        else:
            triangle = lib.sfcgal_triangle_create()

        return triangle


class PolyhedralSurface(Geometry):
    def __init__(self, coords: Tuple = ()):
        """Initialize the PolyhedralSurface with a tuple of coordinates.

        Parameters
        ----------
        coords : Tuple
            A tuple of coordinates that define the patches of the polyhedral
            surface. If empty, initializes an empty polyhedral surface.
        """
        self._geom = PolyhedralSurface.sfcgal_geom_from_coordinates(list(coords))

    def __len__(self):
        """Get the number of patches in the polyhedral surface.

        Returns
        -------
        int
            The number of patches contained within the polyhedral surface.
        """
        return lib.sfcgal_polyhedral_surface_num_patches(self._geom)

    def __iter__(self):
        """Iterate over the patches of the polyhedral surface.

        Yields
        ------
        Geometry
            Each patch of the polyhedral surface as a Geometry object.
        """
        for n in range(0, len(self)):
            yield Geometry.from_sfcgal_geometry(
                lib.sfcgal_polyhedral_surface_patch_n(self._geom, n),
                owned=False,
            )

    def __get_geometry_n(self, n):
        """Returns the n-th polygon within the polyhedral surface.

        This method assumes that the index is valid for the geometry.

        Parameters
        ----------
        n : int
            Index of the polygon to recover.

        Returns
        -------
        Geometry
            The polygon at the specified index as a Geometry object.
        """
        return Geometry.from_sfcgal_geometry(
            lib.sfcgal_polyhedral_surface_patch_n(self._geom, n),
            owned=False,
        )

    def __getitem__(self, key):
        """Get a patch (or several) within the polyhedral surface, identified through
        an index or a slice.

        Raises an IndexError if the key is invalid for the geometry.

        Raises a TypeError if the key is neither an integer nor a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the polygon(s) to recover.

        Returns
        -------
        Geometry or list of Geometry
            The patch(es) at the specified index or slice.
        """
        length = self.__len__()
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_geometry_n(index)
        elif isinstance(key, slice):
            geoms = [
                self.__get_geometry_n(index) for index in range(*key.indices(length))
            ]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    def __eq__(self, other: object) -> bool:
        """Check if two polyhedral surfaces are equal based on their patches.

        Parameters
        ----------
        other : PolyhedralSurface
            The other polyhedral surface to compare.

        Returns
        -------
        bool
            True if both polyhedral surfaces contain the same polygons, False otherwise.
        """
        if not isinstance(other, PolyhedralSurface):
            return False
        return self[:] == other[:]

    @cond_icontract(lambda self: self.is_valid(), "require")
    def to_solid(self) -> Solid:
        """Convert the polyhedralsurface into a solid.

        Returns
        -------
        Solid
            A solid version of the polyhedralsurface.
        """
        geom = lib.sfcgal_geometry_make_solid(self._geom)
        return cast(Solid, PolyhedralSurface.from_sfcgal_geometry(geom))

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: list) -> ffi.CData:
        """Instantiates a SFCGAL PolyhedralSurface starting from a list of coordinates.

        Parameters
        ----------
        coordinates : list
            PolyhedralSurface coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL PolyhedralSurface

        """
        polyhedralsurface = lib.sfcgal_polyhedral_surface_create()
        for coords in coordinates:
            polygon = Polygon.sfcgal_geom_from_coordinates(coords)
            lib.sfcgal_polyhedral_surface_add_patch(polyhedralsurface, polygon)
        return polyhedralsurface

    @cond_icontract(lambda self, patch: patch.geom_type == "Polygon", "require")
    def add_patch(self, patch: Polygon) -> None:
        """Add a patch to the polyhedralsurface.

        Parameters
        ----------
        patch: Polygon
            The patch to add.
        """
        patch_clone = lib.sfcgal_geometry_clone(patch._geom)
        lib.sfcgal_polyhedral_surface_add_patch(self._geom, patch_clone)

    def to_coordinates(self) -> list:
        """Generates the coordinates of the PolyhedralSurface.

        Uses the __iter__ property of the PolyhedralSurface to iterate over patches.

        Returns
        -------
        list
            List of patches' coordinates.
        """
        return [patch.to_coordinates() for patch in self]


class Solid(Geometry):
    def __init__(self, coords: Tuple = ()):
        """Initialize the Solid with the given coordinates.

        Parameters
        ----------
        coords : list of list of tuples, optional
            A tuple where the first element is the exterior shell coordinates, and the
            subsequent elements are the interior shell coordinates.
            If coords is empty, an empty Solid is created.

        """
        self._geom = Solid.sfcgal_geom_from_coordinates(coords)

    def __iter__(self):
        """Iterate over the shells of the solid.

        Yields
        ------
        Geometry
            Each shell of the solid as a Geometry object.
        """
        for n in range(self.n_shells):
            yield self.__get_shell_n(n)

    def __getitem__(self, key):
        """Get a shell (or several) within a solid, identified through an index or a
        slice. The first shell is always the exterior shell, the next ones are the
        interior shells (optional).

        Raises an IndexError if the key is invalid for the geometry.

        Raises a TypeError if the key is neither an integer nor a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the shell(s) to recover.

        Returns
        -------
        PolyhedralSurface or list of PolyhedralSurface
            The shell(s) at the specified index or slice.
        """
        length = self.n_shells
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_shell_n(index)
        elif isinstance(key, slice):
            geoms = [self.__get_shell_n(index) for index in range(*key.indices(length))]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    def __eq__(self, other: object) -> bool:
        """Two Solids are equal if their shells (exterior and interior) are equal.

        Parameters
        ----------
        other : Solid
            The other solid to compare.

        Returns
        -------
        bool
            True if both solids contain the same shells, False otherwise.
        """
        if not isinstance(other, Solid):
            return False
        if self.n_shells != other.n_shells:
            return False
        return all(phs == other_phs for phs, other_phs in zip(self, other))

    def __len__(self):
        """Return the number of shells in the solid.

        Returns
        -------
        int
            The number of shells contained within the solid.
        """
        return lib.sfcgal_solid_num_shells(self._geom)

    @property
    def n_shells(self):
        """Get the number of shells in the solid.

        Returns
        -------
        int
            The number of shells contained within the solid.
        """
        return len(self)

    @property
    def shells(self):
        """Get the shells of the solid.

        Returns
        -------
        list of Geometry
            A list of shells as Geometry objects.
        """
        _shells = []
        for idx in range(self.n_shells):
            _shells.append(
                Geometry.from_sfcgal_geometry(
                    lib.sfcgal_solid_shell_n(self._geom, idx), owned=False
                )
            )
        return _shells

    def __get_shell_n(self, n):
        """Returns the n-th shell within the solid. This method is internal and makes
        the assumption that the index is valid for the geometry. The 0 index refers to
        the exterior shell.

        Parameters
        ----------
        n : int
            Index of the shell to recover.

        Returns
        -------
        PolyhedralSurface
            The shell at the specified index.
        """
        return self.shells[n]

    def to_polyhedralsurface(
            self, wrapped: bool = True) -> Union[PolyhedralSurface, ffi.CData]:
        """Convert the solid to a PolyhedralSurface.

        Parameters
        ----------
        wrapped : bool, optional
            If True, wrap the returned geometry in a Geometry object. Defaults to True.

        Returns
        -------
        PolyhedralSurface
            The corresponding PolyhedralSurface representation of the solid.
        """
        phs_geom = lib.sfcgal_polyhedral_surface_create()

        for shell in self.shells:
            num_geoms = lib.sfcgal_polyhedral_surface_num_patches(shell._geom)
            for geom_idx in range(num_geoms):
                polygon = lib.sfcgal_polyhedral_surface_patch_n(shell._geom, geom_idx)
                lib.sfcgal_polyhedral_surface_add_patch(
                    phs_geom, lib.sfcgal_geometry_clone(polygon)
                )
        return Geometry.from_sfcgal_geometry(phs_geom) if wrapped else phs_geom

    @staticmethod
    def sfcgal_geom_from_coordinates(
            coordinates: Tuple, close: bool = False) -> ffi.CData:
        """Instantiates a SFCGAL Solid starting from a tuple of coordinates.

        Parameters
        ----------
        coordinates : Tuple
            A tuple of coordinate tuples representing the solid's shells.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL Solid.
        """
        solid = lib.sfcgal_solid_create()
        if coordinates:
            polyhedralsurface = PolyhedralSurface.sfcgal_geom_from_coordinates(
                coordinates[0]
            )
            solid = lib.sfcgal_solid_create_from_exterior_shell(polyhedralsurface)
            for coords in coordinates[1:]:
                polyhedralsurface = PolyhedralSurface.sfcgal_geom_from_coordinates(
                    coords
                )
                lib.sfcgal_solid_add_interior_shell(solid, polyhedralsurface)
        return solid

    @cond_icontract(
        lambda self, shell: shell.geom_type == "PolyhedralSurface", "require")
    def set_exterior_shell(self, shell: PolyhedralSurface) -> None:
        """Sets the exterior of the solid.

        Parameters
        ----------
        shell : PolyhedralSurface
            The new exterior shell

        """
        shell_clone = lib.sfcgal_geometry_clone(shell._geom)
        lib.sfcgal_solid_set_exterior_shell(self._geom, shell_clone)

    @cond_icontract(
        lambda self, shell: shell.geom_type == "PolyhedralSurface", "require")
    def add_interior_shell(self, shell: PolyhedralSurface) -> None:
        """Adds an interior shell to the solid.

        Parameters
        ----------
        shell : PolyhedralSurface
            The interior shell to add

        """
        shell_clone = lib.sfcgal_geometry_clone(shell._geom)
        lib.sfcgal_solid_add_interior_shell(self._geom, shell_clone)

    def to_coordinates(self) -> list:
        """Generates the coordinates of the Solid.

        Uses the __iter__ property of the Solid to iterate over shells.

        Returns
        -------
        list
            List of shells' coordinates.
        """
        return [shells.to_coordinates() for shells in self]


class MultiSolid(GeometryCollectionBase):
    def __init__(self, coords: Tuple = ()):
        """Initialize the MultiSolid with the given coordinates.

        Parameters
        ----------
        coords : tuples, optional
            A tuple where each element is the coordinates of a solid
            If coords is empty, an empty MultiSolid is created.

        """
        self._geom = MultiSolid.sfcgal_geom_from_coordinates(coords)

    @staticmethod
    def sfcgal_geom_from_coordinates(coordinates: Tuple) -> ffi.CData:
        """Instantiates a SFCGAL MultiSolid starting from a tuple of coordinates.

        Parameters
        ----------
        coordinates : Tuple
            MultiSolid coordinates.

        Returns
        -------
        _cffi_backend._CDatabase
            A pointer towards a SFCGAL MultiSolid

        """
        multisolid = lib.sfcgal_multi_solid_create()
        if coordinates:
            for coords in coordinates:
                solid = Solid.sfcgal_geom_from_coordinates(coords)
                lib.sfcgal_geometry_collection_add_geometry(multisolid, solid)
        return multisolid

    @cond_icontract(
        lambda self, solid: solid.geom_type == "SOLID", "require")
    def add_solid(self, solid: Solid) -> None:
        """Add a solid to the multisolid.

        Parameters
        ----------
        solid: Solid
            The sold to add.
        """
        self._add_geometry(solid)


class GeometryCollection(GeometryCollectionBase):
    def __init__(self):
        self._geom = lib.sfcgal_geometry_collection_create()

    def add_geometry(self, geometry: Geometry) -> None:
        """Add a geometry to the collection.

        Parameters
        ----------
        geometry: Geometry
            The geometry to add.
        """
        self._add_geometry(geometry)

    def addGeometry(self, geometry: Geometry) -> None:
        """Add a geometry to the collection.
        This function is deprecated. Use add_geometry instead.

        Parameters
        ----------
        geometry: Geometry
            The geometry to add.
        """
        self.add_geometry(geometry)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GeometryCollection):
            return False
        return all(
            isinstance(other_geom, type(geom)) and geom == other_geom
            for geom, other_geom in zip(self, other)
        )

    def from_coordinates(self):
        """Instantiates a Point starting from a list of coordinates.

        Raises
        ------
        NotImplementedError
            This method is not supported (yet?). That's sounds too hard to infer the
            geometry type from a random coordinates structure.

        """
        raise NotImplementedError(
            "The 'from_coordinates' method is not implemented for GeometryCollection."
        )

    def to_dict(self) -> dict:
        """Generates a geojson-like dict representation of the GeometryCollection.

        This case differs from the general case, as the dictionary contains 'type' and
        'geometries' keys instead of 'type' and 'coordinates'. The 'geometries' key
        refers to the list of the dictionary representations of the geometries that
        belong the collection.

        Returns
        -------
        dict
            Geojson-like representation of the geometry collection

        """
        return {"type": self.geom_type, "geometries": [geom.to_dict() for geom in self]}

    @classmethod
    def from_dict(cls, geojson_data: dict) -> GeometryCollection:
        """Instantiates a GeometryCollection starting from a geojson-like dictionnary.

        The dictionary must contain 'type' and 'geometries' keys; the 'type' value
        should be 'GeometryCollection'. The 'geometries' values should be a list of
        valid geojson-like dictionaries that represents the geometries within the
        collection.

        Parameters
        ----------
        geojson_data : dict
            Description of the collection, in a geojson-like format

        Returns
        -------
        GeometryCollection
            An instance of GeometryCollection
        """
        if geojson_data.get("type") is None:
            raise KeyError("There is no 'type' key in the provided data.")
        if geojson_data["type"] != "GeometryCollection":
            raise ValueError(
                f"The provided 'type' ({geojson_data['type']}) "
                "should be 'GeometryCollection'."
            )
        if geojson_data.get("geometries") is None:
            raise KeyError("There is no 'geometries' key in the provided data.")
        collection = lib.sfcgal_geometry_collection_create()
        for geojson_geometry in geojson_data["geometries"]:
            geom_type = geojson_geometry["type"]
            geometry_cls = geom_type_to_cls[geom_types[geom_type]]
            geometry = geometry_cls.sfcgal_geom_from_coordinates(  # type: ignore
                geojson_geometry["coordinates"]
            )
            lib.sfcgal_geometry_collection_add_geometry(collection, geometry)
        return cast(
            GeometryCollection, GeometryCollection.from_sfcgal_geometry(collection))


class GeometrySequence:
    def __init__(self, parent):
        """Initialize the GeometrySequence with a parent GeometryCollection.

        Parameters
        ----------
        parent : GeometryCollectionBase
            The parent geometry collection that this sequence belongs to.
        """
        # keep reference to parent to avoid garbage collection
        self._parent = parent

    def __iter__(self):
        """Iterate over the geometries in the sequence.

        Yields
        ------
        Geometry
            Each geometry in the sequence as a Geometry object.
        """
        for n in range(0, len(self)):
            yield Geometry.from_sfcgal_geometry(
                lib.sfcgal_geometry_collection_geometry_n(self._parent._geom, n),
                owned=False,
            )

    def __len__(self):
        """Get the number of geometries in the sequence.

        Returns
        -------
        int
            The number of geometries in the collection.
        """
        return lib.sfcgal_geometry_num_geometries(self._parent._geom)

    def __get_geometry_n(self, n):
        """Retrieve the n-th geometry in the sequence.

        Parameters
        ----------
        n : int
            The index of the geometry to retrieve.

        Returns
        -------
        Geometry
            The geometry at the specified index.
        """
        return Geometry.from_sfcgal_geometry(
            lib.sfcgal_geometry_collection_geometry_n(self._parent._geom, n),
            owned=False,
        )

    def __getitem__(self, key):
        """Get a geometry (or several) within the sequence, identified through an index
        or a slice.

        Raises an IndexError if the key is invalid for the geometry.

        Raises a TypeError if the key is neither an integer nor a valid slice.

        Parameters
        ----------
        key : int or slice
            Index (or slice) of the geometry or geometries to recover.

        Returns
        -------
        Geometry or list of Geometry
            The geometry or list of geometries at the specified index or slice.
        """
        length = self.__len__()
        if isinstance(key, int):
            if key + length < 0 or key >= length:
                raise IndexError("geometry sequence index out of range")
            elif key < 0:
                index = length + key
            else:
                index = key
            return self.__get_geometry_n(index)
        elif isinstance(key, slice):
            geoms = [
                self.__get_geometry_n(index) for index in range(*key.indices(length))
            ]
            return geoms
        else:
            raise TypeError(
                "geometry sequence indices must be\
                            integers or slices, not {}".format(
                    key.__class__.__name__
                )
            )

    def __eq__(self, other: object) -> bool:
        """Check equality between this geometry sequence and another.

        Parameters
        ----------
        other : GeometrySequence
            The other geometry sequence to compare.

        Returns
        -------
        bool
            True if both geometry sequences are equal, False otherwise.
        """
        if not isinstance(other, GeometrySequence):
            return False
        return self[:] == other[:]


# Mapping of geometry types to their respective classes
geom_type_to_cls = {
    lib.SFCGAL_TYPE_POINT: Point,
    lib.SFCGAL_TYPE_LINESTRING: LineString,
    lib.SFCGAL_TYPE_POLYGON: Polygon,
    lib.SFCGAL_TYPE_MULTIPOINT: MultiPoint,
    lib.SFCGAL_TYPE_MULTILINESTRING: MultiLineString,
    lib.SFCGAL_TYPE_MULTIPOLYGON: MultiPolygon,
    lib.SFCGAL_TYPE_GEOMETRYCOLLECTION: GeometryCollection,
    lib.SFCGAL_TYPE_TRIANGULATEDSURFACE: Tin,
    lib.SFCGAL_TYPE_TRIANGLE: Triangle,
    lib.SFCGAL_TYPE_POLYHEDRALSURFACE: PolyhedralSurface,
    lib.SFCGAL_TYPE_SOLID: Solid,
    lib.SFCGAL_TYPE_MULTISOLID: MultiSolid,
}

# Dictionary mapping geometry names to their corresponding type IDs
geom_types = {
    "Point": lib.SFCGAL_TYPE_POINT,
    "LineString": lib.SFCGAL_TYPE_LINESTRING,
    "Polygon": lib.SFCGAL_TYPE_POLYGON,
    "MultiPoint": lib.SFCGAL_TYPE_MULTIPOINT,
    "MultiLineString": lib.SFCGAL_TYPE_MULTILINESTRING,
    "MultiPolygon": lib.SFCGAL_TYPE_MULTIPOLYGON,
    "GeometryCollection": lib.SFCGAL_TYPE_GEOMETRYCOLLECTION,
    "TIN": lib.SFCGAL_TYPE_TRIANGULATEDSURFACE,
    "Triangle": lib.SFCGAL_TYPE_TRIANGLE,
    "PolyhedralSurface": lib.SFCGAL_TYPE_POLYHEDRALSURFACE,
    "SOLID": lib.SFCGAL_TYPE_SOLID,
    "MultiSolid": lib.SFCGAL_TYPE_MULTISOLID,
}

# Reverse mapping from type IDs to geometry names
geom_types_r = dict((v, k) for k, v in geom_types.items())


def is_segment_in_coordsequence(coords: list, point_a: Point, point_b: Point) -> bool:
    """Check if the segment defined by two points is in the coordinate sequence.

    Parameters
    ----------
    coords : list
        A list of coordinate tuples.
    point_a : Point
        The first point defining the segment.
    point_b : Point
        The second point defining the segment.

    Returns
    -------
    bool
        True if the segment is found in the coordinate sequence, False otherwise.
    """
    for c1, c2 in zip(coords[1:], coords[:-1]):
        # (point_a, point_b) is in the coord sequence
        if c1 == (point_a.x, point_a.y) and c2 == (point_b.x, point_b.y):
            return True
        # (point_a, point_b) is in reverted coord sequence
        if c2 == (point_a.x, point_a.y) and c1 == (point_b.x, point_b.y):
            return True
    return False
