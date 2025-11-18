"""
Activity Logger for UMAP Analogy Engine

This module provides comprehensive activity logging with file-based persistence
for transparency and auditability of agent activities.

Features:
- JSON-based structured logging
- Automatic timestamping and session management
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Activity categorization (TRAINING, INFERENCE, CONFIG, SYSTEM)
- Thread-safe file operations
- Daily log rotation
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import threading


class LogLevel(Enum):
    """Log severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ActivityType(Enum):
    """Types of activities to log"""
    TRAINING = "TRAINING"
    INFERENCE = "INFERENCE"
    CONFIG = "CONFIG"
    SYSTEM = "SYSTEM"
    MODEL = "MODEL"
    DATA = "DATA"


class ActivityLogger:
    """
    Thread-safe activity logger with file-based persistence.

    Logs are stored in JSON format in the memory/logs directory,
    organized by date and session.

    Example:
        logger = ActivityLogger(task_name="word_analogies")
        logger.log_activity(
            activity_type=ActivityType.TRAINING,
            message="Started training epoch 1",
            metadata={"epoch": 1, "loss": 0.5}
        )
    """

    def __init__(
        self,
        task_name: str = "default",
        log_dir: str = "memory/logs",
        enable_console: bool = True,
        min_level: LogLevel = LogLevel.INFO
    ):
        """
        Initialize the activity logger.

        Args:
            task_name: Name of the current task/session
            log_dir: Directory to store log files
            enable_console: Whether to also print logs to console
            min_level: Minimum log level to record
        """
        self.task_name = task_name
        self.log_dir = Path(log_dir)
        self.enable_console = enable_console
        self.min_level = min_level

        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Generate session ID
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create session-specific log file
        self.log_file = self.log_dir / f"{self.session_id}_{task_name}.jsonl"

        # Thread lock for safe concurrent writes
        self._lock = threading.Lock()

        # Initialize log file with session metadata
        self._write_session_start()

    def _write_session_start(self):
        """Write session start metadata to log file"""
        session_metadata = {
            "log_type": "SESSION_START",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "task_name": self.task_name,
            "log_file": str(self.log_file)
        }
        self._write_log_entry(session_metadata)

    def _write_log_entry(self, entry: Dict[str, Any]):
        """Thread-safe write of a log entry to file"""
        with self._lock:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')

    def _should_log(self, level: LogLevel) -> bool:
        """Check if a log level should be recorded"""
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3
        }
        return level_order[level] >= level_order[self.min_level]

    def log_activity(
        self,
        activity_type: ActivityType,
        message: str,
        level: LogLevel = LogLevel.INFO,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an activity with metadata.

        Args:
            activity_type: Type of activity being logged
            message: Human-readable message
            level: Log severity level
            metadata: Additional structured data (must be JSON-serializable)
        """
        if not self._should_log(level):
            return

        # Create log entry
        entry = {
            "log_type": "ACTIVITY",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "task_name": self.task_name,
            "activity_type": activity_type.value,
            "level": level.value,
            "message": message,
            "metadata": metadata or {}
        }

        # Write to file
        self._write_log_entry(entry)

        # Optionally print to console
        if self.enable_console:
            self._print_console(entry)

    def _print_console(self, entry: Dict[str, Any]):
        """Format and print log entry to console"""
        timestamp = entry["timestamp"].split("T")[1].split(".")[0]  # HH:MM:SS
        level = entry.get("level", "INFO")
        activity_type = entry.get("activity_type", "SYSTEM")
        message = entry.get("message", "")

        # Color codes for different levels
        colors = {
            "DEBUG": "\033[36m",     # Cyan
            "INFO": "\033[32m",      # Green
            "WARNING": "\033[33m",   # Yellow
            "ERROR": "\033[31m",     # Red
        }
        reset = "\033[0m"

        color = colors.get(level, "")
        print(f"{color}[{timestamp}] {level:7} | {activity_type:12} | {message}{reset}")

    def log_training_epoch(
        self,
        epoch: int,
        total_epochs: int,
        losses: Dict[str, float],
        metrics: Optional[Dict[str, Any]] = None
    ):
        """
        Convenience method to log training epoch information.

        Args:
            epoch: Current epoch number
            total_epochs: Total number of epochs
            losses: Dictionary of loss components (e.g., {"total": 0.5, "umap": 0.3})
            metrics: Additional metrics to log
        """
        metadata = {
            "epoch": epoch,
            "total_epochs": total_epochs,
            "losses": losses,
            "metrics": metrics or {}
        }

        message = f"Epoch {epoch}/{total_epochs} - Loss: {losses.get('total', 0.0):.6f}"

        self.log_activity(
            activity_type=ActivityType.TRAINING,
            message=message,
            level=LogLevel.INFO,
            metadata=metadata
        )

    def log_inference(
        self,
        query: str,
        result: Any,
        method: str = "analogy",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Convenience method to log inference/analogy queries.

        Args:
            query: The query or input
            result: The inference result
            method: Inference method used
            metadata: Additional metadata
        """
        meta = metadata or {}
        meta.update({
            "query": str(query),
            "result": str(result),
            "method": method
        })

        self.log_activity(
            activity_type=ActivityType.INFERENCE,
            message=f"Inference query: {query} -> {result}",
            level=LogLevel.INFO,
            metadata=meta
        )

    def log_config(
        self,
        config_name: str,
        config_values: Dict[str, Any]
    ):
        """
        Log configuration changes or settings.

        Args:
            config_name: Name of the configuration
            config_values: Dictionary of configuration values
        """
        self.log_activity(
            activity_type=ActivityType.CONFIG,
            message=f"Configuration: {config_name}",
            level=LogLevel.INFO,
            metadata=config_values
        )

    def log_error(
        self,
        error_message: str,
        exception: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an error with optional exception details.

        Args:
            error_message: Human-readable error description
            exception: Optional exception object
            metadata: Additional error context
        """
        meta = metadata or {}
        if exception:
            meta["exception_type"] = type(exception).__name__
            meta["exception_message"] = str(exception)

        self.log_activity(
            activity_type=ActivityType.SYSTEM,
            message=f"ERROR: {error_message}",
            level=LogLevel.ERROR,
            metadata=meta
        )

    def log_model_info(
        self,
        model_name: str,
        parameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log model information and parameters.

        Args:
            model_name: Name/type of the model
            parameters: Model parameters
            metadata: Additional metadata
        """
        meta = metadata or {}
        meta["model_name"] = model_name
        meta["parameters"] = parameters

        self.log_activity(
            activity_type=ActivityType.MODEL,
            message=f"Model: {model_name}",
            level=LogLevel.INFO,
            metadata=meta
        )

    def close_session(self, summary: Optional[Dict[str, Any]] = None):
        """
        Close the current logging session.

        Args:
            summary: Optional summary statistics for the session
        """
        entry = {
            "log_type": "SESSION_END",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "task_name": self.task_name,
            "summary": summary or {}
        }
        self._write_log_entry(entry)

    def get_log_file_path(self) -> Path:
        """Get the path to the current log file"""
        return self.log_file

    def get_session_id(self) -> str:
        """Get the current session ID"""
        return self.session_id


class LogReader:
    """
    Utility class to read and parse log files.

    Example:
        reader = LogReader()
        logs = reader.read_session("20250118_143000_word_analogies")
        training_logs = reader.filter_by_type(logs, ActivityType.TRAINING)
    """

    def __init__(self, log_dir: str = "memory/logs"):
        """
        Initialize log reader.

        Args:
            log_dir: Directory containing log files
        """
        self.log_dir = Path(log_dir)

    def read_session(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Read all logs from a specific session.

        Args:
            session_id: Session ID to read

        Returns:
            List of log entries
        """
        # Find log file matching session ID
        log_files = list(self.log_dir.glob(f"{session_id}*.jsonl"))

        if not log_files:
            return []

        logs = []
        with open(log_files[0], 'r') as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))

        return logs

    def read_all_logs(self) -> List[Dict[str, Any]]:
        """Read all log files in the log directory"""
        all_logs = []

        for log_file in self.log_dir.glob("*.jsonl"):
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        all_logs.append(json.loads(line))

        return all_logs

    def read_logs_by_date(self, date: str) -> List[Dict[str, Any]]:
        """
        Read logs from a specific date.

        Args:
            date: Date in format YYYYMMDD

        Returns:
            List of log entries from that date
        """
        logs = []

        for log_file in self.log_dir.glob(f"{date}*.jsonl"):
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))

        return logs

    def filter_by_type(
        self,
        logs: List[Dict[str, Any]],
        activity_type: ActivityType
    ) -> List[Dict[str, Any]]:
        """Filter logs by activity type"""
        return [
            log for log in logs
            if log.get("activity_type") == activity_type.value
        ]

    def filter_by_level(
        self,
        logs: List[Dict[str, Any]],
        level: LogLevel
    ) -> List[Dict[str, Any]]:
        """Filter logs by log level"""
        return [
            log for log in logs
            if log.get("level") == level.value
        ]

    def get_sessions(self) -> List[str]:
        """Get list of all session IDs"""
        sessions = set()
        for log_file in self.log_dir.glob("*.jsonl"):
            # Extract session ID from filename (YYYYMMDD_HHMMSS)
            parts = log_file.stem.split("_")
            if len(parts) >= 2:
                session_id = f"{parts[0]}_{parts[1]}"
                sessions.add(session_id)

        return sorted(list(sessions))
