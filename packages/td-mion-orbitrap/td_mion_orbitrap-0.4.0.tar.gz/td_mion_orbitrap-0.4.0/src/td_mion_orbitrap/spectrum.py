import pandas as pd
import numpy as np
import pymzml

def extract_raw_spectrum(
    specs: list[tuple[float, np.ndarray, np.ndarray]],
    scan_index: int = 0
) -> pd.DataFrame:
    """
    Extract the raw mass spectrum (m/z and intensity) from a specified scan.

    Parameters
    ----------
    specs : list of tuples
        Each tuple is (RT, mz_array, intensity_array).
    scan_index : int, optional
        Index of the scan to extract (default: 0).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ['mz', 'intensity'] for the selected scan.
    """
    # Unpack the tuple for the desired scan
    rt, mzs, vals = specs[scan_index]
    df = pd.DataFrame({
        'mz': np.array(mzs),
        'intensity': np.array(vals)
    })
    return df


def remove_blank_spectrum(
    sample_spec: pd.DataFrame,
    blank_spec: pd.DataFrame,
    tol_ppm: float = 50.0
) -> pd.DataFrame:
    """
    Subtract the blank spectrum from the sample spectrum by aligning m/z values.
    """
    samp = sample_spec.sort_values('mz').reset_index(drop=True)
    blnk = blank_spec.sort_values('mz').reset_index(drop=True)

    blnk = blnk.rename(columns={'mz': 'mz_blank', 'intensity': 'intensity_blank'})

    merged = pd.merge_asof(
        samp,
        blnk,
        left_on='mz',
        right_on='mz_blank',
        direction='nearest'
    )
    tol = tol_ppm * merged['mz'] * 1e-6
    mask = merged['mz_blank'].notna() & (abs(merged['mz'] - merged['mz_blank']) <= tol)
    if "intensity_blank" not in merged:
    # No matches found – create column of zeros
        merged["intensity_blank"] = 0.0
    merged['intensity_blank'] = merged['intensity_blank'].where(mask, 0)

    merged['int_blank_removed'] = merged['intensity'] - merged['intensity_blank']
    return merged[['mz', 'intensity', 'int_blank_removed']]


def extract_peaks(
    spec_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Identify peaks in a blank-removed mass spectrum by finding local maxima.
    """
    df = spec_df.sort_values('mz').reset_index(drop=True)
    intens = df["int_blank_removed" if "int_blank_removed" in df.columns else "intensity"].values
    peaks = np.zeros_like(intens, dtype=bool)
    peaks[1:-1] = (intens[1:-1] > intens[:-2]) & (intens[1:-1] > intens[2:])
    return df.loc[peaks].reset_index(drop=True)


def extract_combined_spectrum(
    specs: list[tuple[float, np.ndarray, np.ndarray]],
    scan_indices: list[int] | None = None,
) -> pd.DataFrame:
    """
    Average the full profile spectrum across a set of scans.

    Parameters
    ----------
    specs : list of tuples
        Each tuple is (RT, mz_array, intensity_array).
    scan_indices : list of int, optional
        Indices of scans to average (default: all).

    Returns
    -------
    pd.DataFrame
        DataFrame with ['mz', 'int_blank_removed'], where intensity is the mean across scans.
    """
    if scan_indices is None:
        scan_indices = list(range(len(specs)))
        
    frames: list[pd.DataFrame] = []
    for idx in scan_indices:
        _rt, mzs, vals = specs[idx]
        frames.append(pd.DataFrame({"mz": np.asarray(mzs), "intensity": np.asarray(vals)}))

    return (
        pd.concat(frames, ignore_index=True)
        .groupby("mz", as_index=False)["intensity"]
        .mean()
    )

    """
    dfs = []
    for idx in scan_indices:
        rt, mzs, vals = specs[idx]
        df = pd.DataFrame({'mz': np.array(mzs), 'int_blank_removed': np.array(vals)})
        dfs.append(df)
    all_df = pd.concat(dfs, ignore_index=True)
    avg_df = all_df.groupby('mz', as_index=False)['int_blank_removed'].mean()
    return avg_df
    """