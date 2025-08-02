import pytest
from td_mion_orbitrap.integration import integrate_thermogram

def test_triangle_area(triangle_df):
    # area = 1/2 * base(2) * height(1) = 1
    assert pytest.approx(integrate_thermogram(triangle_df)) == 1.0
