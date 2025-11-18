#!/usr/bin/env python3
"""
CSV Plotting Script for Claude Code Skills

Generates visualizations from CSV files without loading plotting code into context.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional


def plot_csv(
    file_path: Path,
    output_path: Path,
    plot_type: str = "histogram",
    columns: Optional[list] = None
) -> dict:
    """
    Generate plot from CSV file.

    Args:
        file_path: Path to CSV file
        output_path: Path to save plot
        plot_type: Type of plot (histogram, scatter, correlation)
        columns: Optional specific columns to plot

    Returns:
        Dictionary with plot information
    """
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as e:
        raise ImportError(
            f"Required package not found: {e.name}. "
            "Install with: pip install pandas matplotlib numpy"
        )

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

    # Create plot based on type
    plt.figure(figsize=(10, 6))

    if plot_type == "histogram":
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            raise ValueError("No numeric columns found for histogram")

        df[numeric_cols].hist(bins=30, edgecolor='black', alpha=0.7)
        plt.suptitle(f"Histogram: {file_path.name}")
        plt.tight_layout()

    elif plot_type == "scatter":
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            raise ValueError("Need at least 2 numeric columns for scatter plot")

        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        plt.scatter(df[x_col], df[y_col], alpha=0.6)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"Scatter Plot: {x_col} vs {y_col}")
        plt.grid(True, alpha=0.3)

    elif plot_type == "correlation":
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 2:
            raise ValueError("Need at least 2 numeric columns for correlation matrix")

        corr_matrix = df[numeric_cols].corr()
        plt.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
        plt.colorbar(label='Correlation')
        plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=45, ha='right')
        plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)
        plt.title("Correlation Matrix")
        plt.tight_layout()

    else:
        raise ValueError(f"Unknown plot type: {plot_type}")

    # Save plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return {
        "status": "success",
        "plot_type": plot_type,
        "input_file": str(file_path),
        "output_file": str(output_path),
        "columns_plotted": columns or "all"
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate plots from CSV files"
    )
    parser.add_argument(
        "file_path",
        help="Path to CSV file"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output image path"
    )
    parser.add_argument(
        "--type",
        choices=["histogram", "scatter", "correlation"],
        default="histogram",
        help="Type of plot to generate"
    )
    parser.add_argument(
        "--columns",
        nargs="+",
        help="Specific columns to plot"
    )

    args = parser.parse_args()

    try:
        file_path = Path(args.file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {args.file_path}")

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        result = plot_csv(file_path, output_path, args.type, args.columns)
        print(json.dumps(result, indent=2))
        return 0

    except Exception as e:
        error = {"status": "error", "message": str(e)}
        print(json.dumps(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
