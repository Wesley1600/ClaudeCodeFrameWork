#!/usr/bin/env python3
"""
Helper utilities for Claude Skills.

This module provides common functions that can be used across multiple skills
for data processing, file handling, and text manipulation.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load JSON data from a file.

    Args:
        filepath: Path to the JSON file

    Returns:
        Parsed JSON data as a dictionary

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file isn't valid JSON
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> None:
    """
    Save data to a JSON file.

    Args:
        data: Dictionary to save
        filepath: Path where to save the JSON file
        indent: JSON indentation level (default: 2)
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)


def format_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """
    Generate a markdown table from headers and rows.

    Args:
        headers: List of column headers
        rows: List of rows, where each row is a list of cell values

    Returns:
        Formatted markdown table as a string

    Example:
        >>> headers = ["Name", "Age", "City"]
        >>> rows = [["Alice", "30", "NYC"], ["Bob", "25", "LA"]]
        >>> print(format_markdown_table(headers, rows))
        | Name  | Age | City |
        |-------|-----|------|
        | Alice | 30  | NYC  |
        | Bob   | 25  | LA   |
    """
    # Determine column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # Build the table
    lines = []

    # Header row
    header_row = "| " + " | ".join(
        str(h).ljust(col_widths[i]) for i, h in enumerate(headers)
    ) + " |"
    lines.append(header_row)

    # Separator row
    separator = "| " + " | ".join(
        "-" * col_widths[i] for i in range(len(headers))
    ) + " |"
    lines.append(separator)

    # Data rows
    for row in rows:
        data_row = "| " + " | ".join(
            str(row[i]).ljust(col_widths[i]) for i in range(len(headers))
        ) + " |"
        lines.append(data_row)

    return "\n".join(lines)


def read_file(filepath: str) -> str:
    """
    Read the contents of a text file.

    Args:
        filepath: Path to the file

    Returns:
        File contents as a string
    """
    with open(filepath, 'r') as f:
        return f.read()


def write_file(filepath: str, content: str) -> None:
    """
    Write content to a text file.

    Args:
        filepath: Path to the file
        content: Content to write
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)


def batch_process(items: List[str], process_fn, batch_size: int = 10) -> List[Any]:
    """
    Process a list of items in batches.

    Args:
        items: List of items to process
        process_fn: Function to apply to each item
        batch_size: Number of items to process per batch

    Returns:
        List of processed results
    """
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        for item in batch:
            results.append(process_fn(item))
    return results
