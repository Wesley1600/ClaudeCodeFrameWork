# Code Execution Skill Package

## Overview

This repository contains a production-ready **Code Execution Skill** for Claude Code and AI agents. The skill provides secure code execution capabilities in a sandboxed environment, enabling agents to run scripts, analyze data, manipulate files, and create visualizations.

## What is this Skill?

The Code Execution Skill is a packaged capability that exposes 8 high-level functions for:

- **Python Code Execution**: Run Python scripts with full access to data science libraries
- **Bash Command Execution**: Execute shell commands securely
- **File Operations**: Read and write files with error handling
- **Data Analysis**: Built-in functions for common data analysis tasks
- **Visualization**: Create charts and plots from data
- **Package Management**: Install Python packages on-demand
- **File Discovery**: Search for files using glob patterns

## Directory Structure

```
skills/code_execution/
├── skill.json              # Skill manifest and metadata
├── main.py                 # Core implementation
├── __init__.py            # Package initialization
├── requirements.txt        # Python dependencies
├── setup.sh               # Installation script
├── README.md              # Full documentation
├── QUICKSTART.md          # Quick start guide
├── SKILL_USAGE.md         # Agent integration guide
├── examples.py            # Usage examples
└── test_skill.py          # Test suite
```

## Key Features

### 1. Secure Sandbox Execution

All code runs in a controlled environment with:
- Configurable timeouts (default: 2-5 minutes)
- Memory limits (default: 512MB)
- Network isolation (disabled by default)
- Error handling and recovery

### 2. Rich Function Library

Eight exposed functions with standardized interfaces:

```python
run_python(code, timeout, return_output)
run_bash(command, timeout)
write_file(file_path, content)
read_file(file_path, offset, limit)
analyze_data(file_path, analysis_type, custom_code)
create_visualization(data_source, plot_type, output_path, custom_code, options)
install_package(package)
list_files(pattern, path)
```

### 3. Data Science Ready

Pre-configured with popular libraries:
- **NumPy**: Numerical computing
- **Pandas**: Data analysis and manipulation
- **Matplotlib**: Data visualization
- **Seaborn**: Statistical visualizations

### 4. Comprehensive Error Handling

All functions return structured responses:

```json
{
  "success": true/false,
  "output/result/content/path": "...",
  "error": "error message or null"
}
```

### 5. Agent-Friendly Design

- **Standardized Interface**: Consistent function signatures
- **JSON Responses**: Easy to parse and handle
- **Multiple Integration Methods**: Direct import, subprocess, CLI
- **Well-Documented**: Extensive examples and documentation

## Quick Start

### Installation

```bash
cd skills/code_execution
./setup.sh
```

### Basic Usage

```python
from skills.code_execution import run_python, analyze_data, create_visualization

# Execute Python code
result = run_python("""
import numpy as np
data = np.array([1, 2, 3, 4, 5])
print(f"Mean: {data.mean()}")
""")

# Analyze data
analysis = analyze_data("/path/to/data.csv", "summary")

# Create visualization
chart = create_visualization(
    data_source="/path/to/data.csv",
    plot_type="scatter",
    output_path="/tmp/chart.png"
)
```

### Running Examples

```bash
python3 examples.py
```

### Running Tests

```bash
python3 test_skill.py
```

## Use Cases

### 1. Data Analysis Pipelines

Agents can analyze datasets, generate insights, and create reports:

```python
# Find all data files
files = list_files("**/*.csv", path="/data")

# Analyze each file
for file in files["files"]:
    analysis = analyze_data(file, "statistics")
    create_visualization(file, "heatmap", f"{file}.png")
```

### 2. Automated Report Generation

Generate comprehensive reports with data and visualizations:

```python
# Analyze data
summary = analyze_data("sales.csv", "summary")
stats = analyze_data("sales.csv", "statistics")

# Create charts
create_visualization("sales.csv", "line", "trend.png")
create_visualization("sales.csv", "bar", "comparison.png")

# Generate report
report = f"""
# Sales Report
{summary['result']}
{stats['result']}
![Trend](trend.png)
![Comparison](comparison.png)
"""
write_file("report.md", report)
```

### 3. Interactive Data Exploration

Enable conversational data analysis:

```python
def answer_data_question(data_path, question):
    if "summary" in question.lower():
        return analyze_data(data_path, "summary")
    elif "visualize" in question.lower():
        return create_visualization(data_path, "heatmap", "/tmp/viz.png")
    else:
        # Generate custom analysis code based on question
        custom_code = generate_code_from_question(question)
        return analyze_data(data_path, "custom", custom_code=custom_code)
```

### 4. Batch Data Processing

Process multiple files automatically:

```python
# Find all CSV files
files = list_files("*.csv", path="/data/raw")

# Process each file
for file in files["files"]:
    run_python(f"""
import pandas as pd
df = pd.read_csv('{file}')
df_clean = df.dropna()
df_clean.to_csv('/data/processed/{file.split('/')[-1]}')
""")
```

## Architecture

### Skill Manifest (skill.json)

Defines the skill metadata, functions, parameters, and sandbox configuration:

```json
{
  "name": "code_execution",
  "version": "1.0.0",
  "functions": [...],
  "dependencies": {...},
  "sandbox": {...}
}
```

### Core Implementation (main.py)

Implements all 8 functions with:
- Input validation
- Error handling
- Timeout management
- Resource control
- Standardized responses

### Package Structure

The skill is a proper Python package with:
- `__init__.py` for imports
- `requirements.txt` for dependencies
- `setup.sh` for installation
- Comprehensive tests

## Integration Patterns

### Pattern 1: Direct Import

```python
from skills.code_execution import run_python, analyze_data

result = run_python("print('Hello')")
```

### Pattern 2: CLI Interface

```bash
python3 skills/code_execution/main.py run_python "print('Hello')"
```

### Pattern 3: Agent Integration

```python
class MyAgent:
    def __init__(self):
        from skills.code_execution import (
            run_python, analyze_data, create_visualization
        )
        self.run_python = run_python
        self.analyze_data = analyze_data
        self.create_visualization = create_visualization

    def analyze(self, data_path):
        summary = self.analyze_data(data_path, "summary")
        self.create_visualization(data_path, "heatmap", "viz.png")
        return summary
```

## Documentation

The skill package includes comprehensive documentation:

1. **README.md** - Full API reference and detailed documentation
2. **QUICKSTART.md** - 5-minute quick start guide
3. **SKILL_USAGE.md** - Agent integration guide with patterns
4. **examples.py** - 7 comprehensive usage examples
5. **test_skill.py** - Complete test suite

## Testing

The skill includes a comprehensive test suite:

```bash
python3 test_skill.py
```

Tests cover:
- Python code execution
- Bash command execution
- File operations (read/write)
- Data analysis
- File discovery
- Error handling
- Timeout management

## Security

The skill is designed with security in mind:

1. **Sandboxed Execution**: All code runs in isolated environment
2. **Timeout Protection**: Prevents infinite loops
3. **Memory Limits**: Prevents memory exhaustion
4. **Network Isolation**: Disabled by default
5. **Input Validation**: Sanitizes inputs
6. **Error Isolation**: Exceptions are caught and returned safely

## Performance

Optimized for efficiency:

- **Fast Execution**: Direct Python subprocess execution
- **Minimal Overhead**: Thin wrapper around core tools
- **Batch Processing**: Support for bulk operations
- **Caching**: Temporary file cleanup and management

## Limitations

Current limitations:

1. **Execution Time**: Maximum 5 minutes per operation
2. **Memory**: Limited to 512MB by default
3. **Network**: Disabled in sandbox mode
4. **Concurrency**: One operation at a time per instance
5. **File Size**: Large files may cause memory issues

These can be adjusted in `skill.json`.

## Future Enhancements

Potential improvements:

- [ ] R language support
- [ ] SQL query execution
- [ ] GPU acceleration support
- [ ] Distributed execution
- [ ] Streaming for large files
- [ ] More visualization types
- [ ] Interactive plotting
- [ ] Notebook execution

## Contributing

To extend this skill:

1. Add new functions to `main.py`
2. Update `skill.json` with function metadata
3. Add tests to `test_skill.py`
4. Update documentation
5. Add examples to `examples.py`

## Version History

### Version 1.0.0 (2025-11-18)

Initial release with:
- ✅ Python code execution
- ✅ Bash command execution
- ✅ File read/write operations
- ✅ Data analysis (summary, statistics, correlations, custom)
- ✅ Visualization (line, scatter, bar, histogram, heatmap, custom)
- ✅ Package management
- ✅ File discovery
- ✅ Comprehensive documentation
- ✅ Test suite
- ✅ Usage examples

## License

MIT License

## Support

For issues and questions:
- **Documentation**: See `skills/code_execution/README.md`
- **Quick Start**: See `skills/code_execution/QUICKSTART.md`
- **Examples**: Run `python3 skills/code_execution/examples.py`
- **Tests**: Run `python3 skills/code_execution/test_skill.py`
- **Issues**: https://github.com/anthropics/claude-code/issues

## Summary

The Code Execution Skill provides a **production-ready, secure, and comprehensive** solution for enabling AI agents to:

✅ Execute Python and Bash code safely
✅ Analyze data with pandas and numpy
✅ Create visualizations with matplotlib
✅ Manipulate files and directories
✅ Install packages dynamically
✅ Discover and process files

All with **standardized interfaces**, **comprehensive error handling**, and **extensive documentation**.

Perfect for data analysis, report generation, batch processing, and interactive exploration use cases.
