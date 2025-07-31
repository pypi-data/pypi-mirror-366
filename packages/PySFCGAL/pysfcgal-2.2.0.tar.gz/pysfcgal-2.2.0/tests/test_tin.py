import icontract
import pytest

from pysfcgal.sfcgal import LineString, MultiPolygon, Tin, Triangle


@pytest.fixture
def expected_triangles(c000, c100, c010, c001):
    yield [
        Triangle([c000, c100, c010]),
        Triangle([c000, c100, c001]),
        Triangle([c000, c010, c001]),
        Triangle([c100, c010, c001]),
    ]


@pytest.fixture
def tin_coordinates(c000, c100, c010, c001):
    yield [
        [c000, c100, c010], [c000, c100, c001], [c000, c010, c001], [c100, c010, c001]
    ]


@pytest.fixture
def expected_multipolygon(c000, c100, c010, c001):
    yield MultiPolygon(
        [
            [[c000, c100, c010]],
            [[c000, c100, c001]],
            [[c000, c010, c001]],
            [[c100, c010, c001]],
        ]
    )


@pytest.fixture
def tin(tin_coordinates):
    yield Tin(tin_coordinates)


@pytest.fixture
def tin_unclosed(c000, c100, c010, c001):
    yield Tin([[c000, c100, c010], [c000, c100, c001], [c000, c010, c001]])


@pytest.fixture
def tin_unordered(c000, c100, c010, c001):
    yield Tin([[c000, c100, c010], [c000, c100, c001], [c000, c010, c001]])


def test_tin(tin, expected_triangles, tin_unclosed, tin_unordered):
    assert len(tin) == 4
    # iteration
    for triangle, expected_triangle in zip(tin, expected_triangles):
        assert triangle == expected_triangle
    # indexing
    for idx in range(len(tin)):
        assert tin[idx] == expected_triangles[idx]
    assert tin[-1] == expected_triangles[-1]
    assert tin[1:3] == expected_triangles[1:3]
    # equality
    assert not tin_unclosed.is_valid()
    assert tin != tin_unclosed
    assert tin != tin_unordered


def test_tin_wkt(tin, tin_coordinates):
    assert tin.to_wkt(0) == (
        "TIN Z ("
        "((0 0 0,1 0 0,0 1 0,0 0 0)),"
        "((0 0 0,1 0 0,0 0 1,0 0 0)),"
        "((0 0 0,0 1 0,0 0 1,0 0 0)),"
        "((1 0 0,0 1 0,0 0 1,1 0 0)))"
    )


def test_tin_to_coordinates(tin, tin_coordinates):
    assert tin.to_coordinates() == tin_coordinates
    cloned_tin = Tin(tin_coordinates)
    assert cloned_tin == tin
    other_tin = Tin.from_coordinates(tin.to_coordinates())
    assert other_tin == tin


def test_tin_to_multipolygon(tin, expected_multipolygon):
    multipoly = tin.to_multipolygon(wrapped=True)
    assert multipoly.geom_type == "MultiPolygon"
    assert multipoly == expected_multipolygon


def test_tin_to_dict(tin):
    tin_data = tin.to_dict()
    other_tin = Tin.from_dict(tin_data)
    assert other_tin == tin


def test_tin_add_patch(tin, c100, c010, c001):
    new_triangle = Triangle([c010, c100, c001])
    assert len(tin) == 4
    assert new_triangle not in tin

    tin.add_patch(new_triangle)
    assert len(tin) == 5
    assert new_triangle in tin


def test_tin_add_linestring_fails(tin, c000, c100, c010):
    # try to add a linestring to a multipoint
    # this is expected to fail
    with pytest.raises(icontract.errors.ViolationError):
        tin.add_patch(LineString([c000, c100, c010]))
