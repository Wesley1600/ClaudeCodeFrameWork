"""
Data Extraction Module

Extract structured information from text, tables, web pages, and PDFs.
Returns structured JSON objects containing parsed entities like dates, names,
amounts, emails, and more.

Features:
- Text entity extraction (dates, names, amounts, emails, phone numbers, URLs)
- Table extraction from HTML and PDFs
- Web page scraping and data extraction
- PDF processing with pdfplumber
"""

import re
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from decimal import Decimal
import warnings


class TextExtractor:
    """Extract structured entities from plain text."""

    # Regex patterns for common entities
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        'url': r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
        'date_iso': r'\b\d{4}-\d{2}-\d{2}\b',
        'date_us': r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
        'date_written': r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b',
        'currency': r'\$\s?\d+(?:,\d{3})*(?:\.\d{2})?',
        'number': r'\b\d+(?:,\d{3})*(?:\.\d+)?\b',
        'percentage': r'\b\d+(?:\.\d+)?%',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'zip_code': r'\b\d{5}(?:-\d{4})?\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    }

    # Common name prefixes and suffixes
    NAME_PREFIXES = {'Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'Sir', 'Madam'}
    NAME_SUFFIXES = {'Jr', 'Sr', 'II', 'III', 'IV', 'PhD', 'MD', 'Esq'}

    def __init__(self):
        """Initialize the text extractor."""
        self.compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.PATTERNS.items()
        }

    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extract all supported entities from text.

        Args:
            text: Input text to parse

        Returns:
            Dictionary with extracted entities organized by type
        """
        return {
            'emails': self.extract_emails(text),
            'phone_numbers': self.extract_phone_numbers(text),
            'urls': self.extract_urls(text),
            'dates': self.extract_dates(text),
            'amounts': self.extract_amounts(text),
            'names': self.extract_names(text),
            'numbers': self.extract_numbers(text),
            'percentages': self.extract_percentages(text),
            'ssns': self.extract_ssns(text),
            'zip_codes': self.extract_zip_codes(text),
            'ip_addresses': self.extract_ip_addresses(text),
        }

    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        return self.compiled_patterns['email'].findall(text)

    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text."""
        matches = self.compiled_patterns['phone'].findall(text)
        # Clean up phone numbers - remove all non-digit characters except +
        return [re.sub(r'[^\d+]', '', match) for match in matches if match]

    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        return self.compiled_patterns['url'].findall(text)

    def extract_dates(self, text: str) -> List[Dict[str, str]]:
        """
        Extract dates from text in various formats.

        Returns:
            List of dictionaries with 'raw' and 'normalized' date strings
        """
        dates = []

        # ISO format (YYYY-MM-DD)
        for match in self.compiled_patterns['date_iso'].findall(text):
            dates.append({
                'raw': match,
                'format': 'iso',
                'normalized': match
            })

        # US format (MM/DD/YYYY)
        for match in self.compiled_patterns['date_us'].findall(text):
            dates.append({
                'raw': match,
                'format': 'us',
                'normalized': self._normalize_us_date(match)
            })

        # Written format (Month DD, YYYY)
        for match in self.compiled_patterns['date_written'].findall(text):
            dates.append({
                'raw': match,
                'format': 'written',
                'normalized': self._normalize_written_date(match)
            })

        return dates

    def extract_amounts(self, text: str) -> List[Dict[str, Union[str, float]]]:
        """
        Extract monetary amounts from text.

        Returns:
            List of dictionaries with 'raw' and 'value' (as float)
        """
        amounts = []
        for match in self.compiled_patterns['currency'].findall(text):
            clean_value = match.replace('$', '').replace(',', '').strip()
            try:
                value = float(clean_value)
                amounts.append({
                    'raw': match,
                    'value': value,
                    'currency': 'USD'
                })
            except ValueError:
                continue
        return amounts

    def extract_numbers(self, text: str) -> List[Dict[str, Union[str, float]]]:
        """
        Extract numeric values from text.

        Returns:
            List of dictionaries with 'raw' and 'value' (as float)
        """
        numbers = []
        for match in self.compiled_patterns['number'].findall(text):
            # Skip if it's part of a date, phone, etc.
            if self._is_part_of_other_entity(text, match):
                continue
            clean_value = match.replace(',', '')
            try:
                value = float(clean_value)
                numbers.append({
                    'raw': match,
                    'value': value
                })
            except ValueError:
                continue
        return numbers

    def extract_percentages(self, text: str) -> List[Dict[str, Union[str, float]]]:
        """Extract percentage values from text."""
        percentages = []
        for match in self.compiled_patterns['percentage'].findall(text):
            clean_value = match.replace('%', '')
            try:
                value = float(clean_value)
                percentages.append({
                    'raw': match,
                    'value': value
                })
            except ValueError:
                continue
        return percentages

    def extract_ssns(self, text: str) -> List[str]:
        """Extract Social Security Numbers (SSNs) from text."""
        return self.compiled_patterns['ssn'].findall(text)

    def extract_zip_codes(self, text: str) -> List[str]:
        """Extract US ZIP codes from text."""
        return self.compiled_patterns['zip_code'].findall(text)

    def extract_ip_addresses(self, text: str) -> List[str]:
        """Extract IP addresses from text."""
        ips = self.compiled_patterns['ip_address'].findall(text)
        # Validate IP addresses
        valid_ips = []
        for ip in ips:
            parts = ip.split('.')
            if all(0 <= int(part) <= 255 for part in parts):
                valid_ips.append(ip)
        return valid_ips

    def extract_names(self, text: str) -> List[str]:
        """
        Extract person names from text using simple heuristics.

        Note: This is a basic implementation. For production use,
        consider using NLP libraries like spaCy or NLTK.
        """
        # Pattern for capitalized words that could be names
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        potential_names = re.findall(name_pattern, text)

        # Filter out common false positives
        names = []
        for name in potential_names:
            # Skip if it's likely a title or location
            if not self._is_likely_name(name):
                continue
            names.append(name)

        return names

    def _normalize_us_date(self, date_str: str) -> str:
        """Convert US format date to ISO format."""
        try:
            parts = date_str.split('/')
            if len(parts) == 3:
                month, day, year = parts
                # Handle 2-digit years
                if len(year) == 2:
                    year = '20' + year if int(year) < 50 else '19' + year
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
        return date_str

    def _normalize_written_date(self, date_str: str) -> str:
        """Convert written date format to ISO format."""
        try:
            # Parse using datetime
            date_obj = datetime.strptime(date_str, '%B %d, %Y')
            return date_obj.strftime('%Y-%m-%d')
        except:
            try:
                # Try abbreviated month
                date_obj = datetime.strptime(date_str, '%b %d, %Y')
                return date_obj.strftime('%Y-%m-%d')
            except:
                pass
        return date_str

    def _is_part_of_other_entity(self, text: str, number: str) -> bool:
        """Check if a number is part of another entity like date or phone."""
        # Find the position of this number
        try:
            idx = text.index(number)
            # Get surrounding context
            start = max(0, idx - 5)
            end = min(len(text), idx + len(number) + 5)
            context = text[start:end]

            # Check if it looks like part of a date or phone
            if '/' in context or '-' in context or '(' in context:
                return True
        except ValueError:
            pass
        return False

    def _is_likely_name(self, text: str) -> bool:
        """Simple heuristic to determine if text is likely a person name."""
        # Skip if it's too long (likely a sentence)
        if len(text.split()) > 4:
            return False

        # Skip common non-name patterns
        skip_words = {
            'The', 'This', 'That', 'These', 'Those',
            'United States', 'New York', 'Los Angeles',
            'North', 'South', 'East', 'West'
        }

        return text not in skip_words

    def to_json(self, data: Dict[str, Any], indent: int = 2) -> str:
        """Convert extracted data to JSON string."""
        return json.dumps(data, indent=indent, default=str)


class TableExtractor:
    """Extract and parse tables from various sources."""

    def __init__(self):
        """Initialize the table extractor."""
        pass

    def extract_from_html(self, html: str) -> List[Dict[str, Any]]:
        """
        Extract tables from HTML content.

        Args:
            html: HTML content containing tables

        Returns:
            List of tables, each as a dictionary with headers and rows
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            warnings.warn("BeautifulSoup4 not installed. Install with: pip install beautifulsoup4")
            return []

        soup = BeautifulSoup(html, 'html.parser')
        tables = []

        for table_elem in soup.find_all('table'):
            table_data = {
                'headers': [],
                'rows': [],
                'metadata': {}
            }

            # Extract headers
            header_row = table_elem.find('thead')
            if header_row:
                headers = header_row.find_all('th')
                table_data['headers'] = [h.get_text(strip=True) for h in headers]
            else:
                # Try first row
                first_row = table_elem.find('tr')
                if first_row:
                    headers = first_row.find_all(['th', 'td'])
                    table_data['headers'] = [h.get_text(strip=True) for h in headers]

            # Extract rows
            tbody = table_elem.find('tbody')
            rows = tbody.find_all('tr') if tbody else table_elem.find_all('tr')[1:]

            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data:  # Skip empty rows
                    table_data['rows'].append(row_data)

            # Add metadata
            if table_elem.get('id'):
                table_data['metadata']['id'] = table_elem['id']
            if table_elem.get('class'):
                table_data['metadata']['class'] = ' '.join(table_elem['class'])

            tables.append(table_data)

        return tables

    def extract_from_csv(self, csv_content: str, delimiter: str = ',') -> Dict[str, Any]:
        """
        Extract table data from CSV content.

        Args:
            csv_content: CSV text content
            delimiter: CSV delimiter (default: ',')

        Returns:
            Dictionary with headers and rows
        """
        import csv
        from io import StringIO

        reader = csv.reader(StringIO(csv_content), delimiter=delimiter)
        rows = list(reader)

        if not rows:
            return {'headers': [], 'rows': []}

        return {
            'headers': rows[0],
            'rows': rows[1:],
            'metadata': {'format': 'csv', 'delimiter': delimiter}
        }

    def table_to_dict_list(self, table: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert table data to list of dictionaries (one per row).

        Args:
            table: Table dictionary with headers and rows

        Returns:
            List of dictionaries mapping headers to values
        """
        headers = table.get('headers', [])
        rows = table.get('rows', [])

        result = []
        for row in rows:
            row_dict = {}
            for i, header in enumerate(headers):
                value = row[i] if i < len(row) else None
                row_dict[header] = value
            result.append(row_dict)

        return result


class WebExtractor:
    """Extract structured data from web pages."""

    def __init__(self):
        """Initialize the web extractor."""
        self.text_extractor = TextExtractor()
        self.table_extractor = TableExtractor()

    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extract structured data from a web page.

        Args:
            url: URL of the web page

        Returns:
            Dictionary with extracted content, metadata, and entities
        """
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            warnings.warn("requests or beautifulsoup4 not installed. "
                        "Install with: pip install requests beautifulsoup4")
            return {}

        # Fetch the page
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        return self.extract_from_html(response.text, url)

    def extract_from_html(self, html: str, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract structured data from HTML content.

        Args:
            html: HTML content
            url: Optional source URL

        Returns:
            Dictionary with extracted content, metadata, and entities
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            warnings.warn("BeautifulSoup4 not installed. Install with: pip install beautifulsoup4")
            return {}

        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()

        # Extract metadata
        metadata = {
            'title': soup.title.string if soup.title else None,
            'url': url,
        }

        # Extract meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_tags[name] = content
        metadata['meta_tags'] = meta_tags

        # Extract text content
        text_content = soup.get_text(separator=' ', strip=True)

        # Extract entities from text
        entities = self.text_extractor.extract_all(text_content)

        # Extract tables
        tables = self.table_extractor.extract_from_html(html)

        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            links.append({
                'text': link.get_text(strip=True),
                'href': link['href']
            })

        # Extract images
        images = []
        for img in soup.find_all('img', src=True):
            images.append({
                'src': img['src'],
                'alt': img.get('alt', '')
            })

        return {
            'metadata': metadata,
            'text_content': text_content[:1000],  # First 1000 chars
            'full_text': text_content,
            'entities': entities,
            'tables': tables,
            'links': links[:20],  # First 20 links
            'images': images[:20],  # First 20 images
        }


class PDFExtractor:
    """Extract text and tables from PDF files using pdfplumber."""

    def __init__(self):
        """Initialize the PDF extractor."""
        self.text_extractor = TextExtractor()

    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured data from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with extracted text, tables, and metadata
        """
        try:
            import pdfplumber
        except ImportError:
            warnings.warn("pdfplumber not installed. Install with: pip install pdfplumber")
            return {}

        result = {
            'metadata': {},
            'pages': [],
            'full_text': '',
            'tables': [],
            'entities': {}
        }

        with pdfplumber.open(pdf_path) as pdf:
            # Extract metadata
            result['metadata'] = {
                'num_pages': len(pdf.pages),
                'pdf_metadata': pdf.metadata
            }

            all_text = []

            # Process each page
            for page_num, page in enumerate(pdf.pages, 1):
                page_data = {
                    'page_number': page_num,
                    'text': '',
                    'tables': []
                }

                # Extract text
                text = page.extract_text()
                if text:
                    page_data['text'] = text
                    all_text.append(text)

                # Extract tables
                tables = page.extract_tables()
                for table in tables:
                    if table and len(table) > 0:
                        # Convert to structured format
                        structured_table = {
                            'headers': table[0] if table else [],
                            'rows': table[1:] if len(table) > 1 else [],
                            'page': page_num
                        }
                        page_data['tables'].append(structured_table)
                        result['tables'].append(structured_table)

                result['pages'].append(page_data)

            # Combine all text
            result['full_text'] = '\n\n'.join(all_text)

            # Extract entities from all text
            result['entities'] = self.text_extractor.extract_all(result['full_text'])

        return result

    def extract_tables_only(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract only tables from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of extracted tables
        """
        data = self.extract_from_pdf(pdf_path)
        return data.get('tables', [])


# Convenience functions
def extract_text_entities(text: str) -> Dict[str, Any]:
    """
    Extract all entities from text.

    Args:
        text: Input text

    Returns:
        Dictionary with extracted entities
    """
    extractor = TextExtractor()
    return extractor.extract_all(text)


def extract_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extract structured data from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with extracted content
    """
    extractor = PDFExtractor()
    return extractor.extract_from_pdf(pdf_path)


def extract_from_url(url: str) -> Dict[str, Any]:
    """
    Extract structured data from a web page.

    Args:
        url: URL of the web page

    Returns:
        Dictionary with extracted content
    """
    extractor = WebExtractor()
    return extractor.extract_from_url(url)


def extract_from_html(html: str) -> Dict[str, Any]:
    """
    Extract structured data from HTML content.

    Args:
        html: HTML content

    Returns:
        Dictionary with extracted content
    """
    extractor = WebExtractor()
    return extractor.extract_from_html(html)


if __name__ == '__main__':
    # Example usage
    sample_text = """
    Contact John Smith at john.smith@example.com or call (555) 123-4567.
    The meeting is scheduled for March 15, 2024.
    The total amount is $1,234.56, representing a 15.5% increase.
    Visit our website at https://www.example.com for more information.
    """

    print("Text Entity Extraction Demo")
    print("=" * 50)

    extractor = TextExtractor()
    results = extractor.extract_all(sample_text)

    print(json.dumps(results, indent=2))
