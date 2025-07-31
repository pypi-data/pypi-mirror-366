import pytest

from pysfcgal.sfcgal import LineString, Point, Polygon, Triangle


@pytest.mark.parametrize(
    "coordinates, factor",
    [
        [(1, 2), 2.],
        [(1, 2, 3), 2.],
        [(1, 2, 3, 4), 2.],
        [(1, 2, 3), 0.],
        [(1, 2, 3), -1.],
    ],
)
def test_scale_uniform(coordinates, factor):
    point = Point(*coordinates)
    scaled_point = point.scale_uniform(factor)
    assert scaled_point.to_coordinates() == tuple(
        factor * coord if idx < 3 else coord for idx, coord in enumerate(coordinates)
    )


def test_scale_uniform_default():
    coordinates = 1., 2.
    point = Point(*coordinates)
    scaled_point = point.scale_uniform()
    assert point == scaled_point


@pytest.mark.parametrize(
    "coordinates",
    [
        ((0, 0), (1, 1), (2, 0)),
        ((0, 0, 0), (1, 1, 1), (2, 0, 2)),
    ],
)
def test_scale_uniform_linestring(coordinates):
    linestring = LineString(coordinates)
    factor = 2.
    scaled_ls = linestring.scale_uniform(factor)
    assert scaled_ls.to_coordinates() == [
        tuple(factor * coord for coord in point) for point in coordinates
    ]


@pytest.mark.parametrize(
    "coordinates,factors",
    [
        [(1, 2), (2., 3.)],
        [(1, 2), (2., 3., 1.)],
        [(1, 2, 3), (2., 3., 4.)],
        [(1, 2, 3, 4), (2., 3., 4.)],
        [(1, 2, None, 4), (2., 3., 4.)],
    ],
)
def test_scale(coordinates, factors):
    point = Point(*coordinates)
    scaled_point = point.scale(*factors)
    # fill in the factors so as to feed the zip during assertion
    factors = [
        factors[idx] if idx < len(factors) else 1. for idx in range(len(coordinates))
    ]
    assert scaled_point.to_coordinates() == tuple(
        None if coord is None else (factor * coord if idx < 3 else coord)
        for idx, (coord, factor)
        in enumerate(zip(coordinates, factors))
    )
    # Check the dimensionality preservation
    assert not point.has_z ^ scaled_point.has_z
    assert not point.has_m ^ scaled_point.has_m


def test_scale_default():
    coordinates = 1., 2.
    point = Point(*coordinates)
    scaled_point = point.scale()
    assert point == scaled_point


@pytest.mark.parametrize(
    "ring, factors",
    [
        [((0, 0), (1, 0), (1, 1), (0, 1), (0, 0)), (2., 3., 1.)],
        [((0, 0), (1, 0), (1, 1), (0, 1), (0, 0)), (2., 3.)],
        [((0, 0, 0), (1, 0, 0), (1, 1, 1), (0, 1, 1), (0, 0, 0)), (2., 3., 4.)],
    ],
)
def test_scale_polygon(ring, factors):
    polygon = Polygon(ring)
    scaled_polygon = polygon.scale(*factors)
    assert scaled_polygon.to_coordinates() == [
        [
            tuple(factor * coord for coord, factor in zip(point, factors))
            for point in ring
        ]
    ]


@pytest.mark.parametrize(
    "coordinates, factors, center_coordinates, expected_coordinates",
    [
        [(3., 4.), (2., 2., 1.), (1, 1, 0), (5., 7.)],
        [(3., 4., 5.), (2., 2., 2.), (1, 1, 1), (5., 7., 9.)],
        [(3., 4., 5., 6.), (2., 2., 2.), (1, 1, 1), (5., 7., 9., 6.)],
    ],
)
def test_scale_around_center(
    coordinates, factors, center_coordinates, expected_coordinates
):
    point = Point(*coordinates)
    scaled_point = point.scale_around_center(*factors, *center_coordinates)
    assert scaled_point.to_coordinates() == expected_coordinates


@pytest.mark.parametrize(
    "coordinates",
    [
        ((0, 0), (1, 0), (0, 1)),
        ((0, 0, 0), (1, 0, 0), (0, 1, 0)),
    ],
)
def test_scale_triangle(coordinates):
    triangle = Triangle(coordinates)
    factor = 2.
    scaled_triangle = triangle.scale_uniform(factor)
    assert scaled_triangle.to_coordinates() == [
        tuple(factor * coord for coord in point) for point in coordinates
    ]
