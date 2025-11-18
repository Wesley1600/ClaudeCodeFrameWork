# Code Execution Skill - Quick Start Guide

Get started with the Code Execution Skill in 5 minutes!

## Installation

### Step 1: Install Dependencies

```bash
cd skills/code_execution
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
pip3 install -r requirements.txt
```

### Step 2: Verify Installation

```bash
python3 test_skill.py
```

You should see: `TEST RESULTS: 7 passed, 0 failed`

## Basic Usage

### Example 1: Run Python Code

```python
from skills.code_execution import run_python

result = run_python("""
import numpy as np
data = np.array([1, 2, 3, 4, 5])
print(f"Mean: {data.mean()}")
""")

print(result["output"])
# Output: Mean: 3.0
```

### Example 2: Analyze Data

```python
from skills.code_execution import analyze_data

result = analyze_data("/path/to/data.csv", "summary")

if result["success"]:
    print(result["result"])
```

### Example 3: Create Visualization

```python
from skills.code_execution import create_visualization

result = create_visualization(
    data_source="/path/to/data.csv",
    plot_type="scatter",
    output_path="/tmp/chart.png",
    options={"title": "My Data", "xlabel": "X", "ylabel": "Y"}
)

print(f"Chart saved to: {result['path']}")
```

### Example 4: File Operations

```python
from skills.code_execution import write_file, read_file

# Write a file
write_file("/tmp/myfile.txt", "Hello, World!")

# Read it back
result = read_file("/tmp/myfile.txt")
print(result["content"])
# Output: Hello, World!
```

## Running Examples

See all features in action:

```bash
python3 examples.py
```

This runs 7 comprehensive examples demonstrating:
1. Simple Python execution
2. Bash commands
3. File operations
4. Data analysis
5. Visualizations
6. File discovery
7. Complete workflow

## Common Use Cases

### Use Case 1: Quick Data Summary

```python
from skills.code_execution import analyze_data

analyze_data("sales.csv", "statistics")
```

### Use Case 2: Create Report with Chart

```python
from skills.code_execution import analyze_data, create_visualization, write_file

# Analyze
analysis = analyze_data("data.csv", "summary")

# Visualize
create_visualization("data.csv", "bar", "chart.png")

# Write report
write_file("report.md", f"# Report\n\n{analysis['result']}")
```

### Use Case 3: Batch File Processing

```python
from skills.code_execution import list_files, run_python

# Find all CSV files
files = list_files("**/*.csv", path="/data")

# Process each file
for file in files["files"]:
    run_python(f"""
import pandas as pd
df = pd.read_csv('{file}')
print(f"Processed {len(df)} rows from {file}")
""")
```

## Available Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `run_python(code, ...)` | Execute Python code | output, success |
| `run_bash(command, ...)` | Execute shell command | output, success |
| `write_file(path, content)` | Write file | path, success |
| `read_file(path, ...)` | Read file | content, success |
| `analyze_data(file, type, ...)` | Analyze data | result, success |
| `create_visualization(...)` | Create charts | path, success |
| `install_package(name)` | Install Python package | output, success |
| `list_files(pattern, ...)` | Find files | files, success |

## Response Format

All functions return a dictionary with this structure:

```python
{
    "success": True/False,      # Whether operation succeeded
    "output/result/content/path": ...,  # The result (varies by function)
    "error": "error message" or None    # Error if failed
}
```

Always check `success` before using results:

```python
result = run_python("print('Hello')")

if result["success"]:
    print(result["output"])
else:
    print(f"Error: {result['error']}")
```

## Next Steps

1. **Read full documentation**: See `README.md` for complete API reference
2. **Agent integration**: See `SKILL_USAGE.md` for using this skill in agents
3. **Run examples**: Execute `python3 examples.py` for comprehensive demos
4. **Run tests**: Execute `python3 test_skill.py` to verify functionality

## Troubleshooting

### Problem: "No module named 'pandas'"

**Solution**: Install dependencies

```bash
./setup.sh
# or
pip3 install -r requirements.txt
```

### Problem: "Command timed out"

**Solution**: Increase timeout

```python
run_python(code, timeout=300000)  # 5 minutes
```

### Problem: "Permission denied"

**Solution**: Check file paths and permissions

```python
# Use /tmp for temporary files
write_file("/tmp/myfile.txt", content)
```

## Support

- **Documentation**: README.md, SKILL_USAGE.md
- **Examples**: examples.py
- **Tests**: test_skill.py
- **Issues**: https://github.com/anthropics/claude-code/issues

## Quick Reference Card

```python
# Import all functions
from skills.code_execution import *

# Python execution
run_python("print('Hello')")

# Bash commands
run_bash("ls -la")

# File I/O
write_file("/tmp/file.txt", "content")
read_file("/tmp/file.txt")

# Data analysis
analyze_data("data.csv", "summary")
analyze_data("data.csv", "statistics")
analyze_data("data.csv", "correlations")

# Visualization
create_visualization("data.csv", "line", "plot.png")
create_visualization("data.csv", "scatter", "plot.png")
create_visualization("data.csv", "heatmap", "plot.png")

# Package management
install_package("scikit-learn")

# File discovery
list_files("*.csv", path="/data")
```

Happy coding! 🚀
