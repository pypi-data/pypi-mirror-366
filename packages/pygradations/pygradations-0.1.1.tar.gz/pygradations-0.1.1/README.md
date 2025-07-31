# pygradations

A Python package for analyzing and manipulating size distributions (gradations) from mineral processing streams.

## Overview

Gradations are size distributions typically represented as dataframes with the following columns:
- `sieve`: sieve aperture in mm
- `p`: weight % retained in each sieve
- `wr`: cumulative % retained (cumsum of p)
- `wp`: % passing through each sieve (100 - wr)

## Features

- **Data Loading**: Import gradation data from CSV and Excel files
- **Curve Fitting**: Fit various distribution models to gradation data:
  - Gaudin-Schuhmann distribution
  - Rosin-Rammler distribution
  - Cubic spline interpolation
- **Visualization**: Plot gradation curves with fitted distributions
- **Analysis**: Calculate characteristic sizes (D10, D30, D50, D60, D90) and coefficients
- **Interpolation**: Interpolate gradation data to standard sieve sizes
- **Comparison**: Compare multiple gradations on the same scale

## Installation

```bash
pip install pygradations
```

## Quick Start

### Loading Data

```python
import pygradations as pg

# Load from CSV file
gradation = pg.load_gradation_from_csv("sample_data.csv", name="Sample 1")

# Load from Excel file
gradation = pg.load_gradation_from_excel("sample_data.xlsx", sheet_name="Sheet1", name="Sample 2")
```

### Basic Usage

```python
import pygradations as pg
import pandas as pd

# Example gradation data
data = pd.DataFrame({
    'sieve': [63.50, 50.80, 38.10, 31.75, 25.40, 19.05, 12.70, 9.53, 6.73, 4.76],
    'p': [0.0, 3.65, 29.37, 18.26, 14.74, 9.86, 9.22, 3.59, 3.11, 1.87],
    'wr': [0.0, 3.65, 33.02, 51.28, 66.02, 75.88, 85.1, 88.69, 91.8, 93.67],
    'wp': [100.0, 96.35, 66.98, 48.72, 33.98, 24.12, 14.9, 11.31, 8.2, 6.33]
})

# Create Gradation object
grad = pg.Gradation(data, name="Example Gradation")

# Get basic information
print(grad)
print(f"Number of sieves: {len(grad.data)}")
print(f"Sieve sizes: {grad.get_sieve_sizes()}")
```

### Curve Fitting

```python
import matplotlib.pyplot as plt

# Get data for fitting
sieve_sizes = grad.get_sieve_sizes()
passing_percentages = grad.get_passing_percentages()

# Fit different models
k, m, r_sq_gs = pg.gaudin_schuhmann_fit(sieve_sizes, passing_percentages)
x_63, n, r_sq_rr = pg.rosin_rammler_fit(sieve_sizes, passing_percentages)

print(f"Gaudin-Schuhmann: k={k:.2f}, m={m:.2f}, R²={r_sq_gs:.3f}")
print(f"Rosin-Rammler: x₆₃={x_63:.2f}, n={n:.2f}, R²={r_sq_rr:.3f}")

# Plot fitted curves
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

pg.plot_fitted_curve(sieve_sizes, passing_percentages, 'gaudin_schuhmann', ax=axes[0])
pg.plot_fitted_curve(sieve_sizes, passing_percentages, 'rosin_rammler', ax=axes[1])
pg.plot_fitted_curve(sieve_sizes, passing_percentages, 'cubic_spline', ax=axes[2])

plt.tight_layout()
plt.show()
```

### Analysis

```python
# Calculate characteristic sizes
char_sizes = pg.get_characteristic_sizes(grad.data)
print("Characteristic sizes:")
for size_name, size_value in char_sizes.items():
    print(f"  {size_name}: {size_value:.2f} mm")

# Calculate coefficients
uniformity = pg.calculate_uniformity_coefficient(grad.data)
curvature = pg.calculate_curvature_coefficient(grad.data)
print(f"Uniformity coefficient: {uniformity:.2f}")
print(f"Curvature coefficient: {curvature:.2f}")
```

### Interpolation

```python
# Interpolate to standard sieve sizes
standard_sieves = pg.create_standard_sieve_series()
interpolated = pg.interpolate_to_sieves(grad.data, standard_sieves, method='cubic_spline')

print("Interpolated data:")
print(interpolated.head())
```

### Multiple Gradations

```python
# Create a dictionary of gradations
gradations = {
    "Sample 1": grad.data,
    "Sample 2": another_grad.data,
    "Sample 3": third_grad.data
}

# Compare gradations
comparison = pg.compare_gradations(gradations)
print(comparison.head())

# Export results
pg.export_gradation_to_csv(comparison, "comparison_results.csv")
```

## API Reference

### Core Classes

#### `Gradation(data, name)`
Main class for representing gradation data.

**Methods:**
- `get_sieve_sizes()`: Return sieve sizes as numpy array
- `get_passing_percentages()`: Return passing percentages as numpy array
- `get_retained_percentages()`: Return retained percentages as numpy array
- `get_cumulative_retained()`: Return cumulative retained percentages as numpy array

### Data Loading

#### `load_gradation_from_csv(filepath, name=None)`
Load gradation data from CSV file.

#### `load_gradation_from_excel(filepath, sheet_name=0, name=None)`
Load gradation data from Excel file.

### Curve Fitting

#### `gaudin_schuhmann_fit(sieve_sizes, passing_percentages)`
Fit Gaudin-Schuhmann distribution. Returns (k, m, r_squared).

#### `rosin_rammler_fit(sieve_sizes, passing_percentages)`
Fit Rosin-Rammler distribution. Returns (x_63, n, r_squared).

#### `cubic_spline_fit(sieve_sizes, passing_percentages)`
Fit cubic spline. Returns CubicSpline object.

#### `plot_fitted_curve(sieve_sizes, passing_percentages, fit_type, ax=None)`
Plot original data and fitted curve.

### Analysis

#### `get_characteristic_sizes(data)`
Calculate D10, D30, D50, D60, D90 characteristic sizes.

#### `calculate_uniformity_coefficient(data)`
Calculate uniformity coefficient (D60/D10).

#### `calculate_curvature_coefficient(data)`
Calculate curvature coefficient (D30²/(D10*D60)).

### Utilities

#### `calculate_cumulative_percentages(data)`
Calculate wr and wp from individual retained percentages.

#### `validate_gradation_data(data)`
Validate gradation data format and consistency.

#### `create_standard_sieve_series()`
Get standard sieve sizes for interpolation.

#### `compare_gradations(gradations, target_sieves=None)`
Compare multiple gradations by interpolating to same sieve sizes.

## Data Format

The package expects gradation data in the following format:

| sieve (mm) | p (%) | wr (%) | wp (%) |
| ---------- | ----- | ------ | ------ |
| 63.50      | 0.0   | 0.0    | 100.0  |
| 50.80      | 3.65  | 3.65   | 96.35  |
| 38.10      | 29.37 | 33.02  | 66.98  |
| ...        | ...   | ...    | ...    |

Where:
- `sieve`: Sieve aperture in mm
- `p`: Weight % retained in each sieve
- `wr`: Cumulative % retained (cumsum of p)
- `wp`: % passing through each sieve (100 - wr)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
