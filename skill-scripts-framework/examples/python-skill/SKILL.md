# CSV Data Analysis Skill

Analyzes CSV files and generates statistical reports without loading analysis code into context.

## Description

This skill provides data analysis capabilities for CSV files using Python scripts. It calculates statistics, detects patterns, and generates insights.

## When to Use

Use this skill when:
- User wants to analyze a CSV file
- User requests statistics or insights from tabular data
- User needs data validation or quality checks

## Usage

### Basic Analysis

1. Ask the user for the CSV file path
2. Execute: `python .claude/skills/csv-analysis/scripts/python/analyze_csv.py <file_path>`
3. Parse the JSON output and present insights to the user

### With Visualization

1. Run analysis (as above)
2. Execute: `python .claude/skills/csv-analysis/scripts/python/plot_data.py <file_path> --output <output_path>`
3. Show the generated plot to the user

### Data Validation

Execute: `python .claude/skills/csv-analysis/scripts/python/validate.py <file_path>`

## Script Reference

### analyze_csv.py

**Arguments:**
- `file_path`: Path to CSV file (required)
- `--columns`: Specific columns to analyze (optional)
- `--format`: Output format: json|text (default: json)

**Output:** JSON with statistics and insights

**Exit Codes:**
- 0: Success
- 1: File not found
- 2: Invalid CSV format
- 3: Processing error

### plot_data.py

**Arguments:**
- `file_path`: Path to CSV file (required)
- `--output`: Output image path (required)
- `--type`: Plot type: histogram|scatter|correlation (default: histogram)

**Output:** Saves plot to specified path

### validate.py

**Arguments:**
- `file_path`: Path to CSV file (required)

**Output:** JSON with validation results

## Error Handling

All scripts output JSON errors to stderr:
```json
{
  "status": "error",
  "code": 2,
  "message": "Invalid CSV format: missing headers"
}
```

## Dependencies

Scripts require:
- Python 3.8+
- pandas
- numpy
- matplotlib (for plotting)

Note: Dependencies should be available in the environment. If missing, inform the user.

## Examples

**Example 1: Quick Analysis**
```bash
python scripts/python/analyze_csv.py data/sales.csv
```

**Example 2: Column-Specific Analysis**
```bash
python scripts/python/analyze_csv.py data/sales.csv --columns revenue,profit
```

**Example 3: Generate Histogram**
```bash
python scripts/python/plot_data.py data/sales.csv --output sales_hist.png --type histogram
```

## Security

This skill uses read-only operations and is safe for untrusted CSV files. Scripts include input validation and size limits.
