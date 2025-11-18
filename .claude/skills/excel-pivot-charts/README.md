# Excel Pivot Charts & Advanced Spreadsheet Skill

A comprehensive Claude Code skill for creating and manipulating Excel spreadsheets with enhanced capabilities including pivot tables, charts, summary statistics, and advanced data analysis.

## Overview

This skill extends Claude's built-in Excel capabilities by providing specialized tools for:

- **Pivot Tables**: Multi-dimensional data summarization and aggregation
- **Charts & Visualizations**: Bar, line, pie, scatter charts with professional styling
- **Summary Statistics**: Descriptive statistics, correlation matrices, distribution analysis
- **Advanced Formulas**: Dynamic calculations, conditional logic, aggregations
- **Outlier Detection**: Statistical outlier identification using IQR method
- **Regression Analysis**: Linear regression with statistical significance testing
- **Professional Formatting**: Color scales, conditional formatting, styled headers

## Installation

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

### Core Dependencies

- `openpyxl` - Excel file creation and manipulation
- `pandas` - Data analysis and pivot table functionality
- `numpy` - Numerical operations and statistics
- `scipy` - Advanced statistical analysis

## Usage

This skill is automatically invoked when you request Excel-related operations that involve:

1. Creating spreadsheets with formulas
2. Generating pivot tables
3. Creating charts from data
4. Calculating summary statistics
5. Performing data analysis

### Example Requests

**Basic Sales Report:**
```
Create an Excel sales report for Q1-Q4 with three products.
Include totals, averages, and a bar chart.
```

**Pivot Table Dashboard:**
```
Create an Excel dashboard analyzing sales by region, product, and quarter.
Include pivot tables, charts, and key statistics.
```

**Statistical Analysis:**
```
Analyze my sales data and create a statistical report with correlations,
distributions, and outlier detection in Excel.
```

## Features

### 1. Pivot Tables

Create multi-dimensional data summaries:

- Row and column groupings
- Multiple aggregation functions (SUM, COUNT, AVERAGE, MIN, MAX)
- Calculated fields
- Subtotals and grand totals
- Professional formatting

**Example Output:**
```
Region    | Product   | Q1 Sales | Q2 Sales | Total
----------|-----------|----------|----------|-------
North     | Product A | $15,000  | $18,000  | $33,000
North     | Product B | $12,000  | $13,500  | $25,500
South     | Product A | $14,500  | $16,000  | $30,500
```

### 2. Charts & Visualizations

Supported chart types:

- **Bar Charts**: Categorical comparisons
- **Line Charts**: Trend analysis over time
- **Pie Charts**: Proportional distributions
- **Scatter Charts**: Relationship analysis

All charts include:
- Custom titles and axis labels
- Professional styling
- Legend placement
- Multiple data series support

### 3. Summary Statistics

Comprehensive statistical analysis:

- **Descriptive Statistics**: Mean, median, mode, std deviation
- **Quartiles**: Q1, Q3, IQR
- **Distribution Shape**: Skewness, kurtosis
- **Range Statistics**: Min, max, range
- **Frequency Distributions**: Binned data with percentages

### 4. Correlation Analysis

Identify relationships between variables:

- Pearson correlation coefficients
- Color-coded correlation matrix
- Strength indicators (strong, moderate, weak)
- Visual heatmap representation

### 5. Outlier Detection

Statistical outlier identification:

- IQR (Interquartile Range) method
- Upper and lower bounds
- List of outlier values
- Visual highlighting in data

### 6. Regression Analysis

Linear regression modeling:

- Slope and intercept calculation
- R-squared (coefficient of determination)
- P-value for statistical significance
- Standard error
- Scatter plots with trend lines
- Predicted vs actual values

### 7. Professional Formatting

Enhanced visual presentation:

- **Headers**: Bold fonts, background colors, white text
- **Number Formats**: Currency, percentages, thousands separators
- **Conditional Formatting**: Color scales, cell highlighting
- **Borders**: Clean table separators
- **Alignment**: Centered headers, right-aligned numbers
- **Auto-fit Columns**: Optimal column widths

## File Structure

```
.claude/skills/excel-pivot-charts/
├── README.md                    # This file
├── skill.md                     # Main skill implementation
├── requirements.txt             # Python dependencies
└── examples/
    ├── basic_sales_report.md           # Simple report example
    ├── pivot_table_dashboard.md        # Dashboard example
    └── advanced_statistics.md          # Statistical analysis example
```

## Examples

### Example 1: Basic Sales Report

Creates a simple quarterly sales report with:
- Product sales by quarter
- Total and average formulas
- Grand totals row
- Bar chart visualization
- Currency formatting

**See**: `examples/basic_sales_report.md`

### Example 2: Pivot Table Dashboard

Creates a comprehensive dashboard with:
- Multiple pivot table views
- Region, product, and time analysis
- Bar, line, and pie charts
- Summary statistics sheet
- Top performers identification

**See**: `examples/pivot_table_dashboard.md`

### Example 3: Advanced Statistics

Creates a statistical analysis report with:
- Descriptive statistics for all variables
- Correlation matrix with color coding
- Distribution analysis with histograms
- Outlier detection using IQR method
- Linear regression analysis
- Scatter plots

**See**: `examples/advanced_statistics.md`

## Capabilities Matrix

| Feature | Support Level | Notes |
|---------|---------------|-------|
| Basic formulas (SUM, AVERAGE, etc.) | ✅ Full | All standard Excel functions |
| Pivot-like summaries | ✅ Full | Using pandas pivot_table |
| Charts (Bar, Line, Pie, Scatter) | ✅ Full | Via openpyxl.chart |
| Conditional formatting | ✅ Full | Color scales, cell rules |
| Named ranges | ✅ Full | For dynamic formulas |
| Multiple sheets | ✅ Full | Unlimited sheets per workbook |
| Number formatting | ✅ Full | Currency, percentages, custom |
| Statistical analysis | ✅ Full | Using pandas, numpy, scipy |
| Correlation matrices | ✅ Full | Pearson coefficients |
| Regression analysis | ✅ Full | Linear regression with stats |
| Native pivot tables | ⚠️ Limited | openpyxl has basic support |
| Macros/VBA | ❌ None | Use Python automation instead |
| Advanced chart types | ⚠️ Limited | Waterfall, sunburst not supported |

## Limitations & Workarounds

### Limitation 1: Native Pivot Tables

**Issue**: openpyxl has limited native pivot table creation support.

**Workaround**: Use pandas `pivot_table()` to create pivot-like summaries and write them to Excel as formatted tables. The result is functionally equivalent and often more flexible.

### Limitation 2: Macros/VBA

**Issue**: openpyxl cannot create Excel macros or VBA code.

**Workaround**: Use Python scripts to automate tasks instead of Excel macros. This provides better version control, debugging, and cross-platform compatibility.

### Limitation 3: Advanced Chart Types

**Issue**: Some chart types (waterfall, sunburst, treemap) are not supported by openpyxl.

**Workaround**: Use supported chart types (bar, line, pie, scatter) or export data for visualization in matplotlib/seaborn.

### Limitation 4: Real-time Data Connections

**Issue**: Cannot create live database connections or external data sources.

**Workaround**: Extract data in Python and write static snapshots to Excel. Use formulas for dynamic calculations within the workbook.

## Best Practices

### 1. Data Organization

- Place raw data on the first sheet
- Use separate sheets for different analyses
- Include a summary/dashboard sheet
- Use meaningful sheet names

### 2. Formatting

- Always format headers (bold, background color)
- Use number formats appropriate to data type
- Apply conditional formatting sparingly
- Maintain consistent styling across sheets

### 3. Formulas

- Use formulas for calculations when possible
- Name important cell ranges for clarity
- Document complex formulas with comments
- Avoid hardcoded values in formulas

### 4. Charts

- Place charts on dedicated sheets or beside data
- Use clear, descriptive titles
- Label axes appropriately
- Choose chart types that match data

### 5. Performance

- Limit data to reasonable sizes (< 100K rows)
- Use pivot summaries instead of raw data when possible
- Optimize formulas to avoid circular references
- Test with sample data before full datasets

## Technical Details

### Supported Excel Formats

- `.xlsx` - Modern Excel format (recommended)
- `.xlsm` - Macro-enabled workbooks (limited support)

### Cross-Platform Compatibility

All features work on:
- Windows (Excel 2010+)
- macOS (Excel 2016+)
- Linux (LibreOffice Calc 6.0+)
- Google Sheets (import/export)

### Python Version Requirements

- Python 3.8 or higher
- Tested on Python 3.10, 3.11, 3.12

## Troubleshooting

### Issue: Charts not displaying

**Solution**: Ensure chart references point to valid data ranges. Check that the sheet exists and data is populated.

### Issue: Formulas showing as text

**Solution**: Formulas must start with `=`. Ensure cell value is set as formula, not plain text.

### Issue: Conditional formatting not applying

**Solution**: Verify the range is correct. Some conditional formatting rules require specific data types.

### Issue: Pivot table not updating

**Solution**: Pivot-like summaries created with pandas are static. Rerun the Python script to refresh data.

### Issue: Large files taking too long

**Solution**: Reduce data size, use sampling, or split into multiple workbooks. Consider database storage for very large datasets.

## Contributing

To extend this skill:

1. Add new patterns to `skill.md`
2. Create example files in `examples/`
3. Update `requirements.txt` if adding dependencies
4. Document new features in this README
5. Test across different Excel versions

## Resources

- [openpyxl Documentation](https://openpyxl.readthedocs.io/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [Excel Formula Reference](https://support.microsoft.com/en-us/office/excel-functions-alphabetical-b3944572-255d-4efb-bb96-c6d90033e188)
- [Chart Types Guide](https://support.microsoft.com/en-us/office/available-chart-types-in-office-a6187218-807e-4103-9e0a-27cdb19afb90)

## License

This skill is part of the Claude Code framework and follows the same license terms.

## Support

For issues or questions:
1. Check the examples in `examples/`
2. Review the skill implementation in `skill.md`
3. Consult the troubleshooting section above
4. Refer to Claude Code documentation

---

**Version**: 1.0.0
**Last Updated**: 2025-11-18
**Author**: Claude Code Framework
**Status**: Production Ready
