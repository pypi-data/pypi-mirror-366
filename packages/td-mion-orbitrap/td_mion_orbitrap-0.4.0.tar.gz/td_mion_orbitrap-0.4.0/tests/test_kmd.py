import numpy as np
import pandas as pd
from td_mion_orbitrap.kmd import compute_kmd

def test_kmd_values():
    df = pd.DataFrame({'mz': [14.01565, 28.03130], 'int_blank_removed': [1,1]})
    # Using CH2 base: nominal 14, exact 14.01565 → first points
    out = compute_kmd(df, nominal_base=14.0, exact_base=14.01565)
    # For mz=14.01565: KM = 14, KD = 14 - 14 = 0
    assert np.isclose(out.loc[0,'KM'], 14.0)
    assert np.isclose(out.loc[0,'KD'], 0.0)
