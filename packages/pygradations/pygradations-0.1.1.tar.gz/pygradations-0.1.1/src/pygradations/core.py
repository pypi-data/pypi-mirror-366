"""
Core functionality for gradation analysis.

This module provides the main Gradation class and functions for loading
gradation data from various file formats.
"""

from typing import (
    Dict,
    Optional,
    Union,
)

import numpy as np
import pandas as pd


class Gradation:
    """
    A class to represent and manipulate gradation data.
    
    Gradation data consists of sieve analysis results with columns:
    - sieve: sieve aperture in mm
    - p: weight % retained in each sieve
    - wr: cumulative % retained
    - wp: % passing through each sieve
    """
    
    def __init__(self, data: pd.DataFrame, name: str = "gradation"):
        """
        Initialize a Gradation object.
        
        Args:
            data: DataFrame with columns ['sieve', 'p', 'wr', 'wp']
            name: Name identifier for this gradation
        """
        self.name = name
        self.data = self._validate_and_process_data(data)
    
    def _validate_and_process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and process the input data.
        
        Args:
            data: Input DataFrame
            
        Returns:
            Processed DataFrame with required columns
        """
        required_columns = ['sieve', 'p', 'wr', 'wp']
        
        # Check if all required columns exist
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Create a copy to avoid modifying the original
        processed_data = data[required_columns].copy()
        
        # Ensure sieve column is numeric and sorted
        processed_data['sieve'] = pd.to_numeric(processed_data['sieve'], errors='coerce')
        processed_data = processed_data.sort_values('sieve', ascending=False)
        
        # Ensure all percentage columns are numeric
        for col in ['p', 'wr', 'wp']:
            processed_data[col] = pd.to_numeric(processed_data[col], errors='coerce')
        
        # Remove any rows with NaN values
        processed_data = processed_data.dropna()
        
        return processed_data
    
    def get_sieve_sizes(self) -> np.ndarray:
        """Get the sieve sizes as a numpy array."""
        return self.data['sieve'].values
    
    def get_passing_percentages(self) -> np.ndarray:
        """Get the passing percentages as a numpy array."""
        return self.data['wp'].values
    
    def get_retained_percentages(self) -> np.ndarray:
        """Get the retained percentages as a numpy array."""
        return self.data['p'].values
    
    def get_cumulative_retained(self) -> np.ndarray:
        """Get the cumulative retained percentages as a numpy array."""
        return self.data['wr'].values
    
    def __repr__(self) -> str:
        return f"Gradation(name='{self.name}', n_sieves={len(self.data)})"
    
    def __str__(self) -> str:
        return f"Gradation '{self.name}' with {len(self.data)} sieve sizes"


def load_gradation_from_csv(filepath: str, name: Optional[str] = None) -> Gradation:
    """
    Load gradation data from a CSV file.
    
    Args:
        filepath: Path to the CSV file
        name: Optional name for the gradation (defaults to filename)
        
    Returns:
        Gradation object
    """
    if name is None:
        name = filepath.split('/')[-1].replace('.csv', '')
    
    data = pd.read_csv(filepath)
    return Gradation(data, name)


def load_gradation_from_excel(filepath: str, sheet_name: Union[str, int] = 0, 
                            name: Optional[str] = None) -> Gradation:
    """
    Load gradation data from an Excel file.
    
    Args:
        filepath: Path to the Excel file
        sheet_name: Name or index of the sheet to read
        name: Optional name for the gradation (defaults to filename_sheetname)
        
    Returns:
        Gradation object
    """
    if name is None:
        base_name = filepath.split('/')[-1].replace('.xlsx', '').replace('.xls', '')
        if isinstance(sheet_name, str):
            name = f"{base_name}_{sheet_name}"
        else:
            name = f"{base_name}_sheet{sheet_name}"
    
    data = pd.read_excel(filepath, sheet_name=sheet_name)
    return Gradation(data, name)


def create_gradation_dict(gradations: Dict[str, Gradation]) -> Dict[str, pd.DataFrame]:
    """
    Convert a dictionary of Gradation objects to a dictionary of DataFrames.
    
    Args:
        gradations: Dictionary with gradation names as keys and Gradation objects as values
        
    Returns:
        Dictionary with gradation names as keys and DataFrames as values
    """
    return {name: gradation.data for name, gradation in gradations.items()}
