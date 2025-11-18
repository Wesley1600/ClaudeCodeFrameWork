#!/usr/bin/env python3
"""
Download PDF files from URLs.
"""

import argparse
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


def download_pdf(url: str, output_path: Path, verify_ssl: bool = True) -> None:
    """
    Download a PDF from a URL.

    Args:
        url: URL of the PDF file
        output_path: Path to save the downloaded PDF
        verify_ssl: Whether to verify SSL certificates
    """
    try:
        print(f"Downloading PDF from: {url}", file=sys.stderr)

        # Make request with streaming
        response = requests.get(url, stream=True, verify=verify_ssl, timeout=30)
        response.raise_for_status()

        # Check content type
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' not in content_type and not url.endswith('.pdf'):
            print(f"Warning: Content-Type is '{content_type}', expected 'application/pdf'", file=sys.stderr)

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Download with progress
        total_size = int(response.headers.get('Content-Length', 0))
        downloaded = 0

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rProgress: {progress:.1f}%", end='', file=sys.stderr)

        if total_size > 0:
            print(file=sys.stderr)  # New line after progress

        print(f"PDF downloaded successfully: {output_path}", file=sys.stderr)
        print(f"File size: {output_path.stat().st_size / 1024:.1f} KB", file=sys.stderr)

    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Download PDF files from URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download PDF
  %(prog)s --url "https://example.com/document.pdf" --output document.pdf

  # Download without SSL verification (use with caution)
  %(prog)s --url "https://example.com/doc.pdf" --output doc.pdf --no-verify-ssl
        """
    )

    parser.add_argument('--url', '-u', required=True, type=str,
                        help='URL of the PDF file')
    parser.add_argument('--output', '-o', required=True, type=Path,
                        help='Output file path')
    parser.add_argument('--no-verify-ssl', action='store_true',
                        help='Disable SSL certificate verification')

    args = parser.parse_args()

    try:
        download_pdf(args.url, args.output, verify_ssl=not args.no_verify_ssl)
    except Exception as e:
        print(f"Failed to download PDF: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
