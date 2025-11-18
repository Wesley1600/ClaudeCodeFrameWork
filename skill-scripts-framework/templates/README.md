# Skill Script Templates

Templates for creating new skills with bundled scripts.

## Available Templates

### 1. Python Script Skill

Location: `python-script-skill/`

Use this template when creating skills that use Python scripts for data processing, analysis, or automation.

**Includes:**
- SKILL.md template
- main.py script template with argparse and error handling
- JSON output format
- Proper exit codes

### 2. Bash Script Skill

Location: `bash-script-skill/`

Use this template when creating skills that use Bash scripts for system operations, build automation, or orchestration.

**Includes:**
- SKILL.md template
- main.sh script template with error handling
- Colored logging
- Configuration file support

### 3. Mixed Script Skill

Location: `mixed-script-skill/`

Use this template when creating skills that combine multiple script types or languages.

**Includes:**
- Multi-language script organization
- Shared configuration
- Coordinated execution patterns

## Using Templates

### Quick Start

1. **Copy a template:**
   ```bash
   cp -r templates/python-script-skill .claude/skills/my-new-skill
   ```

2. **Customize SKILL.md:**
   - Replace `[Skill Name]` with your skill name
   - Fill in description and use cases
   - Document your scripts

3. **Implement scripts:**
   - Edit `scripts/python/main.py` or `scripts/bash/main.sh`
   - Add your processing logic
   - Update error handling as needed

4. **Test:**
   ```bash
   python .claude/skills/my-new-skill/scripts/python/main.py test_input
   ```

5. **Use in Claude Code:**
   Load the skill and trigger it through conversation

### Template Customization

#### For Python Skills

**Edit main.py:**
```python
def process(input_data: str) -> Dict[str, Any]:
    # Add your logic here
    results = {
        "status": "success",
        "data": your_processed_data
    }
    return results
```

**Add dependencies:**
Create `requirements.txt`:
```
pandas>=1.3.0
numpy>=1.20.0
```

#### For Bash Skills

**Edit main.sh:**
```bash
process() {
    local input="$1"

    # Add your logic here
    echo "Processing $input"

    # Return results
    echo "Results here"
}
```

**Add configuration:**
Create `scripts/shared/config.env`:
```bash
# Your configuration variables
SETTING_NAME="value"
```

## Template Structure

### Python Script Skill

```
python-script-skill/
├── SKILL.md              # Skill description
└── scripts/
    ├── python/
    │   └── main.py       # Main Python script
    └── shared/
        └── config.json   # Optional configuration
```

### Bash Script Skill

```
bash-script-skill/
├── SKILL.md              # Skill description
└── scripts/
    ├── bash/
    │   └── main.sh       # Main Bash script
    └── shared/
        └── config.env    # Optional configuration
```

## Best Practices

### 1. Keep SKILL.md Concise

✅ **Good:**
```markdown
Run `python scripts/main.py <file>` to process the file.
```

❌ **Bad:** (Including entire script in SKILL.md)

### 2. Use Standard Interfaces

**Python:** JSON output, argparse for arguments
**Bash:** Environment variables, standard exit codes

### 3. Error Handling

Always include:
- Input validation
- Clear error messages
- Meaningful exit codes
- JSON error format (for Python)

### 4. Documentation

Document in SKILL.md:
- Required arguments
- Output format
- Exit codes
- Environment variables
- Examples

### 5. Testing

Test scripts independently before using in skills:

```bash
# Python
python scripts/python/main.py --help
python scripts/python/main.py test_input

# Bash
bash scripts/bash/main.sh --help
bash scripts/bash/main.sh test_input
```

## Common Patterns

### Pattern 1: Single Script

One main script that does everything.

**Use when:** Simple, focused task

### Pattern 2: Multi-Script Pipeline

Multiple scripts that work together.

**Use when:** Complex workflow with distinct stages

```
scripts/
├── python/
│   ├── 01_preprocess.py
│   ├── 02_process.py
│   └── 03_postprocess.py
```

### Pattern 3: Utility Scripts

Main script + helper utilities.

**Use when:** Reusable utilities across multiple operations

```
scripts/
├── python/
│   ├── main.py
│   └── utils/
│       ├── validation.py
│       └── formatting.py
```

## Checklist

Before deploying your skill:

- [ ] SKILL.md is complete and concise
- [ ] Scripts are executable (`chmod +x`)
- [ ] Scripts handle errors properly
- [ ] Scripts include help text
- [ ] Examples work as documented
- [ ] Dependencies are documented
- [ ] Scripts tested independently
- [ ] Security considerations addressed

## Examples

See the `examples/` directory for complete, working implementations:

- `examples/python-skill` - CSV analysis with Python
- `examples/bash-skill` - Build automation with Bash
- `examples/mixed-skill` - Multi-language pipeline

## Troubleshooting

### Script not executable

```bash
chmod +x scripts/python/main.py
chmod +x scripts/bash/main.sh
```

### Import errors (Python)

Add to script:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### Environment variables not loaded (Bash)

Check that config.env is sourced:
```bash
if [[ -f "$SCRIPT_DIR/../shared/config.env" ]]; then
    source "$SCRIPT_DIR/../shared/config.env"
fi
```

## Resources

- [Skill Scripts Framework Documentation](../SKILL_SCRIPTS_FRAMEWORK.md)
- [Claude Code Skills Documentation](https://code.claude.com/docs/agent-skills)
- [Example Skills](../examples/)
