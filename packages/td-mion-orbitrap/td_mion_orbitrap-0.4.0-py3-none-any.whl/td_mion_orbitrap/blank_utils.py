import pandas as pd
import numpy as np
from td_mion_orbitrap.blank import extract_combined_thermogram

def average_blank_thermogram(
    blank_specs_list: list,
    mz_list: list[float],
    tol_ppm: float
) -> pd.DataFrame:
    """
    Return the average combined-thermogram across multiple blank runs.

    Parameters
    ----------
    blank_specs_list : list of specs (each a list of Spectrum)
    mz_list          : list of float
        The m/z channels to combine (same as in extract_combined_thermogram).
    tol_ppm          : float
        Tolerance in ppm.

    Returns
    -------
    avg_df : pd.DataFrame
        Columns ['RT', 'intensity'], where each intensity is the mean
        across all blank runs at that RT.
    """
    # 1) get one combined DataFrame per blank
    dfs = [
        extract_combined_thermogram(specs, mz_list, tol_ppm)
        for specs in blank_specs_list
    ]

    # 2) build a master RT axis
    all_rts = sorted({rt for df in dfs for rt in df['RT']})

    # 3) for each blank_df, align to all_rts by nearest RT
    aligned = []
    for df in dfs:
        tmp = pd.merge_asof(
            pd.DataFrame({'RT': all_rts}),
            df,
            on='RT',
            direction='nearest'
        )
        # fill missing
        tmp['intensity'] = tmp['intensity'].fillna(0)
        aligned.append(tmp['intensity'].values)

    # 4) compute mean intensity at each RT
    stacked = np.vstack(aligned)  # shape = (n_blanks, n_rts)
    mean_int = stacked.mean(axis=0)

    avg_df = pd.DataFrame({'RT': all_rts, 'intensity': mean_int})
    return avg_df
