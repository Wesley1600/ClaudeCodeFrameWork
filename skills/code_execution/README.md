# Code Execution Skill

A comprehensive Claude Code skill for executing scripts, analyzing data, and creating files in a secure sandbox environment.

## Overview

The Code Execution Skill provides a safe and controlled environment for running Python and Bash code, manipulating files, performing data analysis, and creating visualizations. All operations run in a sandboxed environment with configurable timeouts and resource limits.

## Features

- **Python Code Execution**: Run Python scripts with full access to popular libraries (numpy, pandas, matplotlib, seaborn)
- **Bash Command Execution**: Execute shell commands in a secure sandbox
- **File Operations**: Read and write files with proper error handling
- **Data Analysis**: Built-in functions for common data analysis tasks
- **Visualization**: Create charts and plots from data
- **Package Management**: Install Python packages on-demand
- **File Discovery**: Search for files using glob patterns

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Required Packages

```bash
pip install numpy pandas matplotlib seaborn
```

Or install from the provided requirements file:

```bash
pip install -r requirements.txt
```

## API Reference

### run_python

Execute Python code in a secure sandbox.

**Parameters:**
- `code` (str, required): Python code to execute
- `timeout` (int, optional): Maximum execution time in milliseconds (default: 120000)
- `return_output` (bool, optional): Whether to return stdout/stderr (default: true)

**Returns:**
```json
{
  "success": true,
  "output": "Hello, World!\n",
  "error": null,
  "return_code": 0
}
```

**Example:**
```python
result = run_python("""
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print(f"Mean: {arr.mean()}")
print(f"Std: {arr.std()}")
""")
```

### run_bash

Execute bash commands in a secure sandbox environment.

**Parameters:**
- `command` (str, required): Bash command to execute
- `timeout` (int, optional): Maximum execution time in milliseconds (default: 120000)

**Returns:**
```json
{
  "success": true,
  "output": "file1.txt\nfile2.txt\n",
  "error": null,
  "return_code": 0
}
```

**Example:**
```python
result = run_bash("ls -la /tmp")
```

### write_file

Write content to a file at the specified path.

**Parameters:**
- `file_path` (str, required): Absolute path where the file should be written
- `content` (str, required): Content to write to the file

**Returns:**
```json
{
  "success": true,
  "path": "/path/to/file.txt",
  "error": null
}
```

**Example:**
```python
result = write_file(
    "/tmp/output.txt",
    "This is the file content"
)
```

### read_file

Read content from a file at the specified path.

**Parameters:**
- `file_path` (str, required): Absolute path to the file to read
- `offset` (int, optional): Line number to start reading from
- `limit` (int, optional): Number of lines to read

**Returns:**
```json
{
  "success": true,
  "content": "File content here...",
  "error": null
}
```

**Example:**
```python
result = read_file("/tmp/data.txt", offset=10, limit=20)
```

### analyze_data

Analyze data from a file (CSV, JSON, etc.) using pandas and numpy.

**Parameters:**
- `file_path` (str, required): Path to the data file
- `analysis_type` (str, required): Type of analysis - one of:
  - `'summary'`: Basic info, shape, and first rows
  - `'statistics'`: Descriptive statistics
  - `'correlations'`: Correlation matrix for numeric columns
  - `'custom'`: Run custom analysis code
- `custom_code` (str, optional): Custom Python code (required when analysis_type is 'custom')

**Returns:**
```json
{
  "success": true,
  "result": "Data Shape: (100, 5)\n...",
  "error": null
}
```

**Example:**
```python
# Basic summary
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
```

### create_visualization

Create visualizations (plots, charts) from data using matplotlib/seaborn.

**Parameters:**
- `data_source` (str, required): Path to data file
- `plot_type` (str, required): Type of plot - one of:
  - `'line'`: Line plot
  - `'scatter'`: Scatter plot
  - `'bar'`: Bar chart
  - `'histogram'`: Histogram
  - `'heatmap'`: Correlation heatmap
  - `'custom'`: Custom matplotlib code
- `output_path` (str, required): Path where the visualization should be saved (PNG format)
- `custom_code` (str, optional): Custom matplotlib code (required when plot_type is 'custom')
- `options` (dict, optional): Additional options:
  - `title`: Plot title
  - `xlabel`: X-axis label
  - `ylabel`: Y-axis label

**Returns:**
```json
{
  "success": true,
  "path": "/tmp/plot.png",
  "error": null
}
```

**Example:**
```python
# Basic scatter plot
result = create_visualization(
    data_source="/tmp/data.csv",
    plot_type="scatter",
    output_path="/tmp/scatter.png",
    options={
        "title": "Sales vs Revenue",
        "xlabel": "Sales",
        "ylabel": "Revenue"
    }
)

# Custom visualization
result = create_visualization(
    data_source="/tmp/data.csv",
    plot_type="custom",
    output_path="/tmp/custom.png",
    custom_code="""
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('/tmp/data.csv')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
df['sales'].plot(ax=ax1, title='Sales Over Time')
df['revenue'].plot(ax=ax2, title='Revenue Over Time')
plt.tight_layout()
"""
)
```

### install_package

Install a Python package using pip in the sandbox environment.

**Parameters:**
- `package` (str, required): Package name (optionally with version, e.g., 'pandas==1.5.0')

**Returns:**
```json
{
  "success": true,
  "output": "Successfully installed pandas-1.5.0",
  "error": null
}
```

**Example:**
```python
result = install_package("scikit-learn==1.2.0")
```

### list_files

List files in a directory matching a pattern.

**Parameters:**
- `pattern` (str, required): Glob pattern to match files (e.g., '*.py', 'data/**/*.csv')
- `path` (str, optional): Directory to search in (default: current directory)

**Returns:**
```json
{
  "success": true,
  "files": ["/path/to/file1.py", "/path/to/file2.py"],
  "error": null
}
```

**Example:**
```python
result = list_files("**/*.csv", path="/tmp/data")
```

## Sandbox Configuration

The skill runs in a secure sandbox with the following default settings:

- **Network Access**: Disabled by default
- **Max Execution Time**: 300 seconds (5 minutes)
- **Max Memory**: 512MB
- **Allowed Operations**: File I/O, calculations, visualizations

These settings can be modified in `skill.json`.

## Security Considerations

1. **Code Injection**: Always validate and sanitize input code
2. **File Access**: Restrict file operations to designated directories
3. **Resource Limits**: Enforce timeout and memory limits
4. **Network Isolation**: Keep network access disabled unless required
5. **Package Installation**: Only install trusted packages

## Error Handling

All functions return a standardized response format:

```python
{
    "success": bool,      # Whether the operation succeeded
    "output/result/content/path": ...,  # The result (varies by function)
    "error": str or None  # Error message if operation failed
}
```

## Use Cases

### 1. Data Analysis Pipeline

```python
# Install required packages
install_package("scikit-learn")

# Analyze the data
result = analyze_data("/tmp/sales.csv", "statistics")
print(result["result"])

# Create visualization
create_visualization(
    "/tmp/sales.csv",
    "heatmap",
    "/tmp/correlation.png",
    options={"title": "Sales Correlations"}
)
```

### 2. Automated Report Generation

```python
# Run analysis
analysis_code = """
import pandas as pd
df = pd.read_csv('/tmp/data.csv')

report = f'''
# Monthly Report

Total Records: {len(df)}
Average Revenue: ${df['revenue'].mean():.2f}
Top Product: {df.groupby('product')['revenue'].sum().idxmax()}
'''

print(report)
"""

result = run_python(analysis_code)

# Save report
write_file("/tmp/report.md", result["output"])
```

### 3. Data Transformation

```python
transform_code = """
import pandas as pd

# Load data
df = pd.read_csv('/tmp/raw_data.csv')

# Transform
df['date'] = pd.to_datetime(df['date'])
df['revenue'] = df['price'] * df['quantity']
df = df[df['revenue'] > 0]

# Save
df.to_csv('/tmp/processed_data.csv', index=False)
print(f"Processed {len(df)} records")
"""

result = run_python(transform_code)
```

## Testing

Run the test suite:

```bash
python tests/test_code_execution.py
```

Run individual function tests:

```bash
# Test Python execution
python main.py run_python "print('Hello, World!')"

# Test Bash execution
python main.py run_bash "echo 'Test'"

# Test file writing
python main.py write_file "/tmp/test.txt" "Test content"
```

## Limitations

1. **Execution Time**: Maximum 5 minutes per operation
2. **Memory**: Limited to 512MB by default
3. **Network**: Disabled in sandbox mode
4. **File Size**: Large files may cause memory issues
5. **Concurrent Execution**: One operation at a time per instance

## Troubleshooting

### Timeout Errors

Increase the timeout parameter:

```python
result = run_python(long_running_code, timeout=300000)  # 5 minutes
```

### Memory Errors

Process data in chunks or increase memory limit in `skill.json`.

### Package Not Found

Install the package first:

```python
install_package("package_name")
```

### Permission Denied

Ensure file paths are within allowed directories and check sandbox settings.

## Contributing

Contributions are welcome! Please:

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/anthropics/claude-code/issues)
- Documentation: [Claude Code Docs](https://docs.claude.com/en/docs/claude-code)

## Version History

### 1.0.0 (2025-11-18)
- Initial release
- Python and Bash execution
- File operations
- Data analysis functions
- Visualization support
- Package management
- File discovery
