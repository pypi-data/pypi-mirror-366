import pandas as pd
from td_mion_orbitrap.thermo import extract_thermogram


def normalize_to_charger(
    sample_df: pd.DataFrame,
    run,
    charger_mzs: list[float],
    tol_ppm: float = 5.0
) -> pd.DataFrame:
    """
    Normalize a sample thermogram by summing the average intensities of specified charger ions.

    Parameters
    ----------
    sample_df : pd.DataFrame
        DataFrame with columns ['RT', 'intensity'] for the analyte.
    run : pymzml.run.Reader
        Indexed pymzML run object used to extract charger ion(s).
    charger_mzs : list of float
        List of m/z values for one or more charger ions.
    tol_ppm : float, optional
        Mass tolerance in ppm for charger extraction (default: 5.0 ppm).

    Returns
    -------
    pd.DataFrame
        The input DataFrame with a new column 'int_norm' containing
        intensity normalized by the sum of mean intensities of all specified charger ions.
    """
    # Compute mean intensity for each charger ion
    means = []
    for mz in charger_mzs:
        charger_df = extract_thermogram(run, mz, tol_ppm)
        means.append(charger_df['intensity'].mean())

    # Sum of mean intensities across all chargers
    total_mean = sum(means)

    # Normalize sample intensities by the total charger signal
    out_df = sample_df.copy()
    out_df['int_norm'] = out_df['intensity'] / total_mean
    return out_df

# Alias for backward compatibility
normalize_to_chargers = normalize_to_charger
