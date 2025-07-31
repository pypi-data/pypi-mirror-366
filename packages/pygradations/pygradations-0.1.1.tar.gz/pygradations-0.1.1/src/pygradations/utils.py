"""
Utility functions for gradation analysis.

This module provides helper functions for common gradation calculations
and data processing tasks.
"""

from typing import (
    Dict,
    List,
    Optional,
)

import numpy as np
import pandas as pd


def calculate_cumulative_percentages(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate cumulative percentages from individual retained percentages.
    
    Args:
        data: DataFrame with 'sieve' and 'p' columns
        
    Returns:
        DataFrame with added 'wr' and 'wp' columns
    """
    result = data.copy()
    
    # Calculate cumulative retained (wr)
    result['wr'] = result['p'].cumsum()
    
    # Calculate passing percentage (wp)
    result['wp'] = 100 - result['wr']
    
    return result


def validate_gradation_data(data: pd.DataFrame) -> bool:
    """
    Validate that gradation data meets basic requirements.
    
    Args:
        data: DataFrame to validate
        
    Returns:
        True if data is valid, raises ValueError otherwise
    """
    required_columns = ['sieve', 'p', 'wr', 'wp']
    
    # Check required columns
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Check for negative values
    for col in ['p', 'wr', 'wp']:
        if (data[col] < 0).any():
            raise ValueError(f"Negative values found in column '{col}'")
    
    # Check that percentages sum to approximately 100%
    total_p = data['p'].sum()
    if not (99.5 <= total_p <= 100.5):
        raise ValueError(f"Individual percentages sum to {total_p:.2f}%, should be close to 100%")
    
    # Check that wr and wp are consistent
    calculated_wp = 100 - data['wr']
    if not np.allclose(data['wp'], calculated_wp, atol=0.1):
        raise ValueError("Inconsistent wr and wp values")
    
    return True


def get_characteristic_sizes(data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate characteristic sizes from gradation data.
    
    Args:
        data: DataFrame with gradation data
        
    Returns:
        Dictionary with characteristic sizes (D10, D30, D50, D60, D90)
    """
    sieve_sizes = data['sieve'].values
    passing_percentages = data['wp'].values
    
    # Sort by sieve size for interpolation
    sort_idx = np.argsort(sieve_sizes)
    x = sieve_sizes[sort_idx]
    y = passing_percentages[sort_idx]
    
    # Find characteristic sizes
    characteristic_sizes = {}
    target_percentages = [10, 30, 50, 60, 90]
    
    for p in target_percentages:
        # Find the sieve size where p% passes
        if p <= y.min():
            size = x.max()
        elif p >= y.max():
            size = x.min()
        else:
            # Interpolate to find the size
            idx = np.searchsorted(y, p)
            if idx == 0:
                size = x[0]
            elif idx == len(y):
                size = x[-1]
            else:
                # Linear interpolation
                y1, y2 = y[idx-1], y[idx]
                x1, x2 = x[idx-1], x[idx]
                size = x1 + (p - y1) * (x2 - x1) / (y2 - y1)
        
        characteristic_sizes[f'D{p}'] = size
    
    return characteristic_sizes


def calculate_uniformity_coefficient(data: pd.DataFrame) -> float:
    """
    Calculate the uniformity coefficient (D60/D10).
    
    Args:
        data: DataFrame with gradation data
        
    Returns:
        Uniformity coefficient
    """
    char_sizes = get_characteristic_sizes(data)
    return char_sizes['D60'] / char_sizes['D10']


def calculate_curvature_coefficient(data: pd.DataFrame) -> float:
    """
    Calculate the curvature coefficient (D30²/(D10*D60)).
    
    Args:
        data: DataFrame with gradation data
        
    Returns:
        Curvature coefficient
    """
    char_sizes = get_characteristic_sizes(data)
    return (char_sizes['D30'] ** 2) / (char_sizes['D10'] * char_sizes['D60'])


def create_standard_sieve_series() -> np.ndarray:
    """
    Create a standard sieve series for interpolation.
    
    Returns:
        Array of standard sieve sizes in mm
    """
    # Standard sieve series (mm)
    standard_sieves = np.array([
        100.0, 75.0, 63.0, 50.0, 37.5, 31.5, 26.5, 19.0, 16.0, 13.2, 9.5, 6.7,
        4.75, 3.35, 2.36, 1.18, 0.85, 0.6, 0.425, 0.3, 0.212, 0.15, 0.106, 0.075,
        0.053, 0.037, 0.025, 0.018, 0.0125, 0.009, 0.0063, 0.0045, 0.0032, 0.0022,
        0.0016, 0.0011, 0.0008, 0.00056, 0.0004, 0.00028, 0.0002, 0.00014, 0.0001
    ])
    
    return standard_sieves


def compare_gradations(gradations: Dict[str, pd.DataFrame], 
                      target_sieves: Optional[np.ndarray] = None) -> pd.DataFrame:
    """
    Compare multiple gradations by interpolating to the same sieve sizes.
    
    Args:
        gradations: Dictionary with gradation names as keys and DataFrames as values
        target_sieves: Target sieve sizes for comparison (if None, uses standard series)
        
    Returns:
        DataFrame with comparison results
    """
    if target_sieves is None:
        target_sieves = create_standard_sieve_series()
    
    # Filter target sieves to reasonable range
    all_sieves = []
    for grad_data in gradations.values():
        all_sieves.extend(grad_data['sieve'].values)
    
    min_sieve = min(all_sieves)
    max_sieve = max(all_sieves)
    
    target_sieves = target_sieves[
        (target_sieves >= min_sieve) & (target_sieves <= max_sieve)
    ]
    
    # Interpolate each gradation to target sieves
    comparison_data = []
    
    for name, grad_data in gradations.items():
        from .interpolation import interpolate_to_sieves
        interpolated = interpolate_to_sieves(grad_data, target_sieves)
        interpolated['gradation'] = name
        comparison_data.append(interpolated)
    
    # Combine all results
    result = pd.concat(comparison_data, ignore_index=True)
    return result


def export_gradation_to_csv(data: pd.DataFrame, filepath: str) -> None:
    """
    Export gradation data to CSV file.
    
    Args:
        data: DataFrame with gradation data
        filepath: Path for the output CSV file
    """
    data.to_csv(filepath, index=False)


def export_gradation_to_excel(data: pd.DataFrame, filepath: str, 
                            sheet_name: str = "Gradation") -> None:
    """
    Export gradation data to Excel file.
    
    Args:
        data: DataFrame with gradation data
        filepath: Path for the output Excel file
        sheet_name: Name of the worksheet
    """
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        data.to_excel(writer, sheet_name=sheet_name, index=False) 