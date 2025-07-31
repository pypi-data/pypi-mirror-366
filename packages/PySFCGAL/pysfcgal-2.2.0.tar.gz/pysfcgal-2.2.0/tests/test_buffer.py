import icontract
import pytest

from pysfcgal.sfcgal import BufferType, LineString, Point


def test_buffer_3d_point():
    point = Point(0, 0, 0)
    radius = 10.
    segments = 16
    buffered_point = point.buffer_3d(radius, segments)
    assert buffered_point.has_z
    assert len(buffered_point) > 0
    assert buffered_point.geom_type == "PolyhedralSurface"


@pytest.mark.parametrize("radius, segments", [(0, 0), (0, 16), (10, 0)])
def test_buffer_3d_point_fail(radius, segments):
    with pytest.raises(icontract.ViolationError):
        point = Point(0, 0, 0)
        _ = point.buffer_3d(radius, segments)


def test_buffer_3d_linestring():
    linestring = LineString(
        (
            (-100, 0, 0),
            (40, -70, 0),
            (40, 50, 40),
            (-90, -60, 60),
            (0, 0, -100),
            (30, 0, 150),
        )
    )
    radius = 10.
    segments = 16
    for buffer_type in BufferType:
        buffered_ls = linestring.buffer_3d(radius, segments, buffer_type)
        assert buffered_ls.has_z
        assert len(buffered_ls) > 0
        assert buffered_ls.geom_type == "PolyhedralSurface"


@pytest.mark.parametrize(
    "radius, segments, buffer_type",
    [
        (0, 16, 0),  # radius > 0
        (10, 1, 0),  # segments > 2
        (10, 16, 4),  # buffer_type should be between 0 and 2
        (0, 0, 4),  # radius, segments and buffer_type are wrong
        (0, 0, 0),  # radius and segments are wrong
        (0, 16, 4),  # radius and buffer_type are wrong
        (10, 0, 4),  # segments and buffer_type are wrong
    ]
)
def test_buffer_3d_linestring_fail(radius, segments, buffer_type):
    with pytest.raises(icontract.ViolationError):
        linestring = LineString(((0, 0), (1, 1)))
        _ = linestring.buffer_3d(radius, segments, buffer_type)
