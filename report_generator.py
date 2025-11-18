"""
Report Generator for Activity Logs

This module generates summary reports from activity logs for auditability
and transparency. Supports daily summaries, per-task summaries, and custom
aggregations.

Features:
- Daily activity summaries
- Per-task/session summaries
- Training metrics aggregation
- Error and warning summaries
- Export to Markdown and JSON formats
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict, Counter
import statistics

from activity_logger import LogReader, ActivityType, LogLevel


class ReportGenerator:
    """
    Generate summary reports from activity logs.

    Example:
        generator = ReportGenerator()
        generator.generate_daily_report("20250118")
        generator.generate_session_report("20250118_143000")
    """

    def __init__(
        self,
        log_dir: str = "memory/logs",
        report_dir: str = "memory/reports"
    ):
        """
        Initialize report generator.

        Args:
            log_dir: Directory containing log files
            report_dir: Directory to save generated reports
        """
        self.log_reader = LogReader(log_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def generate_daily_report(
        self,
        date: str,
        output_format: str = "markdown"
    ) -> str:
        """
        Generate a summary report for a specific day.

        Args:
            date: Date in format YYYYMMDD
            output_format: "markdown" or "json"

        Returns:
            Path to the generated report file
        """
        # Read logs for the specified date
        logs = self.log_reader.read_logs_by_date(date)

        if not logs:
            print(f"No logs found for date {date}")
            return ""

        # Compute statistics
        stats = self._compute_daily_statistics(logs)

        # Format report
        if output_format == "markdown":
            report_content = self._format_daily_markdown(date, stats, logs)
            report_file = self.report_dir / f"daily_report_{date}.md"
        else:
            report_content = json.dumps(stats, indent=2)
            report_file = self.report_dir / f"daily_report_{date}.json"

        # Write report
        with open(report_file, 'w') as f:
            f.write(report_content)

        print(f"Daily report generated: {report_file}")
        return str(report_file)

    def generate_session_report(
        self,
        session_id: str,
        output_format: str = "markdown"
    ) -> str:
        """
        Generate a summary report for a specific session/task.

        Args:
            session_id: Session ID (e.g., "20250118_143000")
            output_format: "markdown" or "json"

        Returns:
            Path to the generated report file
        """
        # Read logs for the specified session
        logs = self.log_reader.read_session(session_id)

        if not logs:
            print(f"No logs found for session {session_id}")
            return ""

        # Compute statistics
        stats = self._compute_session_statistics(logs)

        # Format report
        if output_format == "markdown":
            report_content = self._format_session_markdown(session_id, stats, logs)
            report_file = self.report_dir / f"session_report_{session_id}.md"
        else:
            report_content = json.dumps(stats, indent=2)
            report_file = self.report_dir / f"session_report_{session_id}.json"

        # Write report
        with open(report_file, 'w') as f:
            f.write(report_content)

        print(f"Session report generated: {report_file}")
        return str(report_file)

    def generate_training_summary(
        self,
        session_id: str,
        output_format: str = "markdown"
    ) -> str:
        """
        Generate a focused training summary for a session.

        Args:
            session_id: Session ID
            output_format: "markdown" or "json"

        Returns:
            Path to the generated report file
        """
        logs = self.log_reader.read_session(session_id)
        training_logs = self.log_reader.filter_by_type(logs, ActivityType.TRAINING)

        if not training_logs:
            print(f"No training logs found for session {session_id}")
            return ""

        stats = self._compute_training_statistics(training_logs)

        if output_format == "markdown":
            report_content = self._format_training_markdown(session_id, stats, training_logs)
            report_file = self.report_dir / f"training_summary_{session_id}.md"
        else:
            report_content = json.dumps(stats, indent=2)
            report_file = self.report_dir / f"training_summary_{session_id}.json"

        with open(report_file, 'w') as f:
            f.write(report_content)

        print(f"Training summary generated: {report_file}")
        return str(report_file)

    def _compute_daily_statistics(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute aggregate statistics for daily logs"""
        stats = {
            "total_logs": len(logs),
            "sessions": set(),
            "tasks": set(),
            "activity_counts": Counter(),
            "level_counts": Counter(),
            "errors": [],
            "warnings": []
        }

        for log in logs:
            if log.get("session_id"):
                stats["sessions"].add(log["session_id"])
            if log.get("task_name"):
                stats["tasks"].add(log["task_name"])
            if log.get("activity_type"):
                stats["activity_counts"][log["activity_type"]] += 1
            if log.get("level"):
                stats["level_counts"][log["level"]] += 1

            # Collect errors and warnings
            if log.get("level") == "ERROR":
                stats["errors"].append(log)
            elif log.get("level") == "WARNING":
                stats["warnings"].append(log)

        # Convert sets to counts
        stats["session_count"] = len(stats["sessions"])
        stats["task_count"] = len(stats["tasks"])
        stats["sessions"] = list(stats["sessions"])
        stats["tasks"] = list(stats["tasks"])

        return stats

    def _compute_session_statistics(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute statistics for a single session"""
        stats = {
            "total_logs": len(logs),
            "task_name": None,
            "start_time": None,
            "end_time": None,
            "duration_seconds": None,
            "activity_counts": Counter(),
            "level_counts": Counter(),
            "training_epochs": 0,
            "inference_count": 0,
            "errors": [],
            "warnings": []
        }

        # Extract session metadata
        for log in logs:
            if log.get("log_type") == "SESSION_START":
                stats["task_name"] = log.get("task_name")
                stats["start_time"] = log.get("timestamp")
            elif log.get("log_type") == "SESSION_END":
                stats["end_time"] = log.get("timestamp")

            if log.get("activity_type"):
                stats["activity_counts"][log["activity_type"]] += 1

            if log.get("level"):
                stats["level_counts"][log["level"]] += 1

            # Count specific activities
            if log.get("activity_type") == "TRAINING":
                stats["training_epochs"] += 1
            elif log.get("activity_type") == "INFERENCE":
                stats["inference_count"] += 1

            # Collect errors and warnings
            if log.get("level") == "ERROR":
                stats["errors"].append(log)
            elif log.get("level") == "WARNING":
                stats["warnings"].append(log)

        # Calculate duration
        if stats["start_time"] and stats["end_time"]:
            start = datetime.fromisoformat(stats["start_time"])
            end = datetime.fromisoformat(stats["end_time"])
            stats["duration_seconds"] = (end - start).total_seconds()

        return stats

    def _compute_training_statistics(self, training_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute detailed training statistics"""
        stats = {
            "total_epochs": len(training_logs),
            "loss_history": [],
            "loss_components": defaultdict(list),
            "metrics_history": [],
            "final_loss": None,
            "best_loss": None,
            "average_loss": None
        }

        for log in training_logs:
            metadata = log.get("metadata", {})
            losses = metadata.get("losses", {})

            if "total" in losses:
                stats["loss_history"].append(losses["total"])

            # Track individual loss components
            for component, value in losses.items():
                stats["loss_components"][component].append(value)

            # Track metrics
            metrics = metadata.get("metrics", {})
            if metrics:
                stats["metrics_history"].append(metrics)

        # Compute aggregate statistics
        if stats["loss_history"]:
            stats["final_loss"] = stats["loss_history"][-1]
            stats["best_loss"] = min(stats["loss_history"])
            stats["average_loss"] = statistics.mean(stats["loss_history"])

        # Convert defaultdict to regular dict
        stats["loss_components"] = dict(stats["loss_components"])

        return stats

    def _format_daily_markdown(
        self,
        date: str,
        stats: Dict[str, Any],
        logs: List[Dict[str, Any]]
    ) -> str:
        """Format daily report as Markdown"""
        # Convert date format
        formatted_date = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"

        report = f"""# Daily Activity Report - {formatted_date}

## Summary

- **Total Log Entries**: {stats['total_logs']}
- **Sessions**: {stats['session_count']}
- **Tasks**: {stats['task_count']}
- **Errors**: {len(stats['errors'])}
- **Warnings**: {len(stats['warnings'])}

## Activity Breakdown

"""

        # Activity counts
        for activity_type, count in stats['activity_counts'].most_common():
            report += f"- **{activity_type}**: {count}\n"

        report += "\n## Log Level Breakdown\n\n"

        # Level counts
        for level, count in stats['level_counts'].most_common():
            report += f"- **{level}**: {count}\n"

        # Sessions
        report += f"\n## Sessions ({stats['session_count']})\n\n"
        for session in stats['sessions']:
            report += f"- {session}\n"

        # Tasks
        report += f"\n## Tasks ({stats['task_count']})\n\n"
        for task in stats['tasks']:
            report += f"- {task}\n"

        # Errors
        if stats['errors']:
            report += f"\n## Errors ({len(stats['errors'])})\n\n"
            for error in stats['errors']:
                timestamp = error.get('timestamp', 'N/A')
                message = error.get('message', 'N/A')
                report += f"- **{timestamp}**: {message}\n"

        # Warnings
        if stats['warnings']:
            report += f"\n## Warnings ({len(stats['warnings'])})\n\n"
            for warning in stats['warnings']:
                timestamp = warning.get('timestamp', 'N/A')
                message = warning.get('message', 'N/A')
                report += f"- **{timestamp}**: {message}\n"

        report += "\n---\n*Report generated by Activity Logger*\n"

        return report

    def _format_session_markdown(
        self,
        session_id: str,
        stats: Dict[str, Any],
        logs: List[Dict[str, Any]]
    ) -> str:
        """Format session report as Markdown"""
        report = f"""# Session Activity Report - {session_id}

## Session Information

- **Task Name**: {stats['task_name']}
- **Session ID**: {session_id}
- **Start Time**: {stats['start_time']}
- **End Time**: {stats['end_time']}
- **Duration**: {stats['duration_seconds']:.2f} seconds

## Summary

- **Total Log Entries**: {stats['total_logs']}
- **Training Epochs**: {stats['training_epochs']}
- **Inference Queries**: {stats['inference_count']}
- **Errors**: {len(stats['errors'])}
- **Warnings**: {len(stats['warnings'])}

## Activity Breakdown

"""

        # Activity counts
        for activity_type, count in stats['activity_counts'].most_common():
            report += f"- **{activity_type}**: {count}\n"

        report += "\n## Log Level Breakdown\n\n"

        # Level counts
        for level, count in stats['level_counts'].most_common():
            report += f"- **{level}**: {count}\n"

        # Errors
        if stats['errors']:
            report += f"\n## Errors ({len(stats['errors'])})\n\n"
            for error in stats['errors']:
                timestamp = error.get('timestamp', 'N/A')
                message = error.get('message', 'N/A')
                report += f"- **{timestamp}**: {message}\n"

        # Warnings
        if stats['warnings']:
            report += f"\n## Warnings ({len(stats['warnings'])})\n\n"
            for warning in stats['warnings']:
                timestamp = warning.get('timestamp', 'N/A')
                message = warning.get('message', 'N/A')
                report += f"- **{timestamp}**: {warning}\n"

        report += "\n---\n*Report generated by Activity Logger*\n"

        return report

    def _format_training_markdown(
        self,
        session_id: str,
        stats: Dict[str, Any],
        training_logs: List[Dict[str, Any]]
    ) -> str:
        """Format training summary as Markdown"""
        report = f"""# Training Summary - {session_id}

## Training Statistics

- **Total Epochs**: {stats['total_epochs']}
- **Final Loss**: {stats['final_loss']:.6f if stats['final_loss'] else 'N/A'}
- **Best Loss**: {stats['best_loss']:.6f if stats['best_loss'] else 'N/A'}
- **Average Loss**: {stats['average_loss']:.6f if stats['average_loss'] else 'N/A'}

## Loss Components

"""

        # Loss components summary
        for component, values in stats['loss_components'].items():
            if values:
                final_val = values[-1]
                best_val = min(values)
                avg_val = statistics.mean(values)
                report += f"- **{component}**:\n"
                report += f"  - Final: {final_val:.6f}\n"
                report += f"  - Best: {best_val:.6f}\n"
                report += f"  - Average: {avg_val:.6f}\n"

        # Loss history table (sample every N epochs for brevity)
        if stats['loss_history']:
            report += "\n## Loss History\n\n"
            report += "| Epoch | Total Loss |\n"
            report += "|-------|------------|\n"

            # Show first, last, and every 10th epoch
            epochs_to_show = set([0, len(stats['loss_history']) - 1])
            epochs_to_show.update(range(0, len(stats['loss_history']), 10))

            for i in sorted(epochs_to_show):
                if i < len(stats['loss_history']):
                    report += f"| {i} | {stats['loss_history'][i]:.6f} |\n"

        report += "\n---\n*Report generated by Activity Logger*\n"

        return report

    def list_available_sessions(self) -> List[str]:
        """List all available session IDs"""
        return self.log_reader.get_sessions()

    def list_available_reports(self) -> List[str]:
        """List all generated reports"""
        reports = []
        for report_file in self.report_dir.glob("*"):
            if report_file.is_file():
                reports.append(str(report_file.name))
        return sorted(reports)


def generate_all_reports(date: Optional[str] = None):
    """
    Convenience function to generate all reports for a given date.
    If no date is provided, uses today's date.

    Args:
        date: Date in format YYYYMMDD, or None for today
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")

    generator = ReportGenerator()

    # Generate daily report
    print(f"\nGenerating daily report for {date}...")
    generator.generate_daily_report(date, output_format="markdown")
    generator.generate_daily_report(date, output_format="json")

    # Generate session reports for all sessions on that date
    print(f"\nGenerating session reports...")
    all_sessions = generator.list_available_sessions()
    date_sessions = [s for s in all_sessions if s.startswith(date)]

    for session_id in date_sessions:
        print(f"  - Session {session_id}")
        generator.generate_session_report(session_id, output_format="markdown")
        generator.generate_training_summary(session_id, output_format="markdown")

    print(f"\n✓ All reports generated successfully!")
    print(f"  Reports saved to: memory/reports/")


if __name__ == "__main__":
    # Example usage
    generate_all_reports()
