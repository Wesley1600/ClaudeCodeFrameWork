# Task Execution Skill

## Skill Definition

**Name:** `task-execution`

**Description:** Groups related coding tasks (refactoring, testing, code generation) and executes them in sequence with automated test execution, coverage measurement, and consolidated reporting.

**Location:** user

---

## Purpose

This skill helps you efficiently manage and execute batches of related coding tasks with:
- Sequential task execution with dependency management
- Automated test running after each task or batch
- Code coverage measurement and tracking
- Consolidated reporting of all results
- Rollback capability on failures

## When to Use This Skill

Invoke this skill when you need to:
- Execute multiple related refactoring tasks
- Write tests for multiple functions/modules
- Implement a feature that requires multiple sequential changes
- Run tests and track coverage across multiple changes
- Ensure each change passes tests before proceeding to the next

## How It Works

### 1. Task Definition Phase

When you invoke this skill, it will help you:
- Define a list of related tasks to execute
- Specify dependencies between tasks
- Configure test and coverage settings
- Set up rollback behavior on failures

### 2. Task Execution Phase

For each task in sequence:
- Execute the task (refactor, write tests, implement feature)
- Run tests (if configured)
- Measure coverage (if configured)
- Record results
- Proceed to next task or stop on failure

### 3. Reporting Phase

At the end, generate a consolidated report with:
- Summary of all tasks executed
- Test results for each task
- Coverage metrics (before/after for each task)
- Overall success/failure status
- Recommendations for next steps

---

## Task Types Supported

### 1. Refactor Tasks
- Rename functions/variables
- Extract methods
- Simplify complex functions
- Improve code structure

### 2. Test Tasks
- Write unit tests
- Write integration tests
- Add edge case tests
- Improve test coverage

### 3. Implementation Tasks
- Add new functions
- Implement features
- Fix bugs
- Update documentation

### 4. Code Quality Tasks
- Add type hints
- Add docstrings
- Format code
- Fix linting issues

---

## Configuration Options

### Test Execution
```python
{
  "run_tests_after_each_task": true,  # Run tests after each individual task
  "run_tests_at_end": true,           # Run full test suite at end
  "test_command": "pytest",           # Command to run tests
  "test_paths": ["tests/"],           # Paths to test files
  "stop_on_test_failure": true        # Stop execution if tests fail
}
```

### Coverage Measurement
```python
{
  "measure_coverage": true,           # Measure code coverage
  "coverage_command": "pytest --cov=. --cov-report=json",
  "coverage_threshold": 80,           # Minimum coverage percentage
  "track_coverage_delta": true        # Track coverage changes per task
}
```

### Rollback Behavior
```python
{
  "enable_rollback": true,            # Enable git rollback on failures
  "create_checkpoints": true,         # Create git commits after each task
  "checkpoint_prefix": "task-exec"    # Prefix for checkpoint commits
}
```

---

## Usage Examples

### Example 1: Refactor Multiple Functions
```
User: "I need to refactor the data processing functions in utils.py"

Skill invocation:
1. Identify functions to refactor: parse_data, validate_data, transform_data
2. Create tasks:
   - Task 1: Refactor parse_data to use type hints
   - Task 2: Refactor validate_data to extract validation logic
   - Task 3: Refactor transform_data to simplify nested loops
3. Configure: Run tests after each task, measure coverage
4. Execute tasks in sequence
5. Generate report
```

### Example 2: Write Tests for Multiple Modules
```
User: "Write comprehensive tests for the authentication module"

Skill invocation:
1. Identify functions needing tests: login, logout, register, reset_password
2. Create tasks:
   - Task 1: Write tests for login function
   - Task 2: Write tests for logout function
   - Task 3: Write tests for register function
   - Task 4: Write tests for reset_password function
3. Configure: Measure coverage delta, target 90% coverage
4. Execute tasks in sequence
5. Report coverage improvements
```

### Example 3: Implement Feature with Tests
```
User: "Implement user profile editing with validation and tests"

Skill invocation:
1. Break down feature into tasks:
   - Task 1: Create profile model update functions
   - Task 2: Add validation logic
   - Task 3: Write unit tests for validation
   - Task 4: Write integration tests for profile updates
   - Task 5: Add error handling
2. Configure: Run tests after tasks 3 and 4, measure coverage
3. Execute tasks in sequence with checkpoints
4. Generate consolidated report
```

---

## Workflow Steps

When this skill is invoked, follow these steps:

### Step 1: Analyze the Request
- Understand what the user wants to accomplish
- Identify the scope of work
- Determine if tasks are related and suitable for batch execution

### Step 2: Create Task List
Use TodoWrite to create a structured task list:
```
- Analyze codebase and identify components
- Define individual tasks
- Configure test and coverage settings
- Execute Task 1: [description]
- Run tests for Task 1
- Execute Task 2: [description]
- Run tests for Task 2
- ...
- Generate consolidated report
```

### Step 3: Gather Context
- Read relevant files
- Understand current code structure
- Check existing test coverage
- Identify dependencies between tasks

### Step 4: Configure Execution
Ask the user (or infer from context):
- Should tests run after each task or only at the end?
- Should coverage be measured?
- Should git checkpoints be created?
- What's the desired coverage threshold?

### Step 5: Execute Tasks Sequentially
For each task:
```
1. Update TodoWrite - mark task as in_progress
2. Execute the task (refactor, write tests, implement)
3. Create git checkpoint (if enabled)
4. Run tests (if configured)
5. Measure coverage (if configured)
6. Record results in report data structure
7. Check for failures
8. Update TodoWrite - mark task as completed
9. Proceed to next task or stop on failure
```

### Step 6: Generate Consolidated Report
Create a comprehensive report with:
```markdown
# Task Execution Report

## Summary
- Total tasks: X
- Successful: Y
- Failed: Z
- Duration: N seconds

## Task Results
### Task 1: [Name]
- Status: ✓ Success / ✗ Failed
- Tests: X/Y passed
- Coverage: Before: A% → After: B% (ΔC%)
- Duration: N seconds

### Task 2: [Name]
...

## Overall Test Results
- Total tests: X
- Passed: Y
- Failed: Z
- Skipped: W

## Coverage Summary
- Starting coverage: X%
- Final coverage: Y%
- Coverage delta: ΔZ%
- Coverage by module:
  - module1: X%
  - module2: Y%

## Recommendations
- [Suggestions based on results]
```

---

## Integration with Tools

This skill uses the following tools:

### Core Tools
- **Read**: Read source files and test files
- **Write/Edit**: Modify code and create tests
- **TodoWrite**: Track task progress
- **Bash**: Run tests, measure coverage, git operations

### Test Execution
```bash
# Run tests
pytest tests/ -v

# Run tests with coverage
pytest --cov=. --cov-report=term --cov-report=json tests/

# Run specific test file
pytest tests/test_module.py -v
```

### Coverage Measurement
```bash
# Generate coverage report
pytest --cov=. --cov-report=json --cov-report=term-missing

# Parse coverage data
python -c "import json; data=json.load(open('coverage.json')); print(data['totals']['percent_covered'])"
```

### Git Checkpoints
```bash
# Create checkpoint
git add .
git commit -m "task-exec: checkpoint after task N - [description]"

# Rollback to previous checkpoint
git reset --hard HEAD~1
```

---

## Error Handling

### Test Failures
- Stop execution (if stop_on_test_failure=true)
- Record failure in report
- Optionally rollback changes
- Provide detailed error information

### Coverage Below Threshold
- Warn user
- Continue execution (unless strict mode)
- Highlight in final report
- Suggest additional tests

### Task Execution Errors
- Catch and record errors
- Stop execution
- Provide context about failure
- Suggest fixes

---

## Best Practices

1. **Keep Tasks Focused**: Each task should be a single, clear action
2. **Define Dependencies**: Specify which tasks depend on others
3. **Test Incrementally**: Run tests after each task when possible
4. **Track Coverage**: Monitor coverage changes to ensure quality
5. **Create Checkpoints**: Use git commits to enable rollback
6. **Review Reports**: Use consolidated reports to identify patterns
7. **Iterate**: Use report recommendations for next batch of tasks

---

## Advanced Features

### Parallel Task Execution (Future)
- Identify independent tasks
- Execute in parallel when safe
- Merge results

### Smart Test Selection
- Run only tests affected by changes
- Use pytest-picked or similar tools
- Reduce execution time

### Coverage-Guided Task Prioritization
- Prioritize tasks that improve coverage most
- Focus on untested code paths
- Optimize for coverage goals

### Integration with CI/CD
- Export results in CI-compatible formats
- Generate JUnit XML reports
- Update coverage badges

---

## Implementation Guide

This skill is implemented using:
1. **task_execution_skill.md**: Skill definition (this file)
2. **task_executor.py**: Python module with execution logic
3. **task_execution_examples.md**: Usage examples and patterns

To use this skill programmatically, see `task_executor.py` for the TaskExecutor class.
