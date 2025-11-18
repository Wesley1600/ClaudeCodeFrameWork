#!/usr/bin/env python3
"""
Convert PDF files to various formats (Markdown, JSON, plain text).

This script provides comprehensive PDF conversion with structure preservation.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import PyPDF2
except ImportError:
    try:
        import pypdf as PyPDF2
    except ImportError:
        print("Error: PyPDF2 or pypdf library required. Install with: pip install pypdf", file=sys.stderr)
        sys.exit(1)

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    print("Warning: pdfplumber not available. Table extraction will be limited.", file=sys.stderr)


def extract_metadata(pdf_path: Path) -> Dict[str, Any]:
    """Extract PDF metadata."""
    metadata = {}

    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)

            # Basic metadata
            info = pdf_reader.metadata
            if info:
                metadata['title'] = info.get('/Title', 'Unknown')
                metadata['author'] = info.get('/Author', 'Unknown')
                metadata['subject'] = info.get('/Subject', 'Unknown')
                metadata['creator'] = info.get('/Creator', 'Unknown')
                metadata['producer'] = info.get('/Producer', 'Unknown')
                metadata['creation_date'] = str(info.get('/CreationDate', 'Unknown'))
                metadata['modification_date'] = str(info.get('/ModDate', 'Unknown'))

            metadata['pages'] = len(pdf_reader.pages)
            metadata['encrypted'] = pdf_reader.is_encrypted

    except Exception as e:
        print(f"Warning: Could not extract metadata: {e}", file=sys.stderr)

    return metadata


def convert_to_markdown(
    input_path: Path,
    output_path: Path,
    preserve_images: bool = False,
    extract_metadata: bool = True
) -> str:
    """
    Convert PDF to Markdown format.

    Args:
        input_path: Path to input PDF
        output_path: Path to output Markdown file
        preserve_images: Whether to extract and reference images
        extract_metadata: Whether to include metadata header

    Returns:
        Markdown content
    """
    markdown_lines = []

    # Add metadata header
    if extract_metadata:
        metadata = extract_metadata(input_path)
        markdown_lines.append("---\n")
        for key, value in metadata.items():
            markdown_lines.append(f"{key}: {value}\n")
        markdown_lines.append("---\n\n")

    # Extract text content
    with open(input_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)

        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()

            # Add page marker
            markdown_lines.append(f"\n## Page {page_num}\n\n")

            # Process text to improve formatting
            # (basic heuristics - could be enhanced)
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    markdown_lines.append('\n')
                    continue

                # Detect potential headings (all caps, short lines)
                if len(line) < 80 and line.isupper() and len(line.split()) <= 10:
                    markdown_lines.append(f"### {line}\n\n")
                else:
                    markdown_lines.append(f"{line}\n")

            markdown_lines.append('\n')

    # Extract tables if pdfplumber is available
    if pdfplumber:
        try:
            with pdfplumber.open(input_path) as pdf:
                table_count = 0
                for page_num, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables()
                    for table in tables:
                        table_count += 1
                        markdown_lines.append(f"\n### Table {table_count}\n\n")

                        if table and len(table) > 0:
                            # Headers
                            headers = table[0]
                            markdown_lines.append('| ' + ' | '.join(str(h) if h else '' for h in headers) + ' |\n')
                            markdown_lines.append('|' + '|'.join(['---' for _ in headers]) + '|\n')

                            # Rows
                            for row in table[1:]:
                                markdown_lines.append('| ' + ' | '.join(str(cell) if cell else '' for cell in row) + ' |\n')

                        markdown_lines.append('\n')
        except Exception as e:
            print(f"Warning: Table extraction failed: {e}", file=sys.stderr)

    result = ''.join(markdown_lines)

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"PDF converted to Markdown: {output_path}", file=sys.stderr)
    return result


def convert_to_json(
    input_path: Path,
    output_path: Path,
    extract_metadata_flag: bool = True
) -> Dict[str, Any]:
    """
    Convert PDF to structured JSON format.

    Args:
        input_path: Path to input PDF
        output_path: Path to output JSON file
        extract_metadata_flag: Whether to include metadata

    Returns:
        JSON data structure
    """
    data = {
        'source': str(input_path),
        'content': []
    }

    # Add metadata
    if extract_metadata_flag:
        data['metadata'] = extract_metadata(input_path)

    # Extract text content by page
    with open(input_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)

        for page_num, page in enumerate(pdf_reader.pages, start=1):
            page_data = {
                'page': page_num,
                'type': 'text',
                'content': page.extract_text()
            }
            data['content'].append(page_data)

    # Extract tables if available
    if pdfplumber:
        try:
            with pdfplumber.open(input_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables):
                        table_data = {
                            'page': page_num,
                            'type': 'table',
                            'table_index': table_idx,
                            'headers': table[0] if table else [],
                            'rows': table[1:] if len(table) > 1 else []
                        }
                        data['content'].append(table_data)
        except Exception as e:
            print(f"Warning: Table extraction failed: {e}", file=sys.stderr)

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"PDF converted to JSON: {output_path}", file=sys.stderr)
    return data


def convert_to_text(
    input_path: Path,
    output_path: Path
) -> str:
    """
    Convert PDF to plain text.

    Args:
        input_path: Path to input PDF
        output_path: Path to output text file

    Returns:
        Text content
    """
    text_lines = []

    with open(input_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)

        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text_lines.append(f"\n{'='*80}\n")
            text_lines.append(f"PAGE {page_num}\n")
            text_lines.append(f"{'='*80}\n\n")
            text_lines.append(page.extract_text())
            text_lines.append('\n\n')

    result = ''.join(text_lines)

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"PDF converted to text: {output_path}", file=sys.stderr)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF files to various formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert to Markdown
  %(prog)s --input document.pdf --output document.md --format markdown

  # Convert to JSON with metadata
  %(prog)s --input document.pdf --output document.json --format json --extract-metadata

  # Convert to plain text
  %(prog)s --input document.pdf --output document.txt --format text
        """
    )

    parser.add_argument('--input', '-i', required=True, type=Path,
                        help='Input PDF file path')
    parser.add_argument('--output', '-o', required=True, type=Path,
                        help='Output file path')
    parser.add_argument('--format', '-f', choices=['markdown', 'json', 'text'],
                        default='markdown',
                        help='Output format (default: markdown)')
    parser.add_argument('--preserve-images', action='store_true',
                        help='Preserve and extract images (Markdown only)')
    parser.add_argument('--extract-metadata', action='store_true',
                        help='Include PDF metadata in output')

    args = parser.parse_args()

    try:
        if args.format == 'markdown':
            convert_to_markdown(
                args.input,
                args.output,
                preserve_images=args.preserve_images,
                extract_metadata=args.extract_metadata
            )
        elif args.format == 'json':
            convert_to_json(
                args.input,
                args.output,
                extract_metadata_flag=args.extract_metadata
            )
        elif args.format == 'text':
            convert_to_text(args.input, args.output)

    except Exception as e:
        print(f"Failed to convert PDF: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
