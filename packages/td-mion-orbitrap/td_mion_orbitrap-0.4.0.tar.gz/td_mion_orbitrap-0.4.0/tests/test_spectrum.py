import pytest

def test_peak_picking(toy_spec):
    from spectrum import extract_peaks
    peaks = extract_peaks(toy_spec)
    # Should pick the local maxima at mz=60 (50→60→70) and mz=80 (70→80→90)
    assert set(peaks['mz']) == {60, 80}
