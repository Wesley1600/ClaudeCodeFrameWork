"""
Basic test of the activity logging system without requiring full training.

This tests the core logging and reporting functionality.
"""

import time
from activity_logger import ActivityLogger, ActivityType, LogLevel, LogReader
from report_generator import ReportGenerator


def test_basic_logging():
    """Test basic logging functionality"""
    print("=" * 60)
    print("TEST 1: Basic Logging")
    print("=" * 60)

    # Create logger
    logger = ActivityLogger(
        task_name="test_basic",
        enable_console=True,
        min_level=LogLevel.DEBUG
    )

    print(f"\nSession ID: {logger.get_session_id()}")
    print(f"Log file: {logger.get_log_file_path()}")

    # Log different types of activities
    logger.log_config(
        config_name="test_config",
        config_values={
            "param1": 42,
            "param2": "test_value",
            "param3": [1, 2, 3]
        }
    )

    logger.log_activity(
        activity_type=ActivityType.SYSTEM,
        message="System initialization completed",
        level=LogLevel.INFO
    )

    logger.log_training_epoch(
        epoch=1,
        total_epochs=100,
        losses={"total": 0.5, "umap": 0.3, "align": 0.2}
    )

    logger.log_inference(
        query="test_query",
        result="test_result",
        method="test_method",
        metadata={"confidence": 0.95}
    )

    logger.log_activity(
        activity_type=ActivityType.SYSTEM,
        message="This is a warning message",
        level=LogLevel.WARNING,
        metadata={"warning_type": "memory"}
    )

    logger.log_error(
        error_message="Test error (simulated)",
        metadata={"error_code": 123}
    )

    # Close session
    logger.close_session(summary={"test": "completed"})

    print("\n✓ Basic logging test completed")
    return logger.get_session_id()


def test_log_reader(session_id):
    """Test log reading functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Log Reading")
    print("=" * 60)

    reader = LogReader()

    # Read the session
    logs = reader.read_session(session_id)
    print(f"\nRead {len(logs)} log entries from session {session_id}")

    # Filter by type
    training_logs = reader.filter_by_type(logs, ActivityType.TRAINING)
    print(f"Training logs: {len(training_logs)}")

    inference_logs = reader.filter_by_type(logs, ActivityType.INFERENCE)
    print(f"Inference logs: {len(inference_logs)}")

    # Filter by level
    errors = reader.filter_by_level(logs, LogLevel.ERROR)
    print(f"Errors: {len(errors)}")

    warnings = reader.filter_by_level(logs, LogLevel.WARNING)
    print(f"Warnings: {len(warnings)}")

    # List sessions
    sessions = reader.get_sessions()
    print(f"\nTotal sessions: {len(sessions)}")

    print("\n✓ Log reader test completed")


def test_report_generation(session_id):
    """Test report generation"""
    print("\n" + "=" * 60)
    print("TEST 3: Report Generation")
    print("=" * 60)

    generator = ReportGenerator()

    # Generate session report
    print("\nGenerating session report...")
    report_path = generator.generate_session_report(
        session_id=session_id,
        output_format="markdown"
    )
    print(f"  Markdown report: {report_path}")

    report_path_json = generator.generate_session_report(
        session_id=session_id,
        output_format="json"
    )
    print(f"  JSON report: {report_path_json}")

    # Generate daily report
    from datetime import datetime
    today = datetime.now().strftime("%Y%m%d")

    print(f"\nGenerating daily report for {today}...")
    daily_report = generator.generate_daily_report(
        date=today,
        output_format="markdown"
    )
    print(f"  Daily report: {daily_report}")

    # List available reports
    reports = generator.list_available_reports()
    print(f"\nGenerated reports ({len(reports)}):")
    for report in reports:
        print(f"  - {report}")

    print("\n✓ Report generation test completed")


def test_multiple_sessions():
    """Test logging multiple sessions"""
    print("\n" + "=" * 60)
    print("TEST 4: Multiple Sessions")
    print("=" * 60)

    session_ids = []

    for i in range(3):
        print(f"\nCreating session {i+1}/3...")
        logger = ActivityLogger(
            task_name=f"multi_test_{i}",
            enable_console=False  # Suppress output for clarity
        )

        # Log some activities
        for j in range(5):
            logger.log_training_epoch(
                epoch=j,
                total_epochs=5,
                losses={"total": 1.0 / (j + 1)}
            )

        logger.close_session()
        session_ids.append(logger.get_session_id())
        time.sleep(0.1)  # Ensure different timestamps

    print(f"\n✓ Created {len(session_ids)} sessions")

    # Generate reports for all
    generator = ReportGenerator()
    for sid in session_ids:
        generator.generate_session_report(sid, output_format="markdown")

    print("✓ Multiple sessions test completed")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ACTIVITY LOGGING SYSTEM - BASIC TESTS")
    print("=" * 60 + "\n")

    # Test 1: Basic logging
    session_id = test_basic_logging()

    # Test 2: Log reading
    test_log_reader(session_id)

    # Test 3: Report generation
    test_report_generation(session_id)

    # Test 4: Multiple sessions
    test_multiple_sessions()

    # Final summary
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - memory/logs/     : Activity log files (JSONL format)")
    print("  - memory/reports/  : Summary reports (Markdown & JSON)")
    print("\nYou can now:")
    print("  1. Examine the log files in memory/logs/")
    print("  2. Read the generated reports in memory/reports/")
    print("  3. Use the logging system in your own code")
    print()


if __name__ == "__main__":
    main()
