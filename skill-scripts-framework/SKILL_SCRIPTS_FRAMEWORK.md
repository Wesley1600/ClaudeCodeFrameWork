# Skill Scripts Framework

A comprehensive framework for organizing and executing scripts within Claude Code Agent Skills without loading them into context.

## Overview

The Skill Scripts Framework enables you to bundle Python, Bash, and other utility scripts with your Agent Skills. Claude can execute these scripts via bash without loading their contents into the conversation context, making skills more efficient and maintainable.

## Benefits

- **Context Efficiency**: Execute scripts without loading their source into Claude's context window
- **Code Reusability**: Share common utilities across multiple skills
- **Organization**: Keep related scripts bundled with their skills
- **Maintainability**: Update scripts independently of skill descriptions
- **Security**: Control script execution through skill-level permissions

## Architecture

### Directory Structure

```
.claude/
└── skills/
    └── your-skill/
        ├── SKILL.md                 # Skill description (loaded into context)
        ├── scripts/                 # Script directory (not loaded into context)
        │   ├── python/
        │   │   ├── main.py
        │   │   └── utils.py
        │   ├── bash/
        │   │   ├── setup.sh
        │   │   └── cleanup.sh
        │   └── shared/
        │       └── config.json
        ├── allowed-tools.json       # Optional: restrict tool access
        └── README.md                # Optional: developer documentation
```

### Key Components

1. **SKILL.md**: The skill description that Claude loads into context
   - Should reference scripts by path
   - Provides instructions on when and how to execute scripts
   - Keeps script implementation details out of context

2. **scripts/**: Directory containing all executable scripts
   - Organized by language or purpose
   - Scripts are executed via bash tool
   - Not loaded into Claude's context

3. **allowed-tools.json**: Optional security configuration
   - Restricts which tools the skill can use
   - Ensures scripts only have necessary permissions

## Script Organization Patterns

### By Language

```
scripts/
├── python/
│   ├── analyzer.py
│   └── formatter.py
├── bash/
│   ├── build.sh
│   └── deploy.sh
└── nodejs/
    └── server.js
```

### By Function

```
scripts/
├── preprocessing/
│   ├── clean_data.py
│   └── validate.sh
├── processing/
│   ├── transform.py
│   └── analyze.py
└── postprocessing/
    ├── format.py
    └── report.sh
```

### Shared Utilities

```
scripts/
├── core/
│   ├── main.py
│   └── config.py
├── utils/
│   ├── logging.py
│   ├── validation.py
│   └── helpers.sh
└── data/
    ├── sample.json
    └── schema.yaml
```

## Usage Patterns

### Pattern 1: Direct Script Execution

**SKILL.md:**
```markdown
# Data Analysis Skill

Analyzes CSV files using Python scripts.

## Usage

When the user requests data analysis:

1. Ask for the CSV file path
2. Run: `python scripts/python/analyze_csv.py <file_path>`
3. Present the results to the user

The script outputs JSON with statistics and insights.

## Scripts

- `scripts/python/analyze_csv.py`: Main analysis script
- `scripts/python/plot_data.py`: Generates visualizations
```

### Pattern 2: Pipeline Execution

**SKILL.md:**
```markdown
# Build Pipeline Skill

Automates the build and deployment process.

## Usage

When user requests deployment:

1. Run: `bash scripts/bash/build.sh`
2. Run: `bash scripts/bash/test.sh`
3. If tests pass, run: `bash scripts/bash/deploy.sh`

Each script returns exit code 0 on success.

## Scripts

- `scripts/bash/build.sh`: Compiles the project
- `scripts/bash/test.sh`: Runs test suite
- `scripts/bash/deploy.sh`: Deploys to production
```

### Pattern 3: Configuration-Driven Execution

**SKILL.md:**
```markdown
# Code Generator Skill

Generates code from templates.

## Usage

1. Load config: `cat scripts/shared/templates.json`
2. Run generator: `python scripts/python/generate.py --template <name> --output <path>`

Templates are defined in `scripts/shared/templates.json`.

## Scripts

- `scripts/python/generate.py`: Template engine
- `scripts/shared/templates.json`: Template definitions
```

## Best Practices

### 1. Keep SKILL.md Concise

✅ **Good:**
```markdown
Run `python scripts/analyze.py <file>` to analyze the file.
```

❌ **Bad:**
```markdown
Run the following Python script:
\`\`\`python
import pandas as pd
import numpy as np
# ... 100 lines of code ...
\`\`\`
```

### 2. Use Absolute Paths from Skill Root

✅ **Good:**
```bash
python .claude/skills/my-skill/scripts/python/main.py
```

❌ **Bad:**
```bash
cd scripts && python main.py  # Fragile, depends on current directory
```

### 3. Make Scripts Self-Contained

Scripts should:
- Handle their own dependencies
- Include error handling
- Provide clear output
- Return meaningful exit codes

### 4. Document Script Interfaces

Include in SKILL.md:
- Required arguments
- Expected output format
- Exit codes
- Dependencies

### 5. Use Environment Variables for Configuration

```bash
# In SKILL.md
export DATA_PATH=/path/to/data
python scripts/process.py
```

### 6. Implement Proper Error Handling

```python
#!/usr/bin/env python3
import sys
import json

def main():
    try:
        # Script logic here
        result = {"status": "success", "data": {...}}
        print(json.dumps(result))
        return 0
    except Exception as e:
        error = {"status": "error", "message": str(e)}
        print(json.dumps(error), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### 7. Use Standard Output Formats

Prefer structured formats:
- JSON for complex data
- CSV for tabular data
- Plain text for simple messages
- Exit codes for success/failure

## Security Considerations

### 1. Restrict Tool Access

Create `allowed-tools.json`:
```json
{
  "allowed_tools": ["Bash", "Read", "Write"],
  "description": "Only allow file operations and script execution"
}
```

### 2. Validate Inputs

Always validate user inputs in scripts:
```python
import sys
import os

def validate_file_path(path):
    if not os.path.exists(path):
        raise ValueError(f"File not found: {path}")
    if not path.endswith('.csv'):
        raise ValueError("Only CSV files are supported")
    return os.path.abspath(path)
```

### 3. Avoid Arbitrary Code Execution

❌ **Never:**
```python
eval(user_input)  # Dangerous!
os.system(user_command)  # Dangerous!
```

✅ **Instead:**
```python
subprocess.run([command, arg1, arg2], check=True)  # Safe, controlled
```

### 4. Use Read-Only Operations When Possible

If a skill only reads data, document this in `allowed-tools.json`:
```json
{
  "allowed_tools": ["Bash", "Read"],
  "description": "Read-only analysis skill"
}
```

## Testing Your Skills

### Local Testing

```bash
# Test script execution
cd .claude/skills/my-skill
python scripts/python/main.py --test

# Test with sample data
python scripts/python/main.py tests/sample_data.csv
```

### Integration Testing

1. Load the skill in Claude Code
2. Trigger the skill with test scenarios
3. Verify script execution and outputs
4. Check error handling

## Examples

See the `examples/` directory for complete skill implementations:

- **python-skill**: Data analysis with Python scripts
- **bash-skill**: Build automation with Bash scripts
- **mixed-skill**: Multi-language pipeline

## Migration Guide

### Converting Inline Code to Scripts

**Before:**
```markdown
# My Skill

Run this Python code:
\`\`\`python
# 50 lines of code here...
\`\`\`
```

**After:**

1. Extract code to `scripts/python/main.py`
2. Update SKILL.md:
```markdown
# My Skill

Run: `python scripts/python/main.py <args>`
```

### Benefits:
- Reduced context usage
- Better code organization
- Easier maintenance
- Version control friendly

## Troubleshooting

### Script Not Found

**Error:** `python: can't open file 'scripts/main.py'`

**Solution:** Use absolute paths or navigate to skill directory first:
```bash
cd .claude/skills/my-skill && python scripts/main.py
```

### Permission Denied

**Error:** `bash: scripts/deploy.sh: Permission denied`

**Solution:** Make script executable:
```bash
chmod +x scripts/deploy.sh
```

### Import Errors (Python)

**Error:** `ModuleNotFoundError: No module named 'myutils'`

**Solution:** Add parent directory to Python path:
```bash
PYTHONPATH=.claude/skills/my-skill python .claude/skills/my-skill/scripts/main.py
```

## Advanced Patterns

### Script Chaining

```markdown
# Multi-Stage Pipeline Skill

Execute stages in sequence:

1. Preprocess: `python scripts/01_preprocess.py`
2. Analyze: `python scripts/02_analyze.py`
3. Report: `python scripts/03_report.py`

Each script reads from and writes to `scripts/shared/state.json`.
```

### Conditional Execution

```markdown
# Smart Build Skill

1. Check if build needed: `bash scripts/check_changes.sh`
2. If exit code is 0, run: `bash scripts/build.sh`
3. Otherwise, skip build and notify user
```

### Parallel Execution

```markdown
# Batch Processing Skill

For multiple files, process in parallel:

\`\`\`bash
for file in *.csv; do
    python scripts/process.py "$file" &
done
wait
\`\`\`
```

## Contributing

To extend this framework:

1. Add new examples to `examples/`
2. Create templates in `templates/`
3. Document patterns in this file
4. Share best practices

## References

- [Claude Code Skills Documentation](https://code.claude.com/docs)
- [Agent Skills Architecture](https://code.claude.com/docs/agent-skills)
- [Bash Tool Documentation](https://code.claude.com/docs/tools#bash)

## License

MIT License - See LICENSE file for details
