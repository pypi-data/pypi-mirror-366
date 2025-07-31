# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["calculate_momentum_flux"]

def calculate_momentum_flux(df, u_col='U_m_s', v_col='V_m_s', w_col='W_m_s', rho=1.2, freq='30T'):
    """
    Compute tau (momentum flux) over specified windows.
    
    
    Args:
        df: DataFrame with datetime index and u, v, w columns.
        u_col, v_col, w_col: column names.
        rho: air density (kg/m³).
        freq: window size ('30T' for 30 min).
    
    Returns:
        Series of tau (N/m²) indexed by window.
    """
    df = df[[u_col, v_col, w_col]].dropna()

    def compute_tau_window(g):
        u_prime = g[u_col] - g[u_col].mean()
        v_prime = g[v_col] - g[v_col].mean()
        w_prime = g[w_col] - g[w_col].mean()

        uw_cov = (u_prime * w_prime).mean()
        vw_cov = (v_prime * w_prime).mean()

        tau = rho * np.sqrt(uw_cov**2 + vw_cov**2)
        return tau

    tau_series = df.groupby(pd.Grouper(freq=freq)).apply(compute_tau_window)
    tau_series.name = 'tau_N_per_m2'
    return tau_series