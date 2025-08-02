use pyo3::prelude::*;
use numpy::{PyArray1, PyArray2, PyReadonlyArray1, PyReadonlyArray2};
use ndarray::{Array1, Array2, ArrayView1, ArrayView2, Axis};
use rayon::prelude::*;
use std::collections::HashMap;

/// Fast Pearson correlation coefficient calculation
#[pyfunction]
pub fn fast_pearson_correlation(
    py: Python,
    x: PyReadonlyArray1<f64>,
    y: PyReadonlyArray1<f64>
) -> PyResult<f64> {
    let x_array = x.as_array();
    let y_array = y.as_array();
    
    if x_array.len() != y_array.len() {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Arrays must have the same length"
        ));
    }
    
    // Filter out pairs where either value is NaN
    let valid_pairs: Vec<(f64, f64)> = x_array.iter()
        .zip(y_array.iter())
        .filter(|(&x_val, &y_val)| !x_val.is_nan() && !y_val.is_nan())
        .map(|(&x_val, &y_val)| (x_val, y_val))
        .collect();
    
    if valid_pairs.len() < 2 {
        return Ok(f64::NAN);
    }
    
    let n = valid_pairs.len() as f64;
    let x_mean = valid_pairs.iter().map(|(x, _)| x).sum::<f64>() / n;
    let y_mean = valid_pairs.iter().map(|(_, y)| y).sum::<f64>() / n;
    
    let (numerator, x_var, y_var) = valid_pairs.par_iter()
        .map(|&(x, y)| {
            let x_diff = x - x_mean;
            let y_diff = y - y_mean;
            (x_diff * y_diff, x_diff * x_diff, y_diff * y_diff)
        })
        .reduce(|| (0.0, 0.0, 0.0), |a, b| (a.0 + b.0, a.1 + b.1, a.2 + b.2));
    
    let denominator = (x_var * y_var).sqrt();
    
    if denominator == 0.0 {
        Ok(0.0)
    } else {
        Ok(numerator / denominator)
    }
}

/// Fast Spearman correlation coefficient calculation
#[pyfunction]
pub fn fast_spearman_correlation(
    py: Python,
    x: PyReadonlyArray1<f64>,
    y: PyReadonlyArray1<f64>
) -> PyResult<f64> {
    let x_array = x.as_array();
    let y_array = y.as_array();
    
    if x_array.len() != y_array.len() {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Arrays must have the same length"
        ));
    }
    
    // Filter out pairs where either value is NaN
    let valid_pairs: Vec<(f64, f64)> = x_array.iter()
        .zip(y_array.iter())
        .filter(|(&x_val, &y_val)| !x_val.is_nan() && !y_val.is_nan())
        .map(|(&x_val, &y_val)| (x_val, y_val))
        .collect();
    
    if valid_pairs.len() < 2 {
        return Ok(f64::NAN);
    }
    
    // Rank the values
    let x_ranks = rank_values(&valid_pairs.iter().map(|(x, _)| *x).collect::<Vec<_>>());
    let y_ranks = rank_values(&valid_pairs.iter().map(|(_, y)| *y).collect::<Vec<_>>());
    
    // Calculate Pearson correlation on ranks
    let n = x_ranks.len() as f64;
    let x_mean = x_ranks.iter().sum::<f64>() / n;
    let y_mean = y_ranks.iter().sum::<f64>() / n;
    
    let (numerator, x_var, y_var) = x_ranks.par_iter()
        .zip(y_ranks.par_iter())
        .map(|(&x, &y)| {
            let x_diff = x - x_mean;
            let y_diff = y - y_mean;
            (x_diff * y_diff, x_diff * x_diff, y_diff * y_diff)
        })
        .reduce(|| (0.0, 0.0, 0.0), |a, b| (a.0 + b.0, a.1 + b.1, a.2 + b.2));
    
    let denominator = (x_var * y_var).sqrt();
    
    if denominator == 0.0 {
        Ok(0.0)
    } else {
        Ok(numerator / denominator)
    }
}

/// Fast correlation matrix calculation
#[pyfunction]
pub fn fast_correlation_matrix(
    py: Python,
    data: PyReadonlyArray2<f64>,
    method: &str
) -> PyResult<PyObject> {
    let array = data.as_array();
    let (n_rows, n_cols) = array.dim();
    
    let mut correlation_matrix = Array2::zeros((n_cols, n_cols));
    
    // Calculate correlations in parallel
    let correlations: Vec<(usize, usize, f64)> = (0..n_cols)
        .into_par_iter()
        .flat_map(|i| {
            (i..n_cols).into_par_iter().map(move |j| {
                let col_i = array.column(i).to_owned();
                let col_j = array.column(j).to_owned();
                
                let corr = if i == j {
                    1.0
                } else {
                    match method {
                        "pearson" => {
                            calculate_pearson(&col_i.to_vec(), &col_j.to_vec())
                        },
                        "spearman" => {
                            calculate_spearman(&col_i.to_vec(), &col_j.to_vec())
                        },
                        _ => f64::NAN
                    }
                };
                
                (i, j, corr)
            })
        })
        .collect();
    
    // Fill the correlation matrix
    for (i, j, corr) in correlations {
        correlation_matrix[[i, j]] = corr;
        if i != j {
            correlation_matrix[[j, i]] = corr;
        }
    }
    
    Ok(PyArray2::from_array(py, &correlation_matrix).to_object(py))
}

/// Fast Cramér's V calculation for categorical variables
#[pyfunction]
pub fn fast_cramers_v(
    py: Python,
    x: Vec<String>,
    y: Vec<String>
) -> PyResult<f64> {
    if x.len() != y.len() {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Arrays must have the same length"
        ));
    }
    
    if x.is_empty() {
        return Ok(f64::NAN);
    }
    
    // Create contingency table
    let mut contingency_table: HashMap<(String, String), usize> = HashMap::new();
    let mut x_counts: HashMap<String, usize> = HashMap::new();
    let mut y_counts: HashMap<String, usize> = HashMap::new();
    
    for (x_val, y_val) in x.iter().zip(y.iter()) {
        *contingency_table.entry((x_val.clone(), y_val.clone())).or_insert(0) += 1;
        *x_counts.entry(x_val.clone()).or_insert(0) += 1;
        *y_counts.entry(y_val.clone()).or_insert(0) += 1;
    }
    
    let n = x.len() as f64;
    let mut chi_square = 0.0;
    
    // Calculate chi-square statistic
    for ((x_val, y_val), observed) in contingency_table.iter() {
        let x_marginal = *x_counts.get(x_val).unwrap() as f64;
        let y_marginal = *y_counts.get(y_val).unwrap() as f64;
        let expected = (x_marginal * y_marginal) / n;
        
        if expected > 0.0 {
            chi_square += (*observed as f64 - expected).powi(2) / expected;
        }
    }
    
    // Calculate Cramér's V
    let k = x_counts.len().min(y_counts.len()) as f64;
    if k <= 1.0 {
        Ok(0.0)
    } else {
        Ok((chi_square / (n * (k - 1.0))).sqrt())
    }
}

// Helper functions
fn rank_values(values: &[f64]) -> Vec<f64> {
    let mut indexed_values: Vec<(usize, f64)> = values.iter()
        .enumerate()
        .map(|(i, &v)| (i, v))
        .collect();
    
    indexed_values.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
    
    let mut ranks = vec![0.0; values.len()];
    
    for (rank, (original_index, _)) in indexed_values.iter().enumerate() {
        ranks[*original_index] = (rank + 1) as f64;
    }
    
    ranks
}

fn calculate_pearson(x: &[f64], y: &[f64]) -> f64 {
    let valid_pairs: Vec<(f64, f64)> = x.iter()
        .zip(y.iter())
        .filter(|(&x_val, &y_val)| !x_val.is_nan() && !y_val.is_nan())
        .map(|(&x_val, &y_val)| (x_val, y_val))
        .collect();
    
    if valid_pairs.len() < 2 {
        return f64::NAN;
    }
    
    let n = valid_pairs.len() as f64;
    let x_mean = valid_pairs.iter().map(|(x, _)| x).sum::<f64>() / n;
    let y_mean = valid_pairs.iter().map(|(_, y)| y).sum::<f64>() / n;
    
    let (numerator, x_var, y_var) = valid_pairs.iter()
        .map(|&(x, y)| {
            let x_diff = x - x_mean;
            let y_diff = y - y_mean;
            (x_diff * y_diff, x_diff * x_diff, y_diff * y_diff)
        })
        .fold((0.0, 0.0, 0.0), |a, b| (a.0 + b.0, a.1 + b.1, a.2 + b.2));
    
    let denominator = (x_var * y_var).sqrt();
    
    if denominator == 0.0 {
        0.0
    } else {
        numerator / denominator
    }
}

fn calculate_spearman(x: &[f64], y: &[f64]) -> f64 {
    let valid_pairs: Vec<(f64, f64)> = x.iter()
        .zip(y.iter())
        .filter(|(&x_val, &y_val)| !x_val.is_nan() && !y_val.is_nan())
        .map(|(&x_val, &y_val)| (x_val, y_val))
        .collect();
    
    if valid_pairs.len() < 2 {
        return f64::NAN;
    }
    
    let x_ranks = rank_values(&valid_pairs.iter().map(|(x, _)| *x).collect::<Vec<_>>());
    let y_ranks = rank_values(&valid_pairs.iter().map(|(_, y)| *y).collect::<Vec<_>>());
    
    calculate_pearson(&x_ranks, &y_ranks)
}
