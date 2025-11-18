#!/usr/bin/env python3
"""
Task Executor - Sequential task execution with test running and coverage reporting

This module provides a framework for executing related coding tasks in sequence
with automated test execution, coverage measurement, and consolidated reporting.
"""

import json
import subprocess
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import sys


class TaskStatus(Enum):
    """Status of a task execution"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskType(Enum):
    """Type of coding task"""
    REFACTOR = "refactor"
    TEST = "test"
    IMPLEMENTATION = "implementation"
    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"
    BUG_FIX = "bug_fix"


@dataclass
class TestResult:
    """Result of running tests"""
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration: float = 0.0
    output: str = ""
    success: bool = True
    error_details: Optional[str] = None

    @property
    def total(self) -> int:
        return self.passed + self.failed + self.skipped

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "total": self.total,
            "duration": self.duration,
            "success": self.success,
            "error_details": self.error_details
        }


@dataclass
class CoverageResult:
    """Result of coverage measurement"""
    percent_covered: float = 0.0
    lines_covered: int = 0
    lines_total: int = 0
    branches_covered: int = 0
    branches_total: int = 0
    by_module: Dict[str, float] = field(default_factory=dict)
    delta: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "percent_covered": round(self.percent_covered, 2),
            "lines_covered": self.lines_covered,
            "lines_total": self.lines_total,
            "branches_covered": self.branches_covered,
            "branches_total": self.branches_total,
            "by_module": {k: round(v, 2) for k, v in self.by_module.items()},
            "delta": round(self.delta, 2) if self.delta else None
        }


@dataclass
class TaskResult:
    """Result of executing a single task"""
    task_name: str
    task_type: TaskType
    status: TaskStatus
    duration: float = 0.0
    test_result: Optional[TestResult] = None
    coverage_result: Optional[CoverageResult] = None
    error: Optional[str] = None
    checkpoint_commit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_name": self.task_name,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "duration": round(self.duration, 2),
            "test_result": self.test_result.to_dict() if self.test_result else None,
            "coverage_result": self.coverage_result.to_dict() if self.coverage_result else None,
            "error": self.error,
            "checkpoint_commit": self.checkpoint_commit
        }


@dataclass
class Task:
    """A single coding task to execute"""
    name: str
    description: str
    task_type: TaskType
    executor: Callable[[], bool]  # Function that executes the task
    dependencies: List[str] = field(default_factory=list)
    run_tests: bool = True
    measure_coverage: bool = True


@dataclass
class ExecutionConfig:
    """Configuration for task execution"""
    # Test settings
    run_tests_after_each_task: bool = True
    run_tests_at_end: bool = True
    test_command: str = "pytest"
    test_paths: List[str] = field(default_factory=lambda: ["tests/"])
    stop_on_test_failure: bool = True

    # Coverage settings
    measure_coverage: bool = True
    coverage_command: str = "pytest --cov=. --cov-report=json --cov-report=term-missing"
    coverage_threshold: float = 80.0
    track_coverage_delta: bool = True

    # Rollback settings
    enable_rollback: bool = False
    create_checkpoints: bool = True
    checkpoint_prefix: str = "task-exec"

    # Execution settings
    verbose: bool = True
    continue_on_error: bool = False


class TaskExecutor:
    """Executes tasks in sequence with test running and coverage reporting"""

    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()
        self.tasks: List[Task] = []
        self.results: List[TaskResult] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.initial_coverage: Optional[CoverageResult] = None

    def add_task(self, task: Task) -> None:
        """Add a task to the execution queue"""
        self.tasks.append(task)

    def add_tasks(self, tasks: List[Task]) -> None:
        """Add multiple tasks to the execution queue"""
        self.tasks.extend(tasks)

    def run_command(self, command: str, cwd: Optional[str] = None) -> tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timeout after 5 minutes"
        except Exception as e:
            return -1, "", str(e)

    def run_tests(self) -> TestResult:
        """Run tests and parse results"""
        test_result = TestResult()

        if not self.config.run_tests_after_each_task:
            return test_result

        command = f"{self.config.test_command} {' '.join(self.config.test_paths)} -v"

        if self.config.verbose:
            print(f"Running tests: {command}")

        start = time.time()
        exit_code, stdout, stderr = self.run_command(command)
        test_result.duration = time.time() - start
        test_result.output = stdout + stderr

        # Parse pytest output
        if exit_code == 0:
            test_result.success = True
        else:
            test_result.success = False
            test_result.error_details = stderr

        # Try to parse test counts from output
        for line in stdout.split('\n'):
            if 'passed' in line.lower():
                try:
                    # Parse lines like "10 passed, 2 failed, 1 skipped in 1.23s"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'passed' in part and i > 0:
                            test_result.passed = int(parts[i-1])
                        elif 'failed' in part and i > 0:
                            test_result.failed = int(parts[i-1])
                        elif 'skipped' in part and i > 0:
                            test_result.skipped = int(parts[i-1])
                except (ValueError, IndexError):
                    pass

        return test_result

    def measure_coverage(self) -> Optional[CoverageResult]:
        """Measure code coverage"""
        if not self.config.measure_coverage:
            return None

        coverage_result = CoverageResult()

        if self.config.verbose:
            print(f"Measuring coverage: {self.config.coverage_command}")

        exit_code, stdout, stderr = self.run_command(self.config.coverage_command)

        # Try to parse coverage.json if it exists
        coverage_file = Path("coverage.json")
        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    data = json.load(f)

                totals = data.get("totals", {})
                coverage_result.percent_covered = totals.get("percent_covered", 0.0)
                coverage_result.lines_covered = totals.get("covered_lines", 0)
                coverage_result.lines_total = totals.get("num_statements", 0)

                # Parse per-module coverage
                files = data.get("files", {})
                for filepath, file_data in files.items():
                    summary = file_data.get("summary", {})
                    percent = summary.get("percent_covered", 0.0)
                    coverage_result.by_module[filepath] = percent

            except (json.JSONDecodeError, KeyError) as e:
                if self.config.verbose:
                    print(f"Warning: Could not parse coverage.json: {e}")
        else:
            # Try to parse from terminal output
            for line in stdout.split('\n'):
                if 'TOTAL' in line:
                    try:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if '%' in part:
                                coverage_result.percent_covered = float(part.rstrip('%'))
                                break
                    except (ValueError, IndexError):
                        pass

        return coverage_result

    def create_checkpoint(self, task_name: str) -> Optional[str]:
        """Create a git checkpoint commit"""
        if not self.config.create_checkpoints:
            return None

        # Add all changes
        self.run_command("git add .")

        # Create commit
        commit_msg = f"{self.config.checkpoint_prefix}: {task_name}"
        exit_code, stdout, stderr = self.run_command(f'git commit -m "{commit_msg}"')

        if exit_code == 0:
            # Get commit hash
            exit_code, commit_hash, _ = self.run_command("git rev-parse HEAD")
            return commit_hash.strip()

        return None

    def rollback_checkpoint(self) -> bool:
        """Rollback to previous checkpoint"""
        if not self.config.enable_rollback:
            return False

        exit_code, _, _ = self.run_command("git reset --hard HEAD~1")
        return exit_code == 0

    def execute_task(self, task: Task) -> TaskResult:
        """Execute a single task"""
        result = TaskResult(
            task_name=task.name,
            task_type=task.task_type,
            status=TaskStatus.IN_PROGRESS
        )

        if self.config.verbose:
            print(f"\n{'='*60}")
            print(f"Executing task: {task.name}")
            print(f"Type: {task.task_type.value}")
            print(f"Description: {task.description}")
            print(f"{'='*60}")

        start = time.time()

        try:
            # Execute the task
            success = task.executor()

            if success:
                result.status = TaskStatus.COMPLETED
            else:
                result.status = TaskStatus.FAILED
                result.error = "Task executor returned False"

            # Create checkpoint if enabled
            if self.config.create_checkpoints and success:
                commit = self.create_checkpoint(task.name)
                result.checkpoint_commit = commit
                if self.config.verbose and commit:
                    print(f"Created checkpoint: {commit[:8]}")

            # Run tests if configured
            if task.run_tests and self.config.run_tests_after_each_task:
                test_result = self.run_tests()
                result.test_result = test_result

                if not test_result.success and self.config.stop_on_test_failure:
                    result.status = TaskStatus.FAILED
                    result.error = "Tests failed"

                    if self.config.enable_rollback:
                        if self.config.verbose:
                            print("Rolling back due to test failure...")
                        self.rollback_checkpoint()

            # Measure coverage if configured
            if task.measure_coverage and self.config.measure_coverage:
                coverage = self.measure_coverage()
                if coverage and self.config.track_coverage_delta and self.initial_coverage:
                    coverage.delta = coverage.percent_covered - self.initial_coverage.percent_covered
                result.coverage_result = coverage

                if self.config.verbose and coverage:
                    print(f"Coverage: {coverage.percent_covered:.2f}%", end="")
                    if coverage.delta is not None:
                        print(f" (Δ {coverage.delta:+.2f}%)")
                    else:
                        print()

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            if self.config.verbose:
                print(f"Error executing task: {e}")

            if self.config.enable_rollback:
                if self.config.verbose:
                    print("Rolling back due to error...")
                self.rollback_checkpoint()

        finally:
            result.duration = time.time() - start

        return result

    def validate_dependencies(self) -> bool:
        """Validate that all task dependencies are satisfied"""
        task_names = {task.name for task in self.tasks}

        for task in self.tasks:
            for dep in task.dependencies:
                if dep not in task_names:
                    print(f"Error: Task '{task.name}' depends on '{dep}' which doesn't exist")
                    return False

        return True

    def topological_sort(self) -> List[Task]:
        """Sort tasks by dependencies using topological sort"""
        # Build adjacency list
        graph: Dict[str, List[str]] = {task.name: task.dependencies for task in self.tasks}
        task_map = {task.name: task for task in self.tasks}

        # Kahn's algorithm
        in_degree = {task.name: len(task.dependencies) for task in self.tasks}
        queue = [name for name, degree in in_degree.items() if degree == 0]
        sorted_tasks = []

        while queue:
            current = queue.pop(0)
            sorted_tasks.append(task_map[current])

            # Find tasks that depend on current
            for task in self.tasks:
                if current in task.dependencies:
                    in_degree[task.name] -= 1
                    if in_degree[task.name] == 0:
                        queue.append(task.name)

        if len(sorted_tasks) != len(self.tasks):
            raise ValueError("Circular dependency detected in tasks")

        return sorted_tasks

    def execute_all(self) -> bool:
        """Execute all tasks in sequence"""
        if not self.tasks:
            print("No tasks to execute")
            return True

        # Validate dependencies
        if not self.validate_dependencies():
            return False

        # Sort tasks by dependencies
        try:
            sorted_tasks = self.topological_sort()
        except ValueError as e:
            print(f"Error: {e}")
            return False

        print(f"\n{'#'*60}")
        print(f"# Task Execution Started")
        print(f"# Total tasks: {len(sorted_tasks)}")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"{'#'*60}\n")

        self.start_time = time.time()

        # Measure initial coverage
        if self.config.measure_coverage and self.config.track_coverage_delta:
            if self.config.verbose:
                print("Measuring initial coverage...")
            self.initial_coverage = self.measure_coverage()
            if self.initial_coverage:
                print(f"Initial coverage: {self.initial_coverage.percent_covered:.2f}%\n")

        # Execute tasks
        all_success = True
        for i, task in enumerate(sorted_tasks, 1):
            if self.config.verbose:
                print(f"\nTask {i}/{len(sorted_tasks)}")

            result = self.execute_task(task)
            self.results.append(result)

            if result.status == TaskStatus.FAILED:
                all_success = False
                if not self.config.continue_on_error:
                    if self.config.verbose:
                        print(f"\nStopping execution due to task failure: {task.name}")
                    break

        self.end_time = time.time()

        # Run final tests if configured
        if self.config.run_tests_at_end:
            if self.config.verbose:
                print("\n" + "="*60)
                print("Running final test suite...")
                print("="*60)
            final_tests = self.run_tests()
            if self.config.verbose:
                print(f"Final tests: {final_tests.passed} passed, {final_tests.failed} failed")

        return all_success

    def generate_report(self) -> str:
        """Generate a consolidated execution report"""
        if not self.results:
            return "No tasks executed"

        # Calculate statistics
        total_tasks = len(self.results)
        successful = sum(1 for r in self.results if r.status == TaskStatus.COMPLETED)
        failed = sum(1 for r in self.results if r.status == TaskStatus.FAILED)
        total_duration = (self.end_time - self.start_time) if self.start_time and self.end_time else 0

        # Aggregate test results
        total_tests_passed = sum(r.test_result.passed for r in self.results if r.test_result)
        total_tests_failed = sum(r.test_result.failed for r in self.results if r.test_result)
        total_tests_skipped = sum(r.test_result.skipped for r in self.results if r.test_result)

        # Coverage summary
        final_coverage = None
        coverage_delta = None
        if self.results:
            for r in reversed(self.results):
                if r.coverage_result:
                    final_coverage = r.coverage_result
                    break

        if final_coverage and self.initial_coverage:
            coverage_delta = final_coverage.percent_covered - self.initial_coverage.percent_covered

        # Build report
        report = []
        report.append("="*70)
        report.append("TASK EXECUTION REPORT")
        report.append("="*70)
        report.append("")

        # Summary section
        report.append("SUMMARY")
        report.append("-"*70)
        report.append(f"Total tasks:      {total_tasks}")
        report.append(f"Successful:       {successful} ({successful/total_tasks*100:.1f}%)")
        report.append(f"Failed:           {failed} ({failed/total_tasks*100:.1f}%)")
        report.append(f"Total duration:   {total_duration:.2f} seconds")
        report.append("")

        # Task results section
        report.append("TASK RESULTS")
        report.append("-"*70)
        for i, result in enumerate(self.results, 1):
            status_icon = "✓" if result.status == TaskStatus.COMPLETED else "✗"
            report.append(f"\n{i}. {status_icon} {result.task_name}")
            report.append(f"   Type:     {result.task_type.value}")
            report.append(f"   Status:   {result.status.value}")
            report.append(f"   Duration: {result.duration:.2f}s")

            if result.test_result:
                tr = result.test_result
                report.append(f"   Tests:    {tr.passed} passed, {tr.failed} failed, {tr.skipped} skipped")

            if result.coverage_result:
                cr = result.coverage_result
                delta_str = f" (Δ {cr.delta:+.2f}%)" if cr.delta else ""
                report.append(f"   Coverage: {cr.percent_covered:.2f}%{delta_str}")

            if result.error:
                report.append(f"   Error:    {result.error}")

        report.append("")

        # Overall test results
        if total_tests_passed + total_tests_failed + total_tests_skipped > 0:
            report.append("OVERALL TEST RESULTS")
            report.append("-"*70)
            report.append(f"Total tests:  {total_tests_passed + total_tests_failed + total_tests_skipped}")
            report.append(f"Passed:       {total_tests_passed}")
            report.append(f"Failed:       {total_tests_failed}")
            report.append(f"Skipped:      {total_tests_skipped}")
            report.append("")

        # Coverage summary
        if final_coverage:
            report.append("COVERAGE SUMMARY")
            report.append("-"*70)
            if self.initial_coverage:
                report.append(f"Starting coverage: {self.initial_coverage.percent_covered:.2f}%")
            report.append(f"Final coverage:    {final_coverage.percent_covered:.2f}%")
            if coverage_delta is not None:
                report.append(f"Coverage delta:    {coverage_delta:+.2f}%")
            report.append("")

            if final_coverage.by_module:
                report.append("Coverage by module:")
                for module, percent in sorted(final_coverage.by_module.items(), key=lambda x: x[1], reverse=True):
                    report.append(f"  {module:40s} {percent:6.2f}%")
            report.append("")

        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-"*70)

        recommendations = []

        if failed > 0:
            recommendations.append("• Review and fix failed tasks before proceeding")

        if total_tests_failed > 0:
            recommendations.append("• Investigate and fix failing tests")

        if final_coverage and final_coverage.percent_covered < self.config.coverage_threshold:
            recommendations.append(f"• Coverage ({final_coverage.percent_covered:.2f}%) is below threshold ({self.config.coverage_threshold:.2f}%)")
            recommendations.append("• Consider adding more tests to improve coverage")

        if coverage_delta and coverage_delta < 0:
            recommendations.append("• Coverage decreased - review removed or changed tests")

        if successful == total_tasks and total_tests_failed == 0:
            recommendations.append("• All tasks completed successfully!")
            if final_coverage and final_coverage.percent_covered >= self.config.coverage_threshold:
                recommendations.append("• Coverage threshold met - ready for next phase")

        if not recommendations:
            recommendations.append("• No specific recommendations")

        for rec in recommendations:
            report.append(rec)

        report.append("")
        report.append("="*70)

        return "\n".join(report)

    def export_json(self, filepath: str) -> None:
        """Export execution results to JSON file"""
        data = {
            "summary": {
                "total_tasks": len(self.results),
                "successful": sum(1 for r in self.results if r.status == TaskStatus.COMPLETED),
                "failed": sum(1 for r in self.results if r.status == TaskStatus.FAILED),
                "duration": (self.end_time - self.start_time) if self.start_time and self.end_time else 0
            },
            "tasks": [result.to_dict() for result in self.results],
            "initial_coverage": self.initial_coverage.to_dict() if self.initial_coverage else None,
            "config": asdict(self.config)
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def example_refactor_task() -> bool:
    """Example task: refactor a function"""
    print("  → Refactoring function...")
    # Actual refactoring code would go here
    time.sleep(0.5)  # Simulate work
    return True


def example_test_task() -> bool:
    """Example task: write tests"""
    print("  → Writing tests...")
    # Actual test writing code would go here
    time.sleep(0.5)  # Simulate work
    return True


if __name__ == "__main__":
    # Example usage
    print("Task Executor - Example Usage\n")

    # Create configuration
    config = ExecutionConfig(
        run_tests_after_each_task=True,
        measure_coverage=True,
        create_checkpoints=False,  # Disable for demo
        verbose=True
    )

    # Create executor
    executor = TaskExecutor(config)

    # Add tasks
    tasks = [
        Task(
            name="Refactor parse_data function",
            description="Add type hints and improve error handling",
            task_type=TaskType.REFACTOR,
            executor=example_refactor_task,
            run_tests=True,
            measure_coverage=True
        ),
        Task(
            name="Write tests for parse_data",
            description="Add unit tests covering edge cases",
            task_type=TaskType.TEST,
            executor=example_test_task,
            dependencies=["Refactor parse_data function"],
            run_tests=True,
            measure_coverage=True
        ),
        Task(
            name="Refactor validate_data function",
            description="Extract validation logic into separate functions",
            task_type=TaskType.REFACTOR,
            executor=example_refactor_task,
            run_tests=True,
            measure_coverage=True
        ),
    ]

    executor.add_tasks(tasks)

    # Execute all tasks
    success = executor.execute_all()

    # Generate and print report
    report = executor.generate_report()
    print("\n" + report)

    # Export to JSON
    executor.export_json("task_execution_report.json")
    print("\nReport exported to task_execution_report.json")

    sys.exit(0 if success else 1)
