import pytest

from pysfcgal.sfcgal import Polygon, Triangle


@pytest.fixture
def triangle(c000, c100, c010):
    yield Triangle([c000, c100, c010])


@pytest.fixture
def triangle_2(c000, c100, c001):
    yield Triangle([c000, c100, c001])


@pytest.fixture
def triangle_unordered(c000, c100, c010):
    yield Triangle([c100, c010, c000])


@pytest.fixture
def expected_polygon(c000, c100, c010):
    yield Polygon([c000, c100, c010])


def test_triangle(triangle, expected_points, triangle_2, triangle_unordered):
    # iteration
    for point, expected_point in zip(triangle, expected_points):
        assert point == expected_point
    # indexing
    for idx in range(3):
        assert triangle[idx] == expected_points[idx]
    assert triangle[-1] == expected_points[-1]
    assert triangle[1:3] == expected_points[1:3]
    # equality
    assert triangle != triangle_2
    assert triangle != triangle_unordered


def test_triangle_to_polygon(triangle, expected_polygon):
    polygon = triangle.to_polygon(True)
    assert polygon.is_valid()
    assert polygon.geom_type == "Polygon"
    assert polygon == expected_polygon


def test_triangle_to_coordinates(triangle, c000, c100, c010):
    assert triangle.to_coordinates() == [c000, c100, c010]
    cloned_triangle = Triangle(triangle.to_coordinates())
    assert cloned_triangle == triangle
    other_triangle = Triangle.from_coordinates(triangle.to_coordinates())
    assert other_triangle == triangle


def test_triangle_to_dict(triangle):
    triangle_data = triangle.to_dict()
    other_triangle = Triangle.from_dict(triangle_data)
    assert other_triangle == triangle
