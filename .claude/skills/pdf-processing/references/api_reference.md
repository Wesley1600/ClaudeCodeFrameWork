# PDF Processing Scripts - API Reference

Complete reference for all PDF processing scripts in this skill.

## Table of Contents

1. [extract_text.py](#extract_textpy)
2. [extract_tables.py](#extract_tablespy)
3. [convert_pdf.py](#convert_pdfpy)
4. [summarize_pdf.py](#summarize_pdfpy)
5. [download_pdf.py](#download_pdfpy)
6. [decode_pdf.py](#decode_pdfpy)

---

## extract_text.py

Extract text content from PDF files with optional formatting preservation.

### Usage

```bash
python extract_text.py --input INPUT_PDF [OPTIONS]
```

### Arguments

| Argument | Short | Type | Required | Default | Description |
|----------|-------|------|----------|---------|-------------|
| `--input` | `-i` | Path | Yes | - | Input PDF file path |
| `--output` | `-o` | Path | No | stdout | Output text file path |
| `--pages` | `-p` | String | No | all | Pages to extract (e.g., "1,3,5-10") |
| `--password` | - | String | No | - | Password for encrypted PDFs |
| `--preserve-formatting` | - | Boolean | No | true | Preserve formatting with page markers |
| `--chunk-size` | - | Integer | No | - | Process in chunks of N pages |

### Examples

```bash
# Extract all text
python extract_text.py --input document.pdf --output document.txt

# Extract specific pages
python extract_text.py --input document.pdf --pages "1,5-10,15" --output selected.txt

# Extract from encrypted PDF
python extract_text.py --input secure.pdf --password "secret123" --output document.txt

# Process large PDF in chunks
python extract_text.py --input large.pdf --chunk-size 10 --output document.txt

# Print to stdout
python extract_text.py --input document.pdf
```

### Return Codes

- `0` - Success
- `1` - Error (file not found, processing failed, etc.)

### Output Format

```
================================================================================
PAGE 1
================================================================================

[Page 1 text content...]


================================================================================
PAGE 2
================================================================================

[Page 2 text content...]
```

---

## extract_tables.py

Extract tables from PDF files and convert to CSV, JSON, or Markdown.

### Usage

```bash
python extract_tables.py --input INPUT_PDF [OPTIONS]
```

### Arguments

| Argument | Short | Type | Required | Default | Description |
|----------|-------|------|----------|---------|-------------|
| `--input` | `-i` | Path | Yes | - | Input PDF file path |
| `--format` | `-f` | String | No | csv | Output format (csv, json, markdown) |
| `--output-dir` | `-d` | Path | No | - | Directory for individual table files |
| `--output` | `-o` | Path | No | - | Single output file (JSON only) |

### Examples

```bash
# Extract all tables to CSV
python extract_tables.py --input document.pdf --format csv --output-dir ./tables/

# Extract to JSON
python extract_tables.py --input document.pdf --format json --output tables.json

# Extract to Markdown
python extract_tables.py --input document.pdf --format markdown --output-dir ./tables/
```

### Output Files

**CSV Format:**
- `table_1_page_2.csv`
- `table_2_page_5.csv`
- etc.

**JSON Format (single file):**
```json
[
  {
    "page": 2,
    "table_number": 1,
    "headers": ["Column 1", "Column 2", "Column 3"],
    "rows": [
      ["Data 1", "Data 2", "Data 3"],
      ["Data 4", "Data 5", "Data 6"]
    ]
  }
]
```

**Markdown Format:**
```markdown
# Table 1 (Page 2)

| Column 1 | Column 2 | Column 3 |
|---|---|---|
| Data 1 | Data 2 | Data 3 |
| Data 4 | Data 5 | Data 6 |
```

### Return Codes

- `0` - Success
- `1` - Error

---

## convert_pdf.py

Convert PDF files to various formats (Markdown, JSON, plain text).

### Usage

```bash
python convert_pdf.py --input INPUT_PDF --output OUTPUT_FILE [OPTIONS]
```

### Arguments

| Argument | Short | Type | Required | Default | Description |
|----------|-------|------|----------|---------|-------------|
| `--input` | `-i` | Path | Yes | - | Input PDF file path |
| `--output` | `-o` | Path | Yes | - | Output file path |
| `--format` | `-f` | String | No | markdown | Output format (markdown, json, text) |
| `--preserve-images` | - | Flag | No | false | Preserve and extract images (Markdown only) |
| `--extract-metadata` | - | Flag | No | false | Include PDF metadata in output |

### Examples

```bash
# Convert to Markdown
python convert_pdf.py --input document.pdf --output document.md --format markdown

# Convert to JSON with metadata
python convert_pdf.py --input document.pdf --output document.json --format json --extract-metadata

# Convert to text
python convert_pdf.py --input document.pdf --output document.txt --format text

# Markdown with images and metadata
python convert_pdf.py --input document.pdf --output document.md --format markdown --preserve-images --extract-metadata
```

### Output Formats

**Markdown:**
```markdown
---
title: Document Title
author: Author Name
pages: 42
---

## Page 1

Document content...

### Table 1

| Col1 | Col2 |
|------|------|
| A    | B    |
```

**JSON:**
```json
{
  "source": "/path/to/document.pdf",
  "metadata": {
    "title": "Document Title",
    "pages": 42
  },
  "content": [
    {
      "page": 1,
      "type": "text",
      "content": "..."
    },
    {
      "page": 2,
      "type": "table",
      "headers": ["Col1", "Col2"],
      "rows": [["A", "B"]]
    }
  ]
}
```

### Return Codes

- `0` - Success
- `1` - Error

---

## summarize_pdf.py

Summarize PDF content by extracting key information.

### Usage

```bash
python summarize_pdf.py --input INPUT_PDF --output OUTPUT_FILE [OPTIONS]
```

### Arguments

| Argument | Short | Type | Required | Default | Description |
|----------|-------|------|----------|---------|-------------|
| `--input` | `-i` | Path | Yes | - | Input PDF file path |
| `--output` | `-o` | Path | Yes | - | Output summary file (Markdown) |
| `--style` | `-s` | String | No | concise | Summary style (concise, detailed, executive) |

### Summary Styles

| Style | Description | Length | Use Case |
|-------|-------------|--------|----------|
| `concise` | Brief overview with key points | Short | Quick review |
| `detailed` | Comprehensive summary with excerpts | Medium | Thorough understanding |
| `executive` | Executive-level summary with highlights | Medium | Decision-making |

### Examples

```bash
# Concise summary
python summarize_pdf.py --input document.pdf --output summary.md --style concise

# Detailed summary
python summarize_pdf.py --input document.pdf --output summary.md --style detailed

# Executive summary
python summarize_pdf.py --input document.pdf --output summary.md --style executive
```

### Output Format

```markdown
# PDF Document Summary

**Source:** document.pdf
**Generated:** summarize_pdf.py

## Document Information

- **Title:** Document Title
- **Author:** Author Name
- **Pages:** 42
- **Words:** ~10,500
- **Tables:** 5

## Key Content

1. First key point extracted from document.
2. Second key point with important information.
...

---

*This summary was automatically generated.*
```

### Return Codes

- `0` - Success
- `1` - Error

---

## download_pdf.py

Download PDF files from URLs.

### Usage

```bash
python download_pdf.py --url URL --output OUTPUT_FILE [OPTIONS]
```

### Arguments

| Argument | Short | Type | Required | Default | Description |
|----------|-------|------|----------|---------|-------------|
| `--url` | `-u` | String | Yes | - | URL of the PDF file |
| `--output` | `-o` | Path | Yes | - | Output file path |
| `--no-verify-ssl` | - | Flag | No | false | Disable SSL verification |

### Examples

```bash
# Download PDF
python download_pdf.py --url "https://example.com/document.pdf" --output document.pdf

# Download without SSL verification (use with caution)
python download_pdf.py --url "https://example.com/doc.pdf" --output doc.pdf --no-verify-ssl
```

### Output

```
Downloading PDF from: https://example.com/document.pdf
Progress: 100.0%
PDF downloaded successfully: document.pdf
File size: 2543.2 KB
```

### Return Codes

- `0` - Success
- `1` - Error (network error, invalid URL, etc.)

---

## decode_pdf.py

Decode base64-encoded PDF content.

### Usage

```bash
python decode_pdf.py --output OUTPUT_FILE [INPUT_OPTIONS]
```

### Arguments

| Argument | Short | Type | Required | Default | Description |
|----------|-------|------|----------|---------|-------------|
| `--input` | `-i` | Path | No* | - | Input file with base64 content |
| `--string` | `-s` | String | No* | - | Base64 string directly |
| `--output` | `-o` | Path | Yes | - | Output PDF file path |

\* Either `--input` or `--string` must be provided

### Examples

```bash
# Decode from file
python decode_pdf.py --input base64_content.txt --output document.pdf

# Decode from string
python decode_pdf.py --string "JVBERi0xLjQKJeLjz9MKM..." --output document.pdf

# Decode data URI
python decode_pdf.py --string "data:application/pdf;base64,JVBERi..." --output document.pdf
```

### Input Format

The script accepts:
- Plain base64 string
- Data URI format: `data:application/pdf;base64,<base64-data>`
- File containing base64 content

### Output

```
Decoding base64 content...
PDF decoded successfully: document.pdf
File size: 1234.5 KB
```

### Return Codes

- `0` - Success
- `1` - Error (invalid base64, not a PDF, etc.)

---

## Common Error Handling

All scripts follow consistent error handling:

### File Not Found

```
Error: PDF file not found: /path/to/document.pdf
Exit code: 1
```

### Password Protected

```
Error: PDF is password-protected. Please provide password with --password
Exit code: 1
```

### Invalid PDF

```
Warning: Decoded data doesn't appear to be a valid PDF
```

### Processing Error

```
Error: Failed to extract text: [detailed error message]
Exit code: 1
```

## Integration with Claude

All scripts are designed to work seamlessly with Claude's workflow:

1. **Read PDF first** - Use Claude's Read tool to analyze the PDF
2. **Determine needs** - Claude identifies what extraction is needed
3. **Execute script** - Run appropriate script with correct parameters
4. **Validate output** - Check that files were created successfully
5. **Present results** - Show user what was extracted

### Example Integration

```python
# Step 1: Claude reads PDF
Read(file_path="/path/to/document.pdf")

# Step 2: Claude determines user wants tables
# User said: "Extract all tables from this PDF"

# Step 3: Execute extraction
Bash: python .claude/skills/pdf-processing/scripts/extract_tables.py \
  --input /path/to/document.pdf \
  --format csv \
  --output-dir ./extracted_tables/

# Step 4: Validate
Bash: ls -la ./extracted_tables/

# Step 5: Present results
Read: ./extracted_tables/table_1_page_2.csv
```

## Version History

- **1.0.0** (2025-11-18) - Initial API documentation
