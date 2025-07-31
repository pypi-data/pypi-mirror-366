"""
pygradations - A Python package for analyzing size distributions from mineral processing streams.

This package provides tools for:
- Loading gradation data from CSV and Excel files
- Interpolating gradation curves using various methods
- Plotting and analyzing size distributions
"""

from .core import (
    Gradation,
    load_gradation_from_csv,
    load_gradation_from_excel,
)
from .interpolation import (
    cubic_spline_fit,
    gaudin_schuhmann_fit,
    interpolate_to_sieves,
    plot_fitted_curve,
    rosin_rammler_fit,
    swebrec_curve_fit,
)
from .utils import (
    calculate_cumulative_percentages,
    calculate_curvature_coefficient,
    calculate_uniformity_coefficient,
    compare_gradations,
    create_standard_sieve_series,
    export_gradation_to_csv,
    export_gradation_to_excel,
    get_characteristic_sizes,
    validate_gradation_data,
)

__version__ = "0.1.1"

__all__ = [
    "Gradation",
    "load_gradation_from_csv",
    "load_gradation_from_excel",
    "gaudin_schuhmann_fit",
    "rosin_rammler_fit",
    "swebrec_curve_fit",
    "cubic_spline_fit",
    "plot_fitted_curve",
    "interpolate_to_sieves",
    "calculate_cumulative_percentages",
    "validate_gradation_data",
    "get_characteristic_sizes",
    "calculate_uniformity_coefficient",
    "calculate_curvature_coefficient",
    "create_standard_sieve_series",
    "compare_gradations",
    "export_gradation_to_csv",
    "export_gradation_to_excel",
]
