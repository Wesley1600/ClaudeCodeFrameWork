#!/usr/bin/env python3
"""
Extract text content from PDF files with optional formatting preservation.

This script provides flexible text extraction from PDFs including:
- Full document or specific pages
- Formatting preservation
- Password-protected PDFs
- Chunked processing for large files
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List

try:
    import PyPDF2
except ImportError:
    try:
        import pypdf as PyPDF2
    except ImportError:
        print("Error: PyPDF2 or pypdf library required. Install with: pip install pypdf", file=sys.stderr)
        sys.exit(1)


def parse_page_range(page_spec: str, total_pages: int) -> List[int]:
    """
    Parse page specification like '1,3,5-10' into list of page numbers.

    Args:
        page_spec: String specification of pages (e.g., '1,3,5-10')
        total_pages: Total number of pages in document

    Returns:
        List of page numbers (0-indexed)
    """
    pages = set()

    for part in page_spec.split(','):
        if '-' in part:
            start, end = part.split('-')
            start = int(start.strip())
            end = int(end.strip())
            pages.update(range(start - 1, min(end, total_pages)))
        else:
            page = int(part.strip())
            if 0 < page <= total_pages:
                pages.add(page - 1)

    return sorted(list(pages))


def extract_text_from_pdf(
    input_path: Path,
    output_path: Optional[Path] = None,
    pages: Optional[str] = None,
    password: Optional[str] = None,
    preserve_formatting: bool = True,
    chunk_size: Optional[int] = None
) -> str:
    """
    Extract text from a PDF file.

    Args:
        input_path: Path to input PDF file
        output_path: Path to output text file (if None, returns text)
        pages: Page specification (e.g., '1,3,5-10')
        password: Password for encrypted PDFs
        preserve_formatting: Whether to preserve spacing and line breaks
        chunk_size: Process in chunks of N pages (for large files)

    Returns:
        Extracted text content
    """
    if not input_path.exists():
        raise FileNotFoundError(f"PDF file not found: {input_path}")

    extracted_text = []

    try:
        with open(input_path, 'rb') as pdf_file:
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Handle encrypted PDFs
            if pdf_reader.is_encrypted:
                if password:
                    pdf_reader.decrypt(password)
                else:
                    raise ValueError("PDF is password-protected. Please provide password with --password")

            total_pages = len(pdf_reader.pages)
            print(f"Processing PDF with {total_pages} pages...", file=sys.stderr)

            # Determine which pages to extract
            if pages:
                page_list = parse_page_range(pages, total_pages)
                print(f"Extracting pages: {[p+1 for p in page_list]}", file=sys.stderr)
            else:
                page_list = list(range(total_pages))

            # Process pages (with optional chunking)
            if chunk_size:
                for i in range(0, len(page_list), chunk_size):
                    chunk = page_list[i:i+chunk_size]
                    print(f"Processing chunk {i//chunk_size + 1}: pages {chunk[0]+1}-{chunk[-1]+1}", file=sys.stderr)
                    for page_num in chunk:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()

                        if preserve_formatting:
                            extracted_text.append(f"\n{'='*80}\n")
                            extracted_text.append(f"PAGE {page_num + 1}\n")
                            extracted_text.append(f"{'='*80}\n\n")

                        extracted_text.append(text)
                        extracted_text.append("\n\n")
            else:
                for page_num in page_list:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()

                    if preserve_formatting:
                        extracted_text.append(f"\n{'='*80}\n")
                        extracted_text.append(f"PAGE {page_num + 1}\n")
                        extracted_text.append(f"{'='*80}\n\n")

                    extracted_text.append(text)
                    extracted_text.append("\n\n")

            result = ''.join(extracted_text)

            # Write to file if output path provided
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"Text extracted successfully to: {output_path}", file=sys.stderr)

            return result

    except Exception as e:
        print(f"Error extracting text from PDF: {e}", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Extract text content from PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all text from PDF
  %(prog)s --input document.pdf --output document.txt

  # Extract specific pages
  %(prog)s --input document.pdf --pages "1,3,5-10" --output selected.txt

  # Extract from password-protected PDF
  %(prog)s --input secure.pdf --password "secret" --output document.txt

  # Process large PDF in chunks
  %(prog)s --input large.pdf --chunk-size 10 --output document.txt
        """
    )

    parser.add_argument('--input', '-i', required=True, type=Path,
                        help='Input PDF file path')
    parser.add_argument('--output', '-o', type=Path,
                        help='Output text file path (prints to stdout if not specified)')
    parser.add_argument('--pages', '-p', type=str,
                        help='Pages to extract (e.g., "1,3,5-10")')
    parser.add_argument('--password', type=str,
                        help='Password for encrypted PDFs')
    parser.add_argument('--preserve-formatting', type=lambda x: x.lower() == 'true',
                        default=True,
                        help='Preserve formatting with page markers (default: true)')
    parser.add_argument('--chunk-size', type=int,
                        help='Process in chunks of N pages (for large files)')

    args = parser.parse_args()

    try:
        result = extract_text_from_pdf(
            input_path=args.input,
            output_path=args.output,
            pages=args.pages,
            password=args.password,
            preserve_formatting=args.preserve_formatting,
            chunk_size=args.chunk_size
        )

        # Print to stdout if no output file specified
        if not args.output:
            print(result)

    except Exception as e:
        print(f"Failed to extract text: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
