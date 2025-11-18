#!/usr/bin/env python3
"""
Summarize PDF content by extracting key information.

This script provides basic summarization by:
- Extracting document metadata
- Identifying headings and sections
- Extracting first/last paragraphs
- Highlighting key sentences
- Providing statistical overview
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

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


def extract_metadata(pdf_path: Path) -> Dict[str, Any]:
    """Extract PDF metadata."""
    metadata = {}
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            info = pdf_reader.metadata
            if info:
                metadata['title'] = info.get('/Title', 'Unknown')
                metadata['author'] = info.get('/Author', 'Unknown')
                metadata['subject'] = info.get('/Subject', 'Unknown')
                metadata['creator'] = info.get('/Creator', 'Unknown')
            metadata['pages'] = len(pdf_reader.pages)
    except Exception as e:
        print(f"Warning: Could not extract metadata: {e}", file=sys.stderr)
    return metadata


def extract_headings(text: str) -> List[str]:
    """Extract potential headings from text."""
    headings = []
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        # Heuristics for headings:
        # - Short lines (< 80 chars)
        # - All caps or title case
        # - Ends without punctuation
        if line and len(line) < 80:
            if (line.isupper() or line.istitle()) and not line.endswith(('.', ',', ';', ':', '!', '?')):
                headings.append(line)

    return headings[:20]  # Limit to first 20 headings


def extract_key_sentences(text: str, num_sentences: int = 10) -> List[str]:
    """
    Extract key sentences using simple heuristics.

    Prioritizes:
    - First sentence of paragraphs
    - Sentences with numbers/statistics
    - Sentences with emphasis keywords
    """
    # Split into sentences (basic)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    key_sentences = []
    emphasis_words = ['important', 'significant', 'critical', 'key', 'main', 'primary',
                      'conclude', 'therefore', 'however', 'moreover', 'furthermore']

    for sentence in sentences[:50]:  # Check first 50 sentences
        # Check for numbers/statistics
        if re.search(r'\d+', sentence):
            key_sentences.append(sentence)
            continue

        # Check for emphasis words
        if any(word in sentence.lower() for word in emphasis_words):
            key_sentences.append(sentence)
            continue

        if len(key_sentences) >= num_sentences:
            break

    return key_sentences[:num_sentences]


def summarize_pdf(
    input_path: Path,
    output_path: Path,
    style: str = 'concise'
) -> str:
    """
    Generate a summary of a PDF document.

    Args:
        input_path: Path to input PDF
        output_path: Path to output summary file
        style: Summary style ('concise', 'detailed', 'executive')

    Returns:
        Summary text
    """
    if not input_path.exists():
        raise FileNotFoundError(f"PDF file not found: {input_path}")

    print(f"Summarizing PDF: {input_path}", file=sys.stderr)

    # Extract metadata
    metadata = extract_metadata(input_path)

    # Extract full text
    full_text = []
    with open(input_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        for page in pdf_reader.pages:
            full_text.append(page.extract_text())

    all_text = '\n'.join(full_text)

    # Extract structural elements
    headings = extract_headings(all_text)
    key_sentences = extract_key_sentences(all_text, num_sentences=15 if style == 'detailed' else 10)

    # Count tables if pdfplumber available
    table_count = 0
    if pdfplumber:
        try:
            with pdfplumber.open(input_path) as pdf:
                for page in pdf.pages:
                    table_count += len(page.extract_tables())
        except Exception:
            pass

    # Build summary
    summary_lines = []

    # Header
    summary_lines.append("# PDF Document Summary\n\n")
    summary_lines.append(f"**Source:** {input_path.name}\n")
    summary_lines.append(f"**Generated:** {Path(__file__).name}\n\n")

    # Metadata section
    summary_lines.append("## Document Information\n\n")
    for key, value in metadata.items():
        summary_lines.append(f"- **{key.title()}:** {value}\n")

    # Statistics
    word_count = len(all_text.split())
    char_count = len(all_text)
    summary_lines.append(f"- **Words:** ~{word_count:,}\n")
    summary_lines.append(f"- **Characters:** ~{char_count:,}\n")
    if table_count > 0:
        summary_lines.append(f"- **Tables:** {table_count}\n")
    summary_lines.append("\n")

    # Structure overview
    if headings and style in ['detailed', 'executive']:
        summary_lines.append("## Document Structure\n\n")
        summary_lines.append("Detected headings and sections:\n\n")
        for heading in headings[:10]:
            summary_lines.append(f"- {heading}\n")
        summary_lines.append("\n")

    # Key points
    if style == 'executive':
        summary_lines.append("## Executive Summary\n\n")
        summary_lines.append("### Key Points\n\n")
    else:
        summary_lines.append("## Key Content\n\n")

    for i, sentence in enumerate(key_sentences, 1):
        if style == 'concise':
            summary_lines.append(f"{i}. {sentence}.\n")
        else:
            summary_lines.append(f"**Point {i}:** {sentence}.\n\n")

    summary_lines.append("\n")

    # First page excerpt (for detailed/executive)
    if style in ['detailed', 'executive'] and full_text:
        summary_lines.append("## Opening Content\n\n")
        first_page_excerpt = full_text[0][:500]
        summary_lines.append(f"{first_page_excerpt}...\n\n")

    # Last page excerpt (for detailed)
    if style == 'detailed' and len(full_text) > 1:
        summary_lines.append("## Closing Content\n\n")
        last_page_excerpt = full_text[-1][:500]
        summary_lines.append(f"{last_page_excerpt}...\n\n")

    # Footer
    summary_lines.append("---\n\n")
    summary_lines.append("*This summary was automatically generated. ")
    summary_lines.append("For complete information, please refer to the original document.*\n")

    result = ''.join(summary_lines)

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"Summary saved to: {output_path}", file=sys.stderr)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Summarize PDF documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Concise summary
  %(prog)s --input document.pdf --output summary.md --style concise

  # Detailed summary
  %(prog)s --input document.pdf --output summary.md --style detailed

  # Executive summary
  %(prog)s --input document.pdf --output summary.md --style executive
        """
    )

    parser.add_argument('--input', '-i', required=True, type=Path,
                        help='Input PDF file path')
    parser.add_argument('--output', '-o', required=True, type=Path,
                        help='Output summary file path (Markdown)')
    parser.add_argument('--style', '-s', choices=['concise', 'detailed', 'executive'],
                        default='concise',
                        help='Summary style (default: concise)')

    args = parser.parse_args()

    try:
        summarize_pdf(args.input, args.output, args.style)
    except Exception as e:
        print(f"Failed to summarize PDF: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
