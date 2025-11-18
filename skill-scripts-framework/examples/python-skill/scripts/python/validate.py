#!/usr/bin/env python3
"""
CSV Validation Script for Claude Code Skills

Validates CSV files for common issues without loading validation code into context.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any


def validate_csv(file_path: Path) -> Dict[str, Any]:
    """
    Validate CSV file and return validation results.

    Args:
        file_path: Path to CSV file

    Returns:
        Dictionary containing validation results
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required. Install with: pip install pandas")

    issues = []
    warnings = []
    info = {}

    try:
        # Try reading the CSV
        df = pd.read_csv(file_path)
        info["rows"] = len(df)
        info["columns"] = len(df.columns)
        info["file_size_mb"] = file_path.stat().st_size / (1024 * 1024)

        # Check for empty file
        if df.empty:
            issues.append({
                "severity": "error",
                "message": "CSV file is empty",
                "code": "EMPTY_FILE"
            })
            return {
                "valid": False,
                "issues": issues,
                "warnings": warnings,
                "info": info
            }

        # Check for duplicate column names
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            issues.append({
                "severity": "error",
                "message": f"Duplicate column names found: {duplicate_cols}",
                "code": "DUPLICATE_COLUMNS"
            })

        # Check for missing column names
        unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed:')]
        if unnamed_cols:
            warnings.append({
                "severity": "warning",
                "message": f"Columns without names detected: {unnamed_cols}",
                "code": "UNNAMED_COLUMNS"
            })

        # Check for missing values
        missing_counts = df.isnull().sum()
        high_missing = missing_counts[missing_counts > len(df) * 0.5]
        if not high_missing.empty:
            warnings.append({
                "severity": "warning",
                "message": f"Columns with >50% missing values: {high_missing.to_dict()}",
                "code": "HIGH_MISSING_DATA"
            })

        # Check for single-value columns
        single_value_cols = []
        for col in df.columns:
            if df[col].nunique() == 1:
                single_value_cols.append(col)

        if single_value_cols:
            warnings.append({
                "severity": "warning",
                "message": f"Columns with only one unique value: {single_value_cols}",
                "code": "SINGLE_VALUE_COLUMNS"
            })

        # Check for potential data type issues
        for col in df.columns:
            # Numeric columns stored as strings
            if df[col].dtype == 'object':
                try:
                    pd.to_numeric(df[col].dropna())
                    warnings.append({
                        "severity": "info",
                        "message": f"Column '{col}' appears numeric but stored as text",
                        "code": "TYPE_MISMATCH"
                    })
                except (ValueError, TypeError):
                    pass

        # Check file size
        if info["file_size_mb"] > 100:
            warnings.append({
                "severity": "warning",
                "message": f"Large file ({info['file_size_mb']:.2f} MB). Processing may be slow.",
                "code": "LARGE_FILE"
            })

        # Add column information
        info["column_names"] = df.columns.tolist()
        info["dtypes"] = df.dtypes.astype(str).to_dict()
        info["missing_per_column"] = missing_counts.to_dict()

    except pd.errors.EmptyDataError:
        issues.append({
            "severity": "error",
            "message": "CSV file is empty or has no data",
            "code": "EMPTY_DATA"
        })
    except pd.errors.ParserError as e:
        issues.append({
            "severity": "error",
            "message": f"CSV parsing error: {str(e)}",
            "code": "PARSE_ERROR"
        })
    except Exception as e:
        issues.append({
            "severity": "error",
            "message": f"Unexpected error: {str(e)}",
            "code": "UNKNOWN_ERROR"
        })

    # Determine overall validity
    valid = len(issues) == 0

    return {
        "valid": valid,
        "issues": issues,
        "warnings": warnings,
        "info": info
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate CSV files"
    )
    parser.add_argument(
        "file_path",
        help="Path to CSV file"
    )

    args = parser.parse_args()

    try:
        file_path = Path(args.file_path)
        if not file_path.exists():
            error = {
                "valid": False,
                "issues": [{
                    "severity": "error",
                    "message": f"File not found: {args.file_path}",
                    "code": "FILE_NOT_FOUND"
                }],
                "warnings": [],
                "info": {}
            }
            print(json.dumps(error, indent=2))
            return 1

        results = validate_csv(file_path)
        print(json.dumps(results, indent=2))

        return 0 if results["valid"] else 1

    except Exception as e:
        error = {
            "valid": False,
            "issues": [{
                "severity": "error",
                "message": str(e),
                "code": "EXCEPTION"
            }],
            "warnings": [],
            "info": {}
        }
        print(json.dumps(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
