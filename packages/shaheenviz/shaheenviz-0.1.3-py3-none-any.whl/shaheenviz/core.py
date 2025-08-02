"""
Core module for Shaheenviz - Main entry point for EDA report generation.

This module manages EDA mode selection and report generation, choosing between
YData Profiling and Sweetviz based on dataset characteristics.
"""

import pandas as pd
import numpy as np
from typing import Optional, Union, Dict, Any
import warnings
from tqdm import tqdm

# Fix matplotlib backend to prevent threading issues
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from .profiling_wrapper import ProfileWrapper
from .sweetviz_wrapper import SweetvizWrapper
from .utils import detect_target, save_reports


class ShaheenvizReport:
    """
    Main report class that wraps either YData Profiling or Sweetviz reports.
    """
    
    def __init__(self, backend_report, backend_type: str, metadata: Dict[str, Any]):
        """
        Initialize the unified report.
        
        Args:
            backend_report: The underlying report object (ProfileReport or SweetvizReport)
            backend_type: Either 'ydata' or 'sweetviz'
            metadata: Additional metadata about the report generation
        """
        self.backend_report = backend_report
        self.backend_type = backend_type
        self.metadata = metadata
    
    def save_html(self, filepath: str, **kwargs) -> None:
        """Save report as HTML file."""
        if self.backend_type == 'ydata':
            self.backend_report.to_file(filepath, **kwargs)
        elif self.backend_type == 'sweetviz':
            # Sweetviz uses show_html for saving files
            layout = kwargs.pop('layout', 'widescreen')
            scale = kwargs.pop('scale', 1.0)
            self.backend_report.show_html(filepath, layout=layout, scale=scale, **kwargs)
    
    def save_json(self, filepath: str) -> None:
        """Save report as JSON file (YData Profiling only)."""
        if self.backend_type == 'ydata':
            self.backend_report.to_file(filepath)
        else:
            warnings.warn("JSON export is only supported for YData Profiling backend")
    
    def show_notebook(self, **kwargs):
        """Display report in Jupyter notebook."""
        if self.backend_type == 'ydata':
            return self.backend_report.to_notebook_iframe(**kwargs)
        elif self.backend_type == 'sweetviz':
            return self.backend_report.show_notebook(**kwargs)
    
    def get_rejected_variables(self) -> list:
        """Get list of rejected variables (YData Profiling only)."""
        if self.backend_type == 'ydata':
            return self.backend_report.get_rejected_variables()
        else:
            warnings.warn("Rejected variables info is only available for YData Profiling backend")
            return []


def _choose_backend(df: pd.DataFrame, target: Optional[str] = None, 
                   mode: str = 'auto') -> str:
    """
    Choose the appropriate backend based on dataset characteristics.
    
    Args:
        df: Input DataFrame
        target: Target column name
        mode: 'auto', 'ydata', or 'sweetviz'
    
    Returns:
        Backend name: 'ydata' or 'sweetviz'
    """
    if mode in ['ydata', 'sweetviz']:
        return mode
    
    # Auto mode logic
    n_rows, n_cols = df.shape
    
    # Use Sweetviz for smaller datasets (better visualizations, interactive features)
    if n_rows < 5000 and n_cols < 30:
        print(f"Dataset size ({n_rows} rows, {n_cols} cols) - choosing Sweetviz for better visualizations")
        return 'sweetviz'
    
    # Use YData Profiling for larger datasets (better performance, more analysis)
    print(f"Dataset size ({n_rows} rows, {n_cols} cols) - choosing YData Profiling for better performance")
    return 'ydata'


def generate_report(df: pd.DataFrame, 
                   df2: Optional[pd.DataFrame] = None,
                   target: Optional[str] = None,
                   title: str = "Shaheenviz EDA Report",
                   mode: str = 'auto',
                   minimal: bool = False,
                   **kwargs) -> ShaheenvizReport:
    """
    Generate a comprehensive EDA report using the best available backend.
    
    Args:
        df: Primary DataFrame to analyze
        df2: Optional comparison DataFrame (e.g., validation set)
        target: Name of target column for supervised learning analysis
        title: Report title
        mode: Backend selection mode ('auto', 'ydata', 'sweetviz')
        minimal: Generate minimal report for faster processing
        **kwargs: Additional arguments passed to backend
    
    Returns:
        ShaheenvizReport object with unified interface
    """
    
    # Validate inputs
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    
    # Auto-detect target if not provided
    if target is None:
        target = detect_target(df)
        if target:
            print(f"Auto-detected target column: {target}")
    
    # Choose backend
    backend = _choose_backend(df, target, mode)
    print(f"Using {backend.upper()} backend for analysis...")
    
    # Generate metadata
    metadata = {
        'backend': backend,
        'dataset_shape': df.shape,
        'target_column': target,
        'comparison_dataset': df2 is not None,
        'minimal': minimal,
        'title': title
    }
    
    # Generate report based on chosen backend
    with tqdm(desc=f"Generating {backend.upper()} report", unit="step") as pbar:
        
        try:
            if backend == 'ydata':
                wrapper = ProfileWrapper()
                pbar.set_description("Initializing YData Profiling...")
                pbar.update(1)
                
                pbar.set_description("Generating YData profile...")
                report = wrapper.generate_profile(
                    df=df, 
                    target=target, 
                    title=title,
                    minimal=minimal,
                    **kwargs
                )
                pbar.set_description("YData profile complete")
                pbar.update(1)
                
            elif backend == 'sweetviz':
                wrapper = SweetvizWrapper()
                pbar.set_description("Initializing Sweetviz...")
                pbar.update(1)
                
                pbar.set_description("Generating Sweetviz report...")
                report = wrapper.generate_report(
                    df=df,
                    df2=df2,
                    target=target,
                    title=title,
                    **kwargs
                )
                pbar.set_description("Sweetviz report complete")
                pbar.update(1)
        
        except Exception as e:
            pbar.set_description(f"Error generating {backend.upper()} report")
            print(f"\n⚠️  Error with {backend.upper()} backend: {str(e)}")
            
            # Try fallback to the other backend
            fallback_backend = 'ydata' if backend == 'sweetviz' else 'sweetviz'
            print(f"🔄 Attempting fallback to {fallback_backend.upper()} backend...")
            
            try:
                if fallback_backend == 'ydata':
                    wrapper = ProfileWrapper()
                    report = wrapper.generate_profile(
                        df=df, 
                        target=target, 
                        title=title,
                        minimal=minimal,
                        **kwargs
                    )
                    backend = 'ydata'  # Update backend variable
                    metadata['backend'] = 'ydata'
                    metadata['fallback_used'] = True
                    print("✅ Fallback to YData Profiling successful")
                else:
                    wrapper = SweetvizWrapper()
                    report = wrapper.generate_report(
                        df=df,
                        df2=df2,
                        target=target,
                        title=title,
                        **kwargs
                    )
                    backend = 'sweetviz'  # Update backend variable
                    metadata['backend'] = 'sweetviz'
                    metadata['fallback_used'] = True
                    print("✅ Fallback to Sweetviz successful")
            
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Both backends failed. Original error ({backend}): {str(e)}. "
                    f"Fallback error ({fallback_backend}): {str(fallback_error)}"
                )
    
    return ShaheenvizReport(report, backend, metadata)


def compare_datasets(train_df: pd.DataFrame, 
                    test_df: pd.DataFrame,
                    target: Optional[str] = None,
                    title: str = "Dataset Comparison Report") -> ShaheenvizReport:
    """
    Generate a comparison report between training and test datasets.
    
    Args:
        train_df: Training DataFrame
        test_df: Test DataFrame  
        target: Target column name
        title: Report title
    
    Returns:
        ShaheenvizReport with comparison analysis
    """
    return generate_report(
        df=train_df,
        df2=test_df, 
        target=target,
        title=title,
        mode='sweetviz'  # Sweetviz is better for comparisons
    )


def quick_profile(df: pd.DataFrame, target: Optional[str] = None) -> ShaheenvizReport:
    """
    Generate a quick minimal profile for fast overview.
    
    Args:
        df: DataFrame to analyze
        target: Target column name
    
    Returns:
        Minimal ShaheenvizReport
    """
    return generate_report(
        df=df,
        target=target,
        title="Quick Profile",
        minimal=True,
        mode='ydata'  # YData Profiling has better minimal mode
    )
