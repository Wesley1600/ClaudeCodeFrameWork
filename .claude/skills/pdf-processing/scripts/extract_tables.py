#!/usr/bin/env python3
"""
Extract tables from PDF files and convert to CSV, JSON, or Markdown format.

This script uses pdfplumber for robust table detection and extraction.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber library required. Install with: pip install pdfplumber", file=sys.stderr)
    sys.exit(1)


def extract_tables_from_pdf(
    input_path: Path,
    output_format: str = 'csv',
    output_dir: Path = None,
    output_file: Path = None
) -> List[Dict[str, Any]]:
    """
    Extract all tables from a PDF file.

    Args:
        input_path: Path to input PDF file
        output_format: Output format ('csv', 'json', 'markdown')
        output_dir: Directory to save individual table files
        output_file: Single file to save all tables (JSON only)

    Returns:
        List of extracted tables with metadata
    """
    if not input_path.exists():
        raise FileNotFoundError(f"PDF file not found: {input_path}")

    extracted_tables = []

    try:
        with pdfplumber.open(input_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Processing {total_pages} pages for tables...", file=sys.stderr)

            table_count = 0

            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()

                if tables:
                    print(f"Found {len(tables)} table(s) on page {page_num}", file=sys.stderr)

                    for table_idx, table in enumerate(tables):
                        table_count += 1

                        # Store table with metadata
                        table_data = {
                            'page': page_num,
                            'table_number': table_count,
                            'headers': table[0] if table else [],
                            'rows': table[1:] if len(table) > 1 else [],
                            'raw_data': table
                        }

                        extracted_tables.append(table_data)

                        # Save individual table files
                        if output_dir:
                            output_dir.mkdir(parents=True, exist_ok=True)
                            save_table(table_data, output_format, output_dir, table_count)

            print(f"Extracted {table_count} tables total", file=sys.stderr)

            # Save all tables to a single JSON file
            if output_file and output_format == 'json':
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(extracted_tables, f, indent=2, ensure_ascii=False)
                print(f"All tables saved to: {output_file}", file=sys.stderr)

            return extracted_tables

    except Exception as e:
        print(f"Error extracting tables: {e}", file=sys.stderr)
        raise


def save_table(table_data: Dict[str, Any], format: str, output_dir: Path, table_num: int):
    """Save a single table to a file in the specified format."""

    filename = f"table_{table_num}_page_{table_data['page']}"

    if format == 'csv':
        save_as_csv(table_data, output_dir / f"{filename}.csv")
    elif format == 'json':
        save_as_json(table_data, output_dir / f"{filename}.json")
    elif format == 'markdown':
        save_as_markdown(table_data, output_dir / f"{filename}.md")


def save_as_csv(table_data: Dict[str, Any], output_path: Path):
    """Save table as CSV file."""
    import csv

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write headers
        if table_data['headers']:
            writer.writerow(table_data['headers'])

        # Write rows
        for row in table_data['rows']:
            writer.writerow(row)

    print(f"  Saved: {output_path}", file=sys.stderr)


def save_as_json(table_data: Dict[str, Any], output_path: Path):
    """Save table as JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'page': table_data['page'],
            'table_number': table_data['table_number'],
            'headers': table_data['headers'],
            'rows': table_data['rows']
        }, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {output_path}", file=sys.stderr)


def save_as_markdown(table_data: Dict[str, Any], output_path: Path):
    """Save table as Markdown file."""
    lines = []

    lines.append(f"# Table {table_data['table_number']} (Page {table_data['page']})\n\n")

    # Headers
    if table_data['headers']:
        lines.append('| ' + ' | '.join(str(h) if h else '' for h in table_data['headers']) + ' |\n')
        lines.append('|' + '|'.join(['---' for _ in table_data['headers']]) + '|\n')

    # Rows
    for row in table_data['rows']:
        lines.append('| ' + ' | '.join(str(cell) if cell else '' for cell in row) + ' |\n')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"  Saved: {output_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Extract tables from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all tables to CSV files
  %(prog)s --input document.pdf --format csv --output-dir ./tables/

  # Extract tables to JSON
  %(prog)s --input document.pdf --format json --output tables.json

  # Extract tables to Markdown
  %(prog)s --input document.pdf --format markdown --output-dir ./tables/
        """
    )

    parser.add_argument('--input', '-i', required=True, type=Path,
                        help='Input PDF file path')
    parser.add_argument('--format', '-f', choices=['csv', 'json', 'markdown'],
                        default='csv',
                        help='Output format (default: csv)')
    parser.add_argument('--output-dir', '-d', type=Path,
                        help='Output directory for individual table files')
    parser.add_argument('--output', '-o', type=Path,
                        help='Output file for all tables (JSON format only)')

    args = parser.parse_args()

    if not args.output_dir and not args.output:
        print("Error: Either --output-dir or --output must be specified", file=sys.stderr)
        sys.exit(1)

    if args.output and args.format != 'json':
        print("Warning: --output only works with JSON format. Use --output-dir for CSV/Markdown", file=sys.stderr)

    try:
        extract_tables_from_pdf(
            input_path=args.input,
            output_format=args.format,
            output_dir=args.output_dir,
            output_file=args.output
        )

    except Exception as e:
        print(f"Failed to extract tables: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
