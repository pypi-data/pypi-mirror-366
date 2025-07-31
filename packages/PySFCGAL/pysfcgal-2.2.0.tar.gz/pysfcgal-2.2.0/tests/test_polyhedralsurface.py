import icontract
import pytest

from pysfcgal.sfcgal import LineString, Polygon, PolyhedralSurface


@pytest.fixture
def polyhedralsurface(c000, c100, c010, c001):
    yield PolyhedralSurface(
        [
            [[c000, c100, c010]],
            [[c000, c100, c001]],
            [[c000, c010, c001]],
            [[c100, c010, c001]],
        ]
    )


@pytest.fixture
def other_polyhedralsurface(c000, c100, c010, c001):
    yield PolyhedralSurface(
        [[[c000, c100, c010]], [[c000, c100, c001]], [[c000, c010, c001]]]
    )


@pytest.fixture
def polyhedralsurface_unordered(c000, c100, c010, c001):
    yield PolyhedralSurface(
        [
            [[c100, c010, c001]],
            [[c000, c100, c010]],
            [[c000, c100, c001]],
            [[c000, c010, c001]],
        ]
    )


@pytest.fixture
def expected_polygons(c000, c100, c010, c001):
    yield [
        Polygon([c000, c100, c010]),
        Polygon([c000, c100, c001]),
        Polygon([c000, c010, c001]),
        Polygon([c100, c010, c001]),
    ]


def test_polyhedralsurface_len(polyhedralsurface):
    assert len(polyhedralsurface) == 4


def test_polyhedralsurface_iteration(polyhedralsurface, expected_polygons):
    for polygon, expected_polygon in zip(polyhedralsurface, expected_polygons):
        assert polygon == expected_polygon


def test_polyhedralsurface_indexing(polyhedralsurface, expected_polygons):
    for idx in range(len(polyhedralsurface)):
        assert polyhedralsurface[idx] == expected_polygons[idx]
    assert polyhedralsurface[-1] == expected_polygons[-1]
    assert polyhedralsurface[1:3] == expected_polygons[1:3]


def test_polyhedralsurface_equality(
    polyhedralsurface, other_polyhedralsurface, polyhedralsurface_unordered
):
    assert not other_polyhedralsurface.is_valid()
    assert polyhedralsurface != other_polyhedralsurface
    assert polyhedralsurface != polyhedralsurface_unordered


def test_polyhedralsurface_to_coordinates(polyhedralsurface, c000, c100, c010, c001):
    assert polyhedralsurface.to_coordinates() == [
        [[c000, c100, c010, c000]],
        [[c000, c100, c001, c000]],
        [[c000, c010, c001, c000]],
        [[c100, c010, c001, c100]],
    ]
    other_phs = PolyhedralSurface.from_coordinates(polyhedralsurface.to_coordinates())
    assert other_phs == polyhedralsurface


def test_polyhedralsurface_to_dict(polyhedralsurface):
    polyhedralsurface_data = polyhedralsurface.to_dict()
    other_polyhedralsurface = PolyhedralSurface.from_dict(polyhedralsurface_data)
    assert other_polyhedralsurface == polyhedralsurface


def test_to_solid():
    coords_str = (
        "((3.0 3.0 0.0,3.0 8.0 0.0,8.0 8.0 0.0,8.0 3.0 0.0"
        ",3.0 3.0 0.0)),"
        "((3.0 3.0 30.0,8.0 3.0 30.0,8.0 8.0 30.0,3.0 8.0 30.0,3.0 3.0 30.0)),"
        "((3.0 3.0 0.0,3.0 3.0 30.0,3.0 8.0 30.0,3.0 8.0 0.0,3.0 3.0 0.0)),"
        "((3.0 8.0 0.0,3.0 8.0 30.0,8.0 8.0 30.0,8.0 8.0 0.0,3.0 8.0 0.0)),"
        "((8.0 8.0 0.0,8.0 8.0 30.0,8.0 3.0 30.0,8.0 3.0 0.0,8.0 8.0 0.0)),"
        "((8.0 3.0 0.0,8.0 3.0 30.0,3.0 3.0 30.0,3.0 3.0 0.0,8.0 3.0 0.0))"
    )

    wkt_poly = f"POLYHEDRALSURFACE Z ({coords_str})"
    poly = PolyhedralSurface.from_wkt(wkt_poly)
    solid = poly.to_solid()
    expected_wkt = f"SOLID Z (({coords_str}))"
    assert solid.to_wkt(1) == expected_wkt


def test_polyhedralsurface_add_polygon(polyhedralsurface, c100, c010, c001):
    new_polygon = Polygon([c010, c100, c001])
    assert len(polyhedralsurface) == 4
    assert new_polygon not in polyhedralsurface

    polyhedralsurface.add_patch(new_polygon)
    assert len(polyhedralsurface) == 5
    assert new_polygon in polyhedralsurface


def test_polyhedralsurface_add_linestring_fails(polyhedralsurface, c100, c010, c001):
    # try to add a linestring to a polyhedral surface
    # this is expected to fail
    with pytest.raises(icontract.errors.ViolationError):
        polyhedralsurface.add_patch(LineString([c100, c010, c001]))
