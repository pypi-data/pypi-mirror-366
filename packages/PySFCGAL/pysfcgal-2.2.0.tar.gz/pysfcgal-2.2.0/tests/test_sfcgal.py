import pathlib
from filecmp import cmp

import geom_data
import pytest

import pysfcgal.sfcgal as sfcgal
from pysfcgal.sfcgal import (GeometryCollection, LineString, MultiLineString,
                             MultiPoint, Point, Polygon, PolyhedralSurface,
                             Solid, Triangle)


def test_version():
    print(sfcgal.sfcgal_version())


geometry_names, geometry_values = zip(*geom_data.data.items())


@pytest.mark.parametrize("geometry", geometry_values, ids=geometry_names)
def test_integrity(geometry):
    """Test conversion from and to GeoJSON-like data"""
    geom_type = geometry["type"]
    geometry_cls = sfcgal.geom_type_to_cls[sfcgal.geom_types[geom_type]]
    geom = geometry_cls.from_dict(geometry)
    data = geom.to_dict()
    assert geometry == data


@pytest.mark.parametrize("geometry", geometry_values, ids=geometry_names)
def test_wkt_write(geometry):
    geom_type = geometry["type"]
    geometry_cls = sfcgal.geom_type_to_cls[sfcgal.geom_types[geom_type]]
    geom = geometry_cls.from_dict(geometry)
    wkt = geom.to_wkt()
    assert wkt
    data = geometry_cls.from_wkt(wkt).to_dict()
    assert geometry == data


def test_wkt_read():
    good_wkt = "POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))"
    geom = Polygon.from_wkt(good_wkt)
    assert geom.__class__ == Polygon

    good_wkt = "POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0),)"
    geom = Polygon.from_wkt(good_wkt)
    assert geom is None


def test_wkt_str():
    good_wkt = "POLYGON ((0 0, 0 1, 1 1, 1 0, 0 0))"
    geom = Polygon.from_wkt(good_wkt)
    assert str(geom) == "POLYGON ((0.00000000 0.00000000,0.00000000 1.00000000,1.00000000 1.00000000,1.00000000 0.00000000,0.00000000 0.00000000))"  # noqa: E501


def test_wkb_write():
    point = Point(0, 1)
    wkb = point.to_wkb(True)
    expected_wkb = "01010000000000000000000000000000000000f03f"
    assert wkb == expected_wkb

    mp = sfcgal.Polygon([(0, 0), (0, 5), (5, 5), (5, 0), (0, 0)])
    wkb = mp.to_wkb(True)
    expected_wkb = '010300000001000000050000000000000000000000000000000000000000000000000000000000000000001440000000000000144000000000000014400000000000001440000000000000000000000000000000000000000000000000'  # noqa: E501
    assert wkb == expected_wkb

    expected_wkb = '\x01\x03\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x14@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa: E501
    wkb = mp.to_wkb().decode("utf-8")
    assert wkb == expected_wkb


def test_wkb_read():
    wkb_expected = "01020000000300000000000000000000000000000000000000000000000000f03f000000000000f03f00000000000000400000000000000040"  # noqa: E501
    wkt_expected = "LINESTRING (0.0 0.0,1.0 1.0,2.0 2.0)"

    ls = LineString.from_wkt(wkt_expected)
    ls.to_wkb(True) == wkb_expected

    # Special case for EWKB
    # TODO: get srid from PreparedGeometry
    ewkb_ls = "01020000206a0f00000300000000000000000000000000000000000000000000000000f03f000000000000f03f00000000000000400000000000000040"  # noqa: E501
    ls = LineString.from_wkb(ewkb_ls)
    ls.to_wkb(True) == wkb_expected


def test_is_valid():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert poly.is_valid()
    poly = Polygon([(0, 0), (1, 1), (1, 0), (0, 1)])
    assert not poly.is_valid()

    line = LineString([])
    assert line.is_valid()
    line = LineString([(0, 0)])
    assert not line.is_valid()
    line = LineString([(0, 0), (1, 1), (1, 0), (0, 1)])
    assert line.is_valid()

    poly = Polygon([(0, 0), (1, 1), (1, 0), (0, 1)])
    ring, _ = poly.is_valid_detail()
    assert ring == "ring 0 self intersects"


def test_approximate_medial_axis():
    poly = Polygon(
        [
            (190, 190),
            (10, 190),
            (10, 10),
            (190, 10),
            (190, 20),
            (160, 30),
            (60, 30),
            (60, 130),
            (190, 140),
            (190, 190),
        ]
    )
    res_wkt = poly.approximate_medial_axis().to_wkt(2)

    geom1 = MultiLineString.from_wkt(res_wkt)
    geom2 = MultiLineString.from_wkt(
        """MULTILINESTRING ((184.19 15.81,158.38 20.00),
        (50.00 20.00,158.38 20.00),(50.00 20.00,35.00 35.00),(35.00 35.00,35.00
        153.15),(35.00 153.15,40.70 159.30),(164.04 164.04,40.70 159.30))"""
    )
    assert geom1.covers(geom2)


def test_straight_skeleton():
    # Ensure that it works if the input is empty
    empty_polygon = Polygon()
    assert empty_polygon.is_empty
    empty_res = empty_polygon.straight_skeleton()
    assert empty_res.geom_type == "MultiLineString"
    assert empty_res.is_empty

    poly = Polygon(
        [
            (190, 190),
            (10, 190),
            (10, 10),
            (190, 10),
            (190, 20),
            (160, 30),
            (60, 30),
            (60, 130),
            (190, 140),
            (190, 190),
        ]
    )
    res_wkt = poly.straight_skeleton().to_wkt(2)

    geom1 = MultiLineString.from_wkt(res_wkt)
    geom2 = MultiLineString.from_wkt(
        """MULTILINESTRING ((190.00 190.00,164.04 164.04),(10.00
    190.00,40.70 159.30),(10.00 10.00,35.00 35.00),(190.00 10.00,184.19
    15.81),(190.00 20.00,184.19 15.81),(160.00 30.00,158.38 20.00),(60.00
    30.00,50.00 20.00),(60.00 130.00,35.00 153.15),(190.00 140.00,164.04
    164.04),(184.19 15.81,158.38 20.00),(50.00 20.00,158.38 20.00),(50.00
    20.00,35.00 35.00),(35.00 35.00,35.00 153.15),(35.00 153.15,40.70
    159.30),(164.04 164.04,40.70 159.30))"""
    )
    assert geom1.covers(geom2)


def test_extrude_straight_skeleton_polygon():
    """Inspired from testExtrudeStraightSkeleton SFCGAL unit test
    """
    # Ensure that it works if the input is empty
    empty_polygon = Polygon()
    assert empty_polygon.is_empty
    empty_res = empty_polygon.extrude_straight_skeleton(2.0)
    assert empty_res.geom_type == "PolyhedralSurface"
    assert empty_res.is_empty

    geom = Polygon.from_wkt("POLYGON (( 0 0, 5 0, 5 5, 4 5, 4 4, 0 4, 0 0 ))")
    expected_wkt = (
          "POLYHEDRALSURFACE Z (((4.00 5.00 0.00,5.00 5.00 0.00,4.00 4.00 0.00,4.00 "
          "5.00 0.00)),((0.00 4.00 0.00,4.00 4.00 0.00,0.00 0.00 0.00,0.00 4.00 "
          "0.00)),((4.00 4.00 0.00,5.00 0.00 0.00,0.00 0.00 0.00,4.00 4.00 "
          "0.00)),((5.00 5.00 0.00,5.00 0.00 0.00,4.00 4.00 0.00,5.00 5.00 "
          "0.00)),((0.00 4.00 0.00,0.00 0.00 0.00,2.00 2.00 2.00,0.00 4.00 "
          "0.00)),((0.00 0.00 0.00,5.00 0.00 0.00,3.00 2.00 2.00,0.00 0.00 "
          "0.00)),((2.00 2.00 2.00,0.00 0.00 0.00,3.00 2.00 2.00,2.00 2.00 "
          "2.00)),((4.50 3.50 0.50,5.00 5.00 0.00,4.50 4.50 0.50,4.50 3.50 "
          "0.50)),((3.00 2.00 2.00,5.00 0.00 0.00,4.50 3.50 0.50,3.00 2.00 "
          "2.00)),((4.50 3.50 0.50,5.00 0.00 0.00,5.00 5.00 0.00,4.50 3.50 "
          "0.50)),((5.00 5.00 0.00,4.00 5.00 0.00,4.50 4.50 0.50,5.00 5.00 "
          "0.00)),((4.50 4.50 0.50,4.00 4.00 0.00,4.50 3.50 0.50,4.50 4.50 "
          "0.50)),((4.50 4.50 0.50,4.00 5.00 0.00,4.00 4.00 0.00,4.50 4.50 "
          "0.50)),((4.00 4.00 0.00,0.00 4.00 0.00,2.00 2.00 2.00,4.00 4.00 "
          "0.00)),((4.50 3.50 0.50,4.00 4.00 0.00,3.00 2.00 2.00,4.50 3.50 "
          "0.50)),((3.00 2.00 2.00,4.00 4.00 0.00,2.00 2.00 2.00,3.00 2.00 "
          "2.00)))"
    )
    result = geom.extrude_straight_skeleton(2.0)
    assert expected_wkt == result.to_wkt(2)


def test_extrude_straight_skeleton_polygon_with_hole():
    """Inspired from testExtrudeStraightSkeletonPolygonWithHole SFCGAL unit test
    """
    geom = Polygon.from_wkt(
        "POLYGON (( 0 0, 5 0, 5 5, 4 5, 4 4, 0 4, 0 0 ), (1 1, 1 2, 2 2, 2 1, 1 1))"
    )
    expected_wkt = (
        "POLYHEDRALSURFACE Z (((4.00 5.00 0.00,5.00 5.00 0.00,4.00 4.00 0.00,4.00 "
        "5.00 0.00)),((2.00 1.00 0.00,5.00 0.00 0.00,0.00 0.00 0.00,2.00 1.00 "
        "0.00)),((5.00 5.00 0.00,5.00 0.00 0.00,4.00 4.00 0.00,5.00 5.00 "
        "0.00)),((2.00 1.00 0.00,0.00 0.00 0.00,1.00 1.00 0.00,2.00 1.00 "
        "0.00)),((1.00 2.00 0.00,1.00 1.00 0.00,0.00 0.00 0.00,1.00 2.00 "
        "0.00)),((0.00 4.00 0.00,2.00 2.00 0.00,1.00 2.00 0.00,0.00 4.00 "
        "0.00)),((0.00 4.00 0.00,1.00 2.00 0.00,0.00 0.00 0.00,0.00 4.00 "
        "0.00)),((4.00 4.00 0.00,5.00 0.00 0.00,2.00 2.00 0.00,4.00 4.00 "
        "0.00)),((4.00 4.00 0.00,2.00 2.00 0.00,0.00 4.00 0.00,4.00 4.00 "
        "0.00)),((2.00 2.00 0.00,5.00 0.00 0.00,2.00 1.00 0.00,2.00 2.00 "
        "0.00)),((0.50 2.50 0.50,0.00 0.00 0.00,0.50 0.50 0.50,0.50 2.50 "
        "0.50)),((1.00 3.00 1.00,0.00 4.00 0.00,0.50 2.50 0.50,1.00 3.00 "
        "1.00)),((0.50 2.50 0.50,0.00 4.00 0.00,0.00 0.00 0.00,0.50 2.50 "
        "0.50)),((2.50 0.50 0.50,5.00 0.00 0.00,3.50 1.50 1.50,2.50 0.50 "
        "0.50)),((0.00 0.00 0.00,5.00 0.00 0.00,2.50 0.50 0.50,0.00 0.00 "
        "0.00)),((0.50 0.50 0.50,0.00 0.00 0.00,2.50 0.50 0.50,0.50 0.50 "
        "0.50)),((4.50 3.50 0.50,5.00 5.00 0.00,4.50 4.50 0.50,4.50 3.50 "
        "0.50)),((3.50 2.50 1.50,3.50 1.50 1.50,4.50 3.50 0.50,3.50 2.50 "
        "1.50)),((4.50 3.50 0.50,5.00 0.00 0.00,5.00 5.00 0.00,4.50 3.50 "
        "0.50)),((3.50 1.50 1.50,5.00 0.00 0.00,4.50 3.50 0.50,3.50 1.50 "
        "1.50)),((5.00 5.00 0.00,4.00 5.00 0.00,4.50 4.50 0.50,5.00 5.00 "
        "0.00)),((4.50 4.50 0.50,4.00 4.00 0.00,4.50 3.50 0.50,4.50 4.50 "
        "0.50)),((4.50 4.50 0.50,4.00 5.00 0.00,4.00 4.00 0.00,4.50 4.50 "
        "0.50)),((3.00 3.00 1.00,0.00 4.00 0.00,1.00 3.00 1.00,3.00 3.00 "
        "1.00)),((3.50 2.50 1.50,4.50 3.50 0.50,3.00 3.00 1.00,3.50 2.50 "
        "1.50)),((3.00 3.00 1.00,4.00 4.00 0.00,0.00 4.00 0.00,3.00 3.00 "
        "1.00)),((4.50 3.50 0.50,4.00 4.00 0.00,3.00 3.00 1.00,4.50 3.50 "
        "0.50)),((2.00 1.00 0.00,1.00 1.00 0.00,0.50 0.50 0.50,2.00 1.00 "
        "0.00)),((2.50 0.50 0.50,2.00 1.00 0.00,0.50 0.50 0.50,2.50 0.50 "
        "0.50)),((1.00 1.00 0.00,1.00 2.00 0.00,0.50 2.50 0.50,1.00 1.00 "
        "0.00)),((0.50 0.50 0.50,1.00 1.00 0.00,0.50 2.50 0.50,0.50 0.50 "
        "0.50)),((1.00 3.00 1.00,2.00 2.00 0.00,3.00 3.00 1.00,1.00 3.00 "
        "1.00)),((0.50 2.50 0.50,1.00 2.00 0.00,1.00 3.00 1.00,0.50 2.50 "
        "0.50)),((1.00 3.00 1.00,1.00 2.00 0.00,2.00 2.00 0.00,1.00 3.00 "
        "1.00)),((2.00 2.00 0.00,2.00 1.00 0.00,2.50 0.50 0.50,2.00 2.00 "
        "0.00)),((3.50 2.50 1.50,3.00 3.00 1.00,3.50 1.50 1.50,3.50 2.50 "
        "1.50)),((3.50 1.50 1.50,2.00 2.00 0.00,2.50 0.50 0.50,3.50 1.50 "
        "1.50)),((3.00 3.00 1.00,2.00 2.00 0.00,3.50 1.50 1.50,3.00 3.00 "
        "1.00)))"
    )
    result = geom.extrude_straight_skeleton(2.0)
    assert expected_wkt == result.to_wkt(2)


def test_extrude_straight_skeleton_building():
    """Inspired from testExtrudeStraightSkeletonGenerateBuilding SFCGAL unit test
    """
    # Ensure that it works if the input is empty
    empty_polygon = Polygon()
    assert empty_polygon.is_empty
    empty_res = empty_polygon.extrude_polygon_straight_skeleton(9.0, 2.0)
    assert empty_res.geom_type == "PolyhedralSurface"
    assert empty_res.is_empty

    geom = Polygon.from_wkt(
        "POLYGON (( 0 0, 5 0, 5 5, 4 5, 4 4, 0 4, 0 0 ), (1 1, 1 2, 2 2, 2 1, 1 1))"
    )
    expected_wkt = (
        "POLYHEDRALSURFACE Z "
        "(((0.0 0.0 0.0,0.0 4.0 0.0,4.0 4.0 0.0,4.0 5.0 0.0,5.0 5.0 0.0,5.0 0.0 0.0,0.0 0.0 0.0),"  # noqa: E501
        "(1.0 1.0 0.0,2.0 1.0 0.0,2.0 2.0 0.0,1.0 2.0 0.0,1.0 1.0 0.0)),"
        "((0.0 0.0 0.0,0.0 0.0 9.0,0.0 4.0 9.0,0.0 4.0 0.0,0.0 0.0 0.0)),"
        "((0.0 4.0 0.0,0.0 4.0 9.0,4.0 4.0 9.0,4.0 4.0 0.0,0.0 4.0 0.0)),"
        "((4.0 4.0 0.0,4.0 4.0 9.0,4.0 5.0 9.0,4.0 5.0 0.0,4.0 4.0 0.0)),"
        "((4.0 5.0 0.0,4.0 5.0 9.0,5.0 5.0 9.0,5.0 5.0 0.0,4.0 5.0 0.0)),"
        "((5.0 5.0 0.0,5.0 5.0 9.0,5.0 0.0 9.0,5.0 0.0 0.0,5.0 5.0 0.0)),"
        "((5.0 0.0 0.0,5.0 0.0 9.0,0.0 0.0 9.0,0.0 0.0 0.0,5.0 0.0 0.0)),"
        "((1.0 1.0 0.0,1.0 1.0 9.0,2.0 1.0 9.0,2.0 1.0 0.0,1.0 1.0 0.0)),"
        "((2.0 1.0 0.0,2.0 1.0 9.0,2.0 2.0 9.0,2.0 2.0 0.0,2.0 1.0 0.0)),"
        "((2.0 2.0 0.0,2.0 2.0 9.0,1.0 2.0 9.0,1.0 2.0 0.0,2.0 2.0 0.0)),"
        "((1.0 2.0 0.0,1.0 2.0 9.0,1.0 1.0 9.0,1.0 1.0 0.0,1.0 2.0 0.0)),"
        "((0.5 2.5 9.5,0.0 0.0 9.0,0.5 0.5 9.5,0.5 2.5 9.5)),"
        "((1.0 3.0 10.0,0.0 4.0 9.0,0.5 2.5 9.5,1.0 3.0 10.0)),"
        "((0.5 2.5 9.5,0.0 4.0 9.0,0.0 0.0 9.0,0.5 2.5 9.5)),"
        "((2.5 0.5 9.5,5.0 0.0 9.0,3.5 1.5 10.5,2.5 0.5 9.5)),"
        "((0.0 0.0 9.0,5.0 0.0 9.0,2.5 0.5 9.5,0.0 0.0 9.0)),"
        "((0.5 0.5 9.5,0.0 0.0 9.0,2.5 0.5 9.5,0.5 0.5 9.5)),"
        "((4.5 3.5 9.5,5.0 5.0 9.0,4.5 4.5 9.5,4.5 3.5 9.5)),"
        "((3.5 2.5 10.5,3.5 1.5 10.5,4.5 3.5 9.5,3.5 2.5 10.5)),"
        "((4.5 3.5 9.5,5.0 0.0 9.0,5.0 5.0 9.0,4.5 3.5 9.5)),"
        "((3.5 1.5 10.5,5.0 0.0 9.0,4.5 3.5 9.5,3.5 1.5 10.5)),"
        "((5.0 5.0 9.0,4.0 5.0 9.0,4.5 4.5 9.5,5.0 5.0 9.0)),"
        "((4.5 4.5 9.5,4.0 4.0 9.0,4.5 3.5 9.5,4.5 4.5 9.5)),"
        "((4.5 4.5 9.5,4.0 5.0 9.0,4.0 4.0 9.0,4.5 4.5 9.5)),"
        "((3.0 3.0 10.0,0.0 4.0 9.0,1.0 3.0 10.0,3.0 3.0 10.0)),"
        "((3.5 2.5 10.5,4.5 3.5 9.5,3.0 3.0 10.0,3.5 2.5 10.5)),"
        "((3.0 3.0 10.0,4.0 4.0 9.0,0.0 4.0 9.0,3.0 3.0 10.0)),"
        "((4.5 3.5 9.5,4.0 4.0 9.0,3.0 3.0 10.0,4.5 3.5 9.5)),"
        "((2.0 1.0 9.0,1.0 1.0 9.0,0.5 0.5 9.5,2.0 1.0 9.0)),"
        "((2.5 0.5 9.5,2.0 1.0 9.0,0.5 0.5 9.5,2.5 0.5 9.5)),"
        "((1.0 1.0 9.0,1.0 2.0 9.0,0.5 2.5 9.5,1.0 1.0 9.0)),"
        "((0.5 0.5 9.5,1.0 1.0 9.0,0.5 2.5 9.5,0.5 0.5 9.5)),"
        "((1.0 3.0 10.0,2.0 2.0 9.0,3.0 3.0 10.0,1.0 3.0 10.0)),"
        "((0.5 2.5 9.5,1.0 2.0 9.0,1.0 3.0 10.0,0.5 2.5 9.5)),"
        "((1.0 3.0 10.0,1.0 2.0 9.0,2.0 2.0 9.0,1.0 3.0 10.0)),"
        "((2.0 2.0 9.0,2.0 1.0 9.0,2.5 0.5 9.5,2.0 2.0 9.0)),"
        "((3.5 2.5 10.5,3.0 3.0 10.0,3.5 1.5 10.5,3.5 2.5 10.5)),"
        "((3.5 1.5 10.5,2.0 2.0 9.0,2.5 0.5 9.5,3.5 1.5 10.5)),"
        "((3.0 3.0 10.0,2.0 2.0 9.0,3.5 1.5 10.5,3.0 3.0 10.0)))"
    )

    result = geom.extrude_polygon_straight_skeleton(9.0, 2.0)
    assert result.is_valid()
    assert expected_wkt == result.to_wkt(1)


def test_minkowski_sum():
    poly = Polygon(
        [
            (190, 190),
            (10, 190),
            (10, 10),
            (190, 10),
            (190, 20),
            (160, 30),
            (60, 30),
            (60, 130),
            (190, 140),
            (190, 190),
        ]
    )
    poly2 = Polygon([(185, 185), (185, 190), (190, 190), (190, 185), (185, 185)])
    res_wkt = poly.straight_skeleton().minkowski_sum(poly2).to_wkt(2)

    geom1 = Polygon.from_wkt(res_wkt)
    geom2 = Polygon.from_wkt(
        """MULTIPOLYGON (((375.00 210.00,370.11 206.47,349.17
    209.87,350.00 215.00,350.00 220.00,345.00 220.00,343.38 210.00,245.00
    210.00,250.00 215.00,250.00 220.00,245.00 220.00,237.50 212.50,225.00
    225.00,225.00 333.52,245.00 315.00,250.00 315.00,250.00 320.00,227.49
    340.84,230.70 344.30,349.24 348.86,375.00 325.00,380.00 325.00,380.00
    330.00,356.64 351.64,380.00 375.00,380.00 380.00,375.00 380.00,349.04
    354.04,230.51 349.49,200.00 380.00,195.00 380.00,195.00 375.00,223.29
    346.71,220.00 343.15,220.00 225.00,195.00 200.00,195.00 195.00,200.00
    195.00,222.50 217.50,235.00 205.00,240.00 205.00,343.38 205.00,369.19
    200.81,375.00 195.00,380.00 195.00,380.00 200.00,377.09 202.91,380.00
    205.00,380.00 210.00,375.00 210.00)))"""
    )
    assert geom1.covers(geom2)


def test_union():
    poly = Polygon([(0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)])
    poly2 = Polygon([(-1, -1, 10), (-1, 1, 10), (1, 1, 10), (1, -1, 10), (-1, -1, 10)])

    res_wkt = poly.union(poly2).to_wkt(2)

    geom1 = Polygon.from_wkt(res_wkt)
    geom2 = Polygon.from_wkt(
        """POLYGON ((0.00 1.00,-1.00 1.00,-1.00 -1.00,1.00 -1.00,1.00 0.00,1.00
        1.00,0.00 1.00))"""
    )

    assert geom1.covers(geom2)


def test_union_3d():
    poly = Polygon([(0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)])
    poly2 = Polygon([(-1, -1, 10), (-1, 1, 10), (1, 1, 10), (1, -1, 10), (-1, -1, 10)])

    res_wkt = poly.union(poly2).to_wkt(2)

    geom1 = Polygon.from_wkt(res_wkt)
    geom2 = GeometryCollection.from_wkt(
        """GEOMETRYCOLLECTION (TIN (((-0.00 0.00 1.00,-0.00 1.00 1.00,1.00 1.00
        1.00,-0.00 0.00 1.00)),((1.00 -0.00 1.00,-0.00 0.00 1.00,1.00 1.00
        1.00,1.00 -0.00 1.00))),TIN (((-1.00 -1.00 10.00,-1.00 1.00 10.00,1.00
        1.00 10.00,-1.00 -1.00 10.00)),((1.00 -1.00 10.00,-1.00 -1.00 10.00,
        1.00 1.00 10.00,1.00 -1.00 10.00))))"""
    )

    assert geom1.covers(geom2)


def test_instersects():
    line = LineString([(0, 0), (4, 4)])
    line2 = LineString([(0, 4), (4, 0)])

    assert line.intersects(line2)


def test_intersection_3d():
    line = LineString([(0, 0), (4, 4)])
    line2 = LineString([(0, 4), (4, 0)])

    res_wkt = line.intersection_3d(line2).to_wkt(2)

    geom1 = Point.from_wkt(res_wkt)
    geom2 = Point.from_wkt("POINT (2 2)")

    assert geom1.covers(geom2)

    line = LineString([(0, 0, 1), (4, 4, 3)])
    line2 = LineString([(0, 4, 5), (4, 0, 2)])

    assert line.intersection_3d(line2).is_empty == 1

    line = LineString([(0, 0, 2), (4, 4, 4)])
    line2 = LineString([(0, 4, 4), (4, 0, 2)])

    res_wkt = line.intersection_3d(line2).to_wkt(0)

    geom1 = Point.from_wkt(res_wkt)
    geom2 = Point.from_wkt("POINT (2 2 3)")

    assert geom1.covers(geom2)

    p1e = Polygon.from_wkt("POLYGON ( (0 0, 0 1, 1 1, 1 0, 0 0) )").extrude(0, 0, 30)
    p2e = Polygon.from_wkt(
        "POLYGON ((0.5 0.5, 0.5 1.5, 1.5 1.5, 1.5 0.5, 0.5 0.5))"
    ).extrude(0, 0, 30)

    res_intersection = p1e.intersection_3d(p2e)

    assert res_intersection.geom_type == "SOLID"

    expected_intersection = Polygon.from_wkt(
        "POLYGON ((0.5 0.5, 0.5 1, 1 1, 1 0.5, 0.5 0.5))").extrude(0, 0, 30)
    assert res_intersection.covers_3d(expected_intersection)

    res_intersection_polyhedral = res_intersection.to_polyhedralsurface(True)
    assert res_intersection_polyhedral.geom_type == "PolyhedralSurface"


def test_convexhull():
    mp = MultiPoint([(0, 0, 5), (5, 0, 3), (2, 2, 4), (5, 5, 6), (0, 5, 2), (0, 0, 8)])

    # convexhull
    geom = mp.convexhull()
    res_wkt = "POLYGON ((0.0 0.0,5.0 0.0,5.0 5.0,0.0 5.0,0.0 0.0))"
    geom_res = Polygon.from_wkt(res_wkt)
    assert geom.covers(geom_res)

    # convexhull_3d
    geom = mp.convexhull_3d()
    geom_res = PolyhedralSurface.from_wkt(
        """
        POLYHEDRALSURFACE (((5.0 0.0 3.0,0.0 0.0 8.0,0.0 0.0 5.0,5.0 0.0 3.0)),
        ((0.0 0.0 8.0,0.0 5.0 2.0,0.0 0.0 5.0,0.0 0.0 8.0)),
        ((0.0 0.0 8.0,5.0 0.0 3.0,5.0 5.0 6.0,0.0 0.0 8.0)),
        ((5.0 5.0 6.0,0.0 5.0 2.0,0.0 0.0 8.0,5.0 5.0 6.0)),
        ((5.0 0.0 3.0,0.0 5.0 2.0,5.0 5.0 6.0,5.0 0.0 3.0)),
        ((0.0 0.0 5.0,0.0 5.0 2.0,5.0 0.0 3.0,0.0 0.0 5.0)))"""
    )
    assert geom.to_wkt(1) == geom_res.to_wkt(1)


def test_alphaShapes():
    wkt = """MultiPoint ((6.3 8.4),(7.6 8.8),(6.8 7.3),(5.3 1.8),(9.1 5),(8.1 7),
    (8.8 2.9),(2.4 8.2),(3.2 5.1),(3.7 2.3),(2.7 5.4),(8.4 1.9),(7.5 8.7),(4.4 4.2),
    (7.7 6.7),(9 3),(3.6 6.1),(3.2 6.5),(8.1 4.7),(8.8 5.8),(6.8 7.3),(4.9 9.5),(8.1 6),
    (8.7 5),(7.8 1.6),(7.9 2.1),(3 2.2),(7.8 4.3),(2.6 8.5),(4.8 3.4),(3.5 3.5),(3.6 4),
    (3.1 7.9),(8.3 2.9),(2.7 8.4),(5.2 9.8),(7.2 9.5),(8.5 7.1),(7.5 8.4),(7.5 7.7),
    (8.1 2.9),(7.7 7.3),(4.1 4.2),(8.3 7.2),(2.3 3.6),(8.9 5.3),(2.7 5.7),(5.7 9.7),
    (2.7 7.7),(3.9 8.8),(6 8.1),(8 7.2),(5.4 3.2),(5.5 2.6),(6.2 2.2),(7 2),(7.6 2.7),
    (8.4 3.5),(8.7 4.2),(8.2 5.4),(8.3 6.4),(6.9 8.6),(6 9),(5 8.6),(4.3 8),(3.6 7.3),
    (3.6 6.8),(4 7.5),(2.4 6.7),(2.3 6),(2.6 4.4),(2.8 3.3),(4 3.2),(4.3 1.9),(6.5 1.6),
    (7.3 1.6),(3.8 4.6),(3.1 5.9),(3.4 8.6),(4.5 9),(6.4 9.7))"""
    mp = MultiPoint.from_wkt(wkt)

    # alpha_shapes with no arguments
    result = mp.alpha_shapes().to_wkt(1)

    expected = """POLYGON ((8.9 5.3,9.1 5.0,8.7 4.2,9.0 3.0,8.4 1.9,7.8 1.6,7.3 1.6,6.5 1.6,5.3 1.8,4.3 1.9,3.7 2.3,3.0 2.2,2.8 3.3,2.3 3.6,2.6 4.4,2.7 5.4,2.3 6.0,2.4 6.7,2.7 7.7,2.4 8.2,2.6 8.5,3.4 8.6,3.9 8.8,4.5 9.0,4.9 9.5,5.2 9.8,5.7 9.7,6.4 9.7,7.2 9.5,7.6 8.8,7.5 8.4,8.3 7.2,8.5 7.1,8.8 5.8,8.9 5.3))"""  # noqa: E501

    assert result == expected

    # alpha_shapes allows holes
    result = mp.alpha_shapes(allow_holes=True).to_wkt(1)

    expected = """POLYGON ((8.9 5.3,9.1 5.0,8.7 4.2,9.0 3.0,8.4 1.9,7.8 1.6,7.3 1.6,6.5 1.6,5.3 1.8,4.3 1.9,3.7 2.3,3.0 2.2,2.8 3.3,2.3 3.6,2.6 4.4,2.7 5.4,2.3 6.0,2.4 6.7,2.7 7.7,2.4 8.2,2.6 8.5,3.4 8.6,3.9 8.8,4.5 9.0,4.9 9.5,5.2 9.8,5.7 9.7,6.4 9.7,7.2 9.5,7.6 8.8,7.5 8.4,8.3 7.2,8.5 7.1,8.8 5.8,8.9 5.3),(3.6 6.1,3.6 6.8,4.0 7.5,4.3 8.0,6.0 8.1,6.8 7.3,7.7 6.7,8.1 6.0,8.2 5.4,8.1 4.7,7.8 4.3,7.6 2.7,6.2 2.2,5.4 3.2,4.4 4.2,3.8 4.6,3.6 6.1))"""  # noqa: E501

    assert result == expected

    # using optimal alpha
    result = mp.optimal_alpha_shapes().to_wkt(1)

    expected = """POLYGON ((8.9 5.3,9.1 5.0,8.7 4.2,9.0 3.0,8.8 2.9,8.4 1.9,7.8 1.6,7.3 1.6,6.5 1.6,5.3 1.8,4.3 1.9,3.7 2.3,3.0 2.2,2.8 3.3,2.3 3.6,2.6 4.4,2.7 5.4,2.3 6.0,2.4 6.7,2.7 7.7,2.4 8.2,2.6 8.5,3.4 8.6,3.9 8.8,4.5 9.0,4.9 9.5,5.2 9.8,5.7 9.7,6.4 9.7,7.2 9.5,7.6 8.8,7.5 8.4,7.5 7.7,8.3 7.2,8.5 7.1,8.3 6.4,8.8 5.8,8.9 5.3))"""  # noqa: E501

    assert result == expected

    # using optimal alpha with allow_holes
    result = mp.optimal_alpha_shapes(True).to_wkt(1)

    expected = """POLYGON ((8.9 5.3,9.1 5.0,8.7 4.2,9.0 3.0,8.8 2.9,8.4 1.9,7.8 1.6,7.3 1.6,6.5 1.6,5.3 1.8,4.3 1.9,3.7 2.3,3.0 2.2,2.8 3.3,2.3 3.6,2.6 4.4,2.7 5.4,2.3 6.0,2.4 6.7,2.7 7.7,2.4 8.2,2.6 8.5,3.4 8.6,3.9 8.8,4.5 9.0,4.9 9.5,5.2 9.8,5.7 9.7,6.4 9.7,7.2 9.5,7.6 8.8,7.5 8.4,7.5 7.7,8.3 7.2,8.5 7.1,8.3 6.4,8.8 5.8,8.9 5.3),(3.6 6.1,3.6 6.8,4.0 7.5,4.3 8.0,5.0 8.6,6.0 8.1,6.8 7.3,7.7 6.7,8.1 6.0,8.2 5.4,8.1 4.7,7.8 4.3,8.1 2.9,7.6 2.7,7.0 2.0,6.2 2.2,5.5 2.6,5.4 3.2,4.8 3.4,4.4 4.2,3.8 4.6,3.6 6.1))"""  # noqa: E501

    assert result == expected


def test_alpha_wrapping_3d():
    wkt = """MULTIPOINT Z ((3.7 7.4 -0.3), (1.6 3.4 6.0), (1.7 1.4 6.9), (1.5 2.8 -8.1), (3.9 0.3 0.1), (5.0 6.9 -9.5), (1.4 3.9 -4.4), (3.0 0.3 7.8), (6.3 0.6 3.0), (1.3 3.3 2.7), (1.3 3.2 5.3), (1.1 2.7 7.3), (1.0 3.3 1.5), (2.9 0.4 2.8), (4.1 -0.1 8.8), (3.7 0.2 -7.9), (2.5 0.4 -5.5), (1.4 2.2 9.3), (1.2 4.9 7.3), (0.8 3.2 0.5), (5.1 0.0 6.8), (2.9 0.2 -9.0), (5.5 0.6 8.5), (1.4 5.3 -3.1), (3.8 0.4 6.4), (1.4 5.5 1.8), (1.1 2.2 0.2), (2.7 0.9 1.5), (3.8 0.3 -10.0), (2.7 6.8 -8.6), (6.4 0.6 -2.8), (5.7 0.7 -5.7), (2.9 6.6 0.4), (3.5 7.0 5.0), (4.6 7.3 5.1), (6.0 0.4 2.7), (2.6 6.4 -6.7), (1.6 4.0 -8.8), (2.0 5.9 7.0), (4.0 7.2 4.8), (3.8 6.9 -8.6), (1.9 1.4 -9.6), (3.3 6.6 -3.8), (5.6 0.4 1.6), (0.9 3.2 4.7), (2.5 1.0 5.5), (2.5 6.1 -9.4), (6.3 1.2 -9.3), (1.8 5.2 4.2), (3.5 6.7 8.5), (2.0 1.7 -5.0), (6.3 6.6 -8.0), (4.8 -0.0 7.9), (1.9 1.5 -6.0), (1.7 2.6 -2.1), (1.6 6.5 1.6), (1.2 4.4 -5.0), (0.9 4.7 3.4), (3.6 0.7 4.8), (2.8 7.1 -2.8), (4.5 0.6 -4.7), (6.0 1.1 -0.0), (1.8 1.7 0.2), (1.0 2.1 1.6), (2.1 0.7 6.9), (1.4 4.2 7.9), (1.9 1.8 4.8), (2.2 6.5 -1.8), (1.7 1.6 2.1), (1.3 1.8 3.5), (3.3 6.5 -9.4), (1.5 4.6 2.8), (1.2 3.9 -6.4), (4.4 0.1 6.9), (2.9 6.6 -4.6), (5.5 6.6 -8.7), (1.2 2.3 -2.8), (5.8 1.1 7.4), (2.3 1.1 8.3), (1.5 3.0 -3.9), (2.3 0.5 -5.3), (2.8 0.9 5.2), (2.4 0.8 -5.4), (1.3 2.9 -5.7), (1.7 5.4 9.0), (1.2 2.4 4.5), (5.1 7.2 -5.5), (1.4 3.5 -6.7), (0.8 4.5 7.1), (1.8 6.5 6.1), (1.2 4.6 -1.3), (3.0 0.8 -6.9), (5.8 0.5 7.3), (4.3 7.3 -1.8), (5.7 0.8 -3.5), (1.1 3.5 -9.9), (1.8 5.4 -6.8), (0.9 2.3 0.3), (4.5 7.1 5.5), (1.3 5.3 -5.8))"""  # noqa: E501
    multi_point = MultiPoint.from_wkt(wkt)

    # alpha_shapes with no arguments
    result = multi_point.alpha_wrapping_3d(11).to_wkt(1)

    current_dir = pathlib.Path(__file__).parent.resolve()
    expected_alpha_wrappind_3d = current_dir / "alpha_wrapping_3d_expected_wkt.txt"
    with open(expected_alpha_wrappind_3d) as f_in:
        expected = f_in.read().strip()

    assert result == expected


def test_area_3d():
    triangle = Triangle([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
    assert triangle.area_3d() == 0.5


def test_difference_3d():
    geom1 = Solid.from_wkt(
        "SOLID ((((0 0 0, 0 1 0, 1 1 0, 1 0 0, 0 0 0)),"
        "((0 0 0, 0 0 1, 0 1 1, 0 1 0, 0 0 0)),"
        "((0 0 0, 1 0 0, 1 0 1, 0 0 1, 0 0 0)),"
        "((1 1 1, 0 1 1, 0 0 1, 1 0 1, 1 1 1)),"
        "((1 1 1, 1 0 1, 1 0 0, 1 1 0, 1 1 1)),"
        "((1 1 1, 1 1 0, 0 1 0, 0 1 1, 1 1 1))))")
    geom2 = Solid.from_wkt(
        "SOLID ((((0 0 0.5, 0 1 0.5, 1 1 0.5, 1 0 0.5, 0 0 0.5)),"
        "((0 0 0.5, 0 0 1, 0 1 1, 0 1 0.5, 0 0 0.5)),"
        "((0 0 0.5, 1 0 0.5, 1 0 1, 0 0 1, 0 0 0.5)),"
        "((1 1 1, 0 1 1, 0 0 1, 1 0 1, 1 1 1)),"
        "((1 1 1, 1 0 1, 1 0 0.5, 1 1 0.5, 1 1 1)),"
        "((1 1 1, 1 1 0.5, 0 1 0.5, 0 1 1, 1 1 1))))")
    diff = geom1.difference_3d(geom2)
    assert diff.volume() == 0.5


def test_covers_3d():
    geom1 = Solid.from_wkt(
        "SOLID (( ((0 0 0,0 1 0,1 1 0,1 0 0,0 0 0)), "
        "((1 0 0,1 1 0,1 1 1,1 0 1,1 0 0)), ((0 1 0,0 1 1,1 1 1,1 1 0,0 1 0)), "
        "((0 0 1,0 1 1,0 1 0,0 0 0,0 0 1)), ((1 0 1,1 1 1,0 1 1,0 0 1,1 0 1)), "
        "((1 0 0,1 0 1,0 0 1,0 0 0,1 0 0)) ))"
    )
    geom2 = Solid.from_wkt(
        "SOLID (( ((0 0 0,0 0.1 0,0.1 0.1 0,0.1 0 0,0 0 0)), "
        "((0.1 0 0,0.1 0.1 0,0.1 0.1 0.1,0.1 0 0.1,0.1 0 0)), "
        "((0 0.1 0,0 0.1 0.1,0.1 0.1 0.1,0.1 0.1 0,0 0.1 0)), "
        "((0 0 0.1,0 0.1 0.1,0 0.1 0,0 0 0,0 0 0.1)), "
        "((0.1 0 0.1,0.1 0.1 0.1,0 0.1 0.1,0 0 0.1,0.1 0 0.1)), "
        "((0.1 0 0,0.1 0 0.1,0 0 0.1,0 0 0,0.1 0 0)) ))"
    )
    assert geom1.covers_3d(geom2)

    geom1 = Solid.from_wkt(
        "SOLID (( ((0 0 0,0 1 0,1 1 0,1 0 0,0 0 0)), "
        "((1 0 0,1 1 0,1 1 1,1 0 1,1 0 0)), ((0 1 0,0 1 1,1 1 1,1 1 0,0 1 0)), "
        "((0 0 1,0 1 1,0 1 0,0 0 0,0 0 1)), ((1 0 1,1 1 1,0 1 1,0 0 1,1 0 1)), "
        "((1 0 0,1 0 1,0 0 1,0 0 0,1 0 0)) ))"
    )
    geom2 = Solid.from_wkt(
        "SOLID (( ((0.1 0.1 0.1,0.1 1.1 0.1,1.1 1.1 0.1,1.1 0.1 0.1,0.1 0.1 0.1)), "
        "((1.1 0.1 0.1,1.1 1.1 0.1,1.1 1.1 1.1,1.1 0.1 1.1,1.1 0.1 0.1)), "
        "((0.1 1.1 0.1,0.1 1.1 1.1,1.1 1.1 1.1,1.1 1.1 0.1,0.1 1.1 0.1)), "
        "((0.1 0.1 1.1,0.1 1.1 1.1,0.1 1.1 0.1,0.1 0.1 0.1,0.1 0.1 1.1)), "
        "((1.1 0.1 1.1,1.1 1.1 1.1,0.1 1.1 1.1,0.1 0.1 1.1,1.1 0.1 1.1)), "
        "((1.1 0.1 0.1,1.1 0.1 1.1,0.1 0.1 1.1,0.1 0.1 0.1,1.1 0.1 0.1)) ))"
    )

    assert not geom1.covers_3d(geom2)


def test_is_planar():
    geom_planar = Polygon.from_wkt(
        "Polygon((0.0 0.0 1.0, 0.0 1.0 1.0, 1.0 1.0 1.0, 1.0 0.0 1.0, 0.0 0.0 1.0))")
    assert geom_planar.is_planar()

    geom_non_planar = Polygon.from_wkt(
        "Polygon((0.0 0.0 1.0, 0.0 1.0 1.0, 1.0 1.0 1.0, 1.0 0.0 2.0, 0.0 0.0 1.0))")
    assert not geom_non_planar.is_planar()


def test_orientation():
    geom = Polygon.from_wkt(
        "Polygon((0.0 0.0 1.0, 1.0 0.0 1.0, 1.0 1.0 1.0, 0.0 1.0 1.0, 0.0 0.0 1.0))")

    assert geom.orientation() == -1

    geom = Polygon.from_wkt(
        "Polygon((0.0 0.0 1.0, 0.0 1.0 1.0, 1.0 1.0 1.0, 1.0 0.0 1.0, 0.0 0.0 1.0))")

    assert geom.orientation() == 1


def test_line_sub_string():
    geom = LineString.from_wkt('LineString Z (0 0 0, 10 10 10)')

    result = geom.line_sub_string(0.1, 0.5).to_wkt(0)

    assert result == 'LINESTRING Z (1 1 1,5 5 5)'


def test_partition_2():
    geom = Polygon.from_wkt(
        'POLYGON ((391 374,240 431,252 340,374 320,289 214,134 390,68 186,154 259,'
        '161 107,435 108,208 148,295 160,421 212,441 303,391 374))')

    result = geom.y_monotone_partition_2().to_wkt(0)

    assert result == (
        "GEOMETRYCOLLECTION ("
        "POLYGON ((134 390,68 186,154 259,134 390)),"
        "POLYGON ((289 214,134 390,154 259,161 107,435 108,208 148,295 160,421 212,289 214)),"  # noqa: E501
        "POLYGON ((391 374,240 431,252 340,374 320,289 214,421 212,441 303,391 374)))")

    result = geom.approx_convex_partition_2().to_wkt(0)
    assert result == (
        "GEOMETRYCOLLECTION ("
        "POLYGON ((391 374,240 431,252 340,374 320,391 374)),"
        "POLYGON ((134 390,68 186,154 259,134 390)),"
        "POLYGON ((289 214,134 390,154 259,289 214)),"
        "POLYGON ((161 107,435 108,208 148,161 107)),"
        "POLYGON ((154 259,161 107,208 148,154 259)),"
        "POLYGON ((289 214,154 259,208 148,295 160,289 214)),"
        "POLYGON ((374 320,289 214,295 160,421 212,374 320)),"
        "POLYGON ((391 374,374 320,421 212,441 303,391 374)))")

    result = geom.greene_approx_convex_partition_2().to_wkt(0)
    assert result == (
        "GEOMETRYCOLLECTION ("
        "POLYGON ((134 390,68 186,154 259,134 390)),"
        "POLYGON ((161 107,435 108,208 148,161 107)),"
        "POLYGON ((208 148,295 160,421 212,289 214,208 148)),"
        "POLYGON ((154 259,161 107,208 148,154 259)),"
        "POLYGON ((289 214,134 390,154 259,208 148,289 214)),"
        "POLYGON ((374 320,289 214,421 212,374 320)),"
        "POLYGON ((374 320,421 212,441 303,391 374,374 320)),"
        "POLYGON ((391 374,240 431,252 340,374 320,391 374)))")

    result = geom.optimal_convex_partition_2().to_wkt(0)
    assert result == (
        "GEOMETRYCOLLECTION ("
        "POLYGON ((391 374,240 431,252 340,374 320,391 374)),"
        "POLYGON ((134 390,68 186,154 259,134 390)),"
        "POLYGON ((161 107,435 108,208 148,161 107)),"
        "POLYGON ((154 259,161 107,208 148,154 259)),"
        "POLYGON ((289 214,134 390,154 259,208 148,295 160,289 214)),"
        "POLYGON ((374 320,289 214,295 160,421 212,441 303,374 320)),"
        "POLYGON ((391 374,374 320,441 303,391 374)))")


def test_visibility_point():
    """Inspired from testVisibility_PointInPolygon SFCGAL unit test"""
    geom = Polygon.from_wkt("POLYGON (( 0 4, 0 0, 3 2, 4 0, 4 4, 1 2, 0 4 ))")
    point = Point.from_wkt("POINT (0.5 2.0)")
    result = geom.point_visibility(point)
    expected_geom = Polygon.from_wkt("POLYGON ((3 2, 1 2, 0 4, 0 0, 3 2))")
    assert result.covers(expected_geom)


def test_visibility_point_with_hole():
    """Inspired from testVisibility_PointInPolygonHole SFCGAL unit test"""
    geom = Polygon.from_wkt(
        "POLYGON (( 0 4, 0 0, 3 2, 4 0, 4 4, 1 2, 0 4 ), "
        "(0.2 1.75, 0.9 1.8, 0.7 1.2, 0.2 1.75))")
    point = Polygon.from_wkt("POINT (0.5 2.0)")
    result = geom.point_visibility(point)
    expected_geom = Polygon.from_wkt(
        "POLYGON ((0.0 1.6,0.2 1.8,0.9 1.8,1.9 1.3,3.0 2.0,1.0 2.0,0.0 4.0,0.0 1.6))")
    assert result.covers(expected_geom)


def test_visibility_segment():
    """Inspired from testVisibility_SegmentInPolygon SFCGAL unit test"""
    geom = Polygon.from_wkt("POLYGON (( 0 4, 0 0, 3 2, 4 0, 4 4, 1 2, 0 4 ))")
    start_point = Point.from_wkt("POINT (1 2)")
    end_point = Point.from_wkt("POINT (4 4)")
    expected_wkt = "POLYGON ((4.0 0.0,4.0 4.0,1.0 2.0,0.0 1.3,0.0 0.0,3.0 2.0,4.0 0.0))"
    result = geom.segment_visibility(start_point, end_point)
    assert expected_wkt == result.to_wkt(1)


def test_visibility_segment_with_hole():
    """Inspired from testVisibility_SegmentInPolygonHole SFCGAL unit test"""
    geom = Polygon.from_wkt(
        "POLYGON ("
        "(1 2, 12 3, 19 -2, 12 6, 14 14, 9 5, 1 2), "
        "(8 3, 8 4, 10 3, 8 3), "
        "(10 6, 11 7, 11 6, 10 6)"
        ")"
    )
    start_point = Point.from_wkt("POINT (19 -2)")
    end_point = Point.from_wkt("POINT (12 6)")
    expected_wkt = (
        "POLYGON ((19.0 -2.0,12.0 6.0,14.0 14.0,10.4 7.6,11.0 7.0,11.0 6.0,10.0 "
        "6.0,9.6 6.0,9.0 5.0,1.0 2.0,4.7 2.3,8.0 4.0,10.0 3.0,9.9 2.8,12.0 "
        "3.0,19.0 -2.0))"
    )
    result = geom.segment_visibility(start_point, end_point)
    assert expected_wkt == result.to_wkt(1)


def test_extrude():
    mp = Polygon([(0, 0), (0, 5), (5, 5), (5, 0)])
    result = mp.extrude(0, 0, 5)
    expected_wkt = (
        "SOLID Z (("
        "((0.0 0.0 0.0,0.0 5.0 0.0,5.0 5.0 0.0,5.0 0.0 0.0,0.0 0.0 0.0)),"
        "((0.0 0.0 5.0,5.0 0.0 5.0,5.0 5.0 5.0,0.0 5.0 5.0,0.0 0.0 5.0)),"
        "((0.0 0.0 0.0,0.0 0.0 5.0,0.0 5.0 5.0,0.0 5.0 0.0,0.0 0.0 0.0)),"
        "((0.0 5.0 0.0,0.0 5.0 5.0,5.0 5.0 5.0,5.0 5.0 0.0,0.0 5.0 0.0)),"
        "((5.0 5.0 0.0,5.0 5.0 5.0,5.0 0.0 5.0,5.0 0.0 0.0,5.0 5.0 0.0)),"
        "((5.0 0.0 0.0,5.0 0.0 5.0,0.0 0.0 5.0,0.0 0.0 0.0,5.0 0.0 0.0))))")
    assert result.to_wkt(1) == expected_wkt

    p1 = Polygon.from_wkt('POLYGON ( (0 0, 0 1, 1 1, 1 0, 0 0) )')
    p1e = p1.extrude(0, 0, 30)

    assert p1e.geom_type == "SOLID"


def test_vtk(tmp_test_dir):
    """Test vtk output"""
    geom = PolyhedralSurface.from_wkt(
        "POLYHEDRALSURFACE Z ("
        "((0.0 0.0 0.0, 0.0 5.0 0.0, 5.0 5.0 0.0, 5.0 0.0 0.0, 0.0 0.0 0.0)), "
        "((0.0 0.0 5.0, 5.0 0.0 5.0, 5.0 5.0 5.0, 0.0 5.0 5.0, 0.0 0.0 5.0)), "
        "((0.0 0.0 0.0, 0.0 0.0 5.0, 0.0 5.0 5.0, 0.0 5.0 0.0, 0.0 0.0 0.0)), "
        "((0.0 5.0 0.0, 0.0 5.0 5.0, 5.0 5.0 5.0, 5.0 5.0 0.0, 0.0 5.0 0.0)), "
        "((5.0 5.0 0.0, 5.0 5.0 5.0, 5.0 0.0 5.0, 5.0 0.0 0.0, 5.0 5.0 0.0)), "
        "((5.0 0.0 0.0, 5.0 0.0 5.0, 0.0 0.0 5.0, 0.0 0.0 0.0, 5.0 0.0 0.0)))")
    out_filepath = str(tmp_test_dir / "out.vtk")
    geom.write_vtk(out_filepath)
    expected_vtk = pathlib.Path(__file__).parent.resolve() / "expected.vtk"
    assert cmp(out_filepath, expected_vtk)


def test_stl(tmp_test_dir):
    """Test stl output"""
    geom = PolyhedralSurface.from_wkt(
        "POLYHEDRALSURFACE Z ("
        "((0.0 0.0 0.0, 0.0 5.0 0.0, 5.0 5.0 0.0, 5.0 0.0 0.0, 0.0 0.0 0.0)), "
        "((0.0 0.0 5.0, 5.0 0.0 5.0, 5.0 5.0 5.0, 0.0 5.0 5.0, 0.0 0.0 5.0)), "
        "((0.0 0.0 0.0, 0.0 0.0 5.0, 0.0 5.0 5.0, 0.0 5.0 0.0, 0.0 0.0 0.0)), "
        "((0.0 5.0 0.0, 0.0 5.0 5.0, 5.0 5.0 5.0, 5.0 5.0 0.0, 0.0 5.0 0.0)), "
        "((5.0 5.0 0.0, 5.0 5.0 5.0, 5.0 0.0 5.0, 5.0 0.0 0.0, 5.0 5.0 0.0)), "
        "((5.0 0.0 0.0, 5.0 0.0 5.0, 0.0 0.0 5.0, 0.0 0.0 0.0, 5.0 0.0 0.0)))")
    out_filepath = str(tmp_test_dir / "out.stl")
    geom.write_stl(out_filepath)
    expected_stl = pathlib.Path(__file__).parent.resolve() / "expected.stl"
    assert cmp(out_filepath, expected_stl)


def test_rhr_lhr():
    """Test Force_LHR and Force_RHR"""
    extCW_intCCW = "POLYGON ((0 5,5 5,5 0,0 0,0 5),(2 1,2 2,1 2,1 1,2 1),(4 3,4 4,3 4,3 3,4 3))"  # noqa: E501
    extCCW_intCW = "POLYGON ((0 5,0 0,5 0,5 5,0 5),(2 1,1 1,1 2,2 2,2 1),(4 3,3 3,3 4,4 4,4 3))"  # noqa: E501
    allCW = "POLYGON ((0 5,5 5,5 0,0 0,0 5),(2 1,1 1,1 2,2 2,2 1),(4 3,3 3,3 4,4 4,4 3))"  # noqa: E501
    allCCW = "POLYGON ((0 5,0 0,5 0,5 5,0 5),(2 1,2 2,1 2,1 1,2 1),(4 3,4 4,3 4,3 3,4 3))"  # noqa: E501

    # Force_RHR
    geom = Polygon.from_wkt(extCW_intCCW)
    rhr = geom.force_rhr().to_wkt(0)
    assert rhr == extCW_intCCW

    geom = Polygon.from_wkt(extCCW_intCW)
    rhr = geom.force_rhr().to_wkt(0)
    assert rhr == extCW_intCCW

    geom = Polygon.from_wkt(allCW)
    rhr = geom.force_rhr().to_wkt(0)
    assert rhr == extCW_intCCW

    geom = Polygon.from_wkt(allCCW)
    rhr = geom.force_rhr().to_wkt(0)
    assert rhr == extCW_intCCW

    # Force_LHR
    geom = Polygon.from_wkt(extCW_intCCW)
    lhr = geom.force_lhr().to_wkt(0)
    assert lhr == extCCW_intCW

    geom = Polygon.from_wkt(extCCW_intCW)
    lhr = geom.force_lhr().to_wkt(0)
    assert lhr == extCCW_intCW

    geom = Polygon.from_wkt(allCW)
    lhr = geom.force_lhr().to_wkt(0)
    assert lhr == extCCW_intCW

    geom = Polygon.from_wkt(allCCW)
    lhr = geom.force_lhr().to_wkt(0)
    assert lhr == extCCW_intCW


def test_is_valid_detail():
    valid_polygon_wkt = "POLYGON ((0 5,5 5,5 0,0 0,0 5),(2 1,2 2,1 2,1 1,2 1),(4 3,4 4,3 4,3 3,4 3))"  # noqa: E501
    valid_polygon = Polygon.from_wkt(valid_polygon_wkt)
    valid_detail_msg, _ = valid_polygon.is_valid_detail()
    assert valid_detail_msg is None

    # invalid polygon which self intersects
    invalid_polygon_wkt = "POLYGON ((0 5,5 0,5 5,0 0,0 5))"
    invalid_polygon = Polygon.from_wkt(invalid_polygon_wkt)
    invalid_detail_msg, _ = invalid_polygon.is_valid_detail()
    assert invalid_detail_msg == "ring 0 self intersects"


def test_simplify():
    ls = LineString.from_wkt("LINESTRING(1 4, 4 9, 4 12, 4 16, 2 19, -4 20)")
    result = ls.simplify(5, False)
    assert result.to_wkt(0) == "LINESTRING (1 4,2 19,-4 20)"
