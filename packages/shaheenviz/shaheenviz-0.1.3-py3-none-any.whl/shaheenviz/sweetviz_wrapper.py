"""
Sweetviz wrapper module.

This module wraps and customizes Sweetviz functionality to provide
seamless integration with the unified Shaheenviz interface.
"""

import pandas as pd
from typing import Optional, Dict, Any, List, Union
import warnings
import numpy as np

try:
    import sweetviz as sv
    SWEETVIZ_AVAILABLE = True
except ImportError:
    SWEETVIZ_AVAILABLE = False
    sv = None


class SweetvizWrapper:
    """
    Wrapper class for Sweetviz with enhanced configuration and customizations.
    """
    
    def __init__(self):
        """Initialize the SweetvizWrapper."""
        if not SWEETVIZ_AVAILABLE:
            raise ImportError(
                "Sweetviz is not installed. Please install it with: "
                "pip install sweetviz>=2.1.4"
            )
        # Ignore VisibleDeprecationWarning temporarily
        if hasattr(np, 'VisibleDeprecationWarning'):
            warnings.filterwarnings('ignore', category=getattr(np, 'VisibleDeprecationWarning'))
        self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration for Sweetviz.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "target_feat": None,
            "pairwise_analysis": "auto",
            "feat_cfg": None,
            "progress_bar": True,
        }

    def generate_report(self, 
                        df: pd.DataFrame,
                        df2: Optional[pd.DataFrame] = None,
                        target: Optional[str] = None,
                        title: str = "Sweetviz Report",
                        config_overrides: Optional[Dict[str, Any]] = None,
                        **kwargs) -> Any:
        """
        Generate a Sweetviz report with customizations.

        Args:
            df: DataFrame to profile
            df2: Optional comparison DataFrame
            target: Target column for analysis
            title: Report title
            config_overrides: Custom configuration overrides
            **kwargs: Additional arguments passed to Sweetviz analyze
         
        Returns:
            Sweetviz DataframeReport object
        """
        
        # Override default configuration
        if config_overrides:
            self.config.update(config_overrides)
        
        report = None

        # Generating report
        try:
            # Temporarily suppress numpy warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                
                report = sv.analyze([df, target],
                                    feat_cfg=self.config["feat_cfg"],
                                    pairwise_analysis=self.config["pairwise_analysis"],
                                    **kwargs)
                
                # Generate comparison report
                if df2 is not None:
                    report.compare([df2, target], name="Comparison Dataset")
            
            # Don't show HTML immediately - let the user decide when to display
            # The report object can be used later to show or save HTML
            
            return report
        except Exception as e:
            raise RuntimeError(f"Failed to generate Sweetviz report: {str(e)}")

    def add_custom_warnings(self, report: Any, df: pd.DataFrame, target: Optional[str] = None) -> None:
        """
        Add custom warnings to the Sweetviz report.

        Args:
            report: Sweetviz DataframeReport object
            df: Original DataFrame
            target: Target column name
         """
        const_cols = [col for col in df.columns if df[col].nunique() <= 1]
        if const_cols:
            warnings.warn(f"Found constant columns: {const_cols}")

        # Target imbalance
        if target and target in df.columns:
            target_counts = df[target].value_counts()
            if len(target_counts) > 1:
                imbalance_ratio = target_counts.max() / target_counts.min()
                if imbalance_ratio > 10:
                    warnings.warn(f"Target '{target}' is highly imbalanced with a ratio of {imbalance_ratio:.2f}")

    def get_feature_importance(self, report: Any, target: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate feature importance based on target correlation.
        
        Args:
            report: Sweetviz DataframeReport object
            target: Target column name
         
        Returns:
            Dictionary with feature importance scores
        """
        # Implement custom logic to extract feature importance if needed
        return {}

    def get_data_quality_summary(self, report: Any) -> Dict[str, Any]:
        """
        Summarize data quality metrics from the Sweetviz report.
         
        Args:
            report: Sweetviz DataframeReport object
         
        Returns:
            Data quality metrics dictionary
        """
        # Implement custom logic to generate data quality summary if needed
        return {}
