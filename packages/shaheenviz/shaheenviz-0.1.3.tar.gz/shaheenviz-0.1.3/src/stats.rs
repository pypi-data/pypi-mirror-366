use pyo3::prelude::*;
use numpy::{PyArray1, PyReadonlyArray1};
use ndarray::{Array1, ArrayView1};
use rayon::prelude::*;
use std::collections::HashMap;
use statrs::statistics::{Statistics, OrderStatistics};

/// Fast statistical description computation using Rust
#[pyfunction]
pub fn fast_describe(py: Python, data: PyReadonlyArray1<f64>) -> PyResult<PyObject> {
    let array = data.as_array();
    
    // Filter out NaN values
    let valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    if valid_data.is_empty() {
        return Ok(py.None());
    }
    
    let count = valid_data.len() as f64;
    let mean = valid_data.iter().sum::<f64>() / count;
    let std = valid_data.std_dev();
    let min = valid_data.iter().fold(f64::INFINITY, |a, &b| a.min(b));
    let max = valid_data.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
    
    // Calculate percentiles
    let mut sorted_data = valid_data.clone();
    sorted_data.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let percentiles = vec![0.25, 0.5, 0.75];
    let mut quantile_values = Vec::new();
    
    for &p in &percentiles {
        let idx = (p * (count - 1.0)) as usize;
        quantile_values.push(sorted_data[idx]);
    }
    
    let result = HashMap::from([
        ("count", count),
        ("mean", mean),
        ("std", std),
        ("min", min),
        ("25%", quantile_values[0]),
        ("50%", quantile_values[1]),
        ("75%", quantile_values[2]),
        ("max", max),
    ]);
    
    Ok(result.to_object(py))
}

/// Fast quantile computation
#[pyfunction]
pub fn fast_quantiles(
    py: Python,
    data: PyReadonlyArray1<f64>,
    quantiles: Vec<f64>
) -> PyResult<PyObject> {
    let array = data.as_array();
    
    let valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    if valid_data.is_empty() {
        return Ok(py.None());
    }
    
    let mut sorted_data = valid_data.clone();
    sorted_data.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let count = sorted_data.len() as f64;
    let mut results = Vec::new();
    
    for &q in &quantiles {
        let idx = (q * (count - 1.0)) as usize;
        results.push(sorted_data[idx.min(sorted_data.len() - 1)]);
    }
    
    Ok(PyArray1::from_vec(py, results).to_object(py))
}

/// Fast skewness calculation
#[pyfunction]
pub fn fast_skewness(py: Python, data: PyReadonlyArray1<f64>) -> PyResult<f64> {
    let array = data.as_array();
    
    let valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    if valid_data.len() < 3 {
        return Ok(f64::NAN);
    }
    
    let n = valid_data.len() as f64;
    let mean = valid_data.iter().sum::<f64>() / n;
    let std = valid_data.std_dev();
    
    if std == 0.0 {
        return Ok(f64::NAN);
    }
    
    let skewness = valid_data.par_iter()
        .map(|&x| ((x - mean) / std).powi(3))
        .sum::<f64>() / n;
    
    Ok(skewness)
}

/// Fast kurtosis calculation
#[pyfunction]
pub fn fast_kurtosis(py: Python, data: PyReadonlyArray1<f64>) -> PyResult<f64> {
    let array = data.as_array();
    
    let valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    if valid_data.len() < 4 {
        return Ok(f64::NAN);
    }
    
    let n = valid_data.len() as f64;
    let mean = valid_data.iter().sum::<f64>() / n;
    let std = valid_data.std_dev();
    
    if std == 0.0 {
        return Ok(f64::NAN);
    }
    
    let kurtosis = valid_data.par_iter()
        .map(|&x| ((x - mean) / std).powi(4))
        .sum::<f64>() / n - 3.0; // Excess kurtosis
    
    Ok(kurtosis)
}

/// Fast mode calculation for numeric data
#[pyfunction]
pub fn fast_mode(py: Python, data: PyReadonlyArray1<f64>) -> PyResult<PyObject> {
    let array = data.as_array();
    
    let valid_data: Vec<f64> = array.iter()
        .filter(|&&x| !x.is_nan())
        .copied()
        .collect();
    
    if valid_data.is_empty() {
        return Ok(py.None());
    }
    
    let mut frequency_map: HashMap<OrderedF64, usize> = HashMap::new();
    
    for &value in &valid_data {
        *frequency_map.entry(OrderedF64(value)).or_insert(0) += 1;
    }
    
    let mode = frequency_map
        .into_iter()
        .max_by_key(|&(_, count)| count)
        .map(|(OrderedF64(value), _)| value);
    
    Ok(mode.to_object(py))
}

// Helper struct for ordering f64 values in HashMap
#[derive(Hash, Eq, PartialEq, Clone, Copy)]
struct OrderedF64(f64);

impl OrderedF64 {
    fn key(&self) -> u64 {
        self.0.to_bits()
    }
}

impl std::cmp::Ord for OrderedF64 {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.key().cmp(&other.key())
    }
}

impl std::cmp::PartialOrd for OrderedF64 {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}
