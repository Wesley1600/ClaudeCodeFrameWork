# PDF Processing Skill

A comprehensive Claude Code skill for processing, analyzing, and converting PDF documents.

## Overview

This skill provides Claude with powerful PDF processing capabilities including:

- **Text Extraction** - Extract text from PDFs with formatting preservation
- **Table Extraction** - Extract tables and convert to CSV, JSON, or Markdown
- **Document Conversion** - Convert PDFs to Markdown, JSON, or plain text
- **Summarization** - Generate summaries with different styles
- **Visual Analysis** - Analyze charts, graphs, and visual content via Claude's native PDF support
- **Utility Functions** - Download PDFs from URLs, decode base64-encoded PDFs

## Quick Start

### Installation

1. Install required Python packages:

```bash
cd .claude/skills/pdf-processing
pip install -r assets/requirements.txt
```

2. (Optional) Install Tesseract for OCR support:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Usage

The skill activates automatically when working with PDFs. Claude will use the appropriate scripts based on your request.

**Example requests:**
- "Extract text from this PDF"
- "Get all tables from this financial report"
- "Convert this PDF to Markdown"
- "Summarize this research paper"
- "Download and process this PDF: https://example.com/doc.pdf"

## Directory Structure

```
pdf-processing/
├── SKILL.md                    # Main skill definition (read by Claude)
├── README.md                   # This file
├── scripts/                    # Python scripts for PDF processing
│   ├── extract_text.py         # Text extraction
│   ├── extract_tables.py       # Table extraction
│   ├── convert_pdf.py          # Format conversion
│   ├── summarize_pdf.py        # Document summarization
│   ├── download_pdf.py         # Download PDFs from URLs
│   └── decode_pdf.py           # Decode base64-encoded PDFs
├── references/                 # Documentation
│   ├── pdf_capabilities.md     # Claude's PDF capabilities
│   ├── api_reference.md        # Complete API documentation
│   └── examples.md             # Real-world examples
└── assets/                     # Supporting files
    └── requirements.txt        # Python dependencies
```

## Key Features

### 1. Native PDF Reading

Claude can read PDFs directly using the Read tool, which provides:
- Visual content understanding
- Text extraction
- Table recognition
- Chart and graph analysis
- Document structure analysis

### 2. Advanced Text Extraction

```bash
# Extract all text
python scripts/extract_text.py --input document.pdf --output document.txt

# Extract specific pages
python scripts/extract_text.py --input document.pdf --pages "1,5-10" --output text.txt

# Handle password-protected PDFs
python scripts/extract_text.py --input secure.pdf --password "secret" --output text.txt
```

### 3. Table Extraction

```bash
# Extract to CSV
python scripts/extract_tables.py --input report.pdf --format csv --output-dir ./tables/

# Extract to JSON
python scripts/extract_tables.py --input report.pdf --format json --output tables.json

# Extract to Markdown
python scripts/extract_tables.py --input report.pdf --format markdown --output-dir ./tables/
```

### 4. Format Conversion

```bash
# Convert to Markdown
python scripts/convert_pdf.py --input doc.pdf --output doc.md --format markdown

# Convert to JSON with metadata
python scripts/convert_pdf.py --input doc.pdf --output doc.json --format json --extract-metadata

# Convert to text
python scripts/convert_pdf.py --input doc.pdf --output doc.txt --format text
```

### 5. Document Summarization

```bash
# Concise summary
python scripts/summarize_pdf.py --input paper.pdf --output summary.md --style concise

# Detailed summary
python scripts/summarize_pdf.py --input paper.pdf --output summary.md --style detailed

# Executive summary
python scripts/summarize_pdf.py --input paper.pdf --output summary.md --style executive
```

## Common Use Cases

### Academic Research
- Extract key findings from research papers
- Extract data tables for analysis
- Generate literature review summaries

### Financial Analysis
- Extract financial tables from reports
- Analyze quarterly statements
- Process invoices and receipts

### Legal Documents
- Extract specific clauses from contracts
- Search across multiple documents
- Convert to searchable formats

### Technical Documentation
- Convert PDF manuals to Markdown
- Extract API references
- Build searchable documentation

## Dependencies

Required Python packages (see `assets/requirements.txt`):
- `pypdf` - PDF parsing
- `pdfplumber` - Advanced table extraction
- `pdf2image` - Image extraction
- `pytesseract` - OCR support
- `Pillow` - Image processing
- `requests` - URL downloads

## Documentation

- **[SKILL.md](SKILL.md)** - Complete skill instructions for Claude
- **[PDF Capabilities](references/pdf_capabilities.md)** - Detailed breakdown of features
- **[API Reference](references/api_reference.md)** - Complete script documentation
- **[Examples](references/examples.md)** - Real-world use cases and workflows

## Troubleshooting

### Common Issues

**Problem:** "Module not found" errors
```bash
# Solution: Install dependencies
pip install -r assets/requirements.txt
```

**Problem:** Text extraction from scanned PDFs fails
```bash
# Solution: Use OCR
# 1. Install tesseract (see Installation above)
# 2. The skill will automatically detect scanned PDFs
```

**Problem:** Tables not detected
```bash
# Solution: Try different extraction settings or manual verification
# Some complex tables may need manual adjustment
```

**Problem:** Password-protected PDFs
```bash
# Solution: Provide password
python scripts/extract_text.py --input secure.pdf --password "yourpassword" --output text.txt
```

## Performance

| PDF Type | Pages | Processing Time | Memory Usage |
|----------|-------|-----------------|--------------|
| Simple text | 1-50 | <5 seconds | Low |
| Simple text | 51-200 | 5-30 seconds | Medium |
| Complex layout | 1-50 | 10-60 seconds | Medium |
| Scanned (OCR) | 1-50 | 1-10 minutes | High |

## Best Practices

1. **Always read PDFs with Claude's Read tool first** - This provides the best understanding of content and structure
2. **Use appropriate extraction method** - Different PDFs require different approaches
3. **Validate outputs** - Always verify extracted data is accurate
4. **Handle errors gracefully** - Check for password protection, corruption, etc.
5. **Respect privacy** - Don't process sensitive documents without authorization

## Version History

- **1.0.0** (2025-11-18) - Initial release
  - Text extraction
  - Table extraction
  - Format conversion (Markdown, JSON, text)
  - Document summarization
  - PDF download from URLs
  - Base64 PDF decoding
  - Comprehensive documentation

## Contributing

This skill is part of the ClaudeCodeFrameWork project. For issues or improvements, please refer to the main project repository.

## License

This skill follows the license of the parent ClaudeCodeFrameWork project.

## Support

For help with this skill:
1. Check the [API Reference](references/api_reference.md) for detailed usage
2. Review [Examples](references/examples.md) for common use cases
3. Refer to [PDF Capabilities](references/pdf_capabilities.md) for technical details
4. Ask Claude for help - the skill is designed to work seamlessly with Claude's assistance

---

**Note:** This skill leverages Claude's native PDF processing capabilities combined with powerful Python libraries for comprehensive PDF handling.
