# Vision Skill - Quick Reference Card

## Common Commands

### OCR / Text Extraction
```
"Extract text from screenshot.png"
"Read the text in this image"
"Transcribe this handwritten note"
```

### Image Classification
```
"What type of image is this?"
"Classify the objects in photo.jpg"
"Identify the content of this picture"
```

### Chart & Graph Analysis
```
"Analyze this chart and extract the data"
"What trends do you see in sales_graph.png?"
"Convert this chart to CSV format"
```

### Image Comparison
```
"Compare design_v1.png and design_v2.png"
"What changed between these screenshots?"
"Find differences in these two diagrams"
```

### Detailed Description
```
"Describe this image in detail"
"What's in this photo?"
"Generate an alt-text description for accessibility"
```

### UI/UX Analysis
```
"Analyze this UI screenshot"
"List all interactive elements in this mockup"
"Review this design for accessibility issues"
```

### Document Processing
```
"Extract data from this receipt"
"Process this invoice and output JSON"
"Parse this form and extract field values"
```

## Helper Script Quick Commands

### Metadata
```bash
python .claude/skills/vision/scripts/image_processor.py \
  --operation metadata --input image.jpg --json
```

### Convert Format
```bash
python .claude/skills/vision/scripts/image_processor.py \
  --operation convert --input image.png --format jpg
```

### Resize
```bash
python .claude/skills/vision/scripts/image_processor.py \
  --operation resize --input large.jpg --width 1024
```

### Batch Process
```bash
python .claude/skills/vision/scripts/image_processor.py \
  --operation batch --input ./images/ --task resize --width 800
```

## Supported Image Formats

✅ PNG, JPEG/JPG, GIF, WebP, BMP, TIFF
✅ PDF (single page images)
❌ Multi-page PDFs (extract pages first)
❌ Raw formats (RAW, CR2, NEF) - convert first

## Best Practices

### For Best OCR Results
- Use 300 DPI or higher
- Ensure high contrast
- Keep text straight (not rotated)
- Use PNG for screenshots with text

### For Chart Analysis
- Minimum 800×600 resolution
- Clear labels and legends
- Avoid overlapping elements
- Use solid colors

### For UI Analysis
- Full-resolution screenshots
- Capture complete viewport
- Include context (browser chrome if relevant)
- Multiple device sizes if responsive

## Output Formats

| Task | Default Output | Alternative |
|------|---------------|-------------|
| OCR | Markdown text | Plain text, structured JSON |
| Classification | Category labels | Confidence scores, hierarchical |
| Charts | Markdown table + insights | CSV, JSON data |
| Comparison | Diff table | Side-by-side list |
| Description | Paragraph | Bullet list, alt-text |
| UI Analysis | Component breakdown | JSON structure |
| Documents | JSON structured data | CSV, markdown table |

## Privacy Reminders

⚠️ **Before analyzing images:**
- Redact personal information (PII)
- Remove passwords, API keys, tokens
- Check for confidential business data
- Review company policies on cloud processing

## Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| "Cannot read image" | Check file path and format |
| "Low confidence OCR" | Increase resolution, improve contrast |
| "Chart data unclear" | Simplify chart, increase size |
| "Image too large" | Resize with helper script first |

## File Locations

- **Skill Definition:** `.claude/skills/vision/SKILL.md`
- **Helper Script:** `.claude/skills/vision/scripts/image_processor.py`
- **Full Documentation:** `.claude/skills/vision/references/README.md`
- **This Reference:** `.claude/skills/vision/references/QUICK_REFERENCE.md`

## Examples By Industry

### E-commerce
- Product photo analysis
- UI screenshot testing
- Receipt processing

### Healthcare
- Medical chart review
- Form digitization
- Report analysis

### Finance
- Invoice processing
- Chart analysis
- Document extraction

### Development
- UI bug reporting
- Design comparison
- Code screenshot extraction

### Marketing
- Design review
- A/B test comparison
- Asset categorization

### Legal
- Document scanning
- Contract review
- Evidence analysis

## Version

**Vision Skill v1.0.0** | Updated: 2025-11-18

---

*For detailed documentation, see README.md in the references folder.*
