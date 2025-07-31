import icontract
import pytest

from pysfcgal.sfcgal import LineString, MultiPoint


@pytest.fixture
def multipoint(c000, c100, c010):
    yield MultiPoint((c000, c100, c010))


@pytest.fixture
def other_multipoint(c100, c010, c001):
    yield MultiPoint((c100, c010, c001))


@pytest.fixture
def multipoint_unordered(c000, c100, c010):
    yield MultiPoint((c100, c010, c000))


def test_multipoint_constructor(multipoint):
    multipoint_cloned = MultiPoint(multipoint.to_coordinates())
    multipoint_cloned == multipoint


def test_multipoint_iteration(multipoint, expected_points):
    for point, expected_point in zip(multipoint, expected_points):
        assert point == expected_point


def test_multipoint_indexing(multipoint, expected_points):
    for idx in range(len(multipoint)):
        assert multipoint[idx] == expected_points[idx]
    assert multipoint[-1] == expected_points[-1]
    assert multipoint[1:3] == expected_points[1:3]


def test_multipoint_equality(multipoint, other_multipoint, multipoint_unordered):
    assert multipoint != other_multipoint
    assert multipoint[1:] == other_multipoint[:2]
    # the point order is important (be compliant with other GIS softwares)
    assert multipoint != multipoint_unordered


def test_multipoint_to_coordinates(multipoint, c000, c100, c010):
    assert multipoint.to_coordinates() == [c000, c100, c010]
    cloned_multipoint = MultiPoint(multipoint.to_coordinates())
    assert cloned_multipoint == multipoint
    other_multipoint = MultiPoint.from_coordinates(multipoint.to_coordinates())
    assert other_multipoint == multipoint


def test_multipoint_to_dict(multipoint):
    multipoint_data = multipoint.to_dict()
    other_multipoint = MultiPoint.from_dict(multipoint_data)
    assert other_multipoint == multipoint


def test_multipoint_add_point(multipoint, point001):
    assert len(multipoint) == 3
    assert point001 not in multipoint

    multipoint.add_point(point001)
    assert len(multipoint) == 4
    assert point001 in multipoint


def test_multipoint_add_line_fails(multipoint, c000, c100, c010):
    # try to add a linestring to a multipoint
    # this is expected to fail
    with pytest.raises(icontract.errors.ViolationError):
        multipoint.add_point(LineString([c000, c100, c010]))
