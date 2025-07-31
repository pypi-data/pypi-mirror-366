# SPDX-License-Identifier: LGPL-2.1-or-later
# Copyright (c) 2025 Julie Piot
"""
Public API for fluxcalc.
"""

from __future__ import annotations

# Try to expose the installed version
try:
    from importlib.metadata import version as _version, PackageNotFoundError
    try:
        __version__ = _version("fluxcalc")
    except PackageNotFoundError:  # pragma: no cover
        __version__ = "0.1.1"
except Exception:  # pragma: no cover
    __version__ = "0.1.1"

from .io import read_file
from .tau import calculate_momentum_flux
from .tke import calculate_tke_ti
from .heat import calculate_sensible_heat_flux

__all__ = [
    "read_file",
    "calculate_momentum_flux",
    "calculate_tke_ti",
    "calculate_sensible_heat_flux",
    "__version__",
]