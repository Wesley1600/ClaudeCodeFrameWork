"""
Code Execution Skill

A comprehensive skill for executing scripts, analyzing data, and creating files
in a secure sandbox environment.
"""

from .main import (
    run_python,
    run_bash,
    write_file,
    read_file,
    analyze_data,
    create_visualization,
    install_package,
    list_files,
    CodeExecutionSkill
)

__version__ = "1.0.0"
__all__ = [
    "run_python",
    "run_bash",
    "write_file",
    "read_file",
    "analyze_data",
    "create_visualization",
    "install_package",
    "list_files",
    "CodeExecutionSkill"
]
