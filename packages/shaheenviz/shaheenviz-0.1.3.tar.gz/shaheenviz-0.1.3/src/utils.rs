use pyo3::prelude::*;
use numpy::{PyArray1, PyReadonlyArray1};
use rayon::prelude::*;
use std::collections::HashMap;

/// Fast histogram computation
#[pyfunction]
pub fn fast_histogram(
    py: Python,
    data: PyReadonlyArray1<f64>,
    bins: usize
) -> PyResult<PyObject> {
    let array = data.as_array();
    
    let valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    if valid_data.is_empty() {
        return Ok(py.None());
    }
    
    let min_val = valid_data.iter().fold(f64::INFINITY, |a, &b| a.min(b));
    let max_val = valid_data.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
    
    if min_val == max_val {
        // All values are the same
        let mut counts = vec![0; bins];
        counts[0] = valid_data.len();
        let edges: Vec<f64> = (0..=bins).map(|i| min_val + i as f64 * 0.1).collect();
        
        let result = pyo3::types::PyDict::new(py);
        result.set_item("counts", PyArray1::from_vec(py, counts))?;
        result.set_item("edges", PyArray1::from_vec(py, edges))?;
        return Ok(result.to_object(py));
    }
    
    let bin_width = (max_val - min_val) / bins as f64;
    let mut counts = vec![0; bins];
    
    // Count values in each bin
    for &value in &valid_data {
        let bin_index = ((value - min_val) / bin_width).floor() as usize;
        let bin_index = bin_index.min(bins - 1);
        counts[bin_index] += 1;
    }
    
    // Create bin edges
    let edges: Vec<f64> = (0..=bins)
        .map(|i| min_val + i as f64 * bin_width)
        .collect();
    
    let result = pyo3::types::PyDict::new(py);
    result.set_item("counts", PyArray1::from_vec(py, counts))?;
    result.set_item("edges", PyArray1::from_vec(py, edges))?;
    
    Ok(result.to_object(py))
}

/// Fast value counts for categorical data
#[pyfunction]
pub fn fast_value_counts(
    py: Python,
    data: Vec<String>,
    normalize: bool
) -> PyResult<PyObject> {
    if data.is_empty() {
        return Ok(py.None());
    }
    
    let mut counts = HashMap::new();
    let total_count = data.len();
    
    for value in &data {
        *counts.entry(value.clone()).or_insert(0) += 1;
    }
    
    let mut sorted_counts: Vec<(String, usize)> = counts.into_iter().collect();
    sorted_counts.sort_by(|a, b| b.1.cmp(&a.1));
    
    let result = pyo3::types::PyDict::new(py);
    
    for (value, count) in sorted_counts {
        if normalize {
            result.set_item(value, count as f64 / total_count as f64)?;
        } else {
            result.set_item(value, count)?;
        }
    }
    
    Ok(result.to_object(py))
}

/// Fast percentile computation
#[pyfunction]
pub fn fast_percentile(
    py: Python,
    data: PyReadonlyArray1<f64>,
    percentile: f64
) -> PyResult<f64> {
    let array = data.as_array();
    
    let mut valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    if valid_data.is_empty() {
        return Ok(f64::NAN);
    }
    
    valid_data.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let n = valid_data.len() as f64;
    let index = (percentile / 100.0) * (n - 1.0);
    
    if index == index.floor() {
        Ok(valid_data[index as usize])
    } else {
        let lower = index.floor() as usize;
        let upper = index.ceil() as usize;
        let weight = index - index.floor();
        Ok(valid_data[lower] * (1.0 - weight) + valid_data[upper] * weight)
    }
}

/// Fast data type inference
#[pyfunction]
pub fn fast_infer_dtype(
    py: Python,
    data: Vec<String>
) -> PyResult<String> {
    if data.is_empty() {
        return Ok("unknown".to_string());
    }
    
    let sample_size = data.len().min(1000);
    let sample: Vec<&String> = data.iter().take(sample_size).collect();
    
    let mut numeric_count = 0;
    let mut integer_count = 0;
    let mut boolean_count = 0;
    let mut date_count = 0;
    
    for value in &sample {
        if value.is_empty() {
            continue;
        }
        
        // Check if boolean
        if value.to_lowercase() == "true" || value.to_lowercase() == "false" ||
           value == "1" || value == "0" || value.to_lowercase() == "yes" || value.to_lowercase() == "no" {
            boolean_count += 1;
            continue;
        }
        
        // Check if numeric
        if let Ok(float_val) = value.parse::<f64>() {
            numeric_count += 1;
            if float_val.fract() == 0.0 {
                integer_count += 1;
            }
            continue;
        }
        
        // Check if date-like (very basic check)
        if is_date_like(value) {
            date_count += 1;
            continue;
        }
    }
    
    let total_valid = sample.len();
    let numeric_ratio = numeric_count as f64 / total_valid as f64;
    let integer_ratio = integer_count as f64 / total_valid as f64;
    let boolean_ratio = boolean_count as f64 / total_valid as f64;
    let date_ratio = date_count as f64 / total_valid as f64;
    
    if boolean_ratio > 0.8 {
        Ok("boolean".to_string())
    } else if date_ratio > 0.8 {
        Ok("datetime".to_string())
    } else if integer_ratio > 0.8 {
        Ok("integer".to_string())
    } else if numeric_ratio > 0.8 {
        Ok("float".to_string())
    } else {
        Ok("string".to_string())
    }
}

/// Fast entropy calculation for categorical data
#[pyfunction]
pub fn fast_entropy(
    py: Python,
    data: Vec<String>
) -> PyResult<f64> {
    if data.is_empty() {
        return Ok(0.0);
    }
    
    let mut counts = HashMap::new();
    for value in &data {
        *counts.entry(value.clone()).or_insert(0) += 1;
    }
    
    let total = data.len() as f64;
    let entropy = counts.values()
        .map(|&count| {
            let p = count as f64 / total;
            -p * p.log2()
        })
        .sum();
    
    Ok(entropy)
}

/// Fast z-score calculation
#[pyfunction]
pub fn fast_zscore(
    py: Python,
    data: PyReadonlyArray1<f64>
) -> PyResult<PyObject> {
    let array = data.as_array();
    
    let valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    if valid_data.is_empty() {
        return Ok(py.None());
    }
    
    let n = valid_data.len() as f64;
    let mean = valid_data.iter().sum::<f64>() / n;
    let variance = valid_data.iter()
        .map(|x| (x - mean).powi(2))
        .sum::<f64>() / n;
    let std_dev = variance.sqrt();
    
    if std_dev == 0.0 {
        let zeros = vec![0.0; valid_data.len()];
        return Ok(PyArray1::from_vec(py, zeros).to_object(py));
    }
    
    let z_scores: Vec<f64> = valid_data.par_iter()
        .map(|&x| (x - mean) / std_dev)
        .collect();
    
    Ok(PyArray1::from_vec(py, z_scores).to_object(py))
}

/// Fast rolling statistics
#[pyfunction]
pub fn fast_rolling_mean(
    py: Python,
    data: PyReadonlyArray1<f64>,
    window: usize
) -> PyResult<PyObject> {
    let array = data.as_array();
    
    if array.len() < window || window == 0 {
        return Ok(py.None());
    }
    
    let mut rolling_means = Vec::new();
    let mut window_sum = 0.0;
    let mut valid_count = 0;
    
    // Initialize first window
    for i in 0..window {
        if !array[i].is_nan() {
            window_sum += array[i];
            valid_count += 1;
        }
    }
    
    if valid_count > 0 {
        rolling_means.push(window_sum / valid_count as f64);
    } else {
        rolling_means.push(f64::NAN);
    }
    
    // Slide the window
    for i in window..array.len() {
        // Remove the element going out of window
        if !array[i - window].is_nan() {
            window_sum -= array[i - window];
            valid_count -= 1;
        }
        
        // Add the new element
        if !array[i].is_nan() {
            window_sum += array[i];
            valid_count += 1;
        }
        
        if valid_count > 0 {
            rolling_means.push(window_sum / valid_count as f64);
        } else {
            rolling_means.push(f64::NAN);
        }
    }
    
    Ok(PyArray1::from_vec(py, rolling_means).to_object(py))
}

// Helper functions

fn is_date_like(s: &str) -> bool {
    // Very basic date pattern matching
    let date_patterns = [
        r"\d{4}-\d{2}-\d{2}",  // YYYY-MM-DD
        r"\d{2}/\d{2}/\d{4}",  // MM/DD/YYYY
        r"\d{2}-\d{2}-\d{4}",  // MM-DD-YYYY
    ];
    
    date_patterns.iter().any(|pattern| {
        // Simple pattern matching without regex for basic cases
        match pattern {
            r"\d{4}-\d{2}-\d{2}" => {
                s.len() == 10 && 
                s.chars().nth(4) == Some('-') && 
                s.chars().nth(7) == Some('-') &&
                s.chars().take(4).all(|c| c.is_ascii_digit()) &&
                s.chars().skip(5).take(2).all(|c| c.is_ascii_digit()) &&
                s.chars().skip(8).take(2).all(|c| c.is_ascii_digit())
            },
            _ => false
        }
    })
}
