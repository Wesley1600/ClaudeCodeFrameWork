# Output Validator Skill

A comprehensive skill for validating code, documents, and configurations against quality standards using linters, formatters, type checkers, and test runners.

## Quick Start

### Invoking the Skill

Use the skill command in Claude Code:
```
/skill output-validator
```

Or simply ask Claude to validate your code:
- "Validate my code"
- "Check this file for errors"
- "Run linters on my changes"
- "Validate before commit"

## What It Does

The Output Validator skill automatically:

1. **Detects file types** - Identifies what kind of files you're working with
2. **Finds available tools** - Checks which validators are installed
3. **Runs appropriate validators** - Executes the right tools for each file type
4. **Presents clear results** - Shows errors, warnings, and suggestions
5. **Offers auto-fixes** - Applies automated fixes when safe
6. **Provides guidance** - Helps fix issues that require manual intervention

## Supported Languages & Tools

### Languages
- JavaScript/TypeScript (ESLint, Prettier, tsc)
- Python (Pylint, Flake8, Black, mypy)
- Go (golint, gofmt, go vet)
- Rust (clippy, rustfmt)
- Ruby (RuboCop, Reek)
- Shell (shellcheck, shfmt)

### Document Types
- Markdown (markdownlint, write-good)
- JSON (jsonlint)
- YAML (yamllint)

### Configuration Files
- Dockerfile (hadolint)
- CSS/SCSS (stylelint)

## Usage Examples

### Example 1: Validate a Single File
```
You: "Validate src/app.ts"

Claude will:
- Run ESLint to check code quality
- Run Prettier to check formatting
- Run TypeScript compiler for type errors
- Present all issues found
- Offer to auto-fix formatting issues
```

### Example 2: Validate Before Committing
```
You: "Validate my staged changes"

Claude will:
- Get list of staged files
- Run appropriate validators for each file type
- Show combined results
- Help fix all issues before commit
```

### Example 3: Full Project Validation
```
You: "Run all validators on the project"

Claude will:
- Look for package.json scripts (lint, test)
- Run project-level validation commands
- Check CI/CD configs
- Generate comprehensive report
```

### Example 4: Validate Documentation
```
You: "Check README.md for issues"

Claude will:
- Run markdownlint for structure
- Check grammar and readability
- Verify links and code blocks
- Offer formatting fixes
```

## Validation Levels

### Quick
Basic syntax and formatting checks - fast and lightweight

### Standard (Default)
Linting and type checking - catches most issues

### Thorough
Full suite including tests and integration checks

### CI Mode
Matches exactly what your CI/CD pipeline runs

## Auto-Fix Capabilities

The skill can automatically fix:
- Code formatting (Prettier, Black, gofmt)
- Import sorting (isort)
- Simple linting issues (ESLint --fix)
- Markdown formatting
- Trailing whitespace
- Missing semicolons
- Indentation issues

You'll always be asked before auto-fixes are applied.

## Configuration

The skill respects your project's existing configuration:
- `.eslintrc`, `.prettierrc` for JavaScript/TypeScript
- `pyproject.toml`, `.flake8` for Python
- `.markdownlint.json` for Markdown
- And more...

## Installation

The skill is ready to use! If validation tools are missing, Claude will:
1. Detect which tools are needed
2. Suggest installation commands
3. Offer to install them for you

Example:
```bash
# JavaScript/TypeScript
npm install -D eslint prettier

# Python
pip install pylint flake8 black mypy

# Markdown
npm install -D markdownlint-cli write-good
```

## Integration with Workflow

### Pre-commit Hooks
Set up automatic validation before commits:
```bash
# .git/hooks/pre-commit
#!/bin/bash
npm run lint
npm test
```

### Editor Integration
Install editor extensions for real-time feedback:
- VS Code: ESLint, Prettier, Pylint
- Enable format-on-save
- See issues as you type

### CI/CD Pipeline
Use the same validators locally and in CI:
```yaml
# .github/workflows/validate.yml
- name: Run Validators
  run: |
    npm run lint
    npm run typecheck
    npm test
```

## Tips for Best Results

1. **Validate early and often** - Catch issues as you write
2. **Fix errors before warnings** - Prioritize critical issues
3. **Use auto-fix for style** - Let tools handle formatting
4. **Review logic issues manually** - Don't auto-fix semantic problems
5. **Run tests after fixes** - Ensure changes don't break functionality

## Troubleshooting

**Validator not found?**
- Check if it's installed: `command -v eslint`
- Install it: `npm install -D eslint`
- Or use project version: `npx eslint`

**Too many issues?**
- Start with errors only
- Fix issues in batches
- Use auto-fix for bulk formatting

**Conflicting rules?**
- Check for multiple config files
- Align ESLint and Prettier settings
- Use shared configs

**Validation too slow?**
- Exclude build/dependency directories
- Use `.eslintignore`, `.prettierignore`
- Validate only changed files

## Advanced Usage

### Custom Validators
Add project-specific validation:
```json
// package.json
{
  "scripts": {
    "validate": "./scripts/custom-validate.sh"
  }
}
```

### Parallel Validation
Run multiple validators at once for faster results

### Incremental Validation
Validate only changed files in large projects

### JSON Output
Export results for integration with other tools

## Learn More

See the full skill documentation in `SKILL.md` for:
- Complete workflow details
- Advanced features
- All supported tools
- Custom configuration options
- Integration patterns

## Support

If you encounter issues:
1. Check that validators are installed
2. Verify configuration files are valid
3. Review error messages for specific guidance
4. Ask Claude for help: "Why is this validator failing?"

---

**Version**: 1.0.0
**Last Updated**: 2025-11-18
**Author**: Claude Code Skills