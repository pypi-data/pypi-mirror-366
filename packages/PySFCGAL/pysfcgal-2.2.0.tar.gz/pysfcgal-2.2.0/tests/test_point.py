import pytest

from pysfcgal.sfcgal import Point


@pytest.fixture
def coords():
    x, y, z, m = 4, 5, 6, 7
    yield x, y, z, m


@pytest.fixture
def point_2d(coords):
    x, y = coords[:2]
    yield Point(x, y)


@pytest.fixture
def point_3d(coords):
    x, y, z = coords[:3]
    yield Point(x, y, z)


@pytest.fixture
def point_4d(coords):
    yield Point(*coords)


@pytest.fixture
def point_3dm(coords):
    x, y, _, m = coords
    yield Point(x, y, m=m)


@pytest.mark.parametrize(
    "x,y,z,m",
    [
        (1, None, None, None),
        (None, 2, None, None),
        (None, None, 3, None),
        (None, None, None, 4),
        (None, None, 3, 4),
    ]
)
def test_point_wrong_param(x, y, z, m):
    with pytest.raises(ValueError):
        _ = Point(x, y, z, m)


@pytest.mark.parametrize(
    "point_fixture, coordinates",
    [
        ("point_3d", (4, 5, 6)),
        ("point_2d", (4, 5)),
        ("point_4d", (4, 5, 6, 7)),
        ("point_3dm", (4, 5, None, 7)),
    ]
)
def test_point_to_coordinates(point_fixture, coordinates, request):
    point = request.getfixturevalue(point_fixture)
    assert point.x == coordinates[0]
    assert point.y == coordinates[1]
    if point_fixture in ("point_3d", "point_4d"):
        assert point.has_z
        assert point.z == coordinates[2]
    if point_fixture in ("point_3dm", "point_4d"):
        assert point.has_m
        assert point.m == coordinates[3]
    assert point.to_coordinates() == coordinates
    other_point = Point.from_coordinates(point.to_coordinates())
    assert point == other_point
    other_point = Point(*point.to_coordinates())
    assert other_point == point


def test_point_to_dict(point_3d):
    point_data = point_3d.to_dict()
    other_point = Point.from_dict(point_data)
    assert other_point == point_3d


def test_point_equivalence(point_2d, point_3d, point_3dm):
    assert not point_2d == point_3d
    assert not point_3dm == point_3d
