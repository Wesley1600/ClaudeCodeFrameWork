# Script Utilities

Helper utilities for working with skill scripts.

## Available Utilities

### 1. script_executor.py

Executes skill scripts with proper error handling and output parsing.

**Features:**
- Execute Python and Bash scripts
- Parse JSON output
- Handle timeouts
- Capture stdout and stderr
- Environment variable support

**Usage:**

```python
from script_executor import ScriptExecutor

# Initialize
executor = ScriptExecutor("/path/to/skill")

# Execute Python script
exit_code, stdout, stderr = executor.execute_python(
    "python/analyze.py",
    args=["data.csv"],
    timeout=60
)

# Execute and parse JSON
results = executor.execute_and_parse_json(
    "python",
    "python/analyze.py",
    args=["data.csv", "--format", "json"]
)
print(results["status"])
```

**Command Line:**

```bash
# Execute script
python script_executor.py /path/to/skill python python/main.py arg1 arg2

# Parse JSON output
python script_executor.py /path/to/skill python python/main.py --json arg1
```

### 2. script_validator.py

Validates skill scripts for common issues and best practices.

**Features:**
- Structure validation
- SKILL.md checks
- Script syntax checks
- Permission checks
- Best practice validation

**Usage:**

```python
from script_validator import ScriptValidator

# Initialize
validator = ScriptValidator("/path/to/skill")

# Validate
results = validator.validate_all()

# Check results
for result in results:
    print(result)

if validator.has_errors():
    print("Validation failed!")
```

**Command Line:**

```bash
# Validate skill
python script_validator.py /path/to/skill

# JSON output
python script_validator.py /path/to/skill --json
```

## Integration with Skills

### Using in SKILL.md

Instead of documenting complex execution logic, reference the executor:

```markdown
# My Analysis Skill

When user requests analysis:

1. Use the script executor to run the analysis
2. Parse the JSON output
3. Present results to the user

Execute: `python scripts/python/analyze.py <file>`
```

### Validation in CI/CD

Add validation to your CI pipeline:

```yaml
# .github/workflows/validate-skills.yml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate skills
        run: |
          for skill in .claude/skills/*/; do
            python utils/script_validator.py "$skill" || exit 1
          done
```

### Pre-commit Hook

Validate skills before committing:

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Validating skills..."
for skill in .claude/skills/*/; do
    if ! python utils/script_validator.py "$skill"; then
        echo "Skill validation failed: $skill"
        exit 1
    fi
done
```

## Examples

### Example 1: Execute Script with Error Handling

```python
from script_executor import ScriptExecutor

executor = ScriptExecutor("/path/to/skill")

try:
    results = executor.execute_and_parse_json(
        "python",
        "python/process.py",
        args=["input.txt"]
    )

    if results["status"] == "success":
        print(f"Processed: {results['data']}")
    else:
        print(f"Error: {results['message']}")

except RuntimeError as e:
    print(f"Script execution failed: {e}")
except json.JSONDecodeError as e:
    print(f"Invalid JSON output: {e}")
```

### Example 2: Batch Validation

```python
from pathlib import Path
from script_validator import ScriptValidator

skills_dir = Path(".claude/skills")

for skill_path in skills_dir.iterdir():
    if skill_path.is_dir():
        print(f"\nValidating: {skill_path.name}")

        validator = ScriptValidator(skill_path)
        results = validator.validate_all()

        if validator.has_errors():
            print(f"  ❌ Failed")
            for r in results:
                if r.severity == "error":
                    print(f"    {r}")
        else:
            print(f"  ✅ Passed")
```

### Example 3: Custom Execution Wrapper

```python
import sys
from script_executor import ScriptExecutor

def run_analysis(skill_path: str, data_file: str) -> dict:
    """
    Run analysis script and return results.

    Args:
        skill_path: Path to skill directory
        data_file: Path to data file

    Returns:
        Analysis results as dictionary
    """
    executor = ScriptExecutor(skill_path)

    try:
        return executor.execute_and_parse_json(
            "python",
            "python/analyze.py",
            args=[data_file, "--format", "json"],
            timeout=300
        )
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Use it
if __name__ == "__main__":
    results = run_analysis(sys.argv[1], sys.argv[2])
    print(f"Status: {results['status']}")
```

## Extending the Utilities

### Adding New Validators

Add custom validation checks:

```python
class MyValidator(ScriptValidator):
    def _check_custom(self):
        """Custom validation check."""
        # Your validation logic
        if condition:
            self.results.append(ValidationResult(
                "warning",
                "Custom warning message",
                "file.py"
            ))

    def validate_all(self):
        """Override to include custom checks."""
        super().validate_all()
        self._check_custom()
        return self.results
```

### Adding New Executors

Support for other languages:

```python
class ExtendedExecutor(ScriptExecutor):
    def execute_nodejs(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: int = 300
    ) -> Tuple[int, str, str]:
        """Execute a Node.js script."""
        full_path = self.scripts_dir / script_path
        cmd = ["node", str(full_path)]
        if args:
            cmd.extend(args)
        return self._run_command(cmd, env, timeout)
```

## Testing

Test the utilities:

```bash
# Test executor
cd examples/python-skill
python ../../utils/script_executor.py . python python/analyze.py test.csv --json

# Test validator
cd examples/python-skill
python ../../utils/script_validator.py .
```

## Dependencies

Both utilities require:
- Python 3.8+
- Standard library only (no external dependencies)

## License

MIT License
