# SPDX-License-Identifier: LGPL-2.1-or-later
from __future__ import annotations

import os
import tempfile
from pathlib import Path
import numpy as np
import xarray as xr
from xarray.backends.api import to_netcdf as _to_netcdf

__all__ = ["read_netcdf", "write_netcdf"]

def read_netcdf(path: str | Path, *, chunks: Mapping[str, int] | None = None,
                engine: str | None = None, decode_cf: bool = True) -> xr.Dataset:
    return xr.open_dataset(Path(path), chunks=chunks, engine=engine, decode_cf=decode_cf)

def write_netcdf(ds: xr.Dataset, path: str | Path, *, overwrite: bool = False,
                 engine: str | None = None, encoding: dict[str, Any] | None = None,
                 mode: str = "w") -> Path:
    path = Path(path)
    if path.exists() and not overwrite and mode == "w":
        raise FileExistsError(f"{path} exists (set overwrite=True or use mode='a').")
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp"); os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        _to_netcdf(ds, tmp_path, mode=mode, engine=engine, encoding=encoding)
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            try: tmp_path.unlink()
            except OSError: pass
    return path