import pytest

from pysfcgal.sfcgal import GeometryCollection, LineString, Polygon


@pytest.fixture
def expected_geometries(point000, c000, c100, c010):
    yield [point000, LineString([c000, c100, c010]), Polygon([c000, c100, c010])]


@pytest.fixture
def collection(expected_geometries):
    geom_collec = GeometryCollection()
    for geom in expected_geometries:
        geom_collec.addGeometry(geom)
    yield geom_collec


@pytest.fixture
def other_collection(expected_geometries):
    geom_collec = GeometryCollection()
    for _ in range(3):
        geom_collec.addGeometry(expected_geometries[0])
    yield geom_collec


@pytest.fixture
def collection_unordered(expected_geometries):
    geom_collec = GeometryCollection()
    for geom in expected_geometries[::-1]:
        geom_collec.addGeometry(geom)
    yield geom_collec


def test_geometry_collection_len(collection):
    assert len(collection) == 3


def test_geometry_collection_iteration(collection, expected_geometries):
    for geometry, expected_geometry in zip(collection, expected_geometries):
        assert geometry == expected_geometry


def test_geometry_collection_indexing(collection, expected_geometries):
    assert isinstance(collection[1], LineString)
    assert isinstance(collection[-1], Polygon)
    assert len(collection[:2]) == 2
    for idx in range(len(collection)):
        assert collection[idx] == expected_geometries[idx]
    assert collection[-1] == expected_geometries[-1]
    assert collection[1:3] == expected_geometries[1:3]


def test_geometry_collection_equality(
    collection, other_collection, collection_unordered
):
    assert collection != other_collection
    assert collection != collection_unordered


def test_geometry_collection_to_coordinates(collection, c000, c100, c010, c001):
    assert collection.to_coordinates() == [
        c000,
        [c000, c100, c010],
        [[c000, c100, c010, c000]],
    ]
    # Can't test the clone, as GeometryCollection can't be instantiated from coordinates


def test_geometry_collection_to_dict(collection):
    collection_data = collection.to_dict()
    other_collection = GeometryCollection.from_dict(collection_data)
    assert collection == other_collection
