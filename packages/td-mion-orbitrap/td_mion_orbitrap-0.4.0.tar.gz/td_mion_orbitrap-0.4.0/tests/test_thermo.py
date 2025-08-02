import pandas as pd
from td_mion_orbitrap.thermo import extract_thermogram

def test_extract_thermogram_monotonic():
    # Build a fake specs list: two scans with known mzs and intensities
    specs = [
        (0.0, [100,200,300], [1,2,3]),
        (1.0, [100,200,300], [4,5,6])
    ]
    df = extract_thermogram(specs, target_mz=200, tol_ppm=1e6)
    assert list(df['RT']) == [0.0, 1.0]
    assert list(df['intensity']) == [2,5]
