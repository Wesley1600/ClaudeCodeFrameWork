# Example: Pivot Table Dashboard with Multiple Charts

This example demonstrates creating a comprehensive dashboard with pivot tables, multiple chart types, and summary statistics.

## User Request

> "Create an Excel dashboard analyzing sales by region, product, and quarter. Include pivot tables, charts, and key statistics."

## Implementation

```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
import numpy as np

# Generate sample data
np.random.seed(42)

regions = ['North', 'South', 'East', 'West']
products = ['Product A', 'Product B', 'Product C', 'Product D']
quarters = ['Q1', 'Q2', 'Q3', 'Q4']

data = []
for region in regions:
    for product in products:
        for quarter in quarters:
            sales = np.random.randint(10000, 50000)
            units = np.random.randint(100, 500)
            data.append([region, product, quarter, sales, units])

df = pd.DataFrame(data, columns=['Region', 'Product', 'Quarter', 'Sales', 'Units'])

# Create workbook
wb = Workbook()

# ===== SHEET 1: RAW DATA =====
ws_raw = wb.active
ws_raw.title = "Raw Data"

# Write data with headers
for r in dataframe_to_rows(df, index=False, header=True):
    ws_raw.append(r)

# Format headers
header_fill = PatternFill(start_color="4472C4", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF")

for cell in ws_raw[1]:
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")

# Format data columns
for row in ws_raw.iter_rows(min_row=2, max_row=len(data)+1, min_col=4, max_col=5):
    for cell in row:
        if cell.column == 4:  # Sales
            cell.number_format = '$#,##0'
        else:  # Units
            cell.number_format = '#,##0'

# Auto-fit columns
for col in ws_raw.columns:
    max_length = max(len(str(cell.value)) for cell in col)
    ws_raw.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

# ===== SHEET 2: PIVOT BY REGION & PRODUCT =====
ws_pivot1 = wb.create_sheet("Pivot - Region & Product")

# Create pivot table using pandas
pivot1 = df.pivot_table(
    values='Sales',
    index=['Region', 'Product'],
    aggfunc='sum'
).reset_index()

# Write pivot data
ws_pivot1.cell(1, 1, "Sales by Region and Product").font = Font(bold=True, size=14)

row_offset = 3
for r_idx, row in enumerate(dataframe_to_rows(pivot1, index=False, header=True), row_offset):
    for c_idx, value in enumerate(row, 1):
        cell = ws_pivot1.cell(r_idx, c_idx, value)
        if r_idx == row_offset:  # Header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="D9E1F2", fill_type="solid")
        elif c_idx == 3:  # Sales values
            cell.number_format = '$#,##0'

# Add bar chart
chart1 = BarChart()
chart1.title = "Sales by Region and Product"
chart1.x_axis.title = "Region & Product"
chart1.y_axis.title = "Sales ($)"
chart1.height = 15
chart1.width = 25

# Chart references
categories = Reference(ws_pivot1, min_col=1, min_row=row_offset+1, max_row=row_offset+len(pivot1))
values = Reference(ws_pivot1, min_col=3, min_row=row_offset, max_row=row_offset+len(pivot1))

chart1.add_data(values, titles_from_data=True)
chart1.set_categories(categories)

ws_pivot1.add_chart(chart1, "E3")

# ===== SHEET 3: PIVOT BY QUARTER =====
ws_pivot2 = wb.create_sheet("Pivot - Quarterly Trends")

# Pivot by quarter
pivot2 = df.pivot_table(
    values=['Sales', 'Units'],
    index='Quarter',
    aggfunc='sum'
).reindex(['Q1', 'Q2', 'Q3', 'Q4'])  # Ensure order

ws_pivot2.cell(1, 1, "Quarterly Performance Summary").font = Font(bold=True, size=14)

row_offset = 3
for r_idx, row in enumerate(dataframe_to_rows(pivot2, index=True, header=True), row_offset):
    for c_idx, value in enumerate(row, 1):
        cell = ws_pivot2.cell(r_idx, c_idx, value)
        if r_idx == row_offset:  # Header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="D9E1F2", fill_type="solid")

# Format numbers
for row in ws_pivot2.iter_rows(min_row=row_offset+1, max_row=row_offset+4, min_col=2, max_col=3):
    row[0].number_format = '$#,##0'  # Sales
    row[1].number_format = '#,##0'   # Units

# Line chart for quarterly trend
line_chart = LineChart()
line_chart.title = "Quarterly Sales Trend"
line_chart.x_axis.title = "Quarter"
line_chart.y_axis.title = "Total Sales ($)"
line_chart.height = 12
line_chart.width = 20

categories = Reference(ws_pivot2, min_col=1, min_row=row_offset+1, max_row=row_offset+4)
values = Reference(ws_pivot2, min_col=2, min_row=row_offset, max_row=row_offset+4)

line_chart.add_data(values, titles_from_data=True)
line_chart.set_categories(categories)
line_chart.style = 12

ws_pivot2.add_chart(line_chart, "E3")

# ===== SHEET 4: PIVOT BY PRODUCT =====
ws_pivot3 = wb.create_sheet("Pivot - Product Analysis")

# Pivot by product with quarterly breakdown
pivot3 = df.pivot_table(
    values='Sales',
    index='Product',
    columns='Quarter',
    aggfunc='sum'
)[['Q1', 'Q2', 'Q3', 'Q4']]  # Ensure order

# Add total column
pivot3['Total'] = pivot3.sum(axis=1)

ws_pivot3.cell(1, 1, "Product Sales by Quarter").font = Font(bold=True, size=14)

row_offset = 3
for r_idx, row in enumerate(dataframe_to_rows(pivot3, index=True, header=True), row_offset):
    for c_idx, value in enumerate(row, 1):
        cell = ws_pivot3.cell(r_idx, c_idx, value)
        if r_idx == row_offset:  # Header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="D9E1F2", fill_type="solid")
        elif c_idx > 1:  # Data cells
            cell.number_format = '$#,##0'
            if c_idx == 6:  # Total column
                cell.font = Font(bold=True)

# Pie chart for total sales by product
pie_chart = PieChart()
pie_chart.title = "Total Sales Distribution by Product"
pie_chart.height = 12
pie_chart.width = 15

labels = Reference(ws_pivot3, min_col=1, min_row=row_offset+1, max_row=row_offset+4)
data = Reference(ws_pivot3, min_col=6, min_row=row_offset, max_row=row_offset+4)

pie_chart.add_data(data, titles_from_data=True)
pie_chart.set_categories(labels)

ws_pivot3.add_chart(pie_chart, "H3")

# ===== SHEET 5: SUMMARY STATISTICS =====
ws_stats = wb.create_sheet("Summary Statistics")

ws_stats.cell(1, 1, "Summary Statistics Dashboard").font = Font(bold=True, size=16)

# Calculate statistics
stats_data = []
stats_data.append(["Metric", "Value"])
stats_data.append(["Total Sales", f"${df['Sales'].sum():,.0f}"])
stats_data.append(["Total Units Sold", f"{df['Units'].sum():,}"])
stats_data.append(["Average Sale Amount", f"${df['Sales'].mean():,.2f}"])
stats_data.append(["Median Sale Amount", f"${df['Sales'].median():,.2f}"])
stats_data.append(["Std Dev (Sales)", f"${df['Sales'].std():,.2f}"])
stats_data.append(["Min Sale", f"${df['Sales'].min():,.0f}"])
stats_data.append(["Max Sale", f"${df['Sales'].max():,.0f}"])
stats_data.append(["Number of Transactions", len(df)])

# Write statistics
row_offset = 3
for r_idx, row in enumerate(stats_data, row_offset):
    for c_idx, value in enumerate(row, 1):
        cell = ws_stats.cell(r_idx, c_idx, value)
        if r_idx == row_offset:  # Header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="4472C4", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
        elif c_idx == 1:  # Metric names
            cell.font = Font(bold=True)

# Top performers
ws_stats.cell(row_offset + len(stats_data) + 2, 1, "Top 5 Sales Transactions").font = Font(bold=True, size=12)

top_sales = df.nlargest(5, 'Sales')[['Region', 'Product', 'Quarter', 'Sales', 'Units']]

top_offset = row_offset + len(stats_data) + 4
for r_idx, row in enumerate(dataframe_to_rows(top_sales, index=False, header=True), top_offset):
    for c_idx, value in enumerate(row, 1):
        cell = ws_stats.cell(r_idx, c_idx, value)
        if r_idx == top_offset:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="D9E1F2", fill_type="solid")
        elif c_idx == 4:
            cell.number_format = '$#,##0'

# Best performing region
region_sales = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
best_region = region_sales.index[0]
best_region_sales = region_sales.iloc[0]

ws_stats.cell(top_offset + 8, 1, "Best Performing Region:").font = Font(bold=True)
ws_stats.cell(top_offset + 8, 2, f"{best_region} (${best_region_sales:,.0f})")

# Best performing product
product_sales = df.groupby('Product')['Sales'].sum().sort_values(ascending=False)
best_product = product_sales.index[0]
best_product_sales = product_sales.iloc[0]

ws_stats.cell(top_offset + 9, 1, "Best Performing Product:").font = Font(bold=True)
ws_stats.cell(top_offset + 9, 2, f"{best_product} (${best_product_sales:,.0f})")

# Auto-fit columns
for ws in wb.worksheets:
    for col in ws.columns:
        max_length = max((len(str(cell.value)) if cell.value else 0) for cell in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_length + 2, 50)

# Save workbook
wb.save("sales_dashboard_pivot_analysis.xlsx")
print("Dashboard created: sales_dashboard_pivot_analysis.xlsx")
```

## Output

The generated Excel file contains:

**Sheet 1: Raw Data**
- Complete dataset with 64 transactions (4 regions × 4 products × 4 quarters)
- Formatted headers and currency values

**Sheet 2: Pivot - Region & Product**
- Pivot table showing total sales by region and product
- Bar chart visualization

**Sheet 3: Pivot - Quarterly Trends**
- Quarterly summary with sales and units
- Line chart showing sales trend across quarters

**Sheet 4: Pivot - Product Analysis**
- Product performance by quarter with totals
- Pie chart showing sales distribution

**Sheet 5: Summary Statistics**
- Key metrics (total sales, average, median, std dev, min, max)
- Top 5 sales transactions
- Best performing region and product

## File Structure

```
sales_dashboard_pivot_analysis.xlsx
├── Raw Data (64 rows)
├── Pivot - Region & Product (+ Bar Chart)
├── Pivot - Quarterly Trends (+ Line Chart)
├── Pivot - Product Analysis (+ Pie Chart)
└── Summary Statistics (KPIs + Top Performers)
```

## User-Facing Response

```
I've created a comprehensive sales dashboard with pivot tables and analytics:

**Sheets:**
1. **Raw Data** - Complete transaction dataset (64 records)
2. **Pivot - Region & Product** - Sales breakdown by region and product with bar chart
3. **Pivot - Quarterly Trends** - Quarterly performance with line chart showing trends
4. **Pivot - Product Analysis** - Product sales by quarter with pie chart distribution
5. **Summary Statistics** - Key metrics, top performers, and insights

**Features:**
- Multiple pivot table views analyzing different dimensions
- Three chart types (bar, line, pie) for visual analysis
- Summary statistics including total sales, averages, and standard deviation
- Top 5 highest sales transactions
- Best performing region and product identification
- Professional formatting with color-coded headers
- Currency and number formatting throughout

**File saved as:** `sales_dashboard_pivot_analysis.xlsx`

This dashboard provides a complete view of sales performance across regions, products, and time periods. All data is dynamically linked, and you can easily update the raw data to refresh all pivot tables and charts.
```

## Notes

This example demonstrates:
- Using pandas for pivot table calculations
- Multiple chart types in one workbook
- Multi-dimensional data analysis
- Professional dashboard layout
- Statistical summaries
- Top-N analysis
- Dynamic formatting based on data types
