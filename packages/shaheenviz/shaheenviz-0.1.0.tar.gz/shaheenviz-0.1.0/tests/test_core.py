import pytest
import pandas as pd

from shaheenviz import generate_report, quick_profile, compare_datasets
from shaheenviz.utils import create_sample_data


def test_generate_report():
    # Create sample data
    df = create_sample_data()
    report = generate_report(df, target="target")
    assert report is not None
    assert hasattr(report, 'save_html')
    assert hasattr(report, 'get_rejected_variables')


def test_quick_profile():
    df = create_sample_data(n_rows=100, n_features=5)
    profile = quick_profile(df)
    assert profile is not None
    assert hasattr(profile, 'save_html')


def test_compare_datasets():
    train_df = create_sample_data()
    test_df = create_sample_data()
    comparison_report = compare_datasets(train_df, test_df, target="target")
    assert comparison_report is not None
    assert hasattr(comparison_report, 'save_html')
