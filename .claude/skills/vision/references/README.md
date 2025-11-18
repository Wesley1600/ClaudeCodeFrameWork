# Vision Skill - Reference Documentation

## Overview

This reference guide provides detailed examples, use cases, and best practices for the Vision skill in Claude Code.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Common Use Cases](#common-use-cases)
3. [Advanced Examples](#advanced-examples)
4. [Helper Script Reference](#helper-script-reference)
5. [Tips and Best Practices](#tips-and-best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Activating the Vision Skill

The vision skill is automatically available in Claude Code. Simply provide an image and request analysis:

```
User: "Analyze this screenshot: /path/to/screenshot.png"
```

Claude will automatically read and analyze the image using vision capabilities.

### Basic Operations

**Extract Text (OCR):**
```
"Extract all text from screenshot.png"
"Read the text in this receipt image"
"What does this sign say?"
```

**Classify Images:**
```
"What type of image is this?"
"Classify the content of diagram.png"
"Identify the objects in this photo"
```

**Analyze Charts:**
```
"Analyze the data in this chart"
"Extract values from this graph"
"What trends do you see in sales_chart.png?"
```

**Compare Images:**
```
"Compare design_v1.png and design_v2.png"
"What changed between these two screenshots?"
"Find differences in these diagrams"
```

---

## Common Use Cases

### 1. Screenshot Documentation

**Scenario:** You need to document UI elements from screenshots for testing or documentation.

**Example:**
```
User: "Analyze this UI screenshot and list all the interactive elements"

Claude: (After loading the image)

## UI Element Analysis

**Interactive Elements Detected:**

1. **Navigation Bar** (Top)
   - Logo (top-left)
   - Search bar (center)
   - User menu dropdown (top-right)

2. **Primary Content Area**
   - Submit button (blue, center-right)
   - Cancel button (gray, center-left)
   - 3 input fields (Name, Email, Phone)

3. **Sidebar** (Left)
   - Dashboard link
   - Reports link
   - Settings link

**Accessibility Notes:**
- All buttons have visible labels
- Good color contrast (WCAG AA compliant)
- Touch targets appear to be 44px minimum
```

### 2. Receipt and Invoice Processing

**Scenario:** Extract structured data from receipts for expense tracking.

**Example:**
```
User: "Extract the data from this receipt and format it as JSON"

Claude: (After analyzing the receipt)

```json
{
  "merchant": "Coffee Shop",
  "date": "2025-11-18",
  "time": "09:45 AM",
  "items": [
    {
      "description": "Latte",
      "quantity": 2,
      "unit_price": 4.50,
      "total": 9.00
    },
    {
      "description": "Croissant",
      "quantity": 1,
      "unit_price": 3.25,
      "total": 3.25
    }
  ],
  "subtotal": 12.25,
  "tax": 1.23,
  "total": 13.48,
  "payment_method": "Credit Card ending in 4242"
}
```
```

### 3. Chart Data Extraction

**Scenario:** Convert chart visualizations back into raw data for analysis.

**Example:**
```
User: "Extract the data points from this line chart as a CSV table"

Claude: (After analyzing the chart)

## Extracted Chart Data

```csv
Month,Revenue,Expenses,Profit
January,45000,32000,13000
February,48000,33500,14500
March,52000,35000,17000
April,49000,34000,15000
May,55000,36500,18500
June,58000,37000,21000
```

**Chart Type:** Multi-series line chart
**Time Period:** January - June 2025
**Series:** 3 (Revenue, Expenses, Profit)

**Key Observation:** Consistent upward trend in all metrics, with profit margin improving from 28.9% in January to 36.2% in June.
```

### 4. Design Comparison and Review

**Scenario:** Review design iterations and identify changes.

**Example:**
```
User: "Compare mockup_before.png and mockup_after.png and create a change summary"

Claude: (After analyzing both images)

## Design Revision Summary

### Layout Changes
- **Header height:** Reduced from 80px to 64px
- **Grid system:** Changed from 12-column to 16-column layout
- **Card spacing:** Increased from 16px to 24px

### Color Updates
| Element | Before | After | Change |
|---------|--------|-------|--------|
| Primary Button | #0066CC | #0052A3 | Darker blue |
| Background | #F5F5F5 | #FFFFFF | Pure white |
| Text | #333333 | #1A1A1A | Darker gray |

### Typography Changes
- Body font size: 16px → 15px
- Heading font: Roboto → Inter
- Line height: 1.5 → 1.6

### New Components
- Breadcrumb navigation (below header)
- Filter panel (left sidebar)
- Pagination controls (bottom)

### Removed Components
- Legacy sidebar menu
- Footer quick links

### Overall Assessment
This revision modernizes the design with improved spacing and a cleaner color palette. The typography changes enhance readability. The addition of breadcrumbs and filters improves navigation.
```

### 5. Handwritten Note Transcription

**Scenario:** Digitize handwritten meeting notes.

**Example:**
```
User: "Transcribe the handwritten notes from this meeting photo"

Claude: (After analyzing the image)

## Meeting Notes - Transcription

**Date:** Nov 18, 2025
**Topic:** Q4 Planning

**Action Items:**
1. Review budget proposals by Friday
2. Schedule team workshop for Dec 5th
3. Update project timeline (Sarah)
4. Prepare client presentation (Mike)

**Key Decisions:**
- Approved hiring 2 new developers
- Postponed feature X to Q1 2026
- Increased marketing budget by 15%

**Next Steps:**
- Follow-up meeting: Nov 25, 2:00 PM
- Send calendar invites to all attendees

**Notes:**
- Some text in bottom-right corner partially obscured
- Bullet point symbols interpreted as dashes
- Underlined text indicates priority items
```

### 6. Code Screenshot to Code

**Scenario:** Extract code from screenshots or images.

**Example:**
```
User: "Extract the code from this screenshot and save it to a file"

Claude: (After analyzing the code screenshot)

I'll extract the code and save it:

```python
def calculate_fibonacci(n: int) -> list[int]:
    """
    Calculate Fibonacci sequence up to n terms.

    Args:
        n: Number of terms to generate

    Returns:
        List of Fibonacci numbers
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]

    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])

    return fib


# Example usage
result = calculate_fibonacci(10)
print(f"First 10 Fibonacci numbers: {result}")
```

**Saving to file...**

(Uses Write tool to save the extracted code)

✓ Code extracted and saved to `fibonacci.py`

**Note:** Formatting and indentation preserved from the original screenshot.
```

---

## Advanced Examples

### Multi-Image Analysis Workflow

Process multiple related images:

```
User: "I have 5 product photos. Analyze each and create a comparison table of features visible in each image."

Claude: (After loading all 5 images)

## Product Photo Analysis - Comparison

| Feature | Photo 1 | Photo 2 | Photo 3 | Photo 4 | Photo 5 |
|---------|---------|---------|---------|---------|---------|
| View Angle | Front | Side | Top | Back | Detail |
| USB Ports | 2 visible | 1 visible | - | 3 visible | Close-up |
| Color | Silver | Silver | Silver | Silver | Silver |
| Screen Size | 15" display | - | - | - | - |
| Keyboard | Full-size | Partial | Full view | - | Keys detail |
| Logo Position | Center lid | - | Top-right | Center | - |
| Dimensions | ~ 14" × 10" | ~ 1" thick | Full footprint | - | - |

**Overall Observations:**
- Consistent silver/aluminum finish across all views
- Modern minimalist design
- Multiple connectivity options (USB, likely Thunderbolt)
- Standard laptop form factor, ~15" class

**Recommendation:** These images provide comprehensive coverage for a product listing or documentation.
```

### Diagram to Code Generation

Convert flowcharts or diagrams into code:

```
User: "Convert this flowchart to Python code"

Claude: (After analyzing flowchart image)

Based on the flowchart, here's the Python implementation:

```python
def process_order(order_amount: float, customer_type: str) -> dict:
    """
    Process order based on flowchart logic.

    Args:
        order_amount: Total order amount in dollars
        customer_type: 'new' or 'existing'

    Returns:
        dict with final_amount and discount_applied
    """
    discount = 0.0

    # Check customer type
    if customer_type == 'new':
        discount = 0.10  # 10% discount for new customers
    elif customer_type == 'existing':
        # Check order amount threshold
        if order_amount > 100:
            discount = 0.15  # 15% discount for orders over $100
        else:
            discount = 0.05  # 5% discount for existing customers

    # Calculate final amount
    discount_amount = order_amount * discount
    final_amount = order_amount - discount_amount

    return {
        'original_amount': order_amount,
        'discount_percentage': discount * 100,
        'discount_amount': discount_amount,
        'final_amount': final_amount,
        'customer_type': customer_type
    }


# Example usage
result = process_order(150, 'existing')
print(f"Final amount: ${result['final_amount']:.2f}")
print(f"You saved: ${result['discount_amount']:.2f} ({result['discount_percentage']}%)")
```

**Flowchart Logic Mapped:**
- Diamond 1: Customer Type check → if/elif branches
- Diamond 2: Order Amount > $100 → nested condition
- Rectangles: Discount calculations → variable assignments
- Arrows: Control flow → sequential execution
```

### Visual Bug Reporting

Document visual bugs with detailed analysis:

```
User: "Analyze this screenshot of a layout bug and describe what's wrong"

Claude: (After analyzing the buggy screenshot)

## Visual Bug Analysis

### Issue Summary
**Severity:** High - Layout breaking bug
**Component:** Product grid layout
**Browser:** Appears to be Chrome/modern browser

### Identified Problems

**1. Card Overlap (Critical)**
- **Location:** Row 2, Column 3
- **Description:** Product card overlapping with adjacent card
- **Expected:** 16px margin between cards
- **Actual:** ~8px negative margin causing overlap

**2. Image Aspect Ratio Distortion**
- **Location:** Row 1, Column 2
- **Description:** Product image stretched vertically
- **Expected:** 4:3 aspect ratio
- **Actual:** Approximately 4:5 (squeezed)

**3. Text Truncation**
- **Location:** Multiple cards
- **Description:** Product titles cut off without ellipsis
- **Expected:** "..." after max 2 lines
- **Actual:** Hard cut at container boundary

**4. Button Misalignment**
- **Location:** All cards
- **Description:** "Add to Cart" buttons not bottom-aligned
- **Expected:** Aligned to bottom of card container
- **Actual:** Floating based on content height

### Suspected Root Causes

```css
/* Likely problematic CSS: */
.product-card {
  /* Missing: */
  box-sizing: border-box;

  /* Incorrect: */
  margin: calc(-8px); /* Should be positive value */
}

.product-image {
  /* Missing: */
  object-fit: cover;
  aspect-ratio: 4/3;
}

.product-title {
  /* Missing: */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
```

### Recommended Fixes

1. **Fix card spacing:** Remove negative margin, ensure consistent gap
2. **Fix image aspect:** Add `object-fit: cover` and explicit aspect ratio
3. **Fix text truncation:** Implement multi-line ellipsis with line-clamp
4. **Fix button alignment:** Use flexbox with `margin-top: auto`

### Testing Checklist
- [ ] Test on Chrome, Firefox, Safari
- [ ] Verify at 1920×1080, 1366×768, 768×1024
- [ ] Check with varying content lengths
- [ ] Validate with long product names (50+ chars)
```

---

## Helper Script Reference

### Installation

Ensure Python and Pillow are installed:

```bash
# Install Pillow for image processing
pip install Pillow

# Verify installation
python .claude/skills/vision/scripts/image_processor.py --help
```

### Script Operations

#### 1. Extract Metadata

```bash
# Get image metadata
python .claude/skills/vision/scripts/image_processor.py \
  --operation metadata \
  --input photo.jpg \
  --json

# Output:
# {
#   "filename": "photo.jpg",
#   "format": "JPEG",
#   "width": 1920,
#   "height": 1080,
#   "size": "1920x1080",
#   "size_bytes": 245678,
#   "exif": {...}
# }
```

#### 2. Convert Image Format

```bash
# Convert PNG to JPEG
python .claude/skills/vision/scripts/image_processor.py \
  --operation convert \
  --input image.png \
  --output image.jpg \
  --quality 95

# Convert to WebP
python .claude/skills/vision/scripts/image_processor.py \
  --operation convert \
  --input photo.jpg \
  --format webp
```

#### 3. Resize Images

```bash
# Resize maintaining aspect ratio (width only)
python .claude/skills/vision/scripts/image_processor.py \
  --operation resize \
  --input large.jpg \
  --width 800

# Resize to exact dimensions (no aspect ratio preservation)
python .claude/skills/vision/scripts/image_processor.py \
  --operation resize \
  --input image.jpg \
  --width 1024 \
  --height 768 \
  --no-aspect
```

#### 4. Batch Processing

```bash
# Convert all images in directory to JPG
python .claude/skills/vision/scripts/image_processor.py \
  --operation batch \
  --input ./images/ \
  --task convert \
  --format jpg \
  --quality 90

# Resize all images in directory
python .claude/skills/vision/scripts/image_processor.py \
  --operation batch \
  --input ./photos/ \
  --task resize \
  --width 1024 \
  --output ./photos/resized/

# Extract metadata for all images
python .claude/skills/vision/scripts/image_processor.py \
  --operation batch \
  --input ./screenshots/ \
  --task metadata \
  --json > metadata.json
```

---

## Tips and Best Practices

### Image Quality Guidelines

**For OCR (Text Extraction):**
- Minimum 150 DPI, preferably 300 DPI
- High contrast between text and background
- Minimal compression artifacts
- Straight orientation (not rotated)

**For Chart Analysis:**
- Clear axis labels and legends
- Sufficient resolution (min 800×600)
- Avoid overlapping elements
- Use solid colors rather than patterns

**For UI/UX Analysis:**
- Full-resolution screenshots
- Capture complete viewport
- Include browser chrome if relevant
- Consider multiple device sizes

### Optimization Tips

1. **Crop Before Analysis:** Focus on relevant areas to improve accuracy
2. **Enhance Contrast:** For poor quality scans, enhance before OCR
3. **Multiple Angles:** Provide different views for complex objects
4. **Context Matters:** Mention the domain (medical, legal, technical)

### Privacy and Security

**⚠️ Important Considerations:**

- **Redact sensitive info** before analysis (PII, passwords, API keys)
- **Don't share** screenshots containing confidential data
- **Be aware** of metadata in images (GPS, timestamps)
- **Consider** company policies on cloud image processing

### File Format Recommendations

| Use Case | Recommended Format | Why |
|----------|-------------------|-----|
| Screenshots | PNG | Lossless, good for text |
| Photos | JPEG (90% quality) | Smaller size, good visual quality |
| Diagrams | PNG or SVG | Sharp lines, scalable |
| Archival | TIFF or PNG | Lossless, preserves detail |
| Web | WebP | Modern, efficient compression |

---

## Troubleshooting

### Common Issues

**Issue:** "Cannot read image file"
- **Cause:** File path incorrect or file corrupted
- **Solution:** Verify path, check file integrity, try re-saving

**Issue:** "Low confidence text extraction"
- **Cause:** Poor image quality, low resolution, or bad lighting
- **Solution:** Rescan at higher DPI, improve lighting, enhance contrast

**Issue:** "Unable to detect chart data"
- **Cause:** Chart too stylized, low contrast, or complex overlay
- **Solution:** Simplify chart, increase size, remove background patterns

**Issue:** "Image dimensions too large"
- **Cause:** Very high resolution image exceeding limits
- **Solution:** Resize using helper script before analysis

### Performance Tips

**Large Images:**
```bash
# Resize before analysis
python .claude/skills/vision/scripts/image_processor.py \
  --operation resize \
  --input huge_image.jpg \
  --width 2048 \
  --output optimized.jpg

# Then analyze
"Analyze optimized.jpg..."
```

**Batch Operations:**
- Process in smaller groups (10-20 images)
- Use batch script for preprocessing
- Save results incrementally

### Getting Help

If you encounter issues:

1. Check image format compatibility
2. Verify file permissions
3. Review error messages carefully
4. Try with a simpler test image
5. Consult Claude Code documentation

---

## Version History

- **v1.0.0** (2025-11-18): Initial release
  - Core vision capabilities
  - Helper script implementation
  - Comprehensive documentation

---

## License

This skill is licensed under Apache-2.0.

## Contributing

To improve this skill:

1. Test with various image types
2. Document edge cases
3. Share effective prompts
4. Report issues and suggestions

---

**Questions or feedback?** The vision skill is designed to evolve based on real-world usage. Experiment with different prompts and image types to discover what works best for your use case.
