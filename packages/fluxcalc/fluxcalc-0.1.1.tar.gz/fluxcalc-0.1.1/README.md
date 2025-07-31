# flux_calculations

[![PyPI version](https://img.shields.io/pypi/v/fluxcalc)](https://pypi.org/project/fluxcalc)
[![License](https://img.shields.io/pypi/l/fluxcalc)](LICENSE)

Flexible flux and turbulence calculations from NetCDF files: sensible heat flux, momentum flux, and turbulent kinetic energy.

---

## Features

* **NetCDF File Aggregation**: Combines multiple NetCDF files into a single data frame for each sensor, simplifying data management.
* **Outlier Removal**: Automatically detects and removes outliers beyond 3 standard deviations within a rolling 100-observation window.
* **Advanced Plotting**:
  - Visualize 3-dimensional wind data for comprehensive analysis.
  - Generate FFT (Fast Fourier Transform) plots for frequency domain insights.
* **Flexible Flux Calculations**:
  - Compute **Sensible Heat Flux**, **Momentum Flux**, or **Turbulent Kinetic Energy (TKE)** using a customizable time window (user-defined in minutes).
  - Plot calculated fluxes for easy interpretation and visualization.
* **User-Friendly Design**: Offers intuitive options for data processing, plotting, and analysis, ensuring flexibility and ease of use.

## Installation

```bash
pip install fluxcalc
```

To install the latest version from GitHub:

```bash
pip install git+https://github.com/jpiot1/flux_calculations.git
```

‼️‼️‼️ For development (editable) install with tests: ‼️‼️‼️

```bash
git clone https://github.com/jpiot1/flux_calculations.git
cd flux_calculations
env=".venv"
python -m venv "$env"
source "$env/bin/activate"
pip install -e '.[dev]'
pytest -q
```

## ‼️‼️‼️ Python API ‼️‼️‼️

```python
import xarray as xr
import fluxcalc as fc

# 1. Open dataset
 ds = xr.open_dataset("input.nc").sortby("time")

# 2. Compute wavelet transforms
 row_wt, col_wt, remnant = cf.get_wavelets(ds.copy(), ds.range.values, ds.time.values)

# 3. Detect clouds & precip
 clouds, precip = cf.get_clouds_and_precip(
     ds.beta_att.T.values, ds.range.values, ds.time.values
 )

# 4. Flags and threshold
 fog, cloud, rain, clear = cf.get_flags(
     ds.beta_att.T.values, ds.range.values, ds.time.values
 )
 thresh = cf.get_thresh(remnant, row_wt, col_wt)

# 5. Denoise & extract layers
 clean = cf.remove_noisy_regions(
     ds.beta_att.T.values, thresh, ds.range.values, ds.time.values
 )
 layers = cf.get_layers(clean.values, clean.range.values)

# 6. Write results
 cf.create_file(
     ds, row_wt, col_wt, remnant,
     clouds, precip, fog, rain, cloud, clear,
     clean, layers, ds.overlap_function,
     output_path="output.nc",
     overwrite=True
 )
```

## Contributing

1. Fork the repo and create a feature branch.
2. Write code, tests, and update docs.
3. Follow style: `ruff`, `mypy`, `pytest`.
4. Submit a pull request.

## License

This project is licensed under the GNU Lesser General Public License v2.1 or later. See [LICENSE](LICENSE) for details.
