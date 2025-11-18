# Output Validator Examples

This directory contains example files and scripts to demonstrate the Output Validator skill.

## Files

### Helper Script

**validate-helper.sh** - A standalone bash script that demonstrates validation tool detection and execution. Can be used to validate files directly or as a reference implementation.

Usage:
```bash
# Show available validation tools
./validate-helper.sh --show-tools

# Validate specific files
./validate-helper.sh sample-code.js
./validate-helper.sh sample-code.py sample-markdown.md

# Validate all example files
./validate-helper.sh *.js *.py *.md
```

### Sample Files with Intentional Issues

**sample-code.js** - JavaScript file with common linting and formatting issues:
- Unused variables
- Mixed quotes
- Missing semicolons
- Long lines
- console.log statements
- Inefficient code patterns
- Magic numbers
- Inconsistent spacing
- Use of `var` instead of `const`/`let`

**sample-code.py** - Python file with common linting and formatting issues:
- Unused imports
- Inconsistent spacing
- Long lines
- Missing docstrings
- Inconsistent naming (PascalCase vs snake_case)
- Mutable default arguments
- Bare except clauses
- Missing type hints
- Inefficient patterns
- Comparison to None using `==`
- Not using context managers

**sample-markdown.md** - Markdown file with formatting and prose issues:
- Passive voice
- Missing list item spacing
- Inconsistent list markers
- Code blocks without language tags
- Multiple blank lines
- Extra spaces between words
- Very long lines
- Missing blank lines before headings
- Broken links
- Formatting inconsistencies

## Testing the Output Validator Skill

### Method 1: Using Claude Code

In Claude Code, you can test the skill by asking to validate these files:

```
You: "Use the output-validator skill to check sample-code.js"

You: "Validate all the example files in the output-validator examples directory"

You: "Run validators on sample-code.py and show me what issues are found"
```

### Method 2: Using the Helper Script

Run the helper script directly:

```bash
cd ~/.claude/skills/output-validator/examples

# Check what validation tools are available
./validate-helper.sh --show-tools

# Validate JavaScript example
./validate-helper.sh sample-code.js

# Validate Python example
./validate-helper.sh sample-code.py

# Validate Markdown example
./validate-helper.sh sample-markdown.md

# Validate all examples
./validate-helper.sh sample-code.js sample-code.py sample-markdown.md
```

### Method 3: Manual Validation

Run validators manually to see their output:

**JavaScript/TypeScript:**
```bash
# ESLint (if installed in project)
npx eslint sample-code.js

# Prettier check
npx prettier --check sample-code.js

# Prettier fix
npx prettier --write sample-code.js
```

**Python:**
```bash
# Pylint
pylint sample-code.py

# Flake8
flake8 sample-code.py

# Black check
black --check sample-code.py

# Black fix
black sample-code.py

# mypy
mypy sample-code.py
```

**Markdown:**
```bash
# markdownlint
markdownlint sample-markdown.md

# write-good
write-good sample-markdown.md
```

## Installing Validation Tools

If you want to test with real validators, install them:

### JavaScript/TypeScript Tools

```bash
# Using npm (in a project with package.json)
npm install -D eslint prettier

# Initialize ESLint config
npx eslint --init

# Or install globally
npm install -g eslint prettier
```

### Python Tools

```bash
# Using pip
pip install pylint flake8 black mypy

# Using pip in a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install pylint flake8 black mypy
```

### Markdown Tools

```bash
# Using npm
npm install -g markdownlint-cli write-good

# Or in a project
npm install -D markdownlint-cli write-good
```

### Shell Script Tools

```bash
# On Ubuntu/Debian
sudo apt-get install shellcheck

# On macOS
brew install shellcheck

# On other systems, see: https://github.com/koalaman/shellcheck
```

## Expected Results

When you run validators on the sample files, you should see:

### sample-code.js
- ESLint: ~10-15 issues (unused vars, inconsistent style, etc.)
- Prettier: Formatting issues (can auto-fix)

### sample-code.py
- Pylint: ~15-20 issues (naming, formatting, best practices)
- Flake8: ~10-15 issues (PEP 8 violations)
- Black: Formatting issues (can auto-fix)
- mypy: Type checking issues (missing type hints)

### sample-markdown.md
- markdownlint: ~10-15 issues (formatting, structure)
- write-good: ~5-10 issues (passive voice, weasel words)

## Auto-Fix Demonstration

Some issues can be automatically fixed:

```bash
# JavaScript - auto-fix with ESLint
npx eslint --fix sample-code.js

# JavaScript - auto-format with Prettier
npx prettier --write sample-code.js

# Python - auto-format with Black
black sample-code.py

# Markdown - auto-fix with markdownlint
markdownlint --fix sample-markdown.md
```

After auto-fixing, re-run the validators to see the remaining issues that need manual intervention.

## Learning Objectives

These examples demonstrate:

1. **Issue Detection** - How validators identify problems
2. **Severity Levels** - Errors vs warnings vs style suggestions
3. **Auto-Fix Capabilities** - What can be fixed automatically
4. **Manual Fixes** - What requires human judgment
5. **Multiple Validators** - How different tools catch different issues
6. **Good Practices** - Examples of well-written code for comparison

## Integration Testing

To test the full skill workflow:

1. **Start with issues** - Use the sample files as-is
2. **Run validation** - Use the skill or helper script
3. **Review results** - See all issues categorized by severity
4. **Apply auto-fixes** - Let tools fix formatting/style
5. **Manual fixes** - Fix remaining issues by hand
6. **Re-validate** - Confirm all issues are resolved
7. **Compare** - See the before/after difference

## Customization

You can create your own test files:

1. Write code with intentional issues
2. Run validators to detect them
3. Practice using the skill to fix them
4. Learn what each validator catches

## Troubleshooting

**Validators not found?**
- Make sure they're installed (see installation section above)
- Check that they're in your PATH
- For npm tools, ensure you're in a directory with package.json or use `npx`

**Different results than expected?**
- Validator versions may differ
- Configuration files may be present in parent directories
- Different OSes may have different defaults

**Helper script not working?**
- Make sure it's executable: `chmod +x validate-helper.sh`
- Run with bash explicitly: `bash validate-helper.sh`
- Check that you have bash installed

## Next Steps

After testing with these examples:

1. Try the skill on your own code
2. Set up validators in your projects
3. Configure them to match your team's standards
4. Integrate validation into your workflow
5. Set up pre-commit hooks for automatic validation

---

Happy validating! 🚀