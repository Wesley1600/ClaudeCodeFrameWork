#!/usr/bin/env python3
"""
CSV Analysis Script for Claude Code Skills

Analyzes CSV files and generates statistical insights without loading
analysis code into Claude's context.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional


def validate_file(file_path: str) -> Path:
    """Validate that the file exists and is readable."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    if not path.suffix.lower() == '.csv':
        raise ValueError(f"File is not a CSV: {file_path}")

    return path


def analyze_csv(file_path: Path, columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Analyze CSV file and return statistics.

    Args:
        file_path: Path to CSV file
        columns: Optional list of specific columns to analyze

    Returns:
        Dictionary containing analysis results
    """
    try:
        import pandas as pd
        import numpy as np
    except ImportError as e:
        raise ImportError(f"Required package not found: {e.name}. Install with: pip install pandas numpy")

    # Read CSV
    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("CSV file is empty")

    # Filter columns if specified
    if columns:
        missing_cols = set(columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Columns not found: {missing_cols}")
        df = df[columns]

    # Compute statistics
    results = {
        "file": str(file_path),
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_stats": {},
        "categorical_stats": {},
        "insights": []
    }

    # Numeric column statistics
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        stats = df[col].describe().to_dict()
        results["numeric_stats"][col] = {
            "mean": float(stats.get("mean", 0)),
            "std": float(stats.get("std", 0)),
            "min": float(stats.get("min", 0)),
            "max": float(stats.get("max", 0)),
            "median": float(df[col].median()),
            "q25": float(stats.get("25%", 0)),
            "q75": float(stats.get("75%", 0)),
        }

    # Categorical column statistics
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        results["categorical_stats"][col] = {
            "unique_values": int(df[col].nunique()),
            "most_common": value_counts.head(5).to_dict(),
            "missing_count": int(df[col].isnull().sum())
        }

    # Generate insights
    insights = []

    # Missing data insights
    missing = df.isnull().sum()
    high_missing = missing[missing > len(df) * 0.1]
    if not high_missing.empty:
        insights.append(f"High missing data: {', '.join(high_missing.index.tolist())} (>10%)")

    # Numeric insights
    for col in numeric_cols:
        skew = df[col].skew()
        if abs(skew) > 1:
            insights.append(f"{col} is highly skewed (skewness: {skew:.2f})")

    # Categorical insights
    for col in categorical_cols:
        unique_ratio = df[col].nunique() / len(df)
        if unique_ratio > 0.95:
            insights.append(f"{col} has very high cardinality ({df[col].nunique()} unique values)")
        elif unique_ratio < 0.05:
            insights.append(f"{col} has very low cardinality ({df[col].nunique()} unique values)")

    results["insights"] = insights

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze CSV files and generate statistics"
    )
    parser.add_argument(
        "file_path",
        help="Path to CSV file"
    )
    parser.add_argument(
        "--columns",
        nargs="+",
        help="Specific columns to analyze"
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format"
    )

    args = parser.parse_args()

    try:
        # Validate file
        file_path = validate_file(args.file_path)

        # Analyze
        results = analyze_csv(file_path, args.columns)

        # Output results
        if args.format == "json":
            print(json.dumps(results, indent=2))
        else:
            print(f"CSV Analysis: {results['file']}")
            print(f"Rows: {results['rows']}, Columns: {results['columns']}")
            print(f"\nColumns: {', '.join(results['column_names'])}")

            if results['numeric_stats']:
                print("\nNumeric Statistics:")
                for col, stats in results['numeric_stats'].items():
                    print(f"  {col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}")

            if results['categorical_stats']:
                print("\nCategorical Statistics:")
                for col, stats in results['categorical_stats'].items():
                    print(f"  {col}: {stats['unique_values']} unique values")

            if results['insights']:
                print("\nInsights:")
                for insight in results['insights']:
                    print(f"  - {insight}")

        return 0

    except FileNotFoundError as e:
        error = {"status": "error", "code": 1, "message": str(e)}
        print(json.dumps(error), file=sys.stderr)
        return 1
    except ValueError as e:
        error = {"status": "error", "code": 2, "message": str(e)}
        print(json.dumps(error), file=sys.stderr)
        return 2
    except Exception as e:
        error = {"status": "error", "code": 3, "message": f"Processing error: {str(e)}"}
        print(json.dumps(error), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
