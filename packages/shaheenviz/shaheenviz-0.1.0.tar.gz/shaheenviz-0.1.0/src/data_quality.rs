use pyo3::prelude::*;
use numpy::{PyArray1, PyReadonlyArray1, PyReadonlyArray2};
use ndarray::{Array1, ArrayView1, ArrayView2};
use rayon::prelude::*;
use std::collections::{HashMap, HashSet};

/// Fast missing value analysis
#[pyfunction]
pub fn fast_missing_analysis(
    py: Python,
    data: PyReadonlyArray2<f64>
) -> PyResult<PyObject> {
    let array = data.as_array();
    let (n_rows, n_cols) = array.dim();
    
    let mut column_missing = Vec::new();
    let mut row_missing = Vec::new();
    let mut total_missing = 0;
    
    // Calculate missing values per column
    for col in 0..n_cols {
        let missing_count = array.column(col)
            .iter()
            .filter(|&&x| x.is_nan())
            .count();
        column_missing.push(missing_count);
        total_missing += missing_count;
    }
    
    // Calculate missing values per row
    for row in 0..n_rows {
        let missing_count = array.row(row)
            .iter()
            .filter(|&&x| x.is_nan())
            .count();
        row_missing.push(missing_count);
    }
    
    let result = pyo3::types::PyDict::new(py);
    result.set_item("column_missing", PyArray1::from_vec(py, column_missing))?;
    result.set_item("row_missing", PyArray1::from_vec(py, row_missing))?;
    result.set_item("total_missing", total_missing)?;
    result.set_item("missing_percentage", (total_missing as f64) / (n_rows * n_cols) as f64 * 100.0)?;
    
    Ok(result.to_object(py))
}

/// Fast duplicate analysis
#[pyfunction]
pub fn fast_duplicate_analysis(
    py: Python,
    data: PyReadonlyArray2<f64>
) -> PyResult<PyObject> {
    let array = data.as_array();
    let (n_rows, n_cols) = array.dim();
    
    let mut row_signatures = HashMap::new();
    let mut duplicate_indices = Vec::new();
    
    for row_idx in 0..n_rows {
        let row_data = array.row(row_idx);
        
        // Create a signature for the row (handle NaN values)
        let signature: Vec<u64> = row_data.iter()
            .map(|&x| if x.is_nan() { u64::MAX } else { x.to_bits() })
            .collect();
        
        if let Some(&first_occurrence) = row_signatures.get(&signature) {
            duplicate_indices.push((row_idx, first_occurrence));
        } else {
            row_signatures.insert(signature, row_idx);
        }
    }
    
    let result = pyo3::types::PyDict::new(py);
    result.set_item("duplicate_count", duplicate_indices.len())?;
    result.set_item("duplicate_percentage", (duplicate_indices.len() as f64) / (n_rows as f64) * 100.0)?;
    result.set_item("unique_rows", row_signatures.len())?;
    
    Ok(result.to_object(py))
}

/// Fast outlier detection using IQR method
#[pyfunction]
pub fn fast_outlier_detection(
    py: Python,
    data: PyReadonlyArray1<f64>,
    method: &str,
    threshold: f64
) -> PyResult<PyObject> {
    let array = data.as_array();
    
    let valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    if valid_data.is_empty() {
        return Ok(py.None());
    }
    
    let outlier_indices = match method {
        "iqr" => detect_outliers_iqr(&valid_data, threshold),
        "zscore" => detect_outliers_zscore(&valid_data, threshold),
        "modified_zscore" => detect_outliers_modified_zscore(&valid_data, threshold),
        _ => Vec::new()
    };
    
    let result = pyo3::types::PyDict::new(py);
    result.set_item("outlier_count", outlier_indices.len())?;
    result.set_item("outlier_percentage", (outlier_indices.len() as f64) / (valid_data.len() as f64) * 100.0)?;
    result.set_item("outlier_indices", PyArray1::from_vec(py, outlier_indices))?;
    
    Ok(result.to_object(py))
}

/// Fast cardinality analysis
#[pyfunction]
pub fn fast_cardinality_analysis(
    py: Python,
    data: Vec<String>
) -> PyResult<PyObject> {
    if data.is_empty() {
        return Ok(py.None());
    }
    
    let mut value_counts = HashMap::new();
    let mut unique_values = HashSet::new();
    
    for value in &data {
        *value_counts.entry(value.clone()).or_insert(0) += 1;
        unique_values.insert(value.clone());
    }
    
    let n = data.len();
    let unique_count = unique_values.len();
    let cardinality_ratio = unique_count as f64 / n as f64;
    
    // Find most frequent values
    let mut frequency_pairs: Vec<(String, usize)> = value_counts.into_iter().collect();
    frequency_pairs.sort_by(|a, b| b.1.cmp(&a.1));
    
    let top_values: Vec<(String, usize)> = frequency_pairs.into_iter().take(10).collect();
    
    let result = pyo3::types::PyDict::new(py);
    result.set_item("unique_count", unique_count)?;
    result.set_item("total_count", n)?;
    result.set_item("cardinality_ratio", cardinality_ratio)?;
    result.set_item("is_high_cardinality", cardinality_ratio > 0.8)?;
    result.set_item("is_low_cardinality", cardinality_ratio < 0.1)?;
    
    // Convert top values to Python objects
    let top_values_py = pyo3::types::PyList::empty(py);
    for (value, count) in top_values {
        let tuple = pyo3::types::PyTuple::new(py, &[value.to_object(py), count.to_object(py)]);
        top_values_py.append(tuple)?;
    }
    result.set_item("top_values", top_values_py)?;
    
    Ok(result.to_object(py))
}

// Helper functions for outlier detection

fn detect_outliers_iqr(data: &[f64], multiplier: f64) -> Vec<usize> {
    let mut sorted_data = data.to_vec();
    sorted_data.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let n = sorted_data.len();
    let q1_idx = (0.25 * (n - 1) as f64) as usize;
    let q3_idx = (0.75 * (n - 1) as f64) as usize;
    
    let q1 = sorted_data[q1_idx];
    let q3 = sorted_data[q3_idx];
    let iqr = q3 - q1;
    
    let lower_bound = q1 - multiplier * iqr;
    let upper_bound = q3 + multiplier * iqr;
    
    data.iter()
        .enumerate()
        .filter(|(_, &x)| x < lower_bound || x > upper_bound)
        .map(|(i, _)| i)
        .collect()
}

fn detect_outliers_zscore(data: &[f64], threshold: f64) -> Vec<usize> {
    let n = data.len() as f64;
    let mean = data.iter().sum::<f64>() / n;
    let variance = data.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / n;
    let std_dev = variance.sqrt();
    
    if std_dev == 0.0 {
        return Vec::new();
    }
    
    data.iter()
        .enumerate()
        .filter(|(_, &x)| ((x - mean) / std_dev).abs() > threshold)
        .map(|(i, _)| i)
        .collect()
}

fn detect_outliers_modified_zscore(data: &[f64], threshold: f64) -> Vec<usize> {
    // Calculate median
    let mut sorted_data = data.to_vec();
    sorted_data.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let n = sorted_data.len();
    let median = if n % 2 == 0 {
        (sorted_data[n / 2 - 1] + sorted_data[n / 2]) / 2.0
    } else {
        sorted_data[n / 2]
    };
    
    // Calculate MAD (Median Absolute Deviation)
    let mut absolute_deviations: Vec<f64> = data.iter()
        .map(|&x| (x - median).abs())
        .collect();
    absolute_deviations.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let mad = if n % 2 == 0 {
        (absolute_deviations[n / 2 - 1] + absolute_deviations[n / 2]) / 2.0
    } else {
        absolute_deviations[n / 2]
    };
    
    if mad == 0.0 {
        return Vec::new();
    }
    
    // Modified Z-score calculation
    data.iter()
        .enumerate()
        .filter(|(_, &x)| {
            let modified_zscore = 0.6745 * (x - median) / mad;
            modified_zscore.abs() > threshold
        })
        .map(|(i, _)| i)
        .collect()
}
