import pytest

from pysfcgal import sfcgal


@pytest.mark.parametrize(
    "geom_type, geom_cls",
    [
        (geom_type, sfcgal.geom_type_to_cls[sfcgal_geom])
        for geom_type, sfcgal_geom in sfcgal.geom_types.items()
    ]
)
def test_geometry_empty(geom_type, geom_cls):
    """For every geometry class in PySFCGAL, building an instance with a default
    pararametrization should produce an empty geometry.

    """
    geom = geom_cls()
    assert geom.to_wkt() == f"{geom_type} EMPTY".upper()
