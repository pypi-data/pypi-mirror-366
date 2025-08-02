import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def kendrick_transform(
    mz: np.ndarray,
    nominal_base: float,
    exact_base: float
) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert m/z values to Kendrick mass and defect.
    """
    k_mass = mz * (nominal_base / exact_base)
    k_nominal = np.floor(k_mass)
    k_defect = k_nominal - k_mass
    return k_mass, k_defect


def compute_kmd(
    spec_df: pd.DataFrame,
    intensity_col: str = 'int_blank_removed',
    nominal_base: float = 97.00,
    exact_base: float = 96.9603
) -> pd.DataFrame:
    """
    Compute Kendrick Mass Defect for a given spectrum DataFrame.

    Returns DataFrame with columns ['KM', 'KD', 'intensity'].
    """
    mzs = spec_df['mz'].to_numpy()
    ints = spec_df[intensity_col].to_numpy()
    km, kd = kendrick_transform(mzs, nominal_base, exact_base)
    return pd.DataFrame({'KM': km, 'KD': kd, 'intensity': ints})


def plot_kmd(kmd_df, size_scale=150.0, output_file=None):
    # Only keep valid, positive intensities
    df = kmd_df.dropna(subset=['intensity'])
    df = df[df['intensity'] > 0]
    if df.empty:
        return   # nothing to plot

    sizes = (df['intensity'] / df['intensity'].max()) * size_scale
    plt.figure()
    plt.scatter(df['KM'], df['KD'], s=sizes)
    plt.xlabel('Kendrick Mass')
    plt.ylabel('Kendrick Defect')
    plt.title('Kendrick Mass Defect Plot')
    plt.tight_layout()
    if output_file:
        plt.savefig(output_file, dpi=300)
    plt.close()   # don’t call plt.show() in scripts


def average_spectrum(
    specs: list,
    scan_indices: list[int] = None
) -> pd.DataFrame:
    """
    Average the full profile spectrum across a set of scans.

    Parameters
    ----------
    specs : list of pymzml.spec.Spectrum
        Pre-loaded spectrum objects.
    scan_indices : list of int, optional
        Indices of scans to average (default: all).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ['mz', 'int_blank_removed'],
        where intensity is the mean across scans.
    """
    # Select scans
    if scan_indices is None:
        scan_indices = list(range(len(specs)))
    # Build DataFrame per scan
    dfs = []
    for idx in scan_indices:
        spec = specs[idx]
        df = pd.DataFrame({'mz': np.array(spec.mz), 'int_blank_removed': np.array(spec.i)})
        dfs.append(df)
    # Concatenate and average by mz
    all_df = pd.concat(dfs, ignore_index=True)
    avg_df = all_df.groupby('mz', as_index=False)['int_blank_removed'].mean()
    return avg_df


def filter_peak_list(
    spec_df: pd.DataFrame,
    peak_list: list[float],
    tol_ppm: float = 50.0
) -> pd.DataFrame:
    """
    Filter a spectrum DataFrame to only include m/z values from an external peak list.

    Parameters
    ----------
    spec_df : pd.DataFrame
        DataFrame with ['mz', ...].
    peak_list : list of float
        m/z values to keep.
    tol_ppm : float, optional
        Tolerance in ppm for matching peaks.

    Returns
    -------
    pd.DataFrame
        Subset of spec_df matching the peak_list within tolerance.
    """
    mask = pd.Series(False, index=spec_df.index)
    for p in peak_list:
        ppm_tol = p * tol_ppm * 1e-6
        mask |= spec_df['mz'].between(p - ppm_tol, p + ppm_tol)
    return spec_df.loc[mask].reset_index(drop=True)
