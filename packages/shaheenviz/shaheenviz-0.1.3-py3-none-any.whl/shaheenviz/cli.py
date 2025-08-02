"""
Command-line interface for Shaheenviz.

This module provides a CLI tool for generating EDA reports from CSV files.
"""

import argparse
import sys
import pandas as pd
from pathlib import Path
from typing import Optional

from .core import generate_report, compare_datasets
from .utils import detect_target, get_system_info


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    
    parser = argparse.ArgumentParser(
        description="Shaheenviz - Unified EDA Solution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  shaheenviz --file data.csv
  shaheenviz --file train.csv --target label --output report.html
  shaheenviz --file train.csv --compare test.csv --target target
  shaheenviz --file data.csv --mode ydata --minimal
        """
    )
    
    # Input files
    parser.add_argument(
        "--file", "-f",
        type=str,
        required=True,
        help="Path to the CSV file to analyze"
    )
    
    parser.add_argument(
        "--compare", "-c",
        type=str,
        help="Path to comparison CSV file (e.g., test set)"
    )
    
    # Analysis options
    parser.add_argument(
        "--target", "-t",
        type=str,
        help="Name of target column (auto-detected if not provided)"
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["auto", "ydata", "sweetviz"],
        default="auto",
        help="Backend to use for analysis (default: auto)"
    )
    
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Generate minimal report for faster processing"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="shaheenviz_report.html",
        help="Output file path (default: shaheenviz_report.html)"
    )
    
    parser.add_argument(
        "--title",
        type=str,
        default="Shaheenviz EDA Report",
        help="Report title"
    )
    
    # Additional options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Shaheenviz 0.1.0"
    )
    
    parser.add_argument(
        "--system-info",
        action="store_true",
        help="Display system information"
    )
    
    return parser


def load_csv_file(filepath: str, verbose: bool = False) -> pd.DataFrame:
    """
    Load a CSV file with error handling and validation.
    
    Args:
        filepath: Path to CSV file
        verbose: Whether to print verbose output
    
    Returns:
        Loaded DataFrame
    """
    
    file_path = Path(filepath)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    if not file_path.suffix.lower() == '.csv':
        raise ValueError(f"File must be a CSV file: {filepath}")
    
    if verbose:
        print(f"Loading file: {filepath}")
        print(f"File size: {file_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    try:
        df = pd.read_csv(filepath)
        
        if verbose:
            print(f"Loaded DataFrame with shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        return df
        
    except Exception as e:
        raise RuntimeError(f"Failed to load CSV file: {str(e)}")


def main():
    """Main CLI entry point."""
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Display system info if requested
    if args.system_info:
        print("System Information:")
        print("=" * 50)
        info = get_system_info()
        for key, value in info.items():
            print(f"{key}: {value}")
        return
    
    try:
        # Load primary dataset
        if args.verbose:
            print("Loading primary dataset...")
        
        df = load_csv_file(args.file, args.verbose)
        
        # Load comparison dataset if provided
        df2 = None
        if args.compare:
            if args.verbose:
                print("Loading comparison dataset...")
            df2 = load_csv_file(args.compare, args.verbose)
        
        # Auto-detect target if not provided
        target = args.target
        if not target:
            target = detect_target(df)
            if target and args.verbose:
                print(f"Auto-detected target column: {target}")
        
        # Generate report
        if args.verbose:
            print(f"Generating report using {args.mode} mode...")
        
        if df2 is not None:
            # Comparison report
            report = compare_datasets(
                train_df=df,
                test_df=df2,
                target=target,
                title=args.title
            )
        else:
            # Single dataset report
            report = generate_report(
                df=df,
                target=target,
                title=args.title,
                mode=args.mode,
                minimal=args.minimal
            )
        
        # Save report
        if args.verbose:
            print(f"Saving report to: {args.output}")
        
        report.save_html(args.output)
        
        print(f"✅ Report generated successfully: {args.output}")
        
        # Print summary
        if args.verbose:
            print("\nReport Summary:")
            print("=" * 50)
            print(f"Backend used: {report.backend_type}")
            print(f"Dataset shape: {report.metadata['dataset_shape']}")
            print(f"Target column: {report.metadata['target_column']}")
            print(f"Minimal mode: {report.metadata['minimal']}")
            print(f"Comparison dataset: {report.metadata['comparison_dataset']}")
    
    except KeyboardInterrupt:
        print("\n❌ Process interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
