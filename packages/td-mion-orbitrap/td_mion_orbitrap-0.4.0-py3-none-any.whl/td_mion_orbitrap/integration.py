import numpy as np
import pandas as pd

def integrate_thermogram(
    df: pd.DataFrame,
    rt_start: float = None,
    rt_end: float = None,
    intensity_col: str = 'int_blank_corr'
) -> float:
    """
    Integrate a thermogram signal over a specified RT range using the trapezoidal rule.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns ['RT', intensity_col].
    rt_start : float, optional
        Start retention time (inclusive). If None, uses min RT.
    rt_end : float, optional
        End retention time (inclusive). If None, uses max RT.
    intensity_col : str, default 'int_blank_corr'
        Column in df containing the intensity to integrate.

    Returns
    -------
    float
        Total integrated signal (area under the curve).
    """
    # Copy and filter RT window
    data = df.copy()
    if rt_start is not None:
        data = data[data['RT'] >= rt_start]
    if rt_end is not None:
        data = data[data['RT'] <= rt_end]
    # Sort by RT
    data = data.sort_values('RT')
    x = data['RT'].values
    y = data[intensity_col].values
    # If no data points, return 0
    if len(x) < 2:
        return 0.0
    # Trapezoidal integration
    return float(np.trapezoid(y, x))
