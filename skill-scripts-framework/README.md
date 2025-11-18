# Skill Scripts Framework

A comprehensive framework for organizing and executing scripts within Claude Code Agent Skills without loading them into context.

## Overview

This framework enables you to bundle Python, Bash, and other utility scripts with your Agent Skills. Claude can execute these scripts via bash without loading their contents into the conversation context, making skills more efficient and maintainable.

## Quick Start

### 1. Create a New Skill from Template

```bash
# Copy a template
cp -r skill-scripts-framework/templates/python-script-skill .claude/skills/my-analysis-skill

# Customize SKILL.md
# Implement your scripts
# Test the skill
```

### 2. Use an Example

```bash
# Try the CSV analysis example
cd skill-scripts-framework/examples/python-skill

# Run the analyzer
python scripts/python/analyze_csv.py example.csv

# Run the validator
python scripts/python/validate.py example.csv
```

### 3. Validate Your Skill

```bash
python skill-scripts-framework/utils/script_validator.py .claude/skills/my-skill
```

## Directory Structure

```
skill-scripts-framework/
├── SKILL_SCRIPTS_FRAMEWORK.md    # Complete framework documentation
├── README.md                      # This file
├── examples/                      # Working examples
│   ├── python-skill/             # CSV analysis with Python
│   ├── bash-skill/               # Build automation with Bash
│   └── mixed-skill/              # Multi-language pipeline
├── templates/                     # Skill templates
│   ├── python-script-skill/
│   ├── bash-script-skill/
│   └── README.md
├── utils/                         # Helper utilities
│   ├── script_executor.py        # Execute scripts with error handling
│   ├── script_validator.py       # Validate skill scripts
│   └── README.md
└── docs/                          # Additional documentation
    └── BEST_PRACTICES.md         # Best practices guide
```

## Key Features

### Context Efficiency

Scripts are executed without loading into Claude's context:

```markdown
# In SKILL.md (loaded into context)
Run: `python scripts/analyze.py <file>`

# Scripts not loaded into context
scripts/python/analyze.py (100+ lines)
```

**Result:** ~95% reduction in context usage

### Code Organization

Keep related scripts bundled with their skills:

```
.claude/skills/csv-analysis/
├── SKILL.md                      # ~2KB, loaded into context
└── scripts/
    ├── python/
    │   ├── analyze.py           # Not loaded
    │   ├── validate.py          # Not loaded
    │   └── plot.py              # Not loaded
    └── shared/
        └── config.json
```

### Maintainability

Update scripts without changing skill descriptions:

- Modify implementation in scripts
- Keep SKILL.md interface stable
- No need to reload skill in Claude

## Documentation

- **[Framework Overview](SKILL_SCRIPTS_FRAMEWORK.md)** - Complete documentation
- **[Best Practices](docs/BEST_PRACTICES.md)** - Writing quality scripts
- **[Templates README](templates/README.md)** - Using templates
- **[Utilities README](utils/README.md)** - Helper utilities

## Examples

### Python Example: CSV Analysis

**What it does:** Analyzes CSV files and generates statistical reports

**Key files:**
- `examples/python-skill/SKILL.md` - Skill description
- `examples/python-skill/scripts/python/analyze_csv.py` - Analysis script
- `examples/python-skill/scripts/python/validate.py` - Validation script

**Try it:**
```bash
cd examples/python-skill

# Create test CSV
echo "name,age,score" > test.csv
echo "Alice,25,95" >> test.csv
echo "Bob,30,87" >> test.csv

# Analyze
python scripts/python/analyze_csv.py test.csv

# Validate
python scripts/python/validate.py test.csv
```

### Bash Example: Build Automation

**What it does:** Automates build, test, and deployment processes

**Key files:**
- `examples/bash-skill/SKILL.md` - Skill description
- `examples/bash-skill/scripts/bash/pipeline.sh` - Complete pipeline
- `examples/bash-skill/scripts/bash/build.sh` - Build script
- `examples/bash-skill/scripts/bash/test.sh` - Test script

**Try it:**
```bash
cd examples/bash-skill

# Setup environment
bash scripts/bash/setup.sh

# Run full pipeline
bash scripts/bash/pipeline.sh

# Run individual stages
bash scripts/bash/build.sh
bash scripts/bash/test.sh
```

## Templates

Ready-to-use templates for creating new skills:

### Python Script Skill

```bash
cp -r templates/python-script-skill .claude/skills/my-skill
```

Includes:
- SKILL.md template
- Python script with argparse and error handling
- JSON output format

### Bash Script Skill

```bash
cp -r templates/bash-script-skill .claude/skills/my-skill
```

Includes:
- SKILL.md template
- Bash script with error handling
- Configuration file support

## Utilities

### Script Executor

Execute scripts with proper error handling:

```python
from utils.script_executor import ScriptExecutor

executor = ScriptExecutor("/path/to/skill")
results = executor.execute_and_parse_json(
    "python",
    "python/analyze.py",
    args=["data.csv"]
)
```

### Script Validator

Validate skills for common issues:

```bash
python utils/script_validator.py .claude/skills/my-skill
```

Checks:
- Directory structure
- SKILL.md completeness
- Script syntax
- File permissions
- Best practices

## Benefits

### For Skills

- **Context Efficiency**: 95% less context usage
- **Organization**: Scripts bundled with skills
- **Maintainability**: Update scripts independently
- **Reusability**: Scripts work outside Claude Code

### For Claude

- **Faster Loading**: Only SKILL.md loaded into context
- **Clear Interface**: Simple execution instructions
- **Error Handling**: Scripts handle errors independently
- **Consistency**: Standard output formats (JSON)

### For Developers

- **Version Control**: Scripts track changes easily
- **Testing**: Test scripts independently
- **Debugging**: Standard debugging tools work
- **Collaboration**: Clear separation of concerns

## Common Patterns

### Pattern 1: Single Analysis Script

```
skill/
├── SKILL.md                  # "Run: python scripts/analyze.py <file>"
└── scripts/
    └── python/
        └── analyze.py        # Self-contained analysis
```

### Pattern 2: Multi-Stage Pipeline

```
skill/
├── SKILL.md                  # "Run: bash scripts/pipeline.sh"
└── scripts/
    └── bash/
        ├── pipeline.sh       # Orchestrates stages
        ├── build.sh
        ├── test.sh
        └── deploy.sh
```

### Pattern 3: Shared Utilities

```
skill/
├── SKILL.md
└── scripts/
    ├── python/
    │   ├── main.py          # Uses utilities
    │   └── utils/
    │       ├── validation.py
    │       └── formatting.py
    └── shared/
        └── config.json
```

## Best Practices Summary

1. **Keep SKILL.md Concise** - Only execution instructions
2. **Use Standard Interfaces** - JSON output, argparse
3. **Handle Errors Properly** - Meaningful exit codes and messages
4. **Validate Inputs** - Never trust user input
5. **Document Thoroughly** - Clear usage and examples
6. **Test Independently** - Scripts should work standalone

See [BEST_PRACTICES.md](docs/BEST_PRACTICES.md) for complete guide.

## Validation Checklist

Before deploying a skill:

- [ ] SKILL.md is concise (<5KB)
- [ ] Scripts have shebangs (`#!/usr/bin/env python3`)
- [ ] Scripts are executable (`chmod +x`)
- [ ] Error handling is comprehensive
- [ ] Output format is consistent (JSON)
- [ ] Examples work as documented
- [ ] Validation passes: `python utils/script_validator.py <skill>`

## Troubleshooting

### Script Not Found

**Error:** `python: can't open file 'scripts/main.py'`

**Solution:** Use absolute path or navigate to skill directory:
```bash
cd .claude/skills/my-skill && python scripts/python/main.py
```

### Permission Denied

**Error:** `bash: scripts/main.sh: Permission denied`

**Solution:**
```bash
chmod +x scripts/bash/main.sh
```

### Import Errors (Python)

**Error:** `ModuleNotFoundError`

**Solution:** Add parent to Python path:
```bash
PYTHONPATH=.claude/skills/my-skill python .claude/skills/my-skill/scripts/main.py
```

## Contributing

Contributions welcome! To add:

1. **New Examples:** Add to `examples/` with README
2. **New Templates:** Add to `templates/`
3. **New Utilities:** Add to `utils/`
4. **Documentation:** Update relevant docs

## License

MIT License

## Resources

- [Claude Code Skills Documentation](https://code.claude.com/docs/agent-skills)
- [Agent Skills Architecture](https://code.claude.com/docs)
- [Framework Documentation](SKILL_SCRIPTS_FRAMEWORK.md)
- [Best Practices](docs/BEST_PRACTICES.md)

---

**Status:** Production Ready v1.0

**Last Updated:** 2025-11-18

For questions or issues, please open a GitHub issue.
