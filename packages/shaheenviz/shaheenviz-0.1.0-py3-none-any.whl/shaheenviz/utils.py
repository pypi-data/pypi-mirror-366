"""
Utility functions for Shaheenviz.

This module contains common helper functions used across the package,
including target detection, report saving, and data validation.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Union
import os
import json
import warnings
from pathlib import Path


def detect_target(df: pd.DataFrame, 
                 potential_names: Optional[List[str]] = None,
                 max_unique_ratio: float = 0.1) -> Optional[str]:
    """
    Automatically detect the target column in a DataFrame.
    
    Args:
        df: Input DataFrame
        potential_names: List of potential target column names to check first
        max_unique_ratio: Maximum ratio of unique values for classification targets
    
    Returns:
        Name of detected target column, or None if not found
    """
    
    if potential_names is None:
        potential_names = [
            'target', 'label', 'class', 'y', 'outcome', 'result',
            'prediction', 'response', 'dependent', 'output'
        ]
    
    # First, check for columns with common target names
    for col in df.columns:
        if col.lower() in [name.lower() for name in potential_names]:
            return col
    
    # Look for binary or low-cardinality categorical columns
    for col in df.columns:
        unique_count = df[col].nunique()
        unique_ratio = unique_count / len(df)
        
        # Binary classification
        if unique_count == 2:
            return col
        
        # Multi-class classification (low cardinality)
        if unique_ratio <= max_unique_ratio and unique_count <= 20:
            # Check if it looks like a classification target
            if df[col].dtype in ['object', 'category', 'bool']:
                return col
            elif df[col].dtype in ['int64', 'int32']:
                # Integer classification labels
                return col
    
    return None


def validate_dataframe(df: pd.DataFrame, 
                      min_rows: int = 1,
                      min_cols: int = 1,
                      check_empty: bool = True) -> Dict[str, Any]:
    """
    Validate a DataFrame and return validation results.
    
    Args:
        df: DataFrame to validate
        min_rows: Minimum number of rows required
        min_cols: Minimum number of columns required
        check_empty: Whether to check for completely empty DataFrame
    
    Returns:
        Dictionary with validation results
    """
    
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'info': {
            'shape': df.shape,
            'memory_usage': df.memory_usage(deep=True).sum(),
            'dtypes': df.dtypes.to_dict()
        }
    }
    
    # Check basic requirements
    if df.shape[0] < min_rows:
        validation_results['valid'] = False
        validation_results['errors'].append(f"DataFrame has {df.shape[0]} rows, minimum required: {min_rows}")
    
    if df.shape[1] < min_cols:
        validation_results['valid'] = False
        validation_results['errors'].append(f"DataFrame has {df.shape[1]} columns, minimum required: {min_cols}")
    
    # Check for empty DataFrame
    if check_empty and df.empty:
        validation_results['valid'] = False
        validation_results['errors'].append("DataFrame is empty")
    
    # Check for all-null columns
    null_columns = df.columns[df.isnull().all()].tolist()
    if null_columns:
        validation_results['warnings'].append(f"Found completely null columns: {null_columns}")
    
    # Check for duplicate columns
    if df.columns.duplicated().any():
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        validation_results['warnings'].append(f"Found duplicate column names: {duplicate_cols}")
    
    # Check for high missing value percentage
    missing_percentage = (df.isnull().sum() / len(df) * 100)
    high_missing_cols = missing_percentage[missing_percentage > 50].index.tolist()
    if high_missing_cols:
        validation_results['warnings'].append(f"Columns with >50% missing values: {high_missing_cols}")
    
    return validation_results


def save_reports(report, 
                output_dir: str = "shaheenviz_output",
                base_filename: str = "report",
                formats: List[str] = ["html"],
                **kwargs) -> Dict[str, str]:
    """
    Save reports in multiple formats.
    
    Args:
        report: ShaheenvizReport object
        output_dir: Output directory path
        base_filename: Base filename without extension
        formats: List of formats to save ('html', 'json')
        **kwargs: Additional arguments passed to save methods
    
    Returns:
        Dictionary mapping format to saved file path
    """
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    for fmt in formats:
        try:
            if fmt.lower() == 'html':
                filepath = output_path / f"{base_filename}.html"
                report.save_html(str(filepath), **kwargs)
                saved_files['html'] = str(filepath)
                
            elif fmt.lower() == 'json':
                filepath = output_path / f"{base_filename}.json"
                report.save_json(str(filepath))
                saved_files['json'] = str(filepath)
                
            else:
                warnings.warn(f"Unsupported format: {fmt}")
                
        except Exception as e:
            warnings.warn(f"Failed to save report in {fmt} format: {str(e)}")
    
    return saved_files


def compare_dataframes(df1: pd.DataFrame, 
                      df2: pd.DataFrame,
                      name1: str = "Dataset 1",
                      name2: str = "Dataset 2") -> Dict[str, Any]:
    """
    Compare two DataFrames and return comparison statistics.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame  
        name1: Name for first DataFrame
        name2: Name for second DataFrame
    
    Returns:
        Dictionary with comparison results
    """
    
    comparison = {
        'basic_stats': {
            name1: {'shape': df1.shape, 'memory': df1.memory_usage(deep=True).sum()},
            name2: {'shape': df2.shape, 'memory': df2.memory_usage(deep=True).sum()}
        },
        'column_comparison': {
            'common_columns': list(set(df1.columns) & set(df2.columns)),
            'unique_to_df1': list(set(df1.columns) - set(df2.columns)),
            'unique_to_df2': list(set(df2.columns) - set(df1.columns))
        },
        'dtype_differences': {},
        'missing_value_comparison': {}
    }
    
    # Compare data types for common columns
    common_cols = comparison['column_comparison']['common_columns']
    for col in common_cols:
        if df1[col].dtype != df2[col].dtype:
            comparison['dtype_differences'][col] = {
                name1: str(df1[col].dtype),
                name2: str(df2[col].dtype)
            }
    
    # Compare missing values for common columns
    for col in common_cols:
        missing1 = df1[col].isnull().sum() / len(df1) * 100
        missing2 = df2[col].isnull().sum() / len(df2) * 100
        if abs(missing1 - missing2) > 5:  # >5% difference
            comparison['missing_value_comparison'][col] = {
                name1: f"{missing1:.2f}%",
                name2: f"{missing2:.2f}%"
            }
    
    return comparison


def get_column_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Categorize DataFrame columns by their data types.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Dictionary with column names grouped by type
    """
    
    column_types = {
        'numeric': [],
        'categorical': [],
        'datetime': [],
        'boolean': [],
        'text': [],
        'other': []
    }
    
    for col in df.columns:
        dtype = df[col].dtype
        
        if pd.api.types.is_numeric_dtype(dtype):
            # Further distinguish between continuous and discrete
            if df[col].nunique() <= 20 and df[col].dtype in ['int64', 'int32']:
                column_types['categorical'].append(col)
            else:
                column_types['numeric'].append(col)
                
        elif pd.api.types.is_categorical_dtype(dtype) or dtype == 'object':
            # Check if it's actually numeric stored as object
            try:
                pd.to_numeric(df[col].dropna().head(100))
                column_types['numeric'].append(col)
            except (ValueError, TypeError):
                column_types['categorical'].append(col)
                
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            column_types['datetime'].append(col)
            
        elif pd.api.types.is_bool_dtype(dtype):
            column_types['boolean'].append(col)
            
        else:
            column_types['other'].append(col)
    
    return column_types


def create_sample_data(n_rows: int = 1000, 
                      n_features: int = 10,
                      problem_type: str = "classification",
                      random_state: int = 42) -> pd.DataFrame:
    """
    Create sample data for testing Shaheenviz functionality.
    
    Args:
        n_rows: Number of rows to generate
        n_features: Number of features to generate
        problem_type: Type of ML problem ('classification', 'regression')
        random_state: Random seed for reproducibility
    
    Returns:
        DataFrame with sample data including target column
    """
    
    np.random.seed(random_state)
    
    # Generate feature data
    data = {}
    
    # Numeric features
    for i in range(n_features // 2):
        data[f'numeric_feature_{i}'] = np.random.normal(0, 1, n_rows)
    
    # Categorical features  
    categories = ['A', 'B', 'C', 'D', 'E']
    for i in range(n_features // 4):
        data[f'categorical_feature_{i}'] = np.random.choice(categories, n_rows)
    
    # Boolean features
    for i in range(n_features // 4):
        data[f'boolean_feature_{i}'] = np.random.choice([True, False], n_rows)
    
    df = pd.DataFrame(data)
    
    # Generate target variable
    if problem_type == "classification":
        # Binary classification
        target = np.random.choice([0, 1], n_rows, p=[0.7, 0.3])
        df['target'] = target
    else:  # regression
        # Create target correlated with first numeric feature
        if 'numeric_feature_0' in df.columns:
            target = 2 * df['numeric_feature_0'] + np.random.normal(0, 0.5, n_rows)
        else:
            target = np.random.normal(0, 1, n_rows)
        df['target'] = target
    
    # Add some missing values
    missing_cols = np.random.choice(df.columns[:-1], size=2, replace=False)
    for col in missing_cols:
        missing_idx = np.random.choice(df.index, size=int(0.1 * n_rows), replace=False)
        df.loc[missing_idx, col] = np.nan
    
    return df


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human readable format.
    
    Args:
        bytes_value: Number of bytes
    
    Returns:
        Formatted string (e.g., '1.5 MB')
    """
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging and logging.
    
    Returns:
        Dictionary with system information
    """
    
    import platform
    import sys
    
    info = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'processor': platform.processor(),
        'architecture': platform.architecture(),
        'shaheenviz_version': '0.1.0',  # This would normally be imported
    }
    
    # Try to get package versions
    try:
        import pandas
        info['pandas_version'] = pandas.__version__
    except ImportError:
        info['pandas_version'] = 'Not installed'
    
    try:
        import numpy
        info['numpy_version'] = numpy.__version__
    except ImportError:
        info['numpy_version'] = 'Not installed'
    
    return info
