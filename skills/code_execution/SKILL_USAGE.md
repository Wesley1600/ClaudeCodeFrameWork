# Code Execution Skill - Agent Integration Guide

This document explains how other agents can call and use the Code Execution Skill.

## Overview

The Code Execution Skill exposes 8 functions that agents can call to execute code, manipulate files, analyze data, and create visualizations in a secure sandbox environment.

## Integration Methods

### Method 1: Direct Python Import

```python
from skills.code_execution import (
    run_python,
    run_bash,
    write_file,
    read_file,
    analyze_data,
    create_visualization,
    install_package,
    list_files
)

# Use the functions directly
result = run_python("print('Hello from agent!')")
```

### Method 2: JSON-RPC Style Calls

```python
import json
import subprocess

def call_skill_function(function_name, **kwargs):
    """Call a skill function via subprocess"""
    import sys
    sys.path.insert(0, '/path/to/skills/code_execution')

    from main import globals
    func = globals()[function_name]
    return func(**kwargs)

# Example
result = call_skill_function('run_python', code='print("Hello")')
```

### Method 3: CLI Interface

```bash
python3 skills/code_execution/main.py run_python "print('Hello')"
```

## Function Reference for Agents

### 1. run_python(code, timeout=120000, return_output=True)

Execute Python code in a sandbox.

**Use Cases:**
- Data processing and calculations
- Scientific computing
- Machine learning inference
- Data transformation

**Example:**
```python
result = run_python("""
import numpy as np
data = np.array([1, 2, 3, 4, 5])
print(f"Mean: {data.mean()}")
print(f"Std: {data.std()}")
""", timeout=60000)

if result["success"]:
    print(result["output"])
else:
    print(f"Error: {result['error']}")
```

**Response:**
```json
{
  "success": true,
  "output": "Mean: 3.0\nStd: 1.4142135623730951\n",
  "error": null,
  "return_code": 0
}
```

### 2. run_bash(command, timeout=120000)

Execute shell commands.

**Use Cases:**
- System operations
- File system manipulation
- Process management
- Script execution

**Example:**
```python
result = run_bash("ls -la /tmp | grep csv")

if result["success"]:
    files = result["output"].strip().split('\n')
    print(f"Found {len(files)} CSV files")
```

**Response:**
```json
{
  "success": true,
  "output": "-rw-r--r-- 1 user user 1234 Nov 18 10:00 data.csv\n",
  "error": null,
  "return_code": 0
}
```

### 3. write_file(file_path, content)

Write content to a file.

**Use Cases:**
- Saving analysis results
- Creating configuration files
- Exporting data
- Generating reports

**Example:**
```python
report = """
# Analysis Report

Results: ...
"""

result = write_file("/tmp/report.md", report)

if result["success"]:
    print(f"Report saved to {result['path']}")
```

**Response:**
```json
{
  "success": true,
  "path": "/tmp/report.md",
  "error": null
}
```

### 4. read_file(file_path, offset=None, limit=None)

Read content from a file.

**Use Cases:**
- Loading configuration
- Reading data files
- Processing logs
- Extracting information

**Example:**
```python
result = read_file("/tmp/data.csv", offset=0, limit=100)

if result["success"]:
    lines = result["content"].split('\n')
    print(f"Read {len(lines)} lines")
```

**Response:**
```json
{
  "success": true,
  "content": "col1,col2,col3\n1,2,3\n4,5,6\n",
  "error": null
}
```

### 5. analyze_data(file_path, analysis_type, custom_code=None)

Analyze data files with pandas/numpy.

**Analysis Types:**
- `'summary'`: Basic information and preview
- `'statistics'`: Descriptive statistics
- `'correlations'`: Correlation matrix
- `'custom'`: Custom analysis code

**Use Cases:**
- Quick data insights
- Statistical analysis
- Data quality checks
- Correlation analysis

**Example:**
```python
# Quick summary
result = analyze_data("/tmp/sales.csv", "summary")

# Custom analysis
result = analyze_data(
    "/tmp/sales.csv",
    "custom",
    custom_code="""
import pandas as pd
df = pd.read_csv('/tmp/sales.csv')
print(df.groupby('category')['revenue'].sum())
"""
)

if result["success"]:
    print(result["result"])
```

**Response:**
```json
{
  "success": true,
  "result": "Data Shape: (100, 5)\nColumn Types:\n...",
  "error": null
}
```

### 6. create_visualization(data_source, plot_type, output_path, custom_code=None, options=None)

Create plots and charts from data.

**Plot Types:**
- `'line'`: Line plot
- `'scatter'`: Scatter plot
- `'bar'`: Bar chart
- `'histogram'`: Histogram
- `'heatmap'`: Correlation heatmap
- `'custom'`: Custom matplotlib code

**Use Cases:**
- Data visualization
- Report generation
- Trend analysis
- Pattern recognition

**Example:**
```python
result = create_visualization(
    data_source="/tmp/sales.csv",
    plot_type="line",
    output_path="/tmp/sales_trend.png",
    options={
        "title": "Sales Trend",
        "xlabel": "Date",
        "ylabel": "Revenue ($)"
    }
)

if result["success"]:
    print(f"Chart saved to {result['path']}")
```

**Response:**
```json
{
  "success": true,
  "path": "/tmp/sales_trend.png",
  "error": null
}
```

### 7. install_package(package)

Install Python packages with pip.

**Use Cases:**
- Dynamic dependency installation
- Adding specialized libraries
- Environment setup

**Example:**
```python
result = install_package("scikit-learn==1.2.0")

if result["success"]:
    print("Package installed successfully")
    # Now you can use it in run_python calls
```

**Response:**
```json
{
  "success": true,
  "output": "Successfully installed scikit-learn-1.2.0",
  "error": null
}
```

### 8. list_files(pattern, path=None)

Find files matching a pattern.

**Use Cases:**
- File discovery
- Batch processing
- Data inventory
- Cleanup operations

**Example:**
```python
result = list_files("**/*.csv", path="/tmp/data")

if result["success"]:
    for file in result["files"]:
        print(f"Processing {file}")
        # Process each file...
```

**Response:**
```json
{
  "success": true,
  "files": ["/tmp/data/file1.csv", "/tmp/data/file2.csv"],
  "error": null
}
```

## Common Patterns for Agents

### Pattern 1: Data Processing Pipeline

```python
# 1. Discover data files
files_result = list_files("*.csv", path="/data/input")

if files_result["success"]:
    for data_file in files_result["files"]:
        # 2. Analyze each file
        analysis = analyze_data(data_file, "statistics")

        # 3. Process the data
        process_code = f"""
import pandas as pd
df = pd.read_csv('{data_file}')
# ... processing logic ...
df.to_csv('/data/output/processed_{data_file.split('/')[-1]}')
"""
        run_python(process_code)

        # 4. Create visualization
        create_visualization(
            data_file,
            "heatmap",
            f"/data/output/{data_file.split('/')[-1]}.png"
        )
```

### Pattern 2: Report Generation

```python
# 1. Analyze data
analysis = analyze_data("/data/sales.csv", "summary")

# 2. Generate insights
insights_code = """
import pandas as pd
df = pd.read_csv('/data/sales.csv')

# Calculate metrics
total_revenue = df['revenue'].sum()
avg_sale = df['revenue'].mean()
best_product = df.groupby('product')['revenue'].sum().idxmax()

print(f"Total Revenue: ${total_revenue:.2f}")
print(f"Average Sale: ${avg_sale:.2f}")
print(f"Best Product: {best_product}")
"""
insights = run_python(insights_code)

# 3. Create visualizations
create_visualization(
    "/data/sales.csv",
    "bar",
    "/reports/sales_chart.png"
)

# 4. Generate report
report_content = f"""
# Sales Report

## Summary
{analysis['result']}

## Key Insights
{insights['output']}

## Visualizations
![Sales Chart](sales_chart.png)
"""

write_file("/reports/sales_report.md", report_content)
```

### Pattern 3: Interactive Analysis

```python
def interactive_analysis(data_path, user_query):
    """Agent responds to user questions about data"""

    if "summary" in user_query.lower():
        return analyze_data(data_path, "summary")

    elif "correlation" in user_query.lower():
        return analyze_data(data_path, "correlations")

    elif "visualize" in user_query.lower() or "plot" in user_query.lower():
        result = create_visualization(
            data_path,
            "heatmap",
            "/tmp/analysis.png"
        )
        return {
            "response": f"Visualization created at {result['path']}",
            "path": result['path']
        }

    else:
        # Custom query - use LLM to generate analysis code
        custom_code = generate_analysis_code(user_query, data_path)
        return analyze_data(data_path, "custom", custom_code=custom_code)
```

### Pattern 4: Error Recovery

```python
def robust_execution(code, max_retries=3):
    """Execute code with retry logic"""

    for attempt in range(max_retries):
        result = run_python(code, timeout=60000)

        if result["success"]:
            return result

        # If timeout, increase timeout
        if "timed out" in str(result.get("error", "")).lower():
            code_with_optimization = optimize_code(code)
            code = code_with_optimization

        # If missing package, install it
        elif "No module named" in str(result.get("error", "")):
            import re
            match = re.search(r"No module named '(\w+)'", result["error"])
            if match:
                package = match.group(1)
                install_package(package)

        else:
            # Unrecoverable error
            break

    return result
```

## Security Considerations for Agents

1. **Input Validation**: Always validate user input before passing to skill functions
2. **Path Restrictions**: Use absolute paths and validate they're in allowed directories
3. **Code Injection**: Sanitize any user-provided code
4. **Resource Limits**: Use timeouts to prevent infinite loops
5. **Error Handling**: Always check `success` field before using results

## Performance Tips

1. **Batch Operations**: Process multiple files in a single Python execution
2. **Timeout Management**: Adjust timeouts based on expected execution time
3. **Memory Efficiency**: Use streaming for large files
4. **Parallel Processing**: Use bash commands for parallel file operations
5. **Caching**: Save intermediate results to files

## Example: Complete Agent Workflow

```python
class DataAnalysisAgent:
    """Example agent using Code Execution Skill"""

    def __init__(self):
        from skills.code_execution import (
            run_python, analyze_data, create_visualization, write_file
        )
        self.run_python = run_python
        self.analyze_data = analyze_data
        self.create_visualization = create_visualization
        self.write_file = write_file

    def analyze_and_report(self, data_path, output_dir):
        """Complete analysis workflow"""

        # Step 1: Analyze data
        summary = self.analyze_data(data_path, "summary")
        stats = self.analyze_data(data_path, "statistics")

        if not summary["success"] or not stats["success"]:
            return {"error": "Analysis failed"}

        # Step 2: Create visualizations
        viz1 = self.create_visualization(
            data_path, "histogram",
            f"{output_dir}/distribution.png"
        )

        viz2 = self.create_visualization(
            data_path, "heatmap",
            f"{output_dir}/correlations.png"
        )

        # Step 3: Generate report
        report = f"""
# Data Analysis Report

## Summary
{summary['result']}

## Statistics
{stats['result']}

## Visualizations
![Distribution](distribution.png)
![Correlations](correlations.png)
"""

        self.write_file(f"{output_dir}/report.md", report)

        return {
            "success": True,
            "report_path": f"{output_dir}/report.md",
            "visualizations": [viz1["path"], viz2["path"]]
        }

# Usage
agent = DataAnalysisAgent()
result = agent.analyze_and_report("/data/sales.csv", "/reports")
```

## Support

For issues or questions about integrating this skill:
- Check the main README.md for documentation
- Run examples.py for usage demonstrations
- Run test_skill.py to verify functionality
