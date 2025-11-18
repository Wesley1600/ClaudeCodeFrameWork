"""
Files API Skill for Claude Code

A comprehensive interface for uploading, downloading, and managing files
using the Anthropic Files API.
"""

from .files_manager import (
    FilesManager,
    FilesAPIError,
    AuthenticationError,
    FileNotFoundError,
    FileSizeLimitError
)

__version__ = "1.0.0"
__all__ = [
    "FilesManager",
    "FilesAPIError",
    "AuthenticationError",
    "FileNotFoundError",
    "FileSizeLimitError"
]
