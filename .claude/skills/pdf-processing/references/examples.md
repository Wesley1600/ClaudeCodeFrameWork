# PDF Processing Examples

Real-world examples and use cases for the PDF processing skill.

## Table of Contents

1. [Academic Research](#academic-research)
2. [Financial Reports](#financial-reports)
3. [Legal Documents](#legal-documents)
4. [Technical Documentation](#technical-documentation)
5. [Form Processing](#form-processing)
6. [Invoice Extraction](#invoice-extraction)
7. [Batch Processing](#batch-processing)
8. [Advanced Workflows](#advanced-workflows)

---

## Academic Research

### Use Case: Extract Key Findings from Research Paper

**Scenario:** Researcher wants to quickly extract key findings from a 50-page academic paper.

**Workflow:**

```bash
# Step 1: Read PDF to understand structure
Read(file_path="/path/to/research_paper.pdf")

# Step 2: Generate executive summary
python scripts/summarize_pdf.py \
  --input /path/to/research_paper.pdf \
  --output paper_summary.md \
  --style executive

# Step 3: Extract tables with statistical data
python scripts/extract_tables.py \
  --input /path/to/research_paper.pdf \
  --format csv \
  --output-dir ./paper_tables/

# Step 4: Convert references section to text
python scripts/extract_text.py \
  --input /path/to/research_paper.pdf \
  --pages "48-50" \
  --output references.txt
```

**Output:**
- `paper_summary.md` - Executive summary with key findings
- `./paper_tables/` - CSV files with statistical data
- `references.txt` - Bibliography for citation

---

## Financial Reports

### Use Case: Analyze Quarterly Financial Statement

**Scenario:** Analyst needs to extract financial tables and key metrics from quarterly report.

**Workflow:**

```bash
# Step 1: Read PDF
Read(file_path="/path/to/Q4_2024_Financial_Report.pdf")

# Step 2: Extract all financial tables
python scripts/extract_tables.py \
  --input /path/to/Q4_2024_Financial_Report.pdf \
  --format json \
  --output financial_data.json

# Step 3: Extract key sections
python scripts/extract_text.py \
  --input /path/to/Q4_2024_Financial_Report.pdf \
  --pages "3-5,10-12" \
  --output key_sections.txt

# Step 4: Generate summary
python scripts/summarize_pdf.py \
  --input /path/to/Q4_2024_Financial_Report.pdf \
  --output report_summary.md \
  --style executive
```

**Follow-up Analysis:**

```python
import json
import pandas as pd

# Load extracted tables
with open('financial_data.json') as f:
    tables = json.load(f)

# Convert to DataFrame for analysis
for table in tables:
    if table['type'] == 'table':
        df = pd.DataFrame(table['rows'], columns=table['headers'])
        # Perform financial analysis
        print(df.describe())
```

---

## Legal Documents

### Use Case: Extract Clauses from Contract

**Scenario:** Lawyer needs to extract specific clauses from a 100-page contract.

**Workflow:**

```bash
# Step 1: Read PDF
Read(file_path="/path/to/contract.pdf")

# Step 2: Convert to searchable format
python scripts/convert_pdf.py \
  --input /path/to/contract.pdf \
  --output contract.md \
  --format markdown \
  --extract-metadata

# Step 3: Extract specific pages (identified after reading)
python scripts/extract_text.py \
  --input /path/to/contract.pdf \
  --pages "15-20,45-50,80-85" \
  --output key_clauses.txt
```

**Then search in Markdown:**

```bash
# Search for specific terms
grep -i "liability" contract.md
grep -i "termination" contract.md
grep -i "indemnification" contract.md
```

---

## Technical Documentation

### Use Case: Convert PDF Manual to Markdown Documentation

**Scenario:** Developer wants to convert PDF user manual to Markdown for a wiki.

**Workflow:**

```bash
# Step 1: Read PDF
Read(file_path="/path/to/user_manual.pdf")

# Step 2: Convert to Markdown with metadata
python scripts/convert_pdf.py \
  --input /path/to/user_manual.pdf \
  --output user_manual.md \
  --format markdown \
  --preserve-images \
  --extract-metadata

# Step 3: Extract tables separately for review
python scripts/extract_tables.py \
  --input /path/to/user_manual.pdf \
  --format markdown \
  --output-dir ./manual_tables/

# Step 4: Generate TOC summary
python scripts/summarize_pdf.py \
  --input /path/to/user_manual.pdf \
  --output manual_overview.md \
  --style detailed
```

**Post-Processing:**

```bash
# Clean up Markdown formatting
# Add to version control
git add user_manual.md manual_tables/ manual_overview.md
git commit -m "Add converted user manual"
```

---

## Form Processing

### Use Case: Extract Data from Filled Forms

**Scenario:** Process hundreds of filled PDF forms and extract data to database.

**Workflow:**

```bash
# Step 1: Process single form to understand structure
Read(file_path="/path/to/forms/form_001.pdf")

# Step 2: Extract to structured JSON
python scripts/convert_pdf.py \
  --input /path/to/forms/form_001.pdf \
  --output form_001.json \
  --format json \
  --extract-metadata

# Step 3: Extract any tables (for multi-entry forms)
python scripts/extract_tables.py \
  --input /path/to/forms/form_001.pdf \
  --format json \
  --output form_001_tables.json
```

**Batch Processing:**

```bash
# Process all forms
for form in /path/to/forms/*.pdf; do
    base_name=$(basename "$form" .pdf)
    python scripts/convert_pdf.py \
        --input "$form" \
        --output "processed/${base_name}.json" \
        --format json
done
```

---

## Invoice Extraction

### Use Case: Extract Invoice Data for Accounting

**Scenario:** Accountant needs to extract invoice details from PDF invoices.

**Workflow:**

```bash
# Step 1: Read sample invoice
Read(file_path="/path/to/invoices/invoice_2024_001.pdf")

# Step 2: Extract text to identify key fields
python scripts/extract_text.py \
  --input /path/to/invoices/invoice_2024_001.pdf \
  --output invoice_text.txt

# Step 3: Extract invoice table (line items)
python scripts/extract_tables.py \
  --input /path/to/invoices/invoice_2024_001.pdf \
  --format csv \
  --output-dir ./invoice_data/
```

**Parse Invoice Fields:**

```python
import re

with open('invoice_text.txt') as f:
    text = f.read()

# Extract invoice number
invoice_num = re.search(r'Invoice #(\d+)', text)
# Extract date
date = re.search(r'Date: (\d{2}/\d{2}/\d{4})', text)
# Extract total
total = re.search(r'Total: \$([0-9,]+\.\d{2})', text)

invoice_data = {
    'invoice_number': invoice_num.group(1) if invoice_num else None,
    'date': date.group(1) if date else None,
    'total': total.group(1) if total else None
}
```

---

## Batch Processing

### Use Case: Process Multiple PDFs in Bulk

**Scenario:** Process 100 PDF documents and extract all content.

**Batch Script:**

```bash
#!/bin/bash
# batch_process.sh

INPUT_DIR="./pdfs"
OUTPUT_DIR="./processed"
TABLES_DIR="./tables"
SUMMARIES_DIR="./summaries"

mkdir -p "$OUTPUT_DIR" "$TABLES_DIR" "$SUMMARIES_DIR"

# Process each PDF
for pdf in "$INPUT_DIR"/*.pdf; do
    base_name=$(basename "$pdf" .pdf)
    echo "Processing: $base_name"

    # Extract text
    python scripts/extract_text.py \
        --input "$pdf" \
        --output "$OUTPUT_DIR/${base_name}.txt"

    # Extract tables
    python scripts/extract_tables.py \
        --input "$pdf" \
        --format csv \
        --output-dir "$TABLES_DIR/${base_name}/"

    # Generate summary
    python scripts/summarize_pdf.py \
        --input "$pdf" \
        --output "$SUMMARIES_DIR/${base_name}_summary.md" \
        --style concise

    echo "Completed: $base_name"
done

echo "Batch processing complete!"
```

**Run Batch:**

```bash
chmod +x batch_process.sh
./batch_process.sh
```

---

## Advanced Workflows

### Use Case 1: PDF to Blog Post

**Scenario:** Convert a whitepaper PDF to a blog post with proper formatting.

```bash
# 1. Read PDF
Read(file_path="/path/to/whitepaper.pdf")

# 2. Convert to Markdown
python scripts/convert_pdf.py \
  --input /path/to/whitepaper.pdf \
  --output blog_draft.md \
  --format markdown \
  --preserve-images

# 3. Extract key quotes for callouts
python scripts/summarize_pdf.py \
  --input /path/to/whitepaper.pdf \
  --output key_points.md \
  --style executive

# 4. Manual editing in blog_draft.md
# - Add SEO meta tags
# - Format code blocks
# - Add call-to-action
```

### Use Case 2: PDF Comparison

**Scenario:** Compare two versions of a document.

```bash
# 1. Extract text from both versions
python scripts/extract_text.py \
  --input document_v1.pdf \
  --output v1.txt

python scripts/extract_text.py \
  --input document_v2.pdf \
  --output v2.txt

# 2. Use diff to compare
diff -u v1.txt v2.txt > changes.diff

# 3. Or use a more sophisticated tool
git diff --no-index v1.txt v2.txt
```

### Use Case 3: PDF Data Pipeline

**Scenario:** Automated pipeline for processing uploaded PDFs.

```python
#!/usr/bin/env python3
# pdf_pipeline.py

import subprocess
import json
from pathlib import Path

def process_pdf_pipeline(pdf_path):
    """Complete PDF processing pipeline."""

    base_name = Path(pdf_path).stem
    output_dir = Path(f"./processed/{base_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Extract metadata and convert to JSON
    json_path = output_dir / f"{base_name}.json"
    subprocess.run([
        'python', 'scripts/convert_pdf.py',
        '--input', pdf_path,
        '--output', str(json_path),
        '--format', 'json',
        '--extract-metadata'
    ])

    # Step 2: Extract tables
    tables_dir = output_dir / 'tables'
    subprocess.run([
        'python', 'scripts/extract_tables.py',
        '--input', pdf_path,
        '--format', 'csv',
        '--output-dir', str(tables_dir)
    ])

    # Step 3: Generate summary
    summary_path = output_dir / f"{base_name}_summary.md"
    subprocess.run([
        'python', 'scripts/summarize_pdf.py',
        '--input', pdf_path,
        '--output', str(summary_path),
        '--style', 'concise'
    ])

    # Step 4: Load and return results
    with open(json_path) as f:
        data = json.load(f)

    return {
        'pdf': pdf_path,
        'output_dir': str(output_dir),
        'metadata': data.get('metadata'),
        'tables_count': len(list(tables_dir.glob('*.csv'))) if tables_dir.exists() else 0,
        'summary': str(summary_path)
    }

# Use in automation
if __name__ == '__main__':
    result = process_pdf_pipeline('./uploads/new_document.pdf')
    print(json.dumps(result, indent=2))
```

### Use Case 4: OCR for Scanned PDFs

**Scenario:** Extract text from scanned documents.

```bash
# 1. Convert PDF to images
python -c "
from pdf2image import convert_from_path
images = convert_from_path('scanned_document.pdf')
for i, img in enumerate(images):
    img.save(f'page_{i+1}.png', 'PNG')
"

# 2. Apply OCR to each page
for img in page_*.png; do
    tesseract "$img" "${img%.png}" -l eng
done

# 3. Combine all text files
cat page_*.txt > scanned_document_ocr.txt

# 4. Clean up temporary files
rm page_*.png page_*.txt
```

### Use Case 5: PDF Search Index

**Scenario:** Build searchable index of PDF library.

```python
#!/usr/bin/env python3
# build_search_index.py

import json
import subprocess
from pathlib import Path
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

# Define search schema
schema = Schema(
    path=ID(stored=True),
    filename=TEXT(stored=True),
    content=TEXT,
    title=TEXT(stored=True),
    author=TEXT(stored=True)
)

# Create index
index_dir = Path("./search_index")
index_dir.mkdir(exist_ok=True)
ix = create_in(str(index_dir), schema)

# Process all PDFs
writer = ix.writer()
for pdf_path in Path("./pdf_library").glob("**/*.pdf"):
    print(f"Indexing: {pdf_path}")

    # Extract text
    result = subprocess.run([
        'python', 'scripts/extract_text.py',
        '--input', str(pdf_path)
    ], capture_output=True, text=True)

    text_content = result.stdout

    # Extract metadata
    metadata_result = subprocess.run([
        'python', 'scripts/convert_pdf.py',
        '--input', str(pdf_path),
        '--output', '/tmp/temp.json',
        '--format', 'json',
        '--extract-metadata'
    ], capture_output=True)

    with open('/tmp/temp.json') as f:
        data = json.load(f)
        metadata = data.get('metadata', {})

    # Add to index
    writer.add_document(
        path=str(pdf_path),
        filename=pdf_path.name,
        content=text_content,
        title=metadata.get('title', pdf_path.stem),
        author=metadata.get('author', 'Unknown')
    )

writer.commit()
print("Search index built successfully!")

# Example search
from whoosh.qparser import MultifieldParser

with ix.searcher() as searcher:
    query = MultifieldParser(["content", "title"], ix.schema).parse("machine learning")
    results = searcher.search(query, limit=10)

    print(f"\nFound {len(results)} results for 'machine learning':")
    for hit in results:
        print(f"  - {hit['filename']}: {hit['title']}")
```

---

## Performance Tips

### For Large PDFs (>100 pages)

```bash
# Use chunked processing
python scripts/extract_text.py \
  --input large_document.pdf \
  --chunk-size 20 \
  --output document.txt
```

### For High-Volume Processing

```bash
# Parallel processing with GNU parallel
find ./pdfs -name "*.pdf" | \
parallel python scripts/extract_text.py --input {} --output {.}.txt
```

### For Scanned PDFs

```bash
# Optimize OCR accuracy with preprocessing
convert input.pdf -density 300 -depth 8 -quality 85 output.pdf
python scripts/extract_text.py --input output.pdf --output text.txt
```

---

## Troubleshooting Examples

### Problem: Jumbled Text from Multi-Column PDF

**Solution:**

```bash
# Use pdfplumber for better layout analysis
python -c "
import pdfplumber
with pdfplumber.open('multi_column.pdf') as pdf:
    for page in pdf.pages:
        # Extract with layout preservation
        text = page.extract_text(layout=True)
        print(text)
"
```

### Problem: Missing Tables

**Solution:**

```bash
# Try different table extraction settings
python -c "
import pdfplumber
with pdfplumber.open('document.pdf') as pdf:
    for page in pdf.pages:
        tables = page.extract_tables(table_settings={
            'vertical_strategy': 'text',
            'horizontal_strategy': 'text'
        })
        for table in tables:
            print(table)
"
```

---

## Version History

- **1.0.0** (2025-11-18) - Initial examples documentation
