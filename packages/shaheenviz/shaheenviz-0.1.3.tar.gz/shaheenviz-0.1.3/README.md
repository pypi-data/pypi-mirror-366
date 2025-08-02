# Shaheenviz - Unified EDA Solution 🚀

[![PyPI version](https://badge.fury.io/py/shaheenviz.svg)](https://badge.fury.io/py/shaheenviz)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

Shaheenviz combines the analytical power of **YData Profiling** with the stunning visuals of **Sweetviz** to deliver a unified, automatic EDA solution. Built with pure Python for maximum compatibility! 🐍

## ✨ Features

- 🎯 **Automatic Backend Selection**: Intelligently chooses between YData Profiling and Sweetviz based on dataset characteristics
- 📊 **Comprehensive Analysis**: Statistical summaries, correlations, missing values, outliers, and more
- 🎨 **Beautiful Visualizations**: Interactive plots, histograms, correlation heatmaps, and comparison charts
- 🔍 **Smart Target Detection**: Automatically identifies target columns for supervised learning
- 📈 **Dataset Comparison**: Compare train/test distributions and detect data drift
- 🛡️ **Data Quality Warnings**: Automatic detection of data quality issues
- 💻 **Multiple Interfaces**: Python API, CLI tool, and Jupyter notebook integration
- 📤 **Flexible Output**: HTML reports, JSON export, PDF generation (optional)
- 🌍 **Cross-Platform**: Windows, macOS, and Linux support

## 📦 Installation

### Basic Installation
```bash
pip install shaheenviz
```

### With Optional Dependencies
```bash
pip install shaheenviz[dev,pdf]
```

## 🎯 Quick Start

### Basic Usage

```python
import pandas as pd
from shaheenviz import generate_report

# Load your data
df = pd.read_csv('your_data.csv')

# Generate report (automatically detects target and chooses optimal backend)
report = generate_report(df, title="My Dataset Analysis")

# Save as HTML
report.save_html('analysis_report.html')

# Or display in Jupyter notebook
report.show_notebook()
```

### Dataset Comparison

```python
from shaheenviz import compare_datasets

# Compare training and validation sets
train_df = pd.read_csv('train.csv')
val_df = pd.read_csv('validation.csv')

comparison_report = compare_datasets(train_df, val_df, target='target')
comparison_report.save_html('train_vs_val_comparison.html')
```

### Quick Profile

```python
from shaheenviz import quick_profile

# Generate minimal report for fast overview
quick_report = quick_profile(df, target='target')
quick_report.save_html('quick_analysis.html')
```

### Command Line Interface

```bash
# Basic analysis
shaheenviz --file data.csv

# With specific target and output
shaheenviz --file train.csv --target label --output my_report.html

# Compare datasets
shaheenviz --file train.csv --compare test.csv --target target

# Quick analysis with minimal processing
shaheenviz --file large_dataset.csv --minimal --mode ydata

# Verbose output with system info
shaheenviz --file data.csv --verbose --system-info
```

## 🏗️ Architecture

Shaheenviz uses a modular architecture that automatically selects the best backend



## 🔧 Advanced Configuration

### Backend Selection Logic

```python
# Manual backend selection
report = generate_report(df, mode='ydata')     # Force YData Profiling
report = generate_report(df, mode='sweetviz')  # Force Sweetviz
report = generate_report(df, mode='auto')      # Automatic (default)
```

### Custom Profiling

```python
from shaheenviz import ProfileWrapper

# Custom YData Profiling configuration
profile_wrapper = ProfileWrapper()
config_overrides = {
    "correlations": {
        "spearman": {"calculate": False},  # Disable Spearman for speed
        "cramers": {"calculate": True}     # Enable Cramér's V
    }
}

report = profile_wrapper.generate_profile(
    df, 
    target='target',
    config_overrides=config_overrides
)
```

### Utility Functions

```python
from shaheenviz.utils import detect_target, validate_dataframe, get_column_types

# Auto-detect target column
target = detect_target(df)
print(f"Detected target: {target}")

# Validate DataFrame
validation = validate_dataframe(df)
print(f"Dataset valid: {validation['valid']}")

# Get column types
column_types = get_column_types(df)
print(f"Numeric columns: {column_types['numeric']}")
```



## 📊 Performance Tips

1. **Use Minimal Mode**: For quick analysis, use `minimal=True`
2. **Choose Backend Wisely**: YData Profiling for large datasets, Sweetviz for detailed comparisons
3. **Optimize Memory**: Use appropriate data types (e.g., category for strings)
4. **Target Detection**: Manually specify target column when known to save processing time

## 🎓 Example Use Cases

### Data Science Workflow

```python
import pandas as pd
from shaheenviz import generate_report, compare_datasets
from sklearn.model_selection import train_test_split

# 1. Initial data exploration
raw_data = pd.read_csv('raw_data.csv')
initial_report = generate_report(raw_data, title="Raw Data Analysis")
initial_report.save_html('01_raw_data_analysis.html')

# 2. After data cleaning
cleaned_data = pd.read_csv('cleaned_data.csv')
cleaned_report = generate_report(cleaned_data, title="Cleaned Data Analysis")
cleaned_report.save_html('02_cleaned_data_analysis.html')

# 3. Train/test split comparison
X = cleaned_data.drop('target', axis=1)
y = cleaned_data['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

train_data = pd.concat([X_train, y_train], axis=1)
test_data = pd.concat([X_test, y_test], axis=1)

comparison_report = compare_datasets(
    train_data, test_data, 
    target='target',
    title="Train vs Test Comparison"
)
comparison_report.save_html('03_train_test_comparison.html')
```

### Batch Processing

```python
from pathlib import Path
from shaheenviz import generate_report

def batch_analyze_datasets(data_dir, output_dir):
    """Analyze all CSV files in a directory."""
    
    data_path = Path(data_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for csv_file in data_path.glob('*.csv'):
        print(f"Analyzing {csv_file.name}...")
        
        try:
            df = pd.read_csv(csv_file)
            report = generate_report(
                df, 
                title=f"Analysis of {csv_file.stem}",
                minimal=True  # Use minimal mode for batch processing
            )
            
            output_file = output_path / f"{csv_file.stem}_report.html"
            report.save_html(str(output_file))
            print(f"Report saved: {output_file}")
            
        except Exception as e:
            print(f"Error processing {csv_file.name}: {e}")

# Usage
batch_analyze_datasets('data/', 'reports/')
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Areas for Contribution
- 🐛 Bug fixes and improvements
- 📊 New statistical functions
- 🎨 Visualization enhancements
- 📚 Documentation improvements
- 🧪 Test coverage expansion



## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



## 🔗 Links



- 📦 [PyPI Package](https://pypi.org/project/shaheenviz/)



---

**Developed ❤️ by Hamza**

*Shaheenviz - Making EDA fast, beautiful, and effortless!*
