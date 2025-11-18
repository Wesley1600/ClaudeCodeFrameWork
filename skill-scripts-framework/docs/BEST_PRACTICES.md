# Best Practices for Skill Scripts

A comprehensive guide to writing high-quality, maintainable scripts for Claude Code skills.

## Table of Contents

1. [General Principles](#general-principles)
2. [SKILL.md Guidelines](#skillmd-guidelines)
3. [Python Script Best Practices](#python-script-best-practices)
4. [Bash Script Best Practices](#bash-script-best-practices)
5. [Error Handling](#error-handling)
6. [Output Formats](#output-formats)
7. [Security](#security)
8. [Testing](#testing)
9. [Documentation](#documentation)
10. [Performance](#performance)

## General Principles

### 1. Separation of Concerns

**Keep skill description separate from implementation:**

✅ **Good:**
```markdown
# SKILL.md
Execute: `python scripts/analyze.py <file>`
```

❌ **Bad:**
```markdown
# SKILL.md
Run this code:
\`\`\`python
# 100 lines of implementation...
\`\`\`
```

**Why:** Keeps context usage low and implementation flexible.

### 2. Single Responsibility

Each script should do one thing well.

✅ **Good:**
```
scripts/
├── validate.py     # Just validation
├── process.py      # Just processing
└── format.py       # Just formatting
```

❌ **Bad:**
```
scripts/
└── do_everything.py  # Validation + processing + formatting
```

### 3. Idempotency

Scripts should produce the same result when run multiple times with the same input.

✅ **Good:**
```python
# Always produces same output for same input
def process(data):
    return sorted(set(data))
```

❌ **Bad:**
```python
# Output depends on execution time or random factors
def process(data):
    return data + [random.randint(1, 100)]
```

## SKILL.md Guidelines

### 1. Be Concise

Keep SKILL.md under 5KB when possible.

✅ **Good:**
```markdown
# Data Analysis

Analyzes CSV files.

## Usage
Run: `python scripts/analyze.py <file>`

## Output
JSON with statistics and insights.
```

❌ **Bad:**
```markdown
# Data Analysis

This skill provides comprehensive data analysis capabilities
including statistical analysis, data visualization, pattern
detection, outlier identification... [1000 more words]
```

### 2. Clear Instructions

Provide step-by-step instructions for Claude.

✅ **Good:**
```markdown
## Usage

When user requests analysis:
1. Ask for CSV file path
2. Run: `python scripts/analyze.py <path>`
3. Parse JSON output
4. Present insights to user
```

❌ **Bad:**
```markdown
## Usage
Use the analysis script to analyze data.
```

### 3. Document Script Interfaces

Clearly document arguments, outputs, and exit codes.

✅ **Good:**
```markdown
### analyze.py

**Arguments:**
- `file_path`: Path to CSV (required)
- `--columns`: Specific columns (optional)

**Output:** JSON with structure:
\`\`\`json
{
  "rows": int,
  "columns": int,
  "stats": {...}
}
\`\`\`

**Exit Codes:**
- 0: Success
- 1: File not found
- 2: Invalid format
```

## Python Script Best Practices

### 1. Script Template

Use this template for all Python scripts:

```python
#!/usr/bin/env python3
"""
Script Name

Brief description of what this script does.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict


def process(data: str) -> Dict[str, Any]:
    """
    Main processing function.

    Args:
        data: Input data

    Returns:
        Processing results
    """
    # Implementation here
    return {"status": "success", "data": data}


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("input", help="Input data")
    parser.add_argument("--option", help="Optional parameter")

    args = parser.parse_args()

    try:
        results = process(args.input)
        print(json.dumps(results, indent=2))
        return 0

    except FileNotFoundError as e:
        error = {"status": "error", "code": 1, "message": str(e)}
        print(json.dumps(error), file=sys.stderr)
        return 1
    except ValueError as e:
        error = {"status": "error", "code": 2, "message": str(e)}
        print(json.dumps(error), file=sys.stderr)
        return 2
    except Exception as e:
        error = {"status": "error", "code": 3, "message": str(e)}
        print(json.dumps(error), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
```

### 2. Type Hints

Always use type hints for clarity:

✅ **Good:**
```python
def analyze(data: List[Dict[str, Any]]) -> Dict[str, float]:
    """Analyze data and return statistics."""
    return {"mean": 0.0, "std": 1.0}
```

❌ **Bad:**
```python
def analyze(data):
    return {"mean": 0.0, "std": 1.0}
```

### 3. Input Validation

Validate all inputs before processing:

✅ **Good:**
```python
def validate_file(path: str) -> Path:
    """Validate file exists and is readable."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not p.is_file():
        raise ValueError(f"Not a file: {path}")
    if not p.suffix == '.csv':
        raise ValueError(f"Not a CSV file: {path}")
    return p
```

### 4. JSON Output

Use consistent JSON structure:

✅ **Good:**
```python
# Success
{
  "status": "success",
  "data": {...},
  "metadata": {...}
}

# Error
{
  "status": "error",
  "code": 2,
  "message": "Error description"
}
```

### 5. Docstrings

Write comprehensive docstrings:

✅ **Good:**
```python
def process_csv(file_path: Path, columns: List[str] = None) -> Dict[str, Any]:
    """
    Process CSV file and extract statistics.

    Args:
        file_path: Path to CSV file
        columns: Specific columns to analyze. If None, analyzes all columns.

    Returns:
        Dictionary containing:
        - rows: Number of rows
        - columns: Number of columns
        - stats: Statistical analysis

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If CSV format is invalid
    """
```

## Bash Script Best Practices

### 1. Script Template

Use this template for all Bash scripts:

```bash
#!/usr/bin/env bash
#
# Script Name
# Brief description
#

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load configuration
if [[ -f "$SCRIPT_DIR/../shared/config.env" ]]; then
    source "$SCRIPT_DIR/../shared/config.env"
fi

# Configuration
VAR_NAME="${VAR_NAME:-default_value}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Logging
log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Main function
main() {
    if [[ $# -lt 1 ]]; then
        log_error "Usage: $0 <input>"
        exit 1
    fi

    local input="$1"

    # Process
    log_success "Processing completed"

    exit 0
}

main "$@"
```

### 2. Error Handling

Always use proper error handling:

✅ **Good:**
```bash
set -euo pipefail

# Exit on error
if ! some_command; then
    log_error "Command failed"
    exit 1
fi

# Validate before use
if [[ ! -f "$file" ]]; then
    log_error "File not found: $file"
    exit 1
fi
```

❌ **Bad:**
```bash
# No error handling
some_command
cat "$file"  # Could fail if file doesn't exist
```

### 3. Quoting

Always quote variables:

✅ **Good:**
```bash
file="my file.txt"
if [[ -f "$file" ]]; then
    cat "$file"
fi
```

❌ **Bad:**
```bash
file="my file.txt"
if [[ -f $file ]]; then  # Breaks with spaces
    cat $file
fi
```

### 4. Functions

Break complex logic into functions:

✅ **Good:**
```bash
validate_input() {
    local input="$1"
    if [[ -z "$input" ]]; then
        return 1
    fi
    return 0
}

process_data() {
    local data="$1"
    echo "Processing: $data"
}

main() {
    if ! validate_input "$1"; then
        log_error "Invalid input"
        exit 1
    fi
    process_data "$1"
}
```

## Error Handling

### 1. Meaningful Exit Codes

Use consistent exit codes:

```python
# Standard exit codes
0   # Success
1   # General error / file not found
2   # Invalid input / syntax error
3   # Processing error
124 # Timeout
```

### 2. Error Messages

Provide clear, actionable error messages:

✅ **Good:**
```python
raise ValueError(
    f"Invalid CSV format: missing required column 'id'. "
    f"Available columns: {', '.join(df.columns)}"
)
```

❌ **Bad:**
```python
raise ValueError("Bad CSV")
```

### 3. Error Context

Include context in error messages:

✅ **Good:**
```json
{
  "status": "error",
  "code": 2,
  "message": "Invalid CSV format: missing headers",
  "file": "/path/to/file.csv",
  "line": 1
}
```

## Output Formats

### 1. Structured Output

Prefer structured formats (JSON) over plain text:

✅ **Good:**
```python
output = {
    "status": "success",
    "results": [...],
    "metadata": {
        "processed_at": "2025-01-15T10:30:00Z",
        "version": "1.0.0"
    }
}
print(json.dumps(output, indent=2))
```

### 2. Consistent Schema

Use consistent JSON schema across scripts:

```json
{
  "status": "success" | "error",
  "data": {},           // On success
  "message": "...",     // On error
  "code": 0,            // Error code
  "metadata": {}        // Optional metadata
}
```

### 3. Human-Readable Option

Provide text output option:

```python
parser.add_argument(
    "--format",
    choices=["json", "text"],
    default="json"
)

if args.format == "text":
    print(f"Processed {count} records")
else:
    print(json.dumps({"count": count}))
```

## Security

### 1. Input Validation

Never trust user input:

✅ **Good:**
```python
def validate_path(path: str) -> Path:
    """Validate and sanitize file path."""
    p = Path(path).resolve()

    # Prevent path traversal
    if not str(p).startswith(str(Path.cwd())):
        raise ValueError("Path outside working directory")

    # Validate extension
    if p.suffix not in ['.csv', '.txt']:
        raise ValueError("Invalid file type")

    return p
```

### 2. No Arbitrary Code Execution

Never execute user-provided code:

❌ **Never:**
```python
eval(user_input)
exec(user_code)
os.system(user_command)
```

✅ **Instead:**
```python
# Use allowlist of commands
allowed_commands = ["analyze", "validate", "format"]
if command not in allowed_commands:
    raise ValueError(f"Unknown command: {command}")
```

### 3. Resource Limits

Implement resource limits:

✅ **Good:**
```python
# File size limit
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
if file_path.stat().st_size > MAX_FILE_SIZE:
    raise ValueError("File too large")

# Timeout
result = subprocess.run(
    cmd,
    timeout=300,  # 5 minutes
    capture_output=True
)
```

## Testing

### 1. Test Scripts Independently

Create test cases for each script:

```python
# test_analyze.py
import subprocess
import json

def test_analyze_valid_csv():
    result = subprocess.run(
        ["python", "scripts/python/analyze.py", "test_data.csv"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["status"] == "success"

def test_analyze_invalid_file():
    result = subprocess.run(
        ["python", "scripts/python/analyze.py", "nonexistent.csv"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 1
    error = json.loads(result.stderr)
    assert "not found" in error["message"].lower()
```

### 2. Integration Tests

Test complete workflows:

```bash
#!/bin/bash
# test_workflow.sh

set -e

# Setup
python scripts/setup.py

# Run pipeline
bash scripts/pipeline.sh test_input.txt

# Verify output
if [[ ! -f output.json ]]; then
    echo "Output file not created"
    exit 1
fi

# Cleanup
rm output.json

echo "Integration test passed"
```

## Documentation

### 1. README for Each Skill

Include developer documentation:

```markdown
# Skill Name

## Development

### Setup
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Testing
\`\`\`bash
python -m pytest tests/
\`\`\`

### Scripts

#### analyze.py
Analyzes CSV files...

[Detailed documentation]
```

### 2. Inline Comments

Comment complex logic:

✅ **Good:**
```python
# Cluster difference vectors using soft k-means
# This aligns semantic relationships in the embedding space
distances = torch.cdist(diff_vecs, centroids)
weights = F.softmax(-distances / temperature, dim=1)
```

### 3. Examples

Provide working examples:

```markdown
## Examples

### Example 1: Basic Analysis
\`\`\`bash
python scripts/analyze.py data.csv
\`\`\`

Output:
\`\`\`json
{
  "rows": 1000,
  "columns": 5
}
\`\`\`
```

## Performance

### 1. Lazy Loading

Load dependencies only when needed:

✅ **Good:**
```python
def process(data):
    # Import only when needed
    import pandas as pd
    import numpy as np

    df = pd.DataFrame(data)
    return df.describe()
```

### 2. Streaming for Large Files

Process large files in chunks:

✅ **Good:**
```python
def process_large_csv(file_path: Path, chunk_size: int = 10000):
    """Process CSV in chunks to handle large files."""
    import pandas as pd

    results = []
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        results.append(process_chunk(chunk))

    return aggregate_results(results)
```

### 3. Progress Reporting

Report progress for long operations:

✅ **Good:**
```python
total = len(items)
for i, item in enumerate(items):
    process(item)
    if i % 100 == 0:
        print(f"Progress: {i}/{total}", file=sys.stderr)
```

## Checklist

Before deploying a skill with scripts:

- [ ] SKILL.md is concise (<5KB)
- [ ] Scripts have shebangs
- [ ] Scripts are executable
- [ ] Error handling is comprehensive
- [ ] Input validation is thorough
- [ ] Output format is consistent (JSON)
- [ ] Exit codes are meaningful
- [ ] Documentation is complete
- [ ] Examples work as documented
- [ ] Security is considered
- [ ] Tests are included
- [ ] Performance is acceptable
- [ ] Dependencies are documented

## Resources

- [Skill Scripts Framework](../SKILL_SCRIPTS_FRAMEWORK.md)
- [Templates](../templates/)
- [Examples](../examples/)
- [Utilities](../utils/)
