#!/usr/bin/env python3
"""
Decode base64-encoded PDF content and save as a PDF file.
"""

import argparse
import base64
import sys
from pathlib import Path


def decode_base64_pdf(input_path: Path, output_path: Path) -> None:
    """
    Decode base64-encoded PDF data.

    Args:
        input_path: Path to file containing base64-encoded PDF data
        output_path: Path to save the decoded PDF file
    """
    try:
        # Read base64 content
        with open(input_path, 'r', encoding='utf-8') as f:
            base64_content = f.read().strip()

        # Remove data URI prefix if present
        if base64_content.startswith('data:'):
            # Format: data:application/pdf;base64,<base64-data>
            if ';base64,' in base64_content:
                base64_content = base64_content.split(';base64,')[1]

        # Decode base64
        print("Decoding base64 content...", file=sys.stderr)
        pdf_data = base64.b64decode(base64_content)

        # Verify it's a PDF by checking magic bytes
        if not pdf_data.startswith(b'%PDF'):
            print("Warning: Decoded data doesn't appear to be a valid PDF", file=sys.stderr)

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write PDF file
        with open(output_path, 'wb') as f:
            f.write(pdf_data)

        print(f"PDF decoded successfully: {output_path}", file=sys.stderr)
        print(f"File size: {len(pdf_data) / 1024:.1f} KB", file=sys.stderr)

    except base64.binascii.Error as e:
        print(f"Error: Invalid base64 encoding: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Error decoding PDF: {e}", file=sys.stderr)
        raise


def decode_base64_string(base64_string: str, output_path: Path) -> None:
    """
    Decode base64 string directly (not from file).

    Args:
        base64_string: Base64-encoded PDF data
        output_path: Path to save the decoded PDF file
    """
    try:
        # Remove data URI prefix if present
        if base64_string.startswith('data:'):
            if ';base64,' in base64_string:
                base64_string = base64_string.split(';base64,')[1]

        # Decode base64
        print("Decoding base64 string...", file=sys.stderr)
        pdf_data = base64.b64decode(base64_string.strip())

        # Verify it's a PDF
        if not pdf_data.startswith(b'%PDF'):
            print("Warning: Decoded data doesn't appear to be a valid PDF", file=sys.stderr)

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write PDF file
        with open(output_path, 'wb') as f:
            f.write(pdf_data)

        print(f"PDF decoded successfully: {output_path}", file=sys.stderr)
        print(f"File size: {len(pdf_data) / 1024:.1f} KB", file=sys.stderr)

    except Exception as e:
        print(f"Error decoding PDF: {e}", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Decode base64-encoded PDF content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Decode from file
  %(prog)s --input base64_content.txt --output document.pdf

  # Decode from string
  %(prog)s --string "JVBERi0xLjQKJ..." --output document.pdf
        """
    )

    parser.add_argument('--input', '-i', type=Path,
                        help='Input file containing base64-encoded PDF data')
    parser.add_argument('--string', '-s', type=str,
                        help='Base64-encoded PDF string')
    parser.add_argument('--output', '-o', required=True, type=Path,
                        help='Output PDF file path')

    args = parser.parse_args()

    if not args.input and not args.string:
        print("Error: Either --input or --string must be provided", file=sys.stderr)
        sys.exit(1)

    if args.input and args.string:
        print("Error: Only one of --input or --string should be provided", file=sys.stderr)
        sys.exit(1)

    try:
        if args.input:
            decode_base64_pdf(args.input, args.output)
        else:
            decode_base64_string(args.string, args.output)

    except Exception as e:
        print(f"Failed to decode PDF: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
