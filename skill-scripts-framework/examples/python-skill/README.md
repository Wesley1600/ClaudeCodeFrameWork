# CSV Data Analysis Skill Example

This example demonstrates how to organize Python scripts within a Claude Code skill.

## Structure

```
python-skill/
├── SKILL.md                    # Skill description (loaded into Claude's context)
├── scripts/
│   ├── python/
│   │   ├── analyze_csv.py     # Main analysis script
│   │   ├── plot_data.py       # Visualization script
│   │   └── validate.py        # Validation script
│   └── shared/
│       └── sample_config.json # Configuration file
└── README.md                   # This file (developer documentation)
```

## Key Features

1. **Context Efficiency**: Python analysis logic is in scripts, not in SKILL.md
2. **Modular Design**: Separate scripts for different tasks
3. **Standard Interface**: JSON input/output for easy parsing
4. **Error Handling**: Proper exit codes and error messages
5. **Configuration**: Shared config for consistent behavior

## Usage

### Analyze a CSV File

```bash
python scripts/python/analyze_csv.py data.csv
```

Output:
```json
{
  "file": "data.csv",
  "rows": 1000,
  "columns": 5,
  "numeric_stats": {...},
  "insights": [...]
}
```

### Generate Visualization

```bash
python scripts/python/plot_data.py data.csv --output plot.png --type histogram
```

### Validate CSV

```bash
python scripts/python/validate.py data.csv
```

## Dependencies

Install required packages:

```bash
pip install pandas numpy matplotlib
```

## Testing

Test scripts individually:

```bash
# Create sample CSV
echo "name,age,score\nAlice,25,95\nBob,30,87" > test.csv

# Test analysis
python scripts/python/analyze_csv.py test.csv

# Test validation
python scripts/python/validate.py test.csv

# Test plotting
python scripts/python/plot_data.py test.csv --output test_plot.png
```

## Integration with Claude Code

When Claude Code loads this skill:

1. Only `SKILL.md` is loaded into context
2. Claude reads the instructions and script paths
3. When user requests analysis, Claude executes:
   ```bash
   python .claude/skills/csv-analysis/scripts/python/analyze_csv.py user_file.csv
   ```
4. Claude parses the JSON output and presents insights

## Benefits

- **Reduced Context**: ~3KB (SKILL.md) vs ~30KB (if code was embedded)
- **Maintainability**: Update scripts without changing skill description
- **Reusability**: Scripts can be used outside Claude Code
- **Testability**: Scripts can be tested independently

## Best Practices Demonstrated

1. **Clear interfaces**: Argparse for CLI, JSON for output
2. **Error handling**: Try/except with meaningful error codes
3. **Validation**: Input validation before processing
4. **Documentation**: Docstrings and comments
5. **Configuration**: Externalized config in JSON
6. **Type hints**: Python type annotations for clarity
