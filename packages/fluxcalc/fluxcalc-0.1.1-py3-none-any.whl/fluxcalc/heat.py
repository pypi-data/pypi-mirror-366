# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["calculate_sensible_heat_flux"]

def calculate_sensible_heat_flux(df, freq, var_col = 'T_C', wind_col='W_m_s', rho = 1.2, cp= 1005):
    """"
    Compute sensible heat flux (covariance between temperature and vertical wind) over fixed time windows.
    
    Args:
        df: pd.DataFrame with datetime index
        var_col: name of scalar variable (e.g., T_C)
        wind_col: name of vertical wind column (e.g., W_m_s)
        freq: window size (e.g., '30T' for 30 minutes)
    
    Returns:
        pd.Series: time-indexed flux values
    """
    df = df[[var_col, wind_col]].dropna()

    # Group by 30-minute intervals using the datetime index
    fluxes = df.groupby(pd.Grouper(freq=freq)).apply(
        lambda g: np.mean((g[var_col] - g[var_col].mean()) *
                          (g[wind_col] - g[wind_col].mean()))
    )

    fluxes.name = f"{var_col}_flux"
    return fluxes * rho * cp  # Convert to flux units (e.g., W/m²)