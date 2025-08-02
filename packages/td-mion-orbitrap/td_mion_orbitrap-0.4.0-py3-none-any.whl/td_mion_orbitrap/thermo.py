import numpy as np
import pandas as pd
import pymzml

def load_and_index(mzml_path: str) -> list[tuple[float, np.ndarray, np.ndarray]]:
    """
    Load an indexed mzML or mzML.gz file and return list of (RT, m/z array, intensity array).
    """
    run = pymzml.run.Reader(mzml_path)
    specs = []
    for spec in run:
        rt   = spec.scan_time_in_minutes()
        mzs  = np.array(spec.mz, dtype=float)
        vals = np.array(spec.i, dtype=float)
        specs.append((rt, mzs, vals))
    return specs


def extract_thermogram(
    specs: list[tuple[float, np.ndarray, np.ndarray]],
    target_mz: float,
    tol_ppm: float = 5.0
) -> pd.DataFrame:
    """
    Extract a thermogram for a specific m/z from pre-loaded scan tuples.

    Parameters
    ----------
    specs : list of (RT, mz_array, intensity_array)
    target_mz : float
    tol_ppm : float

    Returns
    -------
    DataFrame with ['RT','intensity']
    """
    # Convert tolerance to absolute m/z delta
    delta = tol_ppm * 1e-6

    rts = []
    ints = []

    for rt, mz_arr, val_arr in specs:
        # Ensure arrays
        mzs = np.asarray(mz_arr, dtype=float)
        vals = np.asarray(val_arr, dtype=float)

        # Mask peaks within delta of target m/z
        mask = np.abs(mzs - target_mz) <= delta

        rts.append(rt)
        ints.append(vals[mask].sum())

    return pd.DataFrame({'RT': rts, 'intensity': ints})
