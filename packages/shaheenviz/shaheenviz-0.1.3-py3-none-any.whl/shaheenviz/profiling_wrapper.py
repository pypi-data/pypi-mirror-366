"""
YData Profiling wrapper module.

This module wraps and customizes YData Profiling functionality to provide
enhanced configuration and integration with the unified Shaheenviz interface.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
import warnings

# Fix matplotlib backend to prevent threading issues
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

try:
    from ydata_profiling import ProfileReport
    from ydata_profiling.config import Config
    YDATA_AVAILABLE = True
except ImportError:
    YDATA_AVAILABLE = False
    ProfileReport = None
    Config = None


class ProfileWrapper:
    """
    Wrapper class for YData Profiling with enhanced configuration and features.
    """
    
    def __init__(self):
        """Initialize the ProfileWrapper."""
        if not YDATA_AVAILABLE:
            raise ImportError(
                "ydata-profiling is not installed. Please install it with: "
                "pip install ydata-profiling>=4.2.0"
            )
        
        self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration optimized for Shaheenviz.
        
        Returns:
            Default configuration dictionary
        """
        return {
            # Dataset
            "dataset": {
                "description": "Dataset profiled with Shaheenviz",
                "creator": "Shaheenviz",
                "author": "Generated automatically",
                "copyright_holder": "",
                "copyright_year": "",
                "url": "",
            },
            
            # Variables
            "vars": {
                "num": {
                    "quantiles": [0.05, 0.25, 0.5, 0.75, 0.95],
                    "skewness_threshold": 20,
                    "low_categorical_threshold": 5,
                },
                "cat": {
                    "length": True,
                    "characters": True,
                    "words": True,
                    "cardinality_threshold": 50,
                },
                "bool": {
                    "n_obs": 3,
                    "imbalance_threshold": 0.5,
                },
                "path": {
                    "active": False,
                },
                "file": {
                    "active": False,
                },
                "image": {
                    "active": False,
                },
            },
            
            # Correlations
            "correlations": {
                "pearson": {"calculate": True, "threshold": 0.9},
                "spearman": {"calculate": True, "threshold": 0.9}, 
                "kendall": {"calculate": False, "threshold": 0.9},
                "phi_k": {"calculate": True, "threshold": 0.9},
                "cramers": {"calculate": True, "threshold": 0.9},
                "auto": {"calculate": True, "threshold": 0.9},
            },
            
            # Missing values
            "missing_diagrams": {
                "bar": True,
                "matrix": True,
                "heatmap": True,
                "dendrogram": True,
            },
            
            # Interactions
            "interactions": {
                "targets": [],
                "continuous": True,
            },
            
            # Samples
            "samples": {
                "head": 5,
                "tail": 5,
                "random": 0,
            },
            
            # Duplicates
            "duplicates": {
                "head": 10,
                "key": "# duplicates",
            },
            
            # Progress bar
            "progress_bar": True,
            
            # HTML
            "html": {
                "minify_html": True,
                "use_local_assets": True,
                "inline": True,
                "navbar_show": True,
                "full_width": False,
                "style": {
                    "theme": None,
                    "logo": "",
                    "primary_color": "#337ab7",
                },
            },
            
            # Notebook
            "notebook": {
                "iframe": {
                    "height": "800px",
                    "width": "100%",
                    "attribute": "srcdoc",
                },
            },
        }
    
    def _get_minimal_config(self) -> Dict[str, Any]:
        """
        Get minimal configuration for faster processing.
        
        Returns:
            Minimal configuration dictionary
        """
        config = self._get_default_config().copy()
        
        # Disable expensive computations
        config["correlations"]["spearman"]["calculate"] = False
        config["correlations"]["kendall"]["calculate"] = False
        config["correlations"]["phi_k"]["calculate"] = False
        config["correlations"]["cramers"]["calculate"] = False
        config["missing_diagrams"]["dendrogram"] = False
        config["interactions"]["continuous"] = False
        config["samples"]["head"] = 3
        config["samples"]["tail"] = 3
        config["duplicates"]["head"] = 5
        
        return config
    
    def generate_profile(self, 
                        df: pd.DataFrame,
                        target: Optional[str] = None,
                        title: str = "YData Profiling Report",
                        minimal: bool = False,
                        config_overrides: Optional[Dict[str, Any]] = None,
                        **kwargs) -> ProfileReport:
        """
        Generate a YData Profiling report with Shaheenviz enhancements.
        
        Args:
            df: DataFrame to profile
            target: Target column for supervised learning analysis
            title: Report title
            minimal: Use minimal configuration for faster processing
            config_overrides: Custom configuration overrides
            **kwargs: Additional arguments passed to ProfileReport
        
        Returns:
            ProfileReport object
        """
        
        # Choose configuration
        if minimal:
            config = self._get_minimal_config()
        else:
            config = self._get_default_config()
        
        # Apply user overrides
        if config_overrides:
            config.update(config_overrides)
        
        # Set target interactions if target is provided
        if target and target in df.columns:
            if "interactions" not in config:
                config["interactions"] = {}
            config["interactions"]["targets"] = [target]
        
        # Generate profile
        try:
            profile = ProfileReport(
                df,
                title=title,
                config_file=None,
                lazy=False,
                **config,
                **kwargs
            )
            
            # Add custom warnings
            self._add_custom_warnings(profile, df, target)
            
            return profile
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate YData Profiling report: {str(e)}")
    
    def _add_custom_warnings(self, profile: ProfileReport, df: pd.DataFrame, target: Optional[str]) -> None:
        """
        Add custom Shaheenviz warnings to the profile.
        
        Args:
            profile: ProfileReport object to modify
            df: Original DataFrame
            target: Target column name
        """
        
        # Check for constant columns
        constant_cols = []
        for col in df.columns:
            if df[col].nunique() <= 1:
                constant_cols.append(col)
        
        if constant_cols:
            warnings.warn(f"Found {len(constant_cols)} constant columns: {constant_cols}")
        
        # Check for high cardinality categorical columns
        high_card_cols = []
        for col in df.select_dtypes(include=['object', 'category']).columns:
            if df[col].nunique() > 0.8 * len(df):
                high_card_cols.append(col)
        
        if high_card_cols:
            warnings.warn(f"Found high cardinality columns: {high_card_cols}")
        
        # Check target imbalance
        if target and target in df.columns:
            target_counts = df[target].value_counts()
            if len(target_counts) > 1:
                imbalance_ratio = target_counts.max() / target_counts.min()
                if imbalance_ratio > 10:
                    warnings.warn(f"Target column '{target}' is highly imbalanced (ratio: {imbalance_ratio:.1f})")
    
    def get_feature_importance(self, profile: ProfileReport, target: Optional[str] = None) -> Dict[str, float]:
        """
        Extract feature importance from correlations with target.
        
        Args:
            profile: ProfileReport object
            target: Target column name
        
        Returns:
            Dictionary of feature importance scores
        """
        if not target:
            return {}
        
        try:
            # Get correlations from profile
            correlations = profile.get_description()["correlations"]
            
            importance_scores = {}
            
            # Extract Pearson correlations with target
            if "pearson" in correlations:
                pearson_matrix = correlations["pearson"]
                if target in pearson_matrix.columns:
                    target_corrs = pearson_matrix[target].abs().sort_values(ascending=False)
                    importance_scores = target_corrs.to_dict()
            
            return importance_scores
            
        except Exception as e:
            warnings.warn(f"Could not extract feature importance: {str(e)}")
            return {}
    
    def get_data_quality_summary(self, profile: ProfileReport) -> Dict[str, Any]:
        """
        Extract data quality summary from the profile.
        
        Args:
            profile: ProfileReport object
        
        Returns:
            Data quality summary dictionary
        """
        try:
            description = profile.get_description()
            
            summary = {
                "n_observations": description["table"]["n"],
                "n_variables": description["table"]["n_var"],
                "missing_cells": description["table"]["n_cells_missing"],
                "missing_percentage": description["table"]["p_cells_missing"] * 100,
                "duplicate_rows": description["table"]["n_duplicates"],
                "duplicate_percentage": description["table"]["p_duplicates"] * 100,
                "memory_size": description["table"]["memory_size"],
                "constant_columns": [],
                "high_cardinality_columns": [],
            }
            
            # Extract problematic columns
            for var_name, var_info in description["variables"].items():
                if var_info.get("n_distinct", 0) <= 1:
                    summary["constant_columns"].append(var_name)
                elif var_info.get("n_distinct", 0) > 0.8 * summary["n_observations"]:
                    summary["high_cardinality_columns"].append(var_name)
            
            return summary
            
        except Exception as e:
            warnings.warn(f"Could not extract data quality summary: {str(e)}")
            return {}
