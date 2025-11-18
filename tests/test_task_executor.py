#!/usr/bin/env python3
"""
Test suite for TaskExecutor

Tests the task execution framework including:
- Task execution
- Test running
- Coverage measurement
- Report generation
- Dependency management
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path to import task_executor
sys.path.insert(0, str(Path(__file__).parent.parent))

from task_executor import (
    TaskExecutor,
    Task,
    TaskType,
    TaskStatus,
    ExecutionConfig,
    TestResult,
    CoverageResult,
    TaskResult
)


class TestTaskResult:
    """Test TaskResult dataclass"""

    def test_task_result_creation(self):
        result = TaskResult(
            task_name="Test Task",
            task_type=TaskType.REFACTOR,
            status=TaskStatus.COMPLETED,
            duration=1.5
        )

        assert result.task_name == "Test Task"
        assert result.task_type == TaskType.REFACTOR
        assert result.status == TaskStatus.COMPLETED
        assert result.duration == 1.5

    def test_task_result_to_dict(self):
        result = TaskResult(
            task_name="Test Task",
            task_type=TaskType.TEST,
            status=TaskStatus.COMPLETED,
            duration=2.5
        )

        data = result.to_dict()

        assert data["task_name"] == "Test Task"
        assert data["task_type"] == "test"
        assert data["status"] == "completed"
        assert data["duration"] == 2.5


class TestTestResult:
    """Test TestResult dataclass"""

    def test_test_result_creation(self):
        result = TestResult(
            passed=10,
            failed=2,
            skipped=1,
            duration=3.5
        )

        assert result.passed == 10
        assert result.failed == 2
        assert result.skipped == 1
        assert result.total == 13
        assert result.duration == 3.5

    def test_test_result_to_dict(self):
        result = TestResult(passed=5, failed=1, skipped=0, duration=1.0)
        data = result.to_dict()

        assert data["passed"] == 5
        assert data["failed"] == 1
        assert data["total"] == 6
        assert data["success"] is True


class TestCoverageResult:
    """Test CoverageResult dataclass"""

    def test_coverage_result_creation(self):
        result = CoverageResult(
            percent_covered=85.5,
            lines_covered=171,
            lines_total=200
        )

        assert result.percent_covered == 85.5
        assert result.lines_covered == 171
        assert result.lines_total == 200

    def test_coverage_result_to_dict(self):
        result = CoverageResult(
            percent_covered=90.5,
            lines_covered=181,
            lines_total=200,
            delta=5.0
        )

        data = result.to_dict()

        assert data["percent_covered"] == 90.5
        assert data["lines_covered"] == 181
        assert data["delta"] == 5.0

    def test_coverage_by_module(self):
        result = CoverageResult(
            percent_covered=85.0,
            by_module={
                "module1.py": 90.5,
                "module2.py": 80.0
            }
        )

        data = result.to_dict()
        assert data["by_module"]["module1.py"] == 90.5
        assert data["by_module"]["module2.py"] == 80.0


class TestExecutionConfig:
    """Test ExecutionConfig"""

    def test_default_config(self):
        config = ExecutionConfig()

        assert config.run_tests_after_each_task is True
        assert config.measure_coverage is True
        assert config.stop_on_test_failure is True
        assert config.test_command == "pytest"

    def test_custom_config(self):
        config = ExecutionConfig(
            run_tests_after_each_task=False,
            measure_coverage=False,
            coverage_threshold=90.0,
            verbose=False
        )

        assert config.run_tests_after_each_task is False
        assert config.measure_coverage is False
        assert config.coverage_threshold == 90.0
        assert config.verbose is False


class TestTaskExecutor:
    """Test TaskExecutor main functionality"""

    def test_executor_creation(self):
        executor = TaskExecutor()

        assert executor.config is not None
        assert executor.tasks == []
        assert executor.results == []

    def test_executor_with_custom_config(self):
        config = ExecutionConfig(verbose=False)
        executor = TaskExecutor(config)

        assert executor.config.verbose is False

    def test_add_task(self):
        executor = TaskExecutor()

        def dummy_task():
            return True

        task = Task(
            name="Test Task",
            description="A test task",
            task_type=TaskType.REFACTOR,
            executor=dummy_task
        )

        executor.add_task(task)

        assert len(executor.tasks) == 1
        assert executor.tasks[0].name == "Test Task"

    def test_add_multiple_tasks(self):
        executor = TaskExecutor()

        def dummy_task():
            return True

        tasks = [
            Task("Task 1", "Description 1", TaskType.REFACTOR, dummy_task),
            Task("Task 2", "Description 2", TaskType.TEST, dummy_task),
        ]

        executor.add_tasks(tasks)

        assert len(executor.tasks) == 2

    def test_run_command(self):
        executor = TaskExecutor()

        exit_code, stdout, stderr = executor.run_command("echo 'Hello World'")

        assert exit_code == 0
        assert "Hello World" in stdout

    def test_run_command_failure(self):
        executor = TaskExecutor()

        exit_code, stdout, stderr = executor.run_command("exit 1")

        assert exit_code == 1


class TestTaskExecution:
    """Test task execution functionality"""

    def test_execute_simple_task(self):
        config = ExecutionConfig(
            run_tests_after_each_task=False,
            measure_coverage=False,
            verbose=False
        )
        executor = TaskExecutor(config)

        execution_count = [0]

        def task_func():
            execution_count[0] += 1
            return True

        task = Task(
            name="Simple Task",
            description="A simple task",
            task_type=TaskType.REFACTOR,
            executor=task_func,
            run_tests=False,
            measure_coverage=False
        )

        executor.add_task(task)
        success = executor.execute_all()

        assert success is True
        assert execution_count[0] == 1
        assert len(executor.results) == 1
        assert executor.results[0].status == TaskStatus.COMPLETED

    def test_execute_failing_task(self):
        config = ExecutionConfig(
            run_tests_after_each_task=False,
            measure_coverage=False,
            verbose=False,
            continue_on_error=False
        )
        executor = TaskExecutor(config)

        def failing_task():
            return False

        task = Task(
            name="Failing Task",
            description="A task that fails",
            task_type=TaskType.REFACTOR,
            executor=failing_task,
            run_tests=False
        )

        executor.add_task(task)
        success = executor.execute_all()

        assert success is False
        assert len(executor.results) == 1
        assert executor.results[0].status == TaskStatus.FAILED

    def test_execute_task_with_exception(self):
        config = ExecutionConfig(
            run_tests_after_each_task=False,
            measure_coverage=False,
            verbose=False
        )
        executor = TaskExecutor(config)

        def exception_task():
            raise ValueError("Test exception")

        task = Task(
            name="Exception Task",
            description="A task that raises exception",
            task_type=TaskType.REFACTOR,
            executor=exception_task,
            run_tests=False
        )

        executor.add_task(task)
        success = executor.execute_all()

        assert success is False
        assert len(executor.results) == 1
        assert executor.results[0].status == TaskStatus.FAILED
        assert "Test exception" in executor.results[0].error

    def test_execute_multiple_tasks_in_sequence(self):
        config = ExecutionConfig(
            run_tests_after_each_task=False,
            measure_coverage=False,
            verbose=False
        )
        executor = TaskExecutor(config)

        execution_order = []

        def task1():
            execution_order.append(1)
            return True

        def task2():
            execution_order.append(2)
            return True

        def task3():
            execution_order.append(3)
            return True

        tasks = [
            Task("Task 1", "First task", TaskType.REFACTOR, task1, run_tests=False),
            Task("Task 2", "Second task", TaskType.REFACTOR, task2, run_tests=False),
            Task("Task 3", "Third task", TaskType.REFACTOR, task3, run_tests=False),
        ]

        executor.add_tasks(tasks)
        success = executor.execute_all()

        assert success is True
        assert execution_order == [1, 2, 3]
        assert len(executor.results) == 3


class TestDependencyManagement:
    """Test task dependency management"""

    def test_validate_dependencies_success(self):
        executor = TaskExecutor()

        def dummy_task():
            return True

        tasks = [
            Task("Task A", "First", TaskType.REFACTOR, dummy_task),
            Task("Task B", "Second", TaskType.REFACTOR, dummy_task, dependencies=["Task A"]),
        ]

        executor.add_tasks(tasks)
        valid = executor.validate_dependencies()

        assert valid is True

    def test_validate_dependencies_failure(self):
        executor = TaskExecutor()

        def dummy_task():
            return True

        tasks = [
            Task("Task A", "First", TaskType.REFACTOR, dummy_task, dependencies=["Task C"]),
        ]

        executor.add_tasks(tasks)
        valid = executor.validate_dependencies()

        assert valid is False

    def test_topological_sort_simple(self):
        executor = TaskExecutor()

        def dummy_task():
            return True

        tasks = [
            Task("Task C", "Third", TaskType.REFACTOR, dummy_task, dependencies=["Task B"]),
            Task("Task A", "First", TaskType.REFACTOR, dummy_task),
            Task("Task B", "Second", TaskType.REFACTOR, dummy_task, dependencies=["Task A"]),
        ]

        executor.add_tasks(tasks)
        sorted_tasks = executor.topological_sort()

        # Extract task names
        names = [t.name for t in sorted_tasks]

        # Task A should come before B, B before C
        assert names.index("Task A") < names.index("Task B")
        assert names.index("Task B") < names.index("Task C")

    def test_topological_sort_complex(self):
        executor = TaskExecutor()

        def dummy_task():
            return True

        tasks = [
            Task("Task D", "Fourth", TaskType.REFACTOR, dummy_task, dependencies=["Task B", "Task C"]),
            Task("Task C", "Third", TaskType.REFACTOR, dummy_task, dependencies=["Task A"]),
            Task("Task A", "First", TaskType.REFACTOR, dummy_task),
            Task("Task B", "Second", TaskType.REFACTOR, dummy_task, dependencies=["Task A"]),
        ]

        executor.add_tasks(tasks)
        sorted_tasks = executor.topological_sort()

        names = [t.name for t in sorted_tasks]

        # Verify dependencies are respected
        assert names.index("Task A") < names.index("Task B")
        assert names.index("Task A") < names.index("Task C")
        assert names.index("Task B") < names.index("Task D")
        assert names.index("Task C") < names.index("Task D")

    def test_circular_dependency_detection(self):
        executor = TaskExecutor()

        def dummy_task():
            return True

        tasks = [
            Task("Task A", "First", TaskType.REFACTOR, dummy_task, dependencies=["Task B"]),
            Task("Task B", "Second", TaskType.REFACTOR, dummy_task, dependencies=["Task A"]),
        ]

        executor.add_tasks(tasks)

        with pytest.raises(ValueError, match="Circular dependency"):
            executor.topological_sort()


class TestReportGeneration:
    """Test report generation"""

    def test_generate_empty_report(self):
        executor = TaskExecutor()
        report = executor.generate_report()

        assert "No tasks executed" in report

    def test_generate_simple_report(self):
        config = ExecutionConfig(
            run_tests_after_each_task=False,
            measure_coverage=False,
            verbose=False
        )
        executor = TaskExecutor(config)

        def task_func():
            return True

        task = Task("Test Task", "A test", TaskType.REFACTOR, task_func, run_tests=False)
        executor.add_task(task)
        executor.execute_all()

        report = executor.generate_report()

        assert "TASK EXECUTION REPORT" in report
        assert "Test Task" in report
        assert "SUMMARY" in report

    def test_report_with_test_results(self):
        config = ExecutionConfig(
            run_tests_after_each_task=False,
            measure_coverage=False,
            verbose=False
        )
        executor = TaskExecutor(config)

        # Add a task result with test results
        executor.results.append(
            TaskResult(
                task_name="Test Task",
                task_type=TaskType.TEST,
                status=TaskStatus.COMPLETED,
                duration=1.5,
                test_result=TestResult(passed=10, failed=0, skipped=1)
            )
        )

        executor.start_time = 0
        executor.end_time = 2

        report = executor.generate_report()

        assert "10 passed" in report
        assert "0 failed" in report

    def test_report_with_coverage(self):
        config = ExecutionConfig(verbose=False)
        executor = TaskExecutor(config)

        executor.initial_coverage = CoverageResult(percent_covered=80.0)

        executor.results.append(
            TaskResult(
                task_name="Test Task",
                task_type=TaskType.REFACTOR,
                status=TaskStatus.COMPLETED,
                duration=1.5,
                coverage_result=CoverageResult(
                    percent_covered=85.0,
                    delta=5.0
                )
            )
        )

        executor.start_time = 0
        executor.end_time = 2

        report = executor.generate_report()

        assert "Starting coverage: 80.00%" in report
        assert "Final coverage:    85.00%" in report
        assert "Coverage delta:    +5.00%" in report


class TestJSONExport:
    """Test JSON export functionality"""

    def test_export_json(self):
        config = ExecutionConfig(
            run_tests_after_each_task=False,
            measure_coverage=False,
            verbose=False
        )
        executor = TaskExecutor(config)

        def task_func():
            return True

        task = Task("Test Task", "A test", TaskType.REFACTOR, task_func, run_tests=False)
        executor.add_task(task)
        executor.execute_all()

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            executor.export_json(filepath)

            # Read and verify JSON
            with open(filepath) as f:
                data = json.load(f)

            assert "summary" in data
            assert "tasks" in data
            assert data["summary"]["total_tasks"] == 1
            assert data["tasks"][0]["task_name"] == "Test Task"

        finally:
            # Cleanup
            Path(filepath).unlink()


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_complete_refactoring_workflow(self):
        """Test a complete refactoring workflow with multiple tasks"""
        config = ExecutionConfig(
            run_tests_after_each_task=False,
            measure_coverage=False,
            create_checkpoints=False,
            verbose=False
        )
        executor = TaskExecutor(config)

        execution_log = []

        def refactor1():
            execution_log.append("refactor1")
            return True

        def refactor2():
            execution_log.append("refactor2")
            return True

        def refactor3():
            execution_log.append("refactor3")
            return True

        tasks = [
            Task("Refactor A", "First refactor", TaskType.REFACTOR, refactor1, run_tests=False),
            Task("Refactor B", "Second refactor", TaskType.REFACTOR, refactor2,
                 dependencies=["Refactor A"], run_tests=False),
            Task("Refactor C", "Third refactor", TaskType.REFACTOR, refactor3,
                 dependencies=["Refactor B"], run_tests=False),
        ]

        executor.add_tasks(tasks)
        success = executor.execute_all()

        assert success is True
        assert execution_log == ["refactor1", "refactor2", "refactor3"]
        assert len(executor.results) == 3
        assert all(r.status == TaskStatus.COMPLETED for r in executor.results)

    def test_stop_on_failure(self):
        """Test that execution stops on failure when configured"""
        config = ExecutionConfig(
            run_tests_after_each_task=False,
            measure_coverage=False,
            verbose=False,
            continue_on_error=False
        )
        executor = TaskExecutor(config)

        execution_log = []

        def task1():
            execution_log.append("task1")
            return True

        def task2():
            execution_log.append("task2")
            return False  # This fails

        def task3():
            execution_log.append("task3")
            return True

        tasks = [
            Task("Task 1", "First", TaskType.REFACTOR, task1, run_tests=False),
            Task("Task 2", "Second", TaskType.REFACTOR, task2, run_tests=False),
            Task("Task 3", "Third", TaskType.REFACTOR, task3, run_tests=False),
        ]

        executor.add_tasks(tasks)
        success = executor.execute_all()

        assert success is False
        assert execution_log == ["task1", "task2"]  # task3 not executed
        assert len(executor.results) == 2


class TestMocking:
    """Tests using mocks for external dependencies"""

    @patch('task_executor.TaskExecutor.run_command')
    def test_run_tests_mocked(self, mock_run_command):
        """Test running tests with mocked subprocess"""
        mock_run_command.return_value = (0, "10 passed in 1.23s", "")

        config = ExecutionConfig(
            run_tests_after_each_task=True,
            measure_coverage=False,
            verbose=False
        )
        executor = TaskExecutor(config)

        test_result = executor.run_tests()

        assert test_result.success is True
        assert test_result.passed == 10
        mock_run_command.assert_called_once()

    @patch('task_executor.TaskExecutor.run_command')
    def test_measure_coverage_mocked(self, mock_run_command):
        """Test coverage measurement with mocked data"""
        # Create mock coverage data
        coverage_data = {
            "totals": {
                "percent_covered": 85.5,
                "covered_lines": 171,
                "num_statements": 200
            },
            "files": {
                "module1.py": {
                    "summary": {"percent_covered": 90.0}
                }
            }
        }

        # Create temporary coverage.json
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, dir='.') as f:
            json.dump(coverage_data, f)
            coverage_file = f.name

        # Mock the run_command to do nothing
        mock_run_command.return_value = (0, "", "")

        try:
            config = ExecutionConfig(measure_coverage=True, verbose=False)
            executor = TaskExecutor(config)

            # Temporarily rename file to coverage.json
            import shutil
            shutil.move(coverage_file, "coverage.json")

            coverage_result = executor.measure_coverage()

            assert coverage_result is not None
            assert coverage_result.percent_covered == 85.5
            assert coverage_result.lines_covered == 171
            assert coverage_result.by_module["module1.py"] == 90.0

        finally:
            # Cleanup
            if Path("coverage.json").exists():
                Path("coverage.json").unlink()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
