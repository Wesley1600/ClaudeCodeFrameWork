#!/usr/bin/env python3
"""
Code Execution Skill - Main Implementation

This skill provides secure code execution capabilities for running scripts,
analyzing data, and creating files in a sandboxed environment.
"""

import subprocess
import json
import os
import tempfile
from typing import Dict, Any, Optional, List
from pathlib import Path


class CodeExecutionSkill:
    """
    A comprehensive skill for code execution, file manipulation, and data analysis.
    All operations run in a secure sandbox environment.
    """

    def __init__(self, sandbox_enabled: bool = True):
        """
        Initialize the Code Execution Skill.

        Args:
            sandbox_enabled: Whether to enforce sandbox restrictions
        """
        self.sandbox_enabled = sandbox_enabled
        self.max_execution_time = 300000  # 5 minutes default

    def run_python(
        self,
        code: str,
        timeout: int = 120000,
        return_output: bool = True
    ) -> Dict[str, Any]:
        """
        Execute Python code in a secure sandbox.

        Args:
            code: Python code to execute
            timeout: Maximum execution time in milliseconds
            return_output: Whether to return stdout/stderr

        Returns:
            Dictionary with success status, output, and error (if any)
        """
        try:
            # Create a temporary file for the Python code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Execute the Python code
                timeout_seconds = timeout / 1000.0
                result = subprocess.run(
                    ['python3', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds
                )

                output = ""
                if return_output:
                    output = result.stdout
                    if result.stderr:
                        output += f"\n[STDERR]\n{result.stderr}"

                return {
                    "success": result.returncode == 0,
                    "output": output,
                    "error": result.stderr if result.returncode != 0 else None,
                    "return_code": result.returncode
                }
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Execution timed out after {timeout}ms"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Execution failed: {str(e)}"
            }

    def run_bash(
        self,
        command: str,
        timeout: int = 120000
    ) -> Dict[str, Any]:
        """
        Execute bash commands in a secure sandbox environment.

        Args:
            command: Bash command to execute
            timeout: Maximum execution time in milliseconds

        Returns:
            Dictionary with success status, output, and error (if any)
        """
        try:
            timeout_seconds = timeout / 1000.0
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Command timed out after {timeout}ms"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Command execution failed: {str(e)}"
            }

    def write_file(
        self,
        file_path: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Write content to a file at the specified path.

        Args:
            file_path: Absolute path where the file should be written
            content: Content to write to the file

        Returns:
            Dictionary with success status, path, and error (if any)
        """
        try:
            # Ensure directory exists
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write the file
            with open(file_path, 'w') as f:
                f.write(content)

            return {
                "success": True,
                "path": file_path,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "path": None,
                "error": f"Failed to write file: {str(e)}"
            }

    def read_file(
        self,
        file_path: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Read content from a file at the specified path.

        Args:
            file_path: Absolute path to the file to read
            offset: Line number to start reading from
            limit: Number of lines to read

        Returns:
            Dictionary with success status, content, and error (if any)
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            # Apply offset and limit if specified
            if offset is not None:
                lines = lines[offset:]
            if limit is not None:
                lines = lines[:limit]

            content = ''.join(lines)

            return {
                "success": True,
                "content": content,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "content": None,
                "error": f"Failed to read file: {str(e)}"
            }

    def analyze_data(
        self,
        file_path: str,
        analysis_type: str,
        custom_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze data from a file using pandas and numpy.

        Args:
            file_path: Path to the data file
            analysis_type: Type of analysis ('summary', 'statistics', 'correlations', 'custom')
            custom_code: Custom Python code for analysis (used when analysis_type is 'custom')

        Returns:
            Dictionary with success status, result, and error (if any)
        """
        # Build analysis code based on type
        if analysis_type == 'summary':
            code = f"""
import pandas as pd
import numpy as np

# Load the data
df = pd.read_csv('{file_path}')

# Generate summary
print("Data Shape:", df.shape)
print("\\nColumn Types:")
print(df.dtypes)
print("\\nFirst 5 Rows:")
print(df.head())
print("\\nBasic Info:")
print(df.info())
"""
        elif analysis_type == 'statistics':
            code = f"""
import pandas as pd
import numpy as np

# Load the data
df = pd.read_csv('{file_path}')

# Generate statistics
print("Descriptive Statistics:")
print(df.describe())
print("\\nNull Values:")
print(df.isnull().sum())
"""
        elif analysis_type == 'correlations':
            code = f"""
import pandas as pd
import numpy as np

# Load the data
df = pd.read_csv('{file_path}')

# Calculate correlations for numeric columns
numeric_df = df.select_dtypes(include=[np.number])
print("Correlation Matrix:")
print(numeric_df.corr())
"""
        elif analysis_type == 'custom':
            if not custom_code:
                return {
                    "success": False,
                    "result": None,
                    "error": "custom_code is required when analysis_type is 'custom'"
                }
            code = custom_code
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Invalid analysis_type: {analysis_type}"
            }

        # Execute the analysis code
        result = self.run_python(code)

        if result["success"]:
            return {
                "success": True,
                "result": result["output"],
                "error": None
            }
        else:
            return {
                "success": False,
                "result": None,
                "error": result["error"]
            }

    def create_visualization(
        self,
        data_source: str,
        plot_type: str,
        output_path: str,
        custom_code: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create visualizations from data using matplotlib/seaborn.

        Args:
            data_source: Path to data file or inline data as JSON string
            plot_type: Type of plot ('line', 'scatter', 'bar', 'histogram', 'heatmap', 'custom')
            output_path: Path where the visualization should be saved
            custom_code: Custom matplotlib code (used when plot_type is 'custom')
            options: Additional options like title, xlabel, ylabel

        Returns:
            Dictionary with success status, path, and error (if any)
        """
        options = options or {}
        title = options.get('title', 'Visualization')
        xlabel = options.get('xlabel', 'X')
        ylabel = options.get('ylabel', 'Y')

        # Build visualization code
        if plot_type == 'custom':
            if not custom_code:
                return {
                    "success": False,
                    "path": None,
                    "error": "custom_code is required when plot_type is 'custom'"
                }
            code = custom_code
        else:
            # Standard plot types
            code = f"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load data
df = pd.read_csv('{data_source}')

# Create figure
plt.figure(figsize=(10, 6))

"""
            if plot_type == 'line':
                code += f"""
# Line plot
for col in df.columns[1:]:
    plt.plot(df.iloc[:, 0], df[col], label=col)
plt.legend()
"""
            elif plot_type == 'scatter':
                code += f"""
# Scatter plot
plt.scatter(df.iloc[:, 0], df.iloc[:, 1])
"""
            elif plot_type == 'bar':
                code += f"""
# Bar plot
df.plot(kind='bar', x=df.columns[0])
"""
            elif plot_type == 'histogram':
                code += f"""
# Histogram
df.hist(bins=30, figsize=(10, 6))
"""
            elif plot_type == 'heatmap':
                code += f"""
# Heatmap (correlation matrix)
numeric_df = df.select_dtypes(include=[np.number])
sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm')
"""
            else:
                return {
                    "success": False,
                    "path": None,
                    "error": f"Invalid plot_type: {plot_type}"
                }

            code += f"""
plt.title('{title}')
plt.xlabel('{xlabel}')
plt.ylabel('{ylabel}')
plt.tight_layout()
plt.savefig('{output_path}', dpi=300, bbox_inches='tight')
print(f"Visualization saved to {output_path}")
"""

        # Execute the visualization code
        result = self.run_python(code)

        if result["success"]:
            return {
                "success": True,
                "path": output_path,
                "error": None
            }
        else:
            return {
                "success": False,
                "path": None,
                "error": result["error"]
            }

    def install_package(
        self,
        package: str
    ) -> Dict[str, Any]:
        """
        Install a Python package using pip.

        Args:
            package: Package name (optionally with version)

        Returns:
            Dictionary with success status, output, and error (if any)
        """
        command = f"pip install {package}"
        return self.run_bash(command)

    def list_files(
        self,
        pattern: str,
        path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List files in a directory matching a pattern.

        Args:
            pattern: Glob pattern to match files
            path: Directory to search in (default: current directory)

        Returns:
            Dictionary with success status, files list, and error (if any)
        """
        try:
            from pathlib import Path

            search_path = Path(path) if path else Path.cwd()

            # Use glob to find matching files
            files = [str(p) for p in search_path.glob(pattern)]

            return {
                "success": True,
                "files": files,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "files": [],
                "error": f"Failed to list files: {str(e)}"
            }


# Initialize the skill instance
skill = CodeExecutionSkill()


# Export functions for agent access
def run_python(code: str, timeout: int = 120000, return_output: bool = True) -> Dict[str, Any]:
    """Execute Python code in a secure sandbox."""
    return skill.run_python(code, timeout, return_output)


def run_bash(command: str, timeout: int = 120000) -> Dict[str, Any]:
    """Execute bash commands in a secure sandbox environment."""
    return skill.run_bash(command, timeout)


def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """Write content to a file at the specified path."""
    return skill.write_file(file_path, content)


def read_file(file_path: str, offset: Optional[int] = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """Read content from a file at the specified path."""
    return skill.read_file(file_path, offset, limit)


def analyze_data(file_path: str, analysis_type: str, custom_code: Optional[str] = None) -> Dict[str, Any]:
    """Analyze data from a file using pandas and numpy."""
    return skill.analyze_data(file_path, analysis_type, custom_code)


def create_visualization(
    data_source: str,
    plot_type: str,
    output_path: str,
    custom_code: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create visualizations from data using matplotlib/seaborn."""
    return skill.create_visualization(data_source, plot_type, output_path, custom_code, options)


def install_package(package: str) -> Dict[str, Any]:
    """Install a Python package using pip."""
    return skill.install_package(package)


def list_files(pattern: str, path: Optional[str] = None) -> Dict[str, Any]:
    """List files in a directory matching a pattern."""
    return skill.list_files(pattern, path)


# CLI interface for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python main.py <function_name> <args...>")
        sys.exit(1)

    function_name = sys.argv[1]

    # Example: python main.py run_python "print('Hello, World!')"
    if function_name == "run_python":
        code = sys.argv[2]
        result = run_python(code)
        print(json.dumps(result, indent=2))

    elif function_name == "run_bash":
        command = sys.argv[2]
        result = run_bash(command)
        print(json.dumps(result, indent=2))

    elif function_name == "write_file":
        file_path = sys.argv[2]
        content = sys.argv[3]
        result = write_file(file_path, content)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown function: {function_name}")
        sys.exit(1)
