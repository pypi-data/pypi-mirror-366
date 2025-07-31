import math

import pytest

from pysfcgal.sfcgal import LineString, Point, Polygon


def is_close(first: float, second: float, tol: float = 1e-9) -> bool:
    """Check if two float values are under a give tolerance.

    Parameters
    ----------
    first: float
        First term of the comparison
    second: float
        Second term of the comparison
    tol: float
        Comparison tolerance

    Returns
    -------
    bool
        True if both values are close, False otherwise

    """
    return abs(first - second) < tol


@pytest.mark.parametrize(
    "coordinates, angle, expected_coordinates",
    [
        [(1., 0.), math.pi / 2, (0., 1.)],
        [(1., 0.), -math.pi / 2, (0., -1.)],
        [(1., 0.), 3 * math.pi / 2, (0., -1.)],
        [(1., 0.), 5 * math.pi / 2, (0., 1.)],
    ],
)
def test_rotate(coordinates, angle, expected_coordinates):
    point = Point(*coordinates)
    rotated_point = point.rotate(angle)
    assert all(
        is_close(rc, ec)
        for rc, ec in zip(rotated_point.to_coordinates(), expected_coordinates)
    )


@pytest.mark.parametrize(
    "coordinates, angle, center_coordinates, expected_coordinates",
    [
        [(2., 0.), math.pi / 2, (1., 0.), (1., 1.)],
    ],
)
def test_rotate_around_2d_point(
    coordinates, angle, center_coordinates, expected_coordinates
):
    point = Point(*coordinates)
    rotated_point = point.rotate_around_2d_point(angle, *center_coordinates)
    assert all(
        is_close(rc, ec)
        for rc, ec in zip(rotated_point.to_coordinates(), expected_coordinates)
    )


@pytest.mark.parametrize(
    "coordinates, angle, vector_axis, expected_coordinates",
    [
        [(1., 0., 1.), math.pi / 2, (0., 0., 1.), (0., 1., 1.)],
        [(1., 0., 0.), math.pi, (1., 1., 1.), (-1/3., 2/3., 2/3.)],
        [(1., 0., 0.), -math.pi / 2, (0., 0., 1.), (0., -1., 0.)],
        [(1., 0., 0.), 3 * math.pi / 2, (0., 1., 0.), (0., 0., 1.)],
        [(1., 0., 0.), 5 * math.pi / 2, (0., 0., 1.), (0., 1., 0.)],
    ],
)
def test_rotate_around_3d_axis(
    coordinates, angle, vector_axis, expected_coordinates
):
    point = Point(*coordinates)
    rotated_point = point.rotate_around_3d_axis(angle, *vector_axis)
    print(rotated_point.to_coordinates())
    assert all(
        is_close(rc, ec)
        for rc, ec in zip(rotated_point.to_coordinates(), expected_coordinates)
    )


@pytest.mark.parametrize(
    "coordinates, angle, vector_axis, center_coordinates, expected_coordinates",
    [
        [(1., 0., 1.), math.pi / 2, (0., 0., 1.), (0, 0, 0), (0., 1., 1.)],
        [(1., 0., 1.), math.pi / 2, (0., 0., 1.), (1, 1, 1), (2., 1., 1.)],
        [(1., 0., 1.), math.pi / 2, (0., 0., 1.), (1, 0, 1), (1., 0., 1.)],
        [(0., 0., 0.), math.pi / 2, (0., 0., 1.), (1, 0, 1), (1., -1., 0.)],
        [(0., 0., 0.), -math.pi / 2, (0., 0., 1.), (1, 0, 1), (1., 1., 0.)],
    ],
)
def test_rotate_3d_around_center(
    coordinates, angle, vector_axis, center_coordinates, expected_coordinates
):
    point = Point(*coordinates)
    rotated_point = point.rotate_3d_around_center(
        angle, *vector_axis, *center_coordinates
    )
    print(rotated_point.to_coordinates())
    assert all(
        is_close(rc, ec)
        for rc, ec in zip(rotated_point.to_coordinates(), expected_coordinates)
    )


@pytest.mark.parametrize(
    "coordinates, angle, expected_coordinates",
    [
        [(0., 1., 0.), math.pi / 2, (0., 0., 1.)],
    ],
)
def test_rotate_x(
    coordinates, angle, expected_coordinates
):
    point = Point(*coordinates)
    rotated_point = point.rotate_x(angle)
    assert all(
        is_close(rc, ec)
        for rc, ec in zip(rotated_point.to_coordinates(), expected_coordinates)
    )


@pytest.mark.parametrize(
    "coordinates, angle, expected_coordinates",
    [
        [(1., 0., 0.), math.pi / 2, (0., 0., -1.)],
    ],
)
def test_rotate_y(
    coordinates, angle, expected_coordinates
):
    point = Point(*coordinates)
    rotated_point = point.rotate_y(angle)
    assert all(
        is_close(rc, ec)
        for rc, ec in zip(rotated_point.to_coordinates(), expected_coordinates)
    )


@pytest.mark.parametrize(
    "coordinates, angle, expected_coordinates",
    [
        [(1., 0., 0.), math.pi / 2, (0., 1., -0.)],
    ],
)
def test_rotate_z(
    coordinates, angle, expected_coordinates
):
    point = Point(*coordinates)
    rotated_point = point.rotate_z(angle)
    assert all(
        is_close(rc, ec)
        for rc, ec in zip(rotated_point.to_coordinates(), expected_coordinates)
    )


@pytest.mark.parametrize(
    "coordinates, angle, expected_coordinates",
    [
        [((1., 0.), (2., 0.)), math.pi / 2, ((0., 1.), (0., 2.))],
        [((1., 0.), (2., 0.)), -math.pi / 2, ((0., -1.), (0., -2.))],
    ],
)
def test_rotate_linestring(
    coordinates, angle, expected_coordinates
):
    geom = LineString(coordinates)
    rotated_geom = geom.rotate(angle)
    assert all(
        all(
            is_close(rc, ec)
            for rc, ec in zip(rpt, ept)
        )
        for rpt, ept in zip(rotated_geom.to_coordinates(), expected_coordinates)
    )


@pytest.mark.parametrize(
    "ring, angle, expected_coordinates",
    [
        [
            ((0., 0.), (1., 0.), (1., 1.), (0., 1.)),
            math.pi / 2,
            [((0., 0.), (0., 1.), (-1., 1.), (-1., 0.), (0., 0.))],
        ],
        [
            ((0., 0.), (1., 0.), (1., 1.), (0., 1.)),
            3 * math.pi / 2,
            [((0., 0.), (0., -1.), (1., -1.), (1., 0.), (0., 0.))],
        ],
    ],
)
def test_rotate_polygon(
    ring, angle, expected_coordinates
):
    geom = Polygon(ring)
    rotated_geom = geom.rotate(angle)
    assert all(
        all(
            all(
                is_close(rc, ec)
                for rc, ec in zip(rpt, ept)
            )
            for rpt, ept in zip(rring, ering)
        )
        for rring, ering in zip(rotated_geom.to_coordinates(), expected_coordinates)
    )
