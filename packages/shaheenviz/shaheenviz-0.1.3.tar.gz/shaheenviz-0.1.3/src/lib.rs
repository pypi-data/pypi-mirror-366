//! Shaheenviz Rust Extensions
//!
//! High-performance statistical and data analysis functions for Shaheenviz.
//! This module provides Rust-accelerated implementations of common EDA operations.

use pyo3::prelude::*;
use numpy::{PyReadonlyArray1};
use std::collections::HashMap;

/// Fast statistical description of numeric data
#[pyfunction]
fn fast_describe(_py: Python, data: PyReadonlyArray1<f64>) -> PyResult<HashMap<String, f64>> {
    let array = data.as_array();
    let valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    if valid_data.is_empty() {
        return Ok(HashMap::new());
    }
    
    let n = valid_data.len() as f64;
    let sum: f64 = valid_data.iter().sum();
    let mean = sum / n;
    
    let variance = valid_data.iter()
        .map(|&x| (x - mean).powi(2))
        .sum::<f64>() / (n - 1.0);
    let std = variance.sqrt();
    
    let mut sorted_data = valid_data.clone();
    sorted_data.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let min = sorted_data[0];
    let max = sorted_data[sorted_data.len() - 1];
    
    let q25_idx = (0.25 * (sorted_data.len() - 1) as f64) as usize;
    let q50_idx = (0.50 * (sorted_data.len() - 1) as f64) as usize;
    let q75_idx = (0.75 * (sorted_data.len() - 1) as f64) as usize;
    
    let q25 = sorted_data[q25_idx];
    let q50 = sorted_data[q50_idx];
    let q75 = sorted_data[q75_idx];
    
    let mut result = HashMap::new();
    result.insert("count".to_string(), n);
    result.insert("mean".to_string(), mean);
    result.insert("std".to_string(), std);
    result.insert("min".to_string(), min);
    result.insert("25%".to_string(), q25);
    result.insert("50%".to_string(), q50);
    result.insert("75%".to_string(), q75);
    result.insert("max".to_string(), max);
    
    Ok(result)
}

/// Fast correlation matrix computation
#[pyfunction]
fn fast_correlation_matrix(_py: Python, data: PyReadonlyArray1<f64>, _method: &str) -> PyResult<Vec<f64>> {
    let array = data.as_array();
    let valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    // Simple correlation coefficient (placeholder)
    Ok(vec![1.0; valid_data.len()])
}

/// Fast missing value analysis
#[pyfunction]
fn fast_missing_analysis(_py: Python, data: PyReadonlyArray1<f64>) -> PyResult<HashMap<String, f64>> {
    let array = data.as_array();
    let total_count = array.len() as f64;
    let missing_count = array.iter().filter(|&&x| x.is_nan()).count() as f64;
    let missing_percentage = (missing_count / total_count) * 100.0;
    
    let mut result = HashMap::new();
    result.insert("total_missing".to_string(), missing_count);
    result.insert("missing_percentage".to_string(), missing_percentage);
    
    Ok(result)
}

/// Fast outlier detection using IQR method
#[pyfunction]
fn fast_outlier_detection(_py: Python, data: PyReadonlyArray1<f64>, _method: &str, threshold: f64) -> PyResult<HashMap<String, f64>> {
    let array = data.as_array();
    let mut valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    if valid_data.is_empty() {
        return Ok(HashMap::new());
    }
    
    valid_data.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let q1_idx = (0.25 * (valid_data.len() - 1) as f64) as usize;
    let q3_idx = (0.75 * (valid_data.len() - 1) as f64) as usize;
    
    let q1 = valid_data[q1_idx];
    let q3 = valid_data[q3_idx];
    let iqr = q3 - q1;
    
    let lower_bound = q1 - threshold * iqr;
    let upper_bound = q3 + threshold * iqr;
    
    let outlier_count = valid_data.iter()
        .filter(|&&x| x < lower_bound || x > upper_bound)
        .count() as f64;
    
    let outlier_percentage = (outlier_count / valid_data.len() as f64) * 100.0;
    
    let mut result = HashMap::new();
    result.insert("outlier_count".to_string(), outlier_count);
    result.insert("outlier_percentage".to_string(), outlier_percentage);
    
    Ok(result)
}

/// Fast numeric profiling
#[pyfunction]
fn fast_profile_numeric(_py: Python, data: PyReadonlyArray1<f64>, _column_name: &str) -> PyResult<HashMap<String, f64>> {
    fast_describe(_py, data)
}

/// Fast categorical profiling
#[pyfunction]
fn fast_profile_categorical(_py: Python, data: Vec<String>, _column_name: &str) -> PyResult<HashMap<String, f64>> {
    let mut result = HashMap::new();
    result.insert("count".to_string(), data.len() as f64);
    result.insert("unique_count".to_string(), data.iter().collect::<std::collections::HashSet<_>>().len() as f64);
    Ok(result)
}

/// Fast Cramér's V calculation
#[pyfunction]
fn fast_cramers_v(_py: Python, _x: Vec<String>, _y: Vec<String>) -> PyResult<f64> {
    // Placeholder implementation
    Ok(0.5)
}

/// High-performance Rust backend for Shaheenviz EDA library
#[pymodule]
fn shaheenviz_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    // Statistical functions
    m.add_function(wrap_pyfunction!(fast_describe, m)?)?;
    m.add_function(wrap_pyfunction!(fast_correlation_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(fast_missing_analysis, m)?)?;
    m.add_function(wrap_pyfunction!(fast_outlier_detection, m)?)?;
    m.add_function(wrap_pyfunction!(fast_profile_numeric, m)?)?;
    m.add_function(wrap_pyfunction!(fast_profile_categorical, m)?)?;
    m.add_function(wrap_pyfunction!(fast_cramers_v, m)?)?;
    
    Ok(())
}
