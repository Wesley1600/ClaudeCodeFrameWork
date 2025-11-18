# Task Execution Skill

A comprehensive skill for grouping related coding tasks and executing them in sequence with automated test execution, coverage measurement, and consolidated reporting.

## Overview

The Task Execution Skill helps you efficiently manage and execute batches of related coding tasks such as:
- Refactoring multiple functions
- Writing comprehensive test suites
- Implementing features with multiple components
- Improving code quality across modules
- Running tests and tracking coverage automatically

## Components

### 1. Skill Definition (`task_execution_skill.md`)
Complete skill specification including:
- Purpose and use cases
- Configuration options
- Workflow steps
- Integration with tools
- Best practices

### 2. Implementation (`task_executor.py`)
Python module providing:
- `TaskExecutor`: Main execution engine
- `Task`: Task definition with dependencies
- `ExecutionConfig`: Configuration options
- `TestResult`, `CoverageResult`: Result types
- Report generation and JSON export

### 3. Examples (`task_execution_examples.md`)
Practical examples including:
- Basic usage
- Refactoring workflows
- Test writing with coverage
- Feature implementation
- Code quality improvements
- CI/CD integration

### 4. Tests (`tests/test_task_executor.py`)
Comprehensive test suite covering:
- Task execution
- Dependency management
- Report generation
- Error handling
- Integration scenarios

## Quick Start

### Installation

```bash
# Install dependencies
pip install pytest pytest-cov

# Clone or download the skill files
# - task_executor.py
# - task_execution_skill.md
# - task_execution_examples.md
```

### Basic Usage

```python
from task_executor import TaskExecutor, Task, TaskType, ExecutionConfig

# Configure execution
config = ExecutionConfig(
    run_tests_after_each_task=True,
    measure_coverage=True,
    verbose=True
)

# Create executor
executor = TaskExecutor(config)

# Define tasks
def refactor_function():
    # Your refactoring code here
    return True

task = Task(
    name="Refactor parse_data",
    description="Add type hints and improve readability",
    task_type=TaskType.REFACTOR,
    executor=refactor_function
)

# Add and execute
executor.add_task(task)
executor.execute_all()

# Generate report
print(executor.generate_report())
```

## Features

### ✓ Sequential Task Execution
- Execute tasks in order with dependency management
- Topological sorting for complex dependencies
- Stop on failure or continue on error

### ✓ Automated Test Running
- Run tests after each task or at the end
- Parse test results automatically
- Stop execution on test failures

### ✓ Coverage Measurement
- Measure code coverage automatically
- Track coverage delta for each task
- Set coverage thresholds

### ✓ Git Checkpoints
- Create git commits after each task
- Enable rollback on failures
- Track progress with commit history

### ✓ Consolidated Reporting
- Detailed execution reports
- Test and coverage summaries
- Recommendations based on results
- JSON export for CI/CD integration

## Configuration Options

```python
ExecutionConfig(
    # Test settings
    run_tests_after_each_task=True,
    run_tests_at_end=True,
    test_command="pytest",
    test_paths=["tests/"],
    stop_on_test_failure=True,

    # Coverage settings
    measure_coverage=True,
    coverage_command="pytest --cov=. --cov-report=json",
    coverage_threshold=80.0,
    track_coverage_delta=True,

    # Rollback settings
    enable_rollback=False,
    create_checkpoints=True,
    checkpoint_prefix="task-exec",

    # Execution settings
    verbose=True,
    continue_on_error=False
)
```

## Task Types

- `REFACTOR`: Code refactoring tasks
- `TEST`: Writing or updating tests
- `IMPLEMENTATION`: New feature implementation
- `CODE_QUALITY`: Linting, formatting, type hints
- `DOCUMENTATION`: Documentation updates
- `BUG_FIX`: Bug fixes

## Example Report

```
======================================================================
TASK EXECUTION REPORT
======================================================================

SUMMARY
----------------------------------------------------------------------
Total tasks:      3
Successful:       3 (100.0%)
Failed:           0 (0.0%)
Total duration:   5.43 seconds

TASK RESULTS
----------------------------------------------------------------------

1. ✓ Refactor parse_data
   Type:     refactor
   Status:   completed
   Duration: 1.82s
   Tests:    45 passed, 0 failed, 0 skipped
   Coverage: 87.50% (Δ +2.30%)

2. ✓ Refactor validate_data
   Type:     refactor
   Status:   completed
   Duration: 1.91s
   Tests:    48 passed, 0 failed, 0 skipped
   Coverage: 89.20% (Δ +1.70%)

3. ✓ Refactor transform_data
   Type:     refactor
   Status:   completed
   Duration: 1.70s
   Tests:    51 passed, 0 failed, 0 skipped
   Coverage: 90.50% (Δ +1.30%)

OVERALL TEST RESULTS
----------------------------------------------------------------------
Total tests:  144
Passed:       144
Failed:       0
Skipped:      0

COVERAGE SUMMARY
----------------------------------------------------------------------
Starting coverage: 85.20%
Final coverage:    90.50%
Coverage delta:    +5.30%

RECOMMENDATIONS
----------------------------------------------------------------------
• All tasks completed successfully!
• Coverage threshold met - ready for next phase

======================================================================
```

## Running Tests

```bash
# Run the test suite
pytest tests/test_task_executor.py -v

# Run with coverage
pytest tests/test_task_executor.py --cov=task_executor --cov-report=term-missing

# Run the example
python task_executor.py
```

## Use Cases

### 1. Refactoring Sprint
Group multiple refactoring tasks and execute them with test verification after each change.

### 2. Test Coverage Drive
Write tests for multiple functions while tracking coverage improvements.

### 3. Feature Implementation
Break down a feature into sequential tasks with testing at key milestones.

### 4. Code Quality Improvements
Systematically improve code quality with type hints, docstrings, and formatting.

### 5. CI/CD Integration
Export results to JSON for integration with CI/CD pipelines.

## Advanced Features

### Dependency Management
```python
tasks = [
    Task("Task A", "First", TaskType.REFACTOR, task_a),
    Task("Task B", "Second", TaskType.REFACTOR, task_b,
         dependencies=["Task A"]),
    Task("Task C", "Third", TaskType.REFACTOR, task_c,
         dependencies=["Task A", "Task B"]),
]
```

### Custom Test Commands
```python
config = ExecutionConfig(
    test_command="pytest -v --tb=short",
    coverage_command="pytest --cov=src --cov-report=html"
)
```

### JSON Export
```python
executor.execute_all()
executor.export_json("results.json")
```

## Best Practices

1. **Keep Tasks Focused**: Each task should do one thing well
2. **Define Dependencies**: Specify task order explicitly
3. **Test Incrementally**: Run tests frequently to catch issues early
4. **Track Coverage**: Monitor coverage changes to maintain quality
5. **Use Checkpoints**: Enable git commits for easy rollback
6. **Review Reports**: Use consolidated reports to identify patterns

## Troubleshooting

### Tests Not Running
- Verify `test_command` is correct (default: `pytest`)
- Check `test_paths` points to your test directory
- Ensure pytest is installed: `pip install pytest`

### Coverage Not Measured
- Install pytest-cov: `pip install pytest-cov`
- Verify `coverage_command` includes `--cov` flags
- Check that `coverage.json` is generated

### Tasks Failing
- Review error messages in the report
- Check task dependencies are satisfied
- Verify executor functions return boolean values

## Contributing

To extend the Task Execution Skill:

1. Add new task types to `TaskType` enum
2. Implement custom result parsers for different test frameworks
3. Add new report formats (JUnit XML, HTML, etc.)
4. Extend with parallel task execution
5. Add support for remote test execution

## License

This skill is part of the ClaudeCodeFrameWork project.

## Documentation

- [Skill Definition](task_execution_skill.md) - Complete skill specification
- [Implementation](task_executor.py) - Source code with detailed comments
- [Examples](task_execution_examples.md) - Practical usage examples
- [Tests](tests/test_task_executor.py) - Test suite

## Support

For issues or questions:
- Review the examples in `task_execution_examples.md`
- Check the test suite for usage patterns
- Consult the skill definition for configuration details

---

**Version:** 1.0.0
**Last Updated:** 2025-11-18
**Status:** Production Ready
