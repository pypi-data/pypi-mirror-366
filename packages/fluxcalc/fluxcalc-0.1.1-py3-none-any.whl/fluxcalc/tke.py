# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["calculate_tke_ti"]

def calculate_tke_ti(df, window_size, u='U_m_s', v='V_m_s', w='W_m_s'):
    """
    Calculate Turbulent Kinetic Energy (TKE) in rolling windows.
    Args:
        df (pd.DataFrame): DataFrame with columns 'U_m_s', 'V_m_s', 'W_m_s'.
        window_size (int): Number of samples per window.
    Returns:
        tke_list (list): List of TKE values for each window.
        time_midpoints (list): List of timestamps at the midpoint of each window.
        ti_list (list): List of Turbulence Intensity (TI) values for each window.
    """
    tke_list = []
    ti_list = []
    time_midpoints = []
    for i in range(0, len(df), window_size):
        window = df.iloc[i:i+window_size]
        if len(window) < window_size:
            continue
        u_prime = window[u] - window[u].mean()
        v_prime = window[v] - window[v].mean()
        w_prime = window[w] - window[w].mean()
        tke = 0.5 * (np.var(u_prime, ddof=1) +
                     np.var(v_prime, ddof=1) +
                     np.var(w_prime, ddof=1))
        tke_list.append(tke)
        time_midpoints.append(window.index[[-1]])
        ti = np.sqrt(2*tke) / np.sqrt(window[u].mean()**2 + window[v].mean()**2 + window[w].mean()**2)
        ti_list.append(ti)

    return tke_list, time_midpoints, ti_list