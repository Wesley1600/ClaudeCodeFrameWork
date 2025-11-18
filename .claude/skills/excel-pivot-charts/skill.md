# Excel Pivot Charts & Advanced Spreadsheet Skill

This skill provides enhanced Excel spreadsheet creation and manipulation capabilities, including pivot tables, charts, summary statistics, and advanced formulas.

## Capabilities

You can now create and manipulate Excel spreadsheets with:

1. **Basic Operations**
   - Create workbooks with multiple sheets
   - Write data with formulas and formatting
   - Read and analyze existing Excel files

2. **Pivot Tables**
   - Create pivot tables from data ranges
   - Configure row/column fields, values, and filters
   - Apply aggregation functions (SUM, COUNT, AVERAGE, etc.)
   - Custom calculated fields

3. **Charts & Visualizations**
   - Bar, column, line, pie, scatter charts
   - Pivot charts linked to pivot tables
   - Custom styling and formatting
   - Multiple chart types in one workbook

4. **Summary Statistics**
   - Descriptive statistics (mean, median, mode, std dev)
   - Correlation matrices
   - Frequency distributions
   - Conditional aggregations

## Required Libraries

Use the `openpyxl` library for Excel manipulation:

```python
import openpyxl
from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, LineChart, PieChart, ScatterChart, Reference
from openpyxl.pivot.table import TableDefinition, PivotTable
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
import numpy as np
```

## Implementation Patterns

### Pattern 1: Create Spreadsheet with Formulas

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

wb = Workbook()
ws = wb.active
ws.title = "Sales Data"

# Headers with formatting
headers = ["Product", "Q1", "Q2", "Q3", "Q4", "Total", "Average"]
for col, header in enumerate(headers, start=1):
    cell = ws.cell(1, col, header)
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

# Data with formulas
data = [
    ["Product A", 1000, 1200, 1100, 1300],
    ["Product B", 800, 900, 950, 1000],
    ["Product C", 1500, 1600, 1550, 1700]
]

for row_idx, row_data in enumerate(data, start=2):
    for col_idx, value in enumerate(row_data, start=1):
        ws.cell(row_idx, col_idx, value)

    # Total formula (sum of Q1-Q4)
    ws.cell(row_idx, 6, f"=SUM(B{row_idx}:E{row_idx})")
    # Average formula
    ws.cell(row_idx, 7, f"=AVERAGE(B{row_idx}:E{row_idx})")

# Grand totals
ws.cell(len(data) + 2, 1, "TOTAL")
for col in range(2, 8):
    col_letter = get_column_letter(col)
    ws.cell(len(data) + 2, col, f"=SUM({col_letter}2:{col_letter}{len(data)+1})")

wb.save("sales_report.xlsx")
```

### Pattern 2: Create Pivot Table

```python
from openpyxl import Workbook
from openpyxl.pivot.table import TableDefinition, PivotTable
from openpyxl.pivot.fields import RowField, ColField, DataField
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Raw Data"

# Sample data
data = [
    ["Region", "Product", "Quarter", "Sales", "Units"],
    ["North", "Product A", "Q1", 5000, 50],
    ["North", "Product A", "Q2", 5500, 55],
    ["North", "Product B", "Q1", 3000, 30],
    ["South", "Product A", "Q1", 4500, 45],
    ["South", "Product B", "Q2", 3500, 35],
    ["East", "Product A", "Q1", 6000, 60],
    ["West", "Product B", "Q2", 4000, 40]
]

for row in data:
    ws.append(row)

# Create pivot table sheet
pivot_ws = wb.create_sheet("Pivot Table")

# Define data range
data_range = f"A1:{get_column_letter(len(data[0]))}{len(data)}"

# Create pivot table
pivot = PivotTable()
pivot.addColumnField("Quarter")
pivot.addRowField("Region")
pivot.addRowField("Product")
pivot.addDataField("Sales", "Sum of Sales")
pivot.addDataField("Units", "Sum of Units")

# Note: openpyxl has limited pivot table support
# For full pivot tables, use pandas or win32com (Windows only)
# This demonstrates the structure for when opening in Excel

# Alternative: Create pivot-like summary using pandas
import pandas as pd
df = pd.DataFrame(data[1:], columns=data[0])
df['Sales'] = pd.to_numeric(df['Sales'])
df['Units'] = pd.to_numeric(df['Units'])

# Create pivot summary
pivot_summary = df.pivot_table(
    values=['Sales', 'Units'],
    index=['Region', 'Product'],
    columns='Quarter',
    aggfunc='sum',
    fill_value=0
)

# Write pivot summary to sheet
for r_idx, row in enumerate(dataframe_to_rows(pivot_summary, index=True, header=True), 1):
    for c_idx, value in enumerate(row, 1):
        pivot_ws.cell(r_idx, c_idx, value)

wb.save("pivot_example.xlsx")
```

### Pattern 3: Create Charts from Data

```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference

wb = Workbook()
ws = wb.active
ws.title = "Monthly Sales"

# Sample data
data = [
    ["Month", "Product A", "Product B", "Product C"],
    ["Jan", 100, 150, 120],
    ["Feb", 120, 160, 130],
    ["Mar", 140, 170, 140],
    ["Apr", 160, 180, 150],
    ["May", 180, 190, 160],
    ["Jun", 200, 200, 170]
]

for row in data:
    ws.append(row)

# Create Bar Chart
bar_chart = BarChart()
bar_chart.title = "Monthly Sales by Product"
bar_chart.x_axis.title = "Month"
bar_chart.y_axis.title = "Sales"

# Data for chart
categories = Reference(ws, min_col=1, min_row=2, max_row=len(data))
values = Reference(ws, min_col=2, max_col=4, min_row=1, max_row=len(data))

bar_chart.add_data(values, titles_from_data=True)
bar_chart.set_categories(categories)
bar_chart.style = 10

ws.add_chart(bar_chart, "F2")

# Create Line Chart on separate sheet
ws_line = wb.create_sheet("Line Chart")
for row in data:
    ws_line.append(row)

line_chart = LineChart()
line_chart.title = "Sales Trend"
line_chart.x_axis.title = "Month"
line_chart.y_axis.title = "Sales"

categories = Reference(ws_line, min_col=1, min_row=2, max_row=len(data))
values = Reference(ws_line, min_col=2, max_col=4, min_row=1, max_row=len(data))

line_chart.add_data(values, titles_from_data=True)
line_chart.set_categories(categories)

ws_line.add_chart(line_chart, "F2")

# Create Pie Chart for first month
ws_pie = wb.create_sheet("Pie Chart")
pie_data = [
    ["Product", "Sales"],
    ["Product A", 100],
    ["Product B", 150],
    ["Product C", 120]
]

for row in pie_data:
    ws_pie.append(row)

pie_chart = PieChart()
pie_chart.title = "January Sales Distribution"

labels = Reference(ws_pie, min_col=1, min_row=2, max_row=4)
data = Reference(ws_pie, min_col=2, min_row=1, max_row=4)

pie_chart.add_data(data, titles_from_data=True)
pie_chart.set_categories(labels)

ws_pie.add_chart(pie_chart, "E2")

wb.save("charts_example.xlsx")
```

### Pattern 4: Summary Statistics

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
import pandas as pd
import numpy as np

# Load or create data
data = {
    'Product': ['A', 'B', 'C', 'A', 'B', 'C'] * 10,
    'Sales': np.random.randint(100, 1000, 60),
    'Units': np.random.randint(10, 100, 60),
    'Region': ['North', 'South', 'East', 'West'] * 15
}

df = pd.DataFrame(data)

# Calculate statistics
stats = df.groupby('Product').agg({
    'Sales': ['count', 'sum', 'mean', 'median', 'std', 'min', 'max'],
    'Units': ['sum', 'mean', 'median']
}).round(2)

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Summary Statistics"

# Write statistics
ws.cell(1, 1, "Summary Statistics by Product").font = Font(bold=True, size=14)

# Headers
row = 3
for c_idx, col in enumerate(stats.columns, start=2):
    ws.cell(row, c_idx, f"{col[0]} - {col[1]}")
    ws.cell(row, c_idx).font = Font(bold=True)

# Product names
for r_idx, product in enumerate(stats.index, start=4):
    ws.cell(r_idx, 1, product).font = Font(bold=True)

# Statistics values
for r_idx, (idx, row_data) in enumerate(stats.iterrows(), start=4):
    for c_idx, value in enumerate(row_data, start=2):
        ws.cell(r_idx, c_idx, value)

# Correlation matrix
ws_corr = wb.create_sheet("Correlation")
ws_corr.cell(1, 1, "Correlation Matrix").font = Font(bold=True, size=14)

corr_matrix = df[['Sales', 'Units']].corr().round(3)

row = 3
for c_idx, col in enumerate([''] + list(corr_matrix.columns), start=1):
    ws_corr.cell(row, c_idx, col).font = Font(bold=True)

for r_idx, (idx, row_data) in enumerate(corr_matrix.iterrows(), start=4):
    ws_corr.cell(r_idx, 1, idx).font = Font(bold=True)
    for c_idx, value in enumerate(row_data, start=2):
        cell = ws_corr.cell(r_idx, c_idx, value)
        if abs(value) > 0.7 and value != 1.0:
            cell.fill = PatternFill(start_color="FFFF00", fill_type="solid")

wb.save("statistics_summary.xlsx")
```

## Usage Instructions

When a user requests Excel functionality:

1. **Determine the requirement:**
   - Simple data entry? Use basic openpyxl
   - Pivot table needed? Use pandas pivot_table + openpyxl
   - Charts? Use openpyxl.chart
   - Statistics? Use pandas + numpy

2. **Create the Excel file:**
   - Write Python code using the patterns above
   - Save to a .xlsx file
   - Provide the user with the filename

3. **For complex requests:**
   - Break into multiple sheets
   - Combine charts, pivot summaries, and raw data
   - Add formatting for readability

4. **Best Practices:**
   - Always format headers (bold, background color)
   - Use formulas where possible for dynamic calculations
   - Add charts on separate sheets or next to data
   - Include a "Summary" sheet for statistics
   - Use meaningful sheet names

## Limitations & Workarounds

**Limitation 1: Native Pivot Tables**
- openpyxl has limited pivot table creation support
- **Workaround:** Use pandas to create pivot-like summaries, write to Excel

**Limitation 2: Advanced Chart Types**
- Some chart types (waterfall, sunburst) not supported
- **Workaround:** Use supported charts or export data for external visualization

**Limitation 3: Macros/VBA**
- openpyxl doesn't create macros
- **Workaround:** Use Python automation instead of Excel macros

**Limitation 4: Windows-Specific Features**
- win32com (pywin32) offers full Excel control but Windows-only
- **Workaround:** Stick to openpyxl for cross-platform compatibility

## Example Workflows

### Workflow 1: Monthly Sales Report
```python
# 1. Load sales data from CSV/database
# 2. Create workbook with:
#    - Raw Data sheet
#    - Pivot Summary sheet (by region, product)
#    - Charts sheet (bar chart, line chart)
#    - Statistics sheet (mean, median, totals)
# 3. Apply formatting
# 4. Save as monthly_sales_report_YYYY_MM.xlsx
```

### Workflow 2: Financial Dashboard
```python
# 1. Create multi-sheet workbook
# 2. Sheet 1: Income Statement with formulas
# 3. Sheet 2: Balance Sheet
# 4. Sheet 3: Cash Flow
# 5. Sheet 4: Charts (revenue trends, expense breakdown)
# 6. Sheet 5: KPIs and statistics
# 7. Format with colors, borders, number formats
```

### Workflow 3: Data Analysis Report
```python
# 1. Load dataset
# 2. Calculate descriptive statistics
# 3. Create correlation matrix
# 4. Generate frequency distributions
# 5. Create visualizations
# 6. Compile everything into formatted Excel report
```

## When to Use This Skill

Use this skill when users request:
- "Create an Excel file with..."
- "Generate a pivot table..."
- "Make a chart showing..."
- "Calculate summary statistics..."
- "Create a sales report..."
- "Build a dashboard in Excel..."
- "Analyze this data in a spreadsheet..."

## Response Template

When creating Excel files, respond with:

```
I've created an Excel file with the following:

**Sheets:**
1. [Sheet Name] - [Description]
2. [Sheet Name] - [Description]

**Features:**
- Formulas for [calculations]
- Pivot summary showing [dimensions]
- [Chart type] visualizing [data]
- Summary statistics including [metrics]

**File saved as:** `[filename].xlsx`

You can open this file in Excel, LibreOffice Calc, or Google Sheets.
```

## Advanced Techniques

### Dynamic Named Ranges
```python
from openpyxl.workbook.defined_name import DefinedName

# Create named range for dynamic formulas
defn = DefinedName('SalesData', attr_text=f"'Raw Data'!$A$1:$E${len(data)}")
wb.defined_names.append(defn)
```

### Conditional Formatting
```python
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule
from openpyxl.styles import PatternFill

# Color scale for values
color_scale = ColorScaleRule(start_type='min', start_color='FF0000',
                             mid_type='percentile', mid_value=50, mid_color='FFFF00',
                             end_type='max', end_color='00FF00')
ws.conditional_formatting.add('B2:E10', color_scale)

# Highlight cells above threshold
red_fill = PatternFill(start_color='FF0000', fill_type='solid')
rule = CellIsRule(operator='greaterThan', formula=['1000'], fill=red_fill)
ws.conditional_formatting.add('B2:E10', rule)
```

### Auto-Fit Columns
```python
for column in ws.columns:
    max_length = 0
    column = [cell for cell in column]
    for cell in column:
        if len(str(cell.value)) > max_length:
            max_length = len(cell.value)
    adjusted_width = (max_length + 2)
    ws.column_dimensions[get_column_letter(column[0].column)].width = adjusted_width
```

---

Remember: Always validate user data before writing to Excel, handle errors gracefully, and provide clear documentation of what was created.
