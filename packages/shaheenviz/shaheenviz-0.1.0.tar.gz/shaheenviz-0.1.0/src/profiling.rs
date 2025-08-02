use pyo3::prelude::*;
use numpy::{PyArray1, PyReadonlyArray1};
use std::collections::HashMap;
use rayon::prelude::*;

/// Fast numeric column profiling
#[pyfunction]
pub fn fast_profile_numeric(
    py: Python,
    data: PyReadonlyArray1<f64>,
    column_name: String
) -> PyResult<PyObject> {
    let array = data.as_array();
    
    let valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    if valid_data.is_empty() {
        return Ok(py.None());
    }
    
    let n = valid_data.len();
    let n_missing = array.len() - n;
    
    // Basic statistics
    let sum = valid_data.par_iter().sum::<f64>();
    let mean = sum / n as f64;
    
    let variance = valid_data.par_iter()
        .map(|&x| (x - mean).powi(2))
        .sum::<f64>() / n as f64;
    let std_dev = variance.sqrt();
    
    let min = valid_data.par_iter().fold(|| f64::INFINITY, |a, &b| a.min(b)).reduce(|| f64::INFINITY, f64::min);
    let max = valid_data.par_iter().fold(|| f64::NEG_INFINITY, |a, &b| a.max(b)).reduce(|| f64::NEG_INFINITY, f64::max);
    
    // Quantiles
    let mut sorted_data = valid_data.clone();
    sorted_data.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let quantiles = calculate_quantiles(&sorted_data, &[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]);
    
    // Skewness and kurtosis
    let skewness = if std_dev > 0.0 {
        valid_data.par_iter()
            .map(|&x| ((x - mean) / std_dev).powi(3))
            .sum::<f64>() / n as f64
    } else {
        f64::NAN
    };
    
    let kurtosis = if std_dev > 0.0 {
        valid_data.par_iter()
            .map(|&x| ((x - mean) / std_dev).powi(4))
            .sum::<f64>() / n as f64 - 3.0 // Excess kurtosis
    } else {
        f64::NAN
    };
    
    // Unique values and mode
    let unique_count = count_unique_numeric(&valid_data);
    let mode = find_mode_numeric(&valid_data);
    
    // Create result dictionary
    let result = pyo3::types::PyDict::new(py);
    result.set_item("column_name", column_name)?;
    result.set_item("dtype", "numeric")?;
    result.set_item("count", n)?;
    result.set_item("missing_count", n_missing)?;
    result.set_item("missing_percentage", (n_missing as f64) / (array.len() as f64) * 100.0)?;
    result.set_item("unique_count", unique_count)?;
    result.set_item("mean", mean)?;
    result.set_item("std", std_dev)?;
    result.set_item("min", min)?;
    result.set_item("max", max)?;
    result.set_item("range", max - min)?;
    result.set_item("skewness", skewness)?;
    result.set_item("kurtosis", kurtosis)?;
    result.set_item("sum", sum)?;
    result.set_item("variance", variance)?;
    
    // Add quantiles
    let quantile_names = ["1%", "5%", "25%", "50%", "75%", "95%", "99%"];
    for (i, &name) in quantile_names.iter().enumerate() {
        result.set_item(name, quantiles[i])?;
    }
    
    if let Some(mode_val) = mode {
        result.set_item("mode", mode_val)?;
    }
    
    Ok(result.to_object(py))
}

/// Fast categorical column profiling
#[pyfunction]
pub fn fast_profile_categorical(
    py: Python,
    data: Vec<String>,
    column_name: String
) -> PyResult<PyObject> {
    if data.is_empty() {
        return Ok(py.None());
    }
    
    let n = data.len();
    let mut value_counts = HashMap::new();
    let mut total_length = 0;
    let mut lengths = Vec::new();
    
    // Count values and calculate string statistics
    for value in &data {
        if !value.is_empty() {
            *value_counts.entry(value.clone()).or_insert(0) += 1;
            total_length += value.len();
            lengths.push(value.len());
        }
    }
    
    let unique_count = value_counts.len();
    let most_frequent = value_counts.iter()
        .max_by_key(|&(_, count)| count)
        .map(|(value, count)| (value.clone(), *count));
    
    // Calculate string length statistics
    let mean_length = if !lengths.is_empty() {
        total_length as f64 / lengths.len() as f64
    } else {
        0.0
    };
    
    lengths.sort_unstable();
    let min_length = lengths.first().copied().unwrap_or(0);
    let max_length = lengths.last().copied().unwrap_or(0);
    let median_length = if !lengths.is_empty() {
        let mid = lengths.len() / 2;
        if lengths.len() % 2 == 0 && mid > 0 {
            (lengths[mid - 1] + lengths[mid]) as f64 / 2.0
        } else {
            lengths[mid] as f64
        }
    } else {
        0.0
    };
    
    // Top values (sorted by frequency)
    let mut sorted_counts: Vec<(String, usize)> = value_counts.into_iter().collect();
    sorted_counts.sort_by(|a, b| b.1.cmp(&a.1));
    let top_values: Vec<(String, usize)> = sorted_counts.into_iter().take(10).collect();
    
    // Create result dictionary
    let result = pyo3::types::PyDict::new(py);
    result.set_item("column_name", column_name)?;
    result.set_item("dtype", "categorical")?;
    result.set_item("count", n)?;
    result.set_item("unique_count", unique_count)?;
    result.set_item("cardinality_ratio", unique_count as f64 / n as f64)?;
    result.set_item("mean_length", mean_length)?;
    result.set_item("min_length", min_length)?;
    result.set_item("max_length", max_length)?;
    result.set_item("median_length", median_length)?;
    
    if let Some((mode_value, mode_count)) = most_frequent {
        result.set_item("mode", mode_value)?;
        result.set_item("mode_count", mode_count)?;
        result.set_item("mode_frequency", mode_count as f64 / n as f64)?;
    }
    
    // Convert top values to Python objects
    let top_values_py = pyo3::types::PyList::empty(py);
    for (value, count) in top_values {
        let item = pyo3::types::PyDict::new(py);
        item.set_item("value", value)?;
        item.set_item("count", count)?;
        item.set_item("frequency", count as f64 / n as f64)?;
        top_values_py.append(item)?;
    }
    result.set_item("top_values", top_values_py)?;
    
    Ok(result.to_object(py))
}

/// Fast dataset summary
#[pyfunction]
pub fn fast_dataset_summary(
    py: Python,
    numeric_data: PyReadonlyArray2<f64>,
    column_names: Vec<String>,
    categorical_columns: Vec<(String, Vec<String>)>
) -> PyResult<PyObject> {
    let array = numeric_data.as_array();
    let (n_rows, n_cols) = array.dim();
    
    // Overall statistics
    let total_cells = n_rows * n_cols;
    let mut total_missing = 0;
    
    // Count missing values in numeric columns
    for col in 0..n_cols {
        total_missing += array.column(col)
            .iter()
            .filter(|&&x| x.is_nan())
            .count();
    }
    
    // Calculate memory usage estimate (rough)
    let numeric_memory = (n_rows * n_cols * 8) as f64; // 8 bytes per f64
    let categorical_memory: usize = categorical_columns.iter()
        .map(|(_, values)| values.iter().map(|s| s.len()).sum::<usize>())
        .sum();
    
    let total_memory = numeric_memory + categorical_memory as f64;
    
    // Column type distribution
    let n_categorical = categorical_columns.len();
    let n_numeric = n_cols;
    
    // Duplicate analysis for numeric data
    let mut unique_rows = std::collections::HashSet::new();
    for row in 0..n_rows {
        let row_signature: Vec<u64> = array.row(row)
            .iter()
            .map(|&x| if x.is_nan() { u64::MAX } else { x.to_bits() })
            .collect();
        unique_rows.insert(row_signature);
    }
    
    let n_duplicates = n_rows - unique_rows.len();
    
    // Create result dictionary
    let result = pyo3::types::PyDict::new(py);
    result.set_item("n_rows", n_rows)?;
    result.set_item("n_columns", n_numeric + n_categorical)?;
    result.set_item("n_numeric_columns", n_numeric)?;
    result.set_item("n_categorical_columns", n_categorical)?;
    result.set_item("total_cells", total_cells + categorical_columns.iter().map(|(_, v)| v.len()).sum::<usize>())?;
    result.set_item("missing_cells", total_missing)?;
    result.set_item("missing_percentage", (total_missing as f64) / (total_cells as f64) * 100.0)?;
    result.set_item("duplicate_rows", n_duplicates)?;
    result.set_item("duplicate_percentage", (n_duplicates as f64) / (n_rows as f64) * 100.0)?;
    result.set_item("memory_usage_bytes", total_memory as u64)?;
    result.set_item("memory_usage_mb", total_memory / (1024.0 * 1024.0))?;
    
    Ok(result.to_object(py))
}

// Helper functions

fn calculate_quantiles(sorted_data: &[f64], quantiles: &[f64]) -> Vec<f64> {
    let n = sorted_data.len();
    quantiles.iter()
        .map(|&q| {
            let index = q * (n - 1) as f64;
            let lower = index.floor() as usize;
            let upper = index.ceil() as usize;
            
            if lower == upper {
                sorted_data[lower]
            } else if upper < n {
                let weight = index - lower as f64;
                sorted_data[lower] * (1.0 - weight) + sorted_data[upper] * weight
            } else {
                sorted_data[n - 1]
            }
        })
        .collect()
}

fn count_unique_numeric(data: &[f64]) -> usize {
    let mut unique_values = std::collections::HashSet::new();
    for &value in data {
        unique_values.insert(value.to_bits());
    }
    unique_values.len()
}

fn find_mode_numeric(data: &[f64]) -> Option<f64> {
    let mut frequency_map = HashMap::new();
    
    for &value in data {
        *frequency_map.entry(value.to_bits()).or_insert(0) += 1;
    }
    
    frequency_map.into_iter()
        .max_by_key(|&(_, count)| count)
        .map(|(bits, _)| f64::from_bits(bits))
}
