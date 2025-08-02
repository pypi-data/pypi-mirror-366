"""
Rust-accelerated functions for Shaheenviz.

This module provides Python wrappers for high-performance Rust implementations
of statistical and data analysis functions.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List, Union
import warnings

# Rust acceleration disabled - using pure Python fallbacks
RUST_AVAILABLE = False
shaheenviz_rs = None
# Rust acceleration disabled - fallback to pure Python implementations


class RustAccelerated:
    """
    High-performance Rust-accelerated statistical functions.
    """
    
    def __init__(self):
        """Initialize the Python fallback backend."""
        self.available = False
    def fast_describe(self, data: Union[pd.Series, np.ndarray]) -> Dict[str, float]:
        """
        Fast statistical description using Python fallback.
        
        Args:
            data: Numeric data to analyze
        
        Returns:
            Dictionary with statistical measures
        """
        return self._fallback_describe(data)
    
    def fast_correlation_matrix(self, 
                               df: pd.DataFrame, 
                               method: str = "pearson") -> np.ndarray:
        """
        Fast correlation matrix computation using Python fallback.
        
        Args:
            df: DataFrame with numeric columns
            method: Correlation method ('pearson' or 'spearman')
        
        Returns:
            Correlation matrix as numpy array
        """
        return self._fallback_correlation_matrix(df, method)
    
    def fast_missing_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Fast missing value analysis using Python fallback.
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Dictionary with missing value statistics
        """
        return self._fallback_missing_analysis(df)
    
    def fast_outlier_detection(self, 
                              data: Union[pd.Series, np.ndarray],
                              method: str = "iqr",
                              threshold: float = 1.5) -> Dict[str, Any]:
        """
        Fast outlier detection using Python fallback.
        
        Args:
            data: Numeric data to analyze
            method: Detection method ('iqr', 'zscore', 'modified_zscore')
            threshold: Threshold for outlier detection
        
        Returns:
            Dictionary with outlier information
        """
        return self._fallback_outlier_detection(data, method, threshold)
    
    def fast_profile_numeric(self, 
                           data: Union[pd.Series, np.ndarray],
                           column_name: str) -> Dict[str, Any]:
        """
        Fast numeric column profiling using Rust.
        
        Args:
            data: Numeric data to profile
            column_name: Name of the column
        
        Returns:
            Dictionary with profiling results
        """
        if not self.available:
            return self._fallback_profile_numeric(data, column_name)
        
        # Convert to numpy array if needed
        if isinstance(data, pd.Series):
            array = data.to_numpy(dtype=np.float64)
        else:
            array = np.asarray(data, dtype=np.float64)
        
        try:
            return shaheenviz_rs.fast_profile_numeric(array, column_name)
        except Exception as e:
            warnings.warn(f"Rust function failed, falling back to Python: {e}")
            return self._fallback_profile_numeric(data, column_name)
    
    def fast_profile_categorical(self, 
                               data: Union[pd.Series, List[str]],
                               column_name: str) -> Dict[str, Any]:
        """
        Fast categorical column profiling using Rust.
        
        Args:
            data: Categorical data to profile
            column_name: Name of the column
        
        Returns:
            Dictionary with profiling results
        """
        if not self.available:
            return self._fallback_profile_categorical(data, column_name)
        
        # Convert to list of strings
        if isinstance(data, pd.Series):
            string_data = data.astype(str).tolist()
        else:
            string_data = [str(x) for x in data]
        
        try:
            return shaheenviz_rs.fast_profile_categorical(string_data, column_name)
        except Exception as e:
            warnings.warn(f"Rust function failed, falling back to Python: {e}")
            return self._fallback_profile_categorical(data, column_name)
    
    def fast_cramers_v(self, 
                      x: Union[pd.Series, List[str]], 
                      y: Union[pd.Series, List[str]]) -> float:
        """
        Fast Cramér's V calculation using Rust.
        
        Args:
            x: First categorical variable
            y: Second categorical variable
        
        Returns:
            Cramér's V coefficient
        """
        if not self.available:
            return self._fallback_cramers_v(x, y)
        
        # Convert to list of strings
        if isinstance(x, pd.Series):
            x_data = x.astype(str).tolist()
        else:
            x_data = [str(item) for item in x]
        
        if isinstance(y, pd.Series):
            y_data = y.astype(str).tolist()
        else:
            y_data = [str(item) for item in y]
        
        try:
            return shaheenviz_rs.fast_cramers_v(x_data, y_data)
        except Exception as e:
            warnings.warn(f"Rust function failed, falling back to Python: {e}")
            return self._fallback_cramers_v(x, y)
    
    # Fallback implementations (pure Python)
    
    def _fallback_describe(self, data: Union[pd.Series, np.ndarray]) -> Dict[str, float]:
        """Fallback statistical description using pandas/numpy."""
        if isinstance(data, pd.Series):
            desc = data.describe()
            return {
                'count': desc['count'],
                'mean': desc['mean'],
                'std': desc['std'],
                'min': desc['min'],
                '25%': desc['25%'],
                '50%': desc['50%'],
                '75%': desc['75%'],
                'max': desc['max']
            }
        else:
            array = np.asarray(data)
            valid_data = array[~np.isnan(array)]
            if len(valid_data) == 0:
                return {}
            
            return {
                'count': len(valid_data),
                'mean': np.mean(valid_data),
                'std': np.std(valid_data),
                'min': np.min(valid_data),
                '25%': np.percentile(valid_data, 25),
                '50%': np.percentile(valid_data, 50),
                '75%': np.percentile(valid_data, 75),
                'max': np.max(valid_data)
            }
    
    def _fallback_correlation_matrix(self, 
                                   df: pd.DataFrame, 
                                   method: str = "pearson") -> np.ndarray:
        """Fallback correlation matrix using pandas."""
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.corr(method=method).to_numpy()
    
    def _fallback_missing_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Fallback missing analysis using pandas."""
        missing_count = df.isnull().sum()
        total_cells = df.shape[0] * df.shape[1]
        total_missing = missing_count.sum()
        
        return {
            'column_missing': missing_count.tolist(),
            'total_missing': total_missing,
            'missing_percentage': (total_missing / total_cells) * 100.0,
            'column_names': list(df.columns)
        }
    
    def _fallback_outlier_detection(self, 
                                  data: Union[pd.Series, np.ndarray],
                                  method: str = "iqr",
                                  threshold: float = 1.5) -> Dict[str, Any]:
        """Fallback outlier detection using numpy."""
        if isinstance(data, pd.Series):
            array = data.to_numpy()
        else:
            array = np.asarray(data)
        
        valid_data = array[~np.isnan(array)]
        
        if method == "iqr":
            q1, q3 = np.percentile(valid_data, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            outliers = (valid_data < lower_bound) | (valid_data > upper_bound)
        elif method == "zscore":
            z_scores = np.abs((valid_data - np.mean(valid_data)) / np.std(valid_data))
            outliers = z_scores > threshold
        else:
            outliers = np.array([])
        
        return {
            'outlier_count': np.sum(outliers),
            'outlier_percentage': (np.sum(outliers) / len(valid_data)) * 100.0,
            'outlier_indices': np.where(outliers)[0].tolist()
        }
    
    def _fallback_profile_numeric(self, 
                                data: Union[pd.Series, np.ndarray],
                                column_name: str) -> Dict[str, Any]:
        """Fallback numeric profiling using pandas/numpy."""
        if isinstance(data, pd.Series):
            series = data
        else:
            series = pd.Series(data)
        
        desc = series.describe()
        return {
            'column_name': column_name,
            'dtype': 'numeric',
            'count': desc['count'],
            'missing_count': series.isnull().sum(),
            'missing_percentage': (series.isnull().sum() / len(series)) * 100.0,
            'unique_count': series.nunique(),
            'mean': desc['mean'],
            'std': desc['std'],
            'min': desc['min'],
            'max': desc['max'],
            'range': desc['max'] - desc['min'],
            'skewness': series.skew(),
            'kurtosis': series.kurtosis(),
            '25%': desc['25%'],
            '50%': desc['50%'],
            '75%': desc['75%']
        }
    
    def _fallback_profile_categorical(self, 
                                    data: Union[pd.Series, List[str]],
                                    column_name: str) -> Dict[str, Any]:
        """Fallback categorical profiling using pandas."""
        if isinstance(data, pd.Series):
            series = data
        else:
            series = pd.Series(data)
        
        value_counts = series.value_counts()
        
        return {
            'column_name': column_name,
            'dtype': 'categorical',
            'count': len(series),
            'unique_count': series.nunique(),
            'cardinality_ratio': series.nunique() / len(series),
            'mode': value_counts.index[0] if len(value_counts) > 0 else None,
            'mode_count': value_counts.iloc[0] if len(value_counts) > 0 else 0,
            'top_values': [
                {'value': str(val), 'count': count, 'frequency': count / len(series)}
                for val, count in value_counts.head(10).items()
            ]
        }
    
    def _fallback_cramers_v(self, 
                          x: Union[pd.Series, List[str]], 
                          y: Union[pd.Series, List[str]]) -> float:
        """Fallback Cramér's V using pandas."""
        try:
            from scipy.stats import chi2_contingency
            
            if isinstance(x, pd.Series):
                x_data = x
            else:
                x_data = pd.Series(x)
            
            if isinstance(y, pd.Series):
                y_data = y
            else:
                y_data = pd.Series(y)
            
            # Create contingency table
            crosstab = pd.crosstab(x_data, y_data)
            
            # Calculate chi-square
            chi2, _, _, _ = chi2_contingency(crosstab)
            
            # Calculate Cramér's V
            n = crosstab.sum().sum()
            k = min(crosstab.shape) - 1
            
            if k == 0:
                return 0.0
            
            return np.sqrt(chi2 / (n * k))
            
        except ImportError:
            warnings.warn("scipy not available, cannot calculate Cramér's V")
            return np.nan


# Global instance
rust_accelerated = RustAccelerated()
