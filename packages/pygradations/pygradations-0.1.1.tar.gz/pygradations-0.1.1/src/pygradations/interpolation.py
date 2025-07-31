"""
Interpolation and curve fitting methods for gradation analysis.

This module provides various methods to fit curves to gradation data:
- Gaudin-Schuhmann distribution
- Rosin-Rammler distribution
- Swebrec distribution
- Cubic spline interpolation
"""

from typing import (
    Optional,
    Tuple,
)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.optimize import curve_fit


def gaudin_schuhmann_fit(sieve_sizes: np.ndarray, passing_percentages: np.ndarray) -> Tuple[float, float, float]:
    """
    Fit a Gaudin-Schuhmann distribution to the gradation data.

    The Gaudin-Schuhmann equation is: P(x) = 100 * (x/k)^m
    where P(x) is the percentage passing, x is the particle size,
    k is the characteristic size, and m is the distribution modulus.

    Args:
        sieve_sizes: Array of sieve sizes in mm
        passing_percentages: Array of passing percentages

    Returns:
        Tuple of (k, m, r_squared) where k is characteristic size,
        m is distribution modulus, and r_squared is goodness of fit
    """
    # Remove zero values and 100% passing values for fitting
    mask = (sieve_sizes > 0) & (passing_percentages > 0) & (passing_percentages < 100)
    x = sieve_sizes[mask]
    y = passing_percentages[mask]

    if len(x) < 2:
        raise ValueError("Insufficient data points for Gaudin-Schuhmann fitting")

    # Define the Gaudin-Schuhmann function
    def gaudin_schuhmann(x, k, m):
        return np.clip(100 * (x / k) ** m, 0, 100)

    # Initial guess for parameters
    k_guess = np.median(x)
    m_guess = 1.0

    try:
        # Fit the curve
        popt, _ = curve_fit(gaudin_schuhmann, x, y, p0=[k_guess, m_guess], bounds=([0.1, 0.1], [np.inf, 10]))
        k, m = popt

        # Calculate R-squared
        y_pred = gaudin_schuhmann(x, k, m)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        return k, m, r_squared

    except (RuntimeError, ValueError):
        # Return default values if fitting fails
        return k_guess, m_guess, 0.0


def rosin_rammler_fit(sieve_sizes: np.ndarray, passing_percentages: np.ndarray) -> Tuple[float, float, float]:
    """
    Fit a Rosin-Rammler distribution to the gradation data.

    The Rosin-Rammler equation is: R(x) = 100 * exp(-(x/x_63)^n)
    where R(x) is the cumulative % retained, x is the particle size,
    x_63 is the size at which 36.8% is retained (63.2% passes), and n is the uniformity coefficient.

    Args:
        sieve_sizes: Array of sieve sizes in mm
        passing_percentages: Array of passing percentages

    Returns:
        Tuple of (x_63, n, r_squared) where x_63 is characteristic size,
        n is uniformity coefficient, and r_squared is goodness of fit
    """
    # Remove zero values and 100% passing values for fitting
    mask = (sieve_sizes > 0) & (passing_percentages > 0) & (passing_percentages < 100)
    x = sieve_sizes[mask]
    y = passing_percentages[mask]

    if len(x) < 2:
        raise ValueError("Insufficient data points for Rosin-Rammler fitting")

    # Convert passing percentages to retained percentages for fitting
    y_retained = 100 - y

    # Define the Rosin-Rammler function for retained percentage
    def rosin_rammler_retained(x, x_63, n):
        return np.clip(100 * np.exp(-((x / x_63) ** n)), 0, 100)

    # Better initial guess for parameters
    # Find the sieve size where approximately 36.8% is retained (63.2% passes)
    idx_63 = np.argmin(np.abs(y_retained - 36.8))
    x_63_guess = x[idx_63] if idx_63 < len(x) else np.median(x)

    # Initial guess for n based on the slope of the curve
    n_guess = 1.0

    # Try to estimate n from the data
    if len(x) >= 3:
        # Use the middle portion of the data to estimate slope
        mid_idx = len(x) // 2
        if mid_idx > 0 and mid_idx < len(x) - 1:
            x1, x2 = x[mid_idx - 1], x[mid_idx + 1]
            y1, y2 = y_retained[mid_idx - 1], y_retained[mid_idx + 1]
            if y1 > 0 and y2 > 0 and x1 > 0 and x2 > 0:
                # Estimate n from the slope in log-log space
                log_slope = (np.log(y1) - np.log(y2)) / (np.log(x1) - np.log(x2))
                n_guess = max(0.1, min(5.0, abs(log_slope)))

    try:
        # Fit the curve with more appropriate bounds
        # x_63 should be positive and reasonable for the data range
        # n should typically be between 0.5 and 3 for most gradations
        x_63_min = x.min() * 0.1
        x_63_max = x.max() * 10
        n_min, n_max = 0.3, 5.0

        popt, _ = curve_fit(
            rosin_rammler_retained,
            x,
            y_retained,
            p0=[x_63_guess, n_guess],
            bounds=([x_63_min, n_min], [x_63_max, n_max]),
        )
        x_63, n = popt

        # Calculate R-squared using the original passing percentages
        # Convert fitted retained back to passing for comparison
        y_retained_pred = rosin_rammler_retained(x, x_63, n)
        y_pred = 100 - y_retained_pred

        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        return x_63, n, r_squared

    except (RuntimeError, ValueError):
        # If fitting fails, try with different initial conditions
        try:
            # Try with different initial guesses
            popt, _ = curve_fit(
                rosin_rammler_retained,
                x,
                y_retained,
                p0=[np.mean(x), 1.5],
                bounds=([x.min() * 0.1, 0.3], [x.max() * 5, 5.0]),
            )
            x_63, n = popt

            # Calculate R-squared
            y_retained_pred = rosin_rammler_retained(x, x_63, n)
            y_pred = 100 - y_retained_pred
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

            return x_63, n, r_squared

        except (RuntimeError, ValueError):
            # Return default values if all fitting attempts fail
            return x_63_guess, n_guess, 0.0


def swebrec_curve_fit(sieve_sizes: np.ndarray, passing_percentages: np.ndarray) -> Tuple[float, float, float, float]:
    """
    Fit a Swebrec distribution to the gradation data.

    The Swebrec equation is: P(x) = 100 / (1 + (ln(x_max/x) / ln(x_max/x_50))^b)
    where P(x) is the percentage passing, x is the particle size,
    x_max is the maximum particle size, x_50 is the median size,
    and b is the shape parameter.

    Args:
        sieve_sizes: Array of sieve sizes in mm
        passing_percentages: Array of passing percentages

    Returns:
        Tuple of (x_max, x_50, b, r_squared) where x_max is maximum size,
        x_50 is median size, b is shape parameter, and r_squared is goodness of fit
    """
    # Remove zero values and 100% passing values for fitting
    mask = (sieve_sizes > 0) & (passing_percentages > 0) & (passing_percentages < 100)
    x = sieve_sizes[mask]
    y = passing_percentages[mask]

    if len(x) < 3:
        raise ValueError("Insufficient data points for Swebrec fitting (minimum 3 required)")

    # Define the Swebrec function
    def swebrec(x, x_max, x_50, b):
        # Avoid division by zero and log of zero
        x_safe = np.maximum(x, 1e-10)
        x_max_safe = np.maximum(x_max, x_safe.max() * 1.1)
        x_50_safe = np.maximum(x_50, 1e-10)

        # Ensure x_50 is less than x_max
        x_50_safe = np.minimum(x_50_safe, x_max_safe * 0.99)

        log_ratio = np.log(x_max_safe / x_safe) / np.log(x_max_safe / x_50_safe)
        return np.clip(100 / (1 + log_ratio**b), 0, 100)

    # Initial guesses for parameters
    x_max_guess = x.max() * 1.2  # Slightly larger than the largest sieve

    # Find x_50 (median size) - size where 50% passes
    idx_50 = np.argmin(np.abs(y - 50))
    x_50_guess = x[idx_50] if idx_50 < len(x) else np.median(x)

    # Initial guess for b (shape parameter) - typically between 1 and 5
    b_guess = 2.0

    try:
        # Fit the curve with appropriate bounds
        x_max_min = x.max()
        x_max_max = x.max() * 10
        x_50_min = x.min() * 0.1
        x_50_max = x.max() * 0.9
        b_min, b_max = 0.5, 10.0

        popt, _ = curve_fit(
            swebrec,
            x,
            y,
            p0=[x_max_guess, x_50_guess, b_guess],
            bounds=([x_max_min, x_50_min, b_min], [x_max_max, x_50_max, b_max]),
            maxfev=5000,
        )
        x_max, x_50, b = popt

        # Calculate R-squared
        y_pred = swebrec(x, x_max, x_50, b)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        return x_max, x_50, b, r_squared

    except (RuntimeError, ValueError):
        # If fitting fails, try with different initial conditions
        try:
            # Try with different initial guesses
            popt, _ = curve_fit(
                swebrec,
                x,
                y,
                p0=[x.max() * 1.5, np.median(x), 1.5],
                bounds=([x.max(), x.min() * 0.5, 0.5], [x.max() * 5, x.max() * 0.8, 5.0]),
                maxfev=5000,
            )
            x_max, x_50, b = popt

            # Calculate R-squared
            y_pred = swebrec(x, x_max, x_50, b)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

            return x_max, x_50, b, r_squared

        except (RuntimeError, ValueError):
            # Return default values if all fitting attempts fail
            return x_max_guess, x_50_guess, b_guess, 0.0


def cubic_spline_fit(sieve_sizes: np.ndarray, passing_percentages: np.ndarray) -> CubicSpline:
    """
    Fit a cubic spline to the gradation data.

    Args:
        sieve_sizes: Array of sieve sizes in mm
        passing_percentages: Array of passing percentages

    Returns:
        CubicSpline object that can be used for interpolation
    """
    # Sort data by sieve size for spline fitting
    sort_idx = np.argsort(sieve_sizes)
    x = sieve_sizes[sort_idx]
    y = passing_percentages[sort_idx]

    # Create cubic spline
    spline = CubicSpline(x, y, bc_type="natural")
    return spline


def plot_fitted_curve(
    sieve_sizes: np.ndarray,
    passing_percentages: np.ndarray,
    fit_type: str = "cubic_spline",
    ax: Optional[plt.Axes] = None,
    **kwargs,
) -> plt.Axes:
    """
    Plot the original data points and fitted curve.

    Args:
        sieve_sizes: Array of sieve sizes in mm
        passing_percentages: Array of passing percentages
        fit_type: Type of fit ('gaudin_schuhmann', 'rosin_rammler', or 'cubic_spline')
        ax: Matplotlib axes object (if None, creates new figure)
        **kwargs: Additional plotting arguments

    Returns:
        Matplotlib axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    # Plot original data points
    ax.scatter(sieve_sizes, passing_percentages, color="blue", s=50, label="Original data", zorder=5)

    # Generate smooth curve for plotting
    # Handle case where sieve sizes include 0.00
    min_sieve = sieve_sizes[sieve_sizes > 0].min() if (sieve_sizes > 0).any() else 0.1
    max_sieve = sieve_sizes.max()
    x_smooth = np.logspace(np.log10(min_sieve), np.log10(max_sieve), 100)

    if fit_type == "gaudin_schuhmann":
        k, m, r_sq = gaudin_schuhmann_fit(sieve_sizes, passing_percentages)
        y_smooth = np.clip(100 * (x_smooth / k) ** m, 0, 100)
        label = f"Gaudin-Schuhmann (k={k:.2f}, m={m:.2f}, R²={r_sq:.3f})"

    elif fit_type == "rosin_rammler":
        x_63, n, r_sq = rosin_rammler_fit(sieve_sizes, passing_percentages)
        # Convert retained to passing for plotting
        y_smooth = np.clip(100 - 100 * np.exp(-((x_smooth / x_63) ** n)), 0, 100)
        label = f"Rosin-Rammler (x₆₃={x_63:.2f}, n={n:.2f}, R²={r_sq:.3f})"

    elif fit_type == "swebrec":
        x_max, x_50, b, r_sq = swebrec_curve_fit(sieve_sizes, passing_percentages)

        # Define the Swebrec function for plotting
        def swebrec_plot(x, x_max, x_50, b):
            x_safe = np.maximum(x, 1e-10)
            x_max_safe = np.maximum(x_max, x_safe.max() * 1.1)
            x_50_safe = np.maximum(x_50, 1e-10)
            x_50_safe = np.minimum(x_50_safe, x_max_safe * 0.99)
            log_ratio = np.log(x_max_safe / x_safe) / np.log(x_max_safe / x_50_safe)
            return np.clip(100 / (1 + log_ratio**b), 0, 100)

        y_smooth = swebrec_plot(x_smooth, x_max, x_50, b)
        label = f"Swebrec (x_max={x_max:.2f}, x₅₀={x_50:.2f}, b={b:.2f}, R²={r_sq:.3f})"

    elif fit_type == "cubic_spline":
        spline = cubic_spline_fit(sieve_sizes, passing_percentages)
        y_smooth = np.clip(spline(x_smooth), 0, 100)
        label = "Cubic Spline"

    else:
        raise ValueError(f"Unknown fit_type: {fit_type}")

    # Plot fitted curve
    ax.plot(x_smooth, y_smooth, color="red", linewidth=2, label=label)

    # Set up the plot
    ax.set_xscale("log")
    ax.set_xlabel("Sieve Size (mm)")
    ax.set_ylabel("Percentage Passing (%)")
    ax.set_title(f'Gradation Curve - {fit_type.replace("_", " ").title()}')
    ax.grid(True, alpha=0.3)
    ax.legend()

    return ax


def interpolate_to_sieves(
    gradation_data: pd.DataFrame, target_sieves: np.ndarray, method: str = "cubic_spline"
) -> pd.DataFrame:
    """
    Interpolate gradation data to a specific set of sieve sizes.

    Args:
        gradation_data: DataFrame with gradation data
        target_sieves: Array of target sieve sizes
        method: Interpolation method ('cubic_spline', 'gaudin_schuhmann', 'rosin_rammler')

    Returns:
        DataFrame with interpolated values at target sieve sizes
    """
    sieve_sizes = gradation_data["sieve"].values
    passing_percentages = gradation_data["wp"].values

    # Sort target sieves
    target_sieves = np.sort(target_sieves)[::-1]  # Descending order

    if method == "cubic_spline":
        spline = cubic_spline_fit(sieve_sizes, passing_percentages)
        interpolated_passing = np.clip(spline(target_sieves), 0, 100)

    elif method == "gaudin_schuhmann":
        k, m, _ = gaudin_schuhmann_fit(sieve_sizes, passing_percentages)
        interpolated_passing = np.clip(100 * (target_sieves / k) ** m, 0, 100)

    elif method == "rosin_rammler":
        x_63, n, _ = rosin_rammler_fit(sieve_sizes, passing_percentages)
        # Convert retained to passing for interpolation
        interpolated_passing = np.clip(100 - 100 * np.exp(-((target_sieves / x_63) ** n)), 0, 100)

    elif method == "swebrec":
        x_max, x_50, b, _ = swebrec_curve_fit(sieve_sizes, passing_percentages)

        # Define the Swebrec function for interpolation
        def swebrec_interp(x, x_max, x_50, b):
            x_safe = np.maximum(x, 1e-10)
            x_max_safe = np.maximum(x_max, x_safe.max() * 1.1)
            x_50_safe = np.maximum(x_50, 1e-10)
            x_50_safe = np.minimum(x_50_safe, x_max_safe * 0.99)
            log_ratio = np.log(x_max_safe / x_safe) / np.log(x_max_safe / x_50_safe)
            return np.clip(100 / (1 + log_ratio**b), 0, 100)

        interpolated_passing = swebrec_interp(target_sieves, x_max, x_50, b)

    else:
        raise ValueError(f"Unknown method: {method}")

    # Create result DataFrame
    result = pd.DataFrame({"sieve": target_sieves, "wp": interpolated_passing, "wr": 100 - interpolated_passing})

    # Calculate individual retained percentages
    result["p"] = result["wr"].diff().fillna(result["wr"])

    return result
