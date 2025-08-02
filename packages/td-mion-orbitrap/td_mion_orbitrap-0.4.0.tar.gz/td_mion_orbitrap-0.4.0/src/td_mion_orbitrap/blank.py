import pandas as pd
from td_mion_orbitrap.thermo import extract_thermogram


def extract_combined_thermogram(
    specs,
    mz_list: list[float],
    tol_ppm: float
) -> pd.DataFrame:
    """
    Sum thermograms across multiple m/z channels for given spectra.

    Parameters
    ----------
    specs : list of pymzml.spec.Spectrum
        Pre-loaded spectrum objects.
    mz_list : list of float
        List of m/z channels to combine.
    tol_ppm : float
        Mass tolerance in ppm.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ['RT', 'intensity'], where 'intensity'
        is the sum across all specified m/z channels.
    """
    combined = None
    for mz in mz_list:
        df = extract_thermogram(specs, mz, tol_ppm)
        if combined is None:
            combined = df.rename(columns={'intensity': 'intensity'})
        else:
            combined['intensity'] += df['intensity']
    return combined


def subtract_blank(
    sample_df: pd.DataFrame,
    blank_df: pd.DataFrame,
    on: str = 'RT'
) -> pd.DataFrame:
    """
    Subtract blank intensities from a sample thermogram (after both are normalized).

    Parameters
    ----------
    sample_df : pd.DataFrame
        DataFrame with ['RT','int_norm'] for the sample.
    blank_df : pd.DataFrame
        DataFrame with ['RT','int_norm'] for the blank.
    on : str, optional
        Column name to align on (default: 'RT').

    Returns
    -------
    pd.DataFrame
        Merged DataFrame with an additional column 'int_blank_corr' = sample_int_norm - blank_int_norm.
    """
    # Sort and align on retention time
    sample_sorted = sample_df.sort_values(on).reset_index(drop=True)
    blank_sorted  = blank_df.sort_values(on).reset_index(drop=True)

    merged = pd.merge_asof(
        sample_sorted,
        blank_sorted,
        on=on,
        suffixes=('', '_blank'),
        direction='nearest'
    )
    # Corrected normalized intensity
    merged['int_blank_corr'] = merged['int_norm'] - merged['int_norm_blank']
    return merged


def normalize_thermogram(
    df: pd.DataFrame,
    specs,
    charger_mzs: list[float],
    tol_ppm: float
) -> pd.DataFrame:
    """
    Normalize any thermogram DataFrame by its own charger-ion signals.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with ['RT','intensity'] or ['RT','intensity_raw'].
    specs : list of spectra
        Pre-loaded spectra for extracting charger thermograms.
    charger_mzs : list of float
        m/z values of charger ions.
    tol_ppm : float
        Mass tolerance in ppm.

    Returns
    -------
    pd.DataFrame
        Input DataFrame with additional column 'int_norm' = intensity / total_charger_mean.
    """
    # Compute mean intensity per charger ion
    means = []
    for mz in charger_mzs:
        ch_df = extract_combined_thermogram(specs, [mz], tol_ppm)
        means.append(ch_df['intensity'].mean())
    total_mean = sum(means)
    out = df.copy()
    # Determine which intensity column to use
    col = 'intensity' if 'intensity' in out.columns else 'intensity_raw'
    out['int_norm'] = out[col] / total_mean
    return out