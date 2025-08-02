import pandas as pd
from td_mion_orbitrap.blank import subtract_blank

def test_subtract_blank_simple():
    sample = pd.DataFrame({'RT': [0,1,2], 'int_norm': [5,10,15]})
    blank  = pd.DataFrame({'RT': [0,1,2], 'int_norm': [1,2,3]})
    out = subtract_blank(sample, blank, on='RT')
    assert list(out['int_blank_corr']) == [4,8,12]
