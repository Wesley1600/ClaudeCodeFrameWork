# Example: Basic Sales Report with Charts

This example demonstrates creating a sales report with formulas, summary statistics, and charts.

## User Request

> "Create an Excel sales report for Q1-Q4 with three products. Include totals, averages, and a bar chart."

## Implementation

```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Sales Report"

# Header styling
headers = ["Product", "Q1", "Q2", "Q3", "Q4", "Total", "Average"]
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF", size=12)

for col, header in enumerate(headers, start=1):
    cell = ws.cell(1, col, header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center")

# Sales data
data = [
    ["Product A", 15000, 18000, 16500, 19000],
    ["Product B", 12000, 13500, 14000, 15500],
    ["Product C", 20000, 21000, 22000, 23500]
]

# Write data and formulas
for row_idx, row_data in enumerate(data, start=2):
    # Write product name and quarterly sales
    for col_idx, value in enumerate(row_data, start=1):
        cell = ws.cell(row_idx, col_idx, value)
        if col_idx == 1:
            cell.font = Font(bold=True)
        else:
            cell.number_format = '$#,##0'

    # Total formula
    total_cell = ws.cell(row_idx, 6, f"=SUM(B{row_idx}:E{row_idx})")
    total_cell.number_format = '$#,##0'
    total_cell.font = Font(bold=True)

    # Average formula
    avg_cell = ws.cell(row_idx, 7, f"=AVERAGE(B{row_idx}:E{row_idx})")
    avg_cell.number_format = '$#,##0'

# Grand totals row
total_row = len(data) + 2
ws.cell(total_row, 1, "GRAND TOTAL").font = Font(bold=True, size=11)

for col in range(2, 8):
    col_letter = get_column_letter(col)
    cell = ws.cell(total_row, col, f"=SUM({col_letter}2:{col_letter}{len(data)+1})")
    cell.number_format = '$#,##0'
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color="D9E1F2", fill_type="solid")

# Adjust column widths
ws.column_dimensions['A'].width = 15
for col in range(2, 8):
    ws.column_dimensions[get_column_letter(col)].width = 12

# Create bar chart
chart = BarChart()
chart.title = "Quarterly Sales by Product"
chart.x_axis.title = "Product"
chart.y_axis.title = "Sales ($)"
chart.style = 10
chart.height = 10
chart.width = 20

# Chart data
categories = Reference(ws, min_col=1, min_row=2, max_row=len(data)+1)
values = Reference(ws, min_col=2, max_col=5, min_row=1, max_row=len(data)+1)

chart.add_data(values, titles_from_data=True)
chart.set_categories(categories)

# Position chart
ws.add_chart(chart, "A7")

# Save workbook
wb.save("sales_report_q1_q4.xlsx")
print("Sales report created: sales_report_q1_q4.xlsx")
```

## Output

The generated Excel file contains:

**Sheet: Sales Report**
- Headers with blue background and white text
- 3 products with quarterly sales data
- Formulas for Total (sum of quarters) and Average
- Grand totals row with light blue background
- Currency formatting ($XX,XXX)
- Bar chart showing all products across all quarters

## File Structure

```
sales_report_q1_q4.xlsx
└── Sales Report
    ├── Data table (A1:G5)
    │   ├── Headers (row 1)
    │   ├── Product data (rows 2-4)
    │   └── Grand totals (row 5)
    └── Bar Chart (A7:K21)
```

## User-Facing Response

```
I've created a sales report for Q1-Q4 with the following:

**Data:**
- 3 products (A, B, C) with quarterly sales figures
- Total column calculating sum of all quarters
- Average column calculating quarterly average
- Grand totals row summing all products

**Formatting:**
- Professional blue header with white text
- Currency formatting for all monetary values
- Bold text for product names and totals

**Visualization:**
- Bar chart displaying all products across all quarters
- Clear labels and title

**File saved as:** `sales_report_q1_q4.xlsx`

You can open this in Excel, LibreOffice, or Google Sheets. All totals and averages are calculated with formulas, so they'll update automatically if you change any values.
```
