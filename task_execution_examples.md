# Task Execution Skill - Usage Examples

This document provides practical examples of using the task execution skill to group and execute related coding tasks with automated testing and coverage reporting.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Refactoring Multiple Functions](#refactoring-multiple-functions)
3. [Writing Tests with Coverage Tracking](#writing-tests-with-coverage-tracking)
4. [Implementing a Feature](#implementing-a-feature)
5. [Code Quality Improvements](#code-quality-improvements)
6. [Advanced: Custom Task Executors](#advanced-custom-task-executors)
7. [Integration with CI/CD](#integration-with-cicd)

---

## Basic Usage

### Simple Task Execution

```python
from task_executor import TaskExecutor, Task, TaskType, ExecutionConfig

# Create a simple configuration
config = ExecutionConfig(
    run_tests_after_each_task=True,
    measure_coverage=False,
    verbose=True
)

# Create executor
executor = TaskExecutor(config)

# Define a simple task
def fix_typo():
    print("Fixing typo in documentation...")
    # Actual fix here
    return True

# Add task
task = Task(
    name="Fix typo in README",
    description="Correct spelling error in introduction",
    task_type=TaskType.DOCUMENTATION,
    executor=fix_typo,
    run_tests=False  # No tests needed for docs
)

executor.add_task(task)

# Execute
executor.execute_all()

# Print report
print(executor.generate_report())
```

---

## Refactoring Multiple Functions

### Example: Refactor Data Processing Module

```python
from task_executor import TaskExecutor, Task, TaskType, ExecutionConfig
from pathlib import Path

def refactor_parse_data():
    """Refactor parse_data to use type hints"""
    # Read the file
    content = Path("data_processor.py").read_text()

    # Apply refactoring (simplified example)
    old_code = """
def parse_data(data):
    result = []
    for item in data:
        result.append(item.strip())
    return result
"""

    new_code = """
def parse_data(data: List[str]) -> List[str]:
    \"\"\"Parse and clean data items.

    Args:
        data: List of raw data strings

    Returns:
        List of cleaned data strings
    \"\"\"
    return [item.strip() for item in data]
"""

    content = content.replace(old_code, new_code)
    Path("data_processor.py").write_text(content)
    return True


def refactor_validate_data():
    """Extract validation logic"""
    # Read the file
    content = Path("data_processor.py").read_text()

    # Extract validation into separate functions
    old_code = """
def validate_data(data):
    if not data:
        raise ValueError("Empty data")
    if len(data) > 1000:
        raise ValueError("Too much data")
    return True
"""

    new_code = """
def _check_not_empty(data: List[str]) -> None:
    if not data:
        raise ValueError("Empty data")

def _check_size_limit(data: List[str], limit: int = 1000) -> None:
    if len(data) > limit:
        raise ValueError(f"Data size {len(data)} exceeds limit {limit}")

def validate_data(data: List[str]) -> bool:
    \"\"\"Validate data meets requirements.

    Args:
        data: Data to validate

    Returns:
        True if valid

    Raises:
        ValueError: If data is invalid
    \"\"\"
    _check_not_empty(data)
    _check_size_limit(data)
    return True
"""

    content = content.replace(old_code, new_code)
    Path("data_processor.py").write_text(content)
    return True


def refactor_transform_data():
    """Simplify transform_data nested loops"""
    # Refactoring implementation here
    return True


# Create configuration with checkpoints
config = ExecutionConfig(
    run_tests_after_each_task=True,
    measure_coverage=True,
    create_checkpoints=True,
    checkpoint_prefix="refactor",
    stop_on_test_failure=True,
    verbose=True
)

executor = TaskExecutor(config)

# Add refactoring tasks
tasks = [
    Task(
        name="Refactor parse_data",
        description="Add type hints and improve readability",
        task_type=TaskType.REFACTOR,
        executor=refactor_parse_data
    ),
    Task(
        name="Refactor validate_data",
        description="Extract validation logic into separate functions",
        task_type=TaskType.REFACTOR,
        executor=refactor_validate_data
    ),
    Task(
        name="Refactor transform_data",
        description="Simplify nested loops using comprehensions",
        task_type=TaskType.REFACTOR,
        executor=refactor_transform_data
    ),
]

executor.add_tasks(tasks)

# Execute all refactoring tasks
success = executor.execute_all()

# Generate report
report = executor.generate_report()
print(report)

# Export to JSON
executor.export_json("refactoring_report.json")
```

**Expected Output:**
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

---

## Writing Tests with Coverage Tracking

### Example: Comprehensive Test Suite for Authentication Module

```python
from task_executor import TaskExecutor, Task, TaskType, ExecutionConfig
from pathlib import Path

def write_login_tests():
    """Write tests for login function"""
    test_code = '''
def test_login_success(auth_client):
    """Test successful login"""
    response = auth_client.login("user@example.com", "password123")
    assert response.success is True
    assert response.token is not None

def test_login_invalid_email(auth_client):
    """Test login with invalid email"""
    response = auth_client.login("invalid-email", "password123")
    assert response.success is False
    assert "Invalid email" in response.error

def test_login_wrong_password(auth_client):
    """Test login with wrong password"""
    response = auth_client.login("user@example.com", "wrongpass")
    assert response.success is False
    assert "Invalid credentials" in response.error

def test_login_locked_account(auth_client):
    """Test login with locked account"""
    response = auth_client.login("locked@example.com", "password123")
    assert response.success is False
    assert "Account locked" in response.error
'''

    # Append to test file
    with open("tests/test_auth.py", "a") as f:
        f.write(test_code)

    return True


def write_logout_tests():
    """Write tests for logout function"""
    test_code = '''
def test_logout_success(auth_client, logged_in_user):
    """Test successful logout"""
    response = auth_client.logout(logged_in_user.token)
    assert response.success is True

def test_logout_invalid_token(auth_client):
    """Test logout with invalid token"""
    response = auth_client.logout("invalid-token")
    assert response.success is False
    assert "Invalid token" in response.error
'''

    with open("tests/test_auth.py", "a") as f:
        f.write(test_code)

    return True


def write_register_tests():
    """Write tests for register function"""
    test_code = '''
def test_register_success(auth_client):
    """Test successful registration"""
    response = auth_client.register(
        email="newuser@example.com",
        password="SecurePass123!",
        name="New User"
    )
    assert response.success is True
    assert response.user_id is not None

def test_register_duplicate_email(auth_client):
    """Test registration with duplicate email"""
    response = auth_client.register(
        email="existing@example.com",
        password="SecurePass123!",
        name="Duplicate User"
    )
    assert response.success is False
    assert "Email already exists" in response.error

def test_register_weak_password(auth_client):
    """Test registration with weak password"""
    response = auth_client.register(
        email="newuser@example.com",
        password="weak",
        name="New User"
    )
    assert response.success is False
    assert "Password too weak" in response.error
'''

    with open("tests/test_auth.py", "a") as f:
        f.write(test_code)

    return True


# Configure for test writing with strict coverage requirements
config = ExecutionConfig(
    run_tests_after_each_task=True,
    measure_coverage=True,
    coverage_threshold=90.0,
    track_coverage_delta=True,
    stop_on_test_failure=True,
    verbose=True
)

executor = TaskExecutor(config)

# Add test writing tasks
tasks = [
    Task(
        name="Write login tests",
        description="Comprehensive tests for login function",
        task_type=TaskType.TEST,
        executor=write_login_tests
    ),
    Task(
        name="Write logout tests",
        description="Tests for logout function",
        task_type=TaskType.TEST,
        executor=write_logout_tests,
        dependencies=["Write login tests"]
    ),
    Task(
        name="Write register tests",
        description="Tests for user registration",
        task_type=TaskType.TEST,
        executor=write_register_tests
    ),
]

executor.add_tasks(tasks)

# Execute all tasks
executor.execute_all()

# Generate and save report
report = executor.generate_report()
print(report)

# Export detailed JSON report
executor.export_json("test_coverage_report.json")
```

---

## Implementing a Feature

### Example: Add User Profile Editing Feature

```python
from task_executor import TaskExecutor, Task, TaskType, ExecutionConfig

def implement_profile_model():
    """Add profile update methods to User model"""
    # Implementation here
    return True

def add_profile_validation():
    """Add validation for profile fields"""
    # Implementation here
    return True

def create_profile_api():
    """Create API endpoint for profile updates"""
    # Implementation here
    return True

def write_validation_tests():
    """Write tests for validation logic"""
    # Implementation here
    return True

def write_api_tests():
    """Write integration tests for API"""
    # Implementation here
    return True

def add_error_handling():
    """Add comprehensive error handling"""
    # Implementation here
    return True


# Configuration for feature implementation
config = ExecutionConfig(
    run_tests_after_each_task=False,  # Only run after test tasks
    run_tests_at_end=True,
    measure_coverage=True,
    create_checkpoints=True,
    stop_on_test_failure=True,
    verbose=True
)

executor = TaskExecutor(config)

# Define feature implementation tasks with dependencies
tasks = [
    Task(
        name="Implement profile model updates",
        description="Add update_profile and validate_profile methods",
        task_type=TaskType.IMPLEMENTATION,
        executor=implement_profile_model,
        run_tests=False  # No tests yet
    ),
    Task(
        name="Add profile validation",
        description="Implement field validation logic",
        task_type=TaskType.IMPLEMENTATION,
        executor=add_profile_validation,
        dependencies=["Implement profile model updates"],
        run_tests=False
    ),
    Task(
        name="Write validation tests",
        description="Unit tests for validation logic",
        task_type=TaskType.TEST,
        executor=write_validation_tests,
        dependencies=["Add profile validation"],
        run_tests=True  # Run tests after this task
    ),
    Task(
        name="Create profile API endpoint",
        description="Add PUT /api/profile endpoint",
        task_type=TaskType.IMPLEMENTATION,
        executor=create_profile_api,
        dependencies=["Add profile validation"],
        run_tests=False
    ),
    Task(
        name="Write API integration tests",
        description="Integration tests for profile API",
        task_type=TaskType.TEST,
        executor=write_api_tests,
        dependencies=["Create profile API endpoint"],
        run_tests=True
    ),
    Task(
        name="Add error handling",
        description="Comprehensive error handling for edge cases",
        task_type=TaskType.IMPLEMENTATION,
        executor=add_error_handling,
        dependencies=["Write API integration tests"],
        run_tests=True
    ),
]

executor.add_tasks(tasks)

# Execute the feature implementation
success = executor.execute_all()

# Generate report
report = executor.generate_report()
print(report)

if success:
    print("\n✓ Feature implementation complete!")
    print("  Ready for code review and deployment")
else:
    print("\n✗ Feature implementation failed")
    print("  Review the report above for details")
```

---

## Code Quality Improvements

### Example: Improve Code Quality Across Module

```python
from task_executor import TaskExecutor, Task, TaskType, ExecutionConfig

def add_type_hints():
    """Add type hints to all functions"""
    # Implementation
    return True

def add_docstrings():
    """Add comprehensive docstrings"""
    # Implementation
    return True

def format_code():
    """Format code with black"""
    import subprocess
    result = subprocess.run(["black", "src/"], capture_output=True)
    return result.returncode == 0

def fix_linting_issues():
    """Fix all flake8 issues"""
    # Implementation
    return True

def add_logging():
    """Add logging statements"""
    # Implementation
    return True


config = ExecutionConfig(
    run_tests_after_each_task=True,
    measure_coverage=False,  # Not needed for code quality tasks
    create_checkpoints=True,
    verbose=True
)

executor = TaskExecutor(config)

tasks = [
    Task(
        name="Add type hints",
        description="Add type hints to all function signatures",
        task_type=TaskType.CODE_QUALITY,
        executor=add_type_hints
    ),
    Task(
        name="Add docstrings",
        description="Add Google-style docstrings",
        task_type=TaskType.CODE_QUALITY,
        executor=add_docstrings,
        dependencies=["Add type hints"]
    ),
    Task(
        name="Format code",
        description="Format with black",
        task_type=TaskType.CODE_QUALITY,
        executor=format_code
    ),
    Task(
        name="Fix linting issues",
        description="Fix all flake8 warnings",
        task_type=TaskType.CODE_QUALITY,
        executor=fix_linting_issues,
        dependencies=["Format code"]
    ),
    Task(
        name="Add logging",
        description="Add structured logging",
        task_type=TaskType.CODE_QUALITY,
        executor=add_logging
    ),
]

executor.add_tasks(tasks)
executor.execute_all()

print(executor.generate_report())
```

---

## Advanced: Custom Task Executors

### Example: Dynamic Task Execution with File Reading

```python
from task_executor import TaskExecutor, Task, TaskType, ExecutionConfig
from pathlib import Path
import ast

def create_dynamic_refactoring_tasks(module_path: str) -> List[Task]:
    """Analyze a Python module and create refactoring tasks"""

    content = Path(module_path).read_text()
    tree = ast.parse(content)

    tasks = []

    # Find all functions without type hints
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if function has type hints
            has_hints = any(arg.annotation for arg in node.args.args)
            has_return_hint = node.returns is not None

            if not has_hints or not has_return_hint:
                # Create a task to add type hints
                def add_hints_to_function(func_name=node.name):
                    # Implementation to add type hints
                    return True

                task = Task(
                    name=f"Add type hints to {node.name}",
                    description=f"Add parameter and return type hints to {node.name}",
                    task_type=TaskType.REFACTOR,
                    executor=add_hints_to_function
                )
                tasks.append(task)

    return tasks


# Use dynamic task creation
config = ExecutionConfig(verbose=True, run_tests_after_each_task=True)
executor = TaskExecutor(config)

# Dynamically create tasks based on code analysis
tasks = create_dynamic_refactoring_tasks("src/data_processor.py")
executor.add_tasks(tasks)

# Execute
executor.execute_all()
print(executor.generate_report())
```

---

## Integration with CI/CD

### Example: Export Results for CI Pipeline

```python
from task_executor import TaskExecutor, Task, TaskType, ExecutionConfig
import sys

def main():
    config = ExecutionConfig(
        run_tests_after_each_task=True,
        measure_coverage=True,
        coverage_threshold=80.0,
        stop_on_test_failure=True,
        verbose=True
    )

    executor = TaskExecutor(config)

    # Add your tasks here
    # ...

    # Execute
    success = executor.execute_all()

    # Generate reports
    print(executor.generate_report())

    # Export JSON for CI tools
    executor.export_json("task_execution_report.json")

    # Export in JUnit format (custom implementation)
    # export_junit_xml(executor.results, "junit_report.xml")

    # Update coverage badge (custom implementation)
    # update_coverage_badge(executor.results)

    # Exit with appropriate code for CI
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

### Example CI Configuration (GitHub Actions)

```yaml
name: Task Execution

on: [push, pull_request]

jobs:
  execute-tasks:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Execute tasks
      run: python task_execution_script.py

    - name: Upload coverage report
      uses: codecov/codecov-action@v2
      with:
        files: ./coverage.json

    - name: Upload task report
      uses: actions/upload-artifact@v2
      with:
        name: task-execution-report
        path: task_execution_report.json

    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v5
      with:
        script: |
          const fs = require('fs');
          const report = fs.readFileSync('task_execution_report.json', 'utf8');
          const data = JSON.parse(report);

          const comment = `## Task Execution Report

          - Total tasks: ${data.summary.total_tasks}
          - Successful: ${data.summary.successful}
          - Failed: ${data.summary.failed}
          - Duration: ${data.summary.duration.toFixed(2)}s
          `;

          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
```

---

## Tips and Best Practices

### 1. Task Granularity
- Keep tasks focused on a single responsibility
- Break complex tasks into smaller subtasks
- Use dependencies to define execution order

### 2. Test Strategy
- Run tests after implementation tasks
- Run full suite at the end for integration verification
- Use `stop_on_test_failure` to catch issues early

### 3. Coverage Goals
- Set realistic coverage thresholds
- Track coverage delta to ensure improvements
- Focus on critical code paths first

### 4. Error Handling
- Enable rollback for experimental changes
- Use checkpoints for incremental progress
- Review error messages in the consolidated report

### 5. Performance
- Disable verbose mode for large task sets
- Consider parallel execution for independent tasks (future feature)
- Use test selection to run only affected tests

---

## Troubleshooting

### Tests not running
- Check that test_command is correct
- Verify test_paths point to valid directories
- Ensure pytest is installed

### Coverage not measured
- Verify coverage_command includes --cov flags
- Check that coverage.json is being generated
- Install pytest-cov if missing

### Tasks failing
- Review error messages in the report
- Check task dependencies are correct
- Verify executor functions return boolean values

### Checkpoints not created
- Ensure git repository is initialized
- Check that create_checkpoints is True
- Verify no uncommitted changes before execution

---

## Next Steps

- Explore parallel task execution (future feature)
- Integrate with your preferred CI/CD platform
- Customize report formatting
- Add custom metrics and validations
- Create reusable task templates

For more information, see:
- `task_execution_skill.md` - Skill definition
- `task_executor.py` - Implementation details
- `tests/test_task_executor.py` - Test suite
