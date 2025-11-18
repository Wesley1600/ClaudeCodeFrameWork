# Python Script Skill Template

A template for creating skills that use Python scripts.

## Description

This skill uses Python scripts to [describe what it does].

## When to Use

Use this skill when:
- User needs to [use case 1]
- User requests [use case 2]

## Usage

### Basic Usage

Execute the main script:

```bash
python .claude/skills/[skill-name]/scripts/python/main.py [args]
```

## Script Reference

### main.py

**Arguments:**
- `input`: Input data (required)
- `--option`: Optional parameter (default: value)

**Output:** JSON formatted results

**Exit Codes:**
- 0: Success
- 1: Invalid input
- 2: Processing error

## Examples

**Example 1:**
```bash
python scripts/python/main.py example_input.txt
```

## Dependencies

- Python 3.8+
- [list required packages]
