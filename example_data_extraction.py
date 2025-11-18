"""
Data Extraction Examples

Demonstrates how to use the data_extraction module to extract
structured information from various sources.
"""

import json
from data_extraction import (
    TextExtractor,
    TableExtractor,
    WebExtractor,
    PDFExtractor,
    extract_text_entities,
    extract_from_pdf,
    extract_from_url,
    extract_from_html,
)


def example_text_extraction():
    """Example: Extract entities from plain text."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Text Entity Extraction")
    print("=" * 70)

    sample_text = """
    Dear Mr. Johnson,

    I hope this email finds you well. I am writing to confirm our meeting
    scheduled for January 15, 2024, at 2:30 PM.

    Please contact me at sarah.williams@company.com or call (555) 987-6543
    if you need to reschedule.

    Regarding the invoice #INV-2024-001, the total amount due is $5,432.10,
    which represents a 12.5% discount from the original price of $6,207.54.

    Payment can be made to account number 1234-5678-9012-3456.

    Our office is located at 123 Main Street, New York, NY 10001.

    You can also visit our website at https://www.example-company.com for
    more information.

    The project timeline shows 45 days until completion, with an estimated
    completion rate of 87.3%.

    Best regards,
    Sarah Williams
    Senior Account Manager
    """

    # Method 1: Using convenience function
    print("\nMethod 1: Using convenience function")
    print("-" * 70)
    entities = extract_text_entities(sample_text)
    print(json.dumps(entities, indent=2))

    # Method 2: Using TextExtractor class
    print("\n\nMethod 2: Using TextExtractor class")
    print("-" * 70)
    extractor = TextExtractor()

    print("\nEmails found:")
    print(extractor.extract_emails(sample_text))

    print("\nPhone numbers found:")
    print(extractor.extract_phone_numbers(sample_text))

    print("\nDates found:")
    print(json.dumps(extractor.extract_dates(sample_text), indent=2))

    print("\nAmounts found:")
    print(json.dumps(extractor.extract_amounts(sample_text), indent=2))

    print("\nPercentages found:")
    print(json.dumps(extractor.extract_percentages(sample_text), indent=2))

    print("\nNames found:")
    print(extractor.extract_names(sample_text))

    print("\nURLs found:")
    print(extractor.extract_urls(sample_text))

    print("\nZIP codes found:")
    print(extractor.extract_zip_codes(sample_text))


def example_table_extraction():
    """Example: Extract tables from HTML."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Table Extraction from HTML")
    print("=" * 70)

    html_content = """
    <html>
    <body>
        <h1>Sales Report Q4 2023</h1>

        <table id="sales-table" class="data-table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Units Sold</th>
                    <th>Revenue</th>
                    <th>Profit Margin</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Widget A</td>
                    <td>1,250</td>
                    <td>$62,500</td>
                    <td>28.5%</td>
                </tr>
                <tr>
                    <td>Widget B</td>
                    <td>850</td>
                    <td>$42,500</td>
                    <td>32.1%</td>
                </tr>
                <tr>
                    <td>Widget C</td>
                    <td>2,100</td>
                    <td>$105,000</td>
                    <td>25.3%</td>
                </tr>
            </tbody>
        </table>

        <table id="employee-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Department</th>
                    <th>Email</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Alice Johnson</td>
                    <td>Engineering</td>
                    <td>alice.j@company.com</td>
                </tr>
                <tr>
                    <td>Bob Smith</td>
                    <td>Marketing</td>
                    <td>bob.s@company.com</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """

    extractor = TableExtractor()
    tables = extractor.extract_from_html(html_content)

    print(f"\nFound {len(tables)} table(s):\n")

    for i, table in enumerate(tables, 1):
        print(f"Table {i}:")
        print(f"  Headers: {table['headers']}")
        print(f"  Rows: {len(table['rows'])}")
        print(f"  Metadata: {table['metadata']}")
        print(f"\nFirst few rows:")
        for row in table['rows'][:3]:
            print(f"    {row}")

        # Convert to list of dictionaries
        print(f"\nAs dictionary list:")
        dict_list = extractor.table_to_dict_list(table)
        for row_dict in dict_list[:2]:
            print(f"    {row_dict}")
        print()


def example_csv_extraction():
    """Example: Extract data from CSV."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: CSV Data Extraction")
    print("=" * 70)

    csv_content = """Name,Age,Email,Salary,Start Date
John Doe,32,john.doe@example.com,$75000,2020-03-15
Jane Smith,28,jane.smith@example.com,$82000,2021-06-01
Bob Johnson,45,bob.j@example.com,$95000,2018-01-10
Alice Williams,36,alice.w@example.com,$88000,2019-09-22"""

    extractor = TableExtractor()
    table = extractor.extract_from_csv(csv_content)

    print("\nCSV Data:")
    print(f"Headers: {table['headers']}")
    print(f"Number of rows: {len(table['rows'])}\n")

    # Convert to dictionary list for easy access
    dict_list = extractor.table_to_dict_list(table)

    print("Employees:")
    for employee in dict_list:
        print(f"  - {employee['Name']}: {employee['Email']} (Salary: {employee['Salary']})")


def example_web_extraction():
    """Example: Extract data from a web page."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Web Page Data Extraction")
    print("=" * 70)

    html_sample = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Company Contact Page</title>
        <meta name="description" content="Contact information for our company">
        <meta property="og:title" content="Contact Us">
    </head>
    <body>
        <h1>Contact Information</h1>

        <p>Reach out to us:</p>
        <p>Email: info@example.com</p>
        <p>Phone: (555) 123-4567</p>
        <p>Address: 456 Business Ave, Suite 100, San Francisco, CA 94105</p>

        <h2>Office Hours</h2>
        <p>Monday - Friday: 9:00 AM - 5:00 PM</p>
        <p>Closed on January 1, 2024 for New Year's Day</p>

        <h2>Quick Links</h2>
        <ul>
            <li><a href="/about">About Us</a></li>
            <li><a href="/services">Our Services</a></li>
            <li><a href="https://blog.example.com">Blog</a></li>
        </ul>

        <img src="/images/office.jpg" alt="Our office building">
    </body>
    </html>
    """

    data = extract_from_html(html_sample, url="https://www.example.com/contact")

    print("\nExtracted Data:\n")
    print(f"Title: {data['metadata']['title']}")
    print(f"\nMeta Tags:")
    for key, value in data['metadata']['meta_tags'].items():
        print(f"  {key}: {value}")

    print(f"\nText Preview (first 200 chars):")
    print(f"  {data['text_content'][:200]}...")

    print(f"\nEntities Found:")
    print(f"  Emails: {data['entities']['emails']}")
    print(f"  Phone Numbers: {data['entities']['phone_numbers']}")
    print(f"  Dates: {[d['raw'] for d in data['entities']['dates']]}")
    print(f"  ZIP Codes: {data['entities']['zip_codes']}")

    print(f"\nLinks Found ({len(data['links'])} total):")
    for link in data['links'][:5]:
        print(f"  - {link['text']}: {link['href']}")

    print(f"\nImages Found ({len(data['images'])} total):")
    for img in data['images']:
        print(f"  - {img['alt']}: {img['src']}")


def example_pdf_extraction():
    """Example: Extract data from PDF (requires pdfplumber)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: PDF Data Extraction")
    print("=" * 70)

    print("\nTo use PDF extraction:")
    print("1. Install pdfplumber: pip install pdfplumber")
    print("2. Call extract_from_pdf(pdf_path)")
    print("\nExample code:")

    example_code = """
    from data_extraction import extract_from_pdf

    # Extract all data from PDF
    data = extract_from_pdf('invoice.pdf')

    # Access metadata
    print(f"Number of pages: {data['metadata']['num_pages']}")

    # Access text from each page
    for page in data['pages']:
        print(f"Page {page['page_number']}:")
        print(page['text'][:200])  # First 200 chars

    # Access tables
    for table in data['tables']:
        print(f"Table on page {table['page']}:")
        print(f"Headers: {table['headers']}")
        print(f"Rows: {len(table['rows'])}")

    # Access extracted entities
    print(f"Emails found: {data['entities']['emails']}")
    print(f"Amounts found: {data['entities']['amounts']}")
    print(f"Dates found: {data['entities']['dates']}")
    """

    print(example_code)


def example_combined_workflow():
    """Example: Combined workflow with multiple extractors."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Combined Workflow")
    print("=" * 70)

    # Simulate a document processing workflow
    document_text = """
    Invoice #INV-2024-0123
    Date: February 15, 2024

    Bill To:
    Acme Corporation
    John Doe, Purchasing Manager
    john.doe@acme.com
    (555) 234-5678

    Items:
    - Widget Pro (Qty: 100) @ $49.99 each = $4,999.00
    - Service Plan (12 months) = $1,200.00

    Subtotal: $6,199.00
    Tax (8.5%): $526.92
    Total: $6,725.92

    Payment due by March 15, 2024
    """

    print("\nProcessing invoice document...\n")

    # Extract all entities
    extractor = TextExtractor()
    entities = extractor.extract_all(document_text)

    # Build structured invoice object
    invoice = {
        'invoice_number': 'INV-2024-0123',
        'date': entities['dates'][0] if entities['dates'] else None,
        'customer': {
            'name': entities['names'][0] if entities['names'] else None,
            'email': entities['emails'][0] if entities['emails'] else None,
            'phone': entities['phone_numbers'][0] if entities['phone_numbers'] else None,
        },
        'amounts': entities['amounts'],
        'total': entities['amounts'][-1] if entities['amounts'] else None,
        'due_date': entities['dates'][1] if len(entities['dates']) > 1 else None,
    }

    print("Structured Invoice Data:")
    print(json.dumps(invoice, indent=2))

    # Extract specific information
    print("\n\nKey Information:")
    print(f"Invoice Number: {invoice['invoice_number']}")
    print(f"Invoice Date: {invoice['date']['raw'] if invoice['date'] else 'N/A'}")
    print(f"Customer: {invoice['customer']['name']}")
    print(f"Email: {invoice['customer']['email']}")
    print(f"Total Amount: ${invoice['total']['value']:.2f}" if invoice['total'] else "N/A")
    print(f"Due Date: {invoice['due_date']['raw'] if invoice['due_date'] else 'N/A'}")


def run_all_examples():
    """Run all examples."""
    print("\n" + "█" * 70)
    print("DATA EXTRACTION MODULE - COMPREHENSIVE EXAMPLES")
    print("█" * 70)

    try:
        example_text_extraction()
    except Exception as e:
        print(f"\nError in text extraction example: {e}")

    try:
        example_table_extraction()
    except Exception as e:
        print(f"\nError in table extraction example: {e}")
        print("Note: Install beautifulsoup4 with: pip install beautifulsoup4")

    try:
        example_csv_extraction()
    except Exception as e:
        print(f"\nError in CSV extraction example: {e}")

    try:
        example_web_extraction()
    except Exception as e:
        print(f"\nError in web extraction example: {e}")
        print("Note: Install beautifulsoup4 with: pip install beautifulsoup4")

    try:
        example_pdf_extraction()
    except Exception as e:
        print(f"\nError in PDF extraction example: {e}")

    try:
        example_combined_workflow()
    except Exception as e:
        print(f"\nError in combined workflow example: {e}")

    print("\n" + "█" * 70)
    print("EXAMPLES COMPLETED")
    print("█" * 70)


if __name__ == '__main__':
    run_all_examples()
