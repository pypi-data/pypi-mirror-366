# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["sigma_spike_removal"]

def sigma_spike_removal(series, window=100, threshold=3):
    series = series.apply(pd.to_numeric, errors='coerce')  # Ensure numeric type
    rolling_mean = series.rolling(window, center=True).mean()
    rolling_std = series.rolling(window, center=True).std()
    mask = np.abs(series - rolling_mean) > threshold * rolling_std
    cleaned = series.copy()
    cleaned[mask] = np.nan
    return cleaned