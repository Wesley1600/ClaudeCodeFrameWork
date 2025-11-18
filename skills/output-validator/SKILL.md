---
name: output-validator
description: Validates outputs (code, documents, configurations) against predefined criteria using linters, formatters, grammar checkers, type checkers, and test runners. Use after generating code or documents to ensure quality and catch issues before committing.
---

# Output Validator Skill

This skill validates outputs against predefined quality criteria using various validation tools based on file type and content. It identifies issues, provides detailed feedback, and offers automated fixes when possible.

## Overview

The Output Validator skill provides comprehensive validation for:
- **Code files**: Linting, formatting, type checking
- **Documents**: Grammar, spelling, markdown linting
- **Configuration files**: Schema validation, syntax checking
- **Test results**: Running and verifying test suites

## Supported Validators

### JavaScript/TypeScript
- **ESLint**: Code quality and style linting
- **Prettier**: Code formatting
- **TypeScript Compiler (tsc)**: Type checking
- **Jest/Mocha/Vitest**: Test runners

### Python
- **Pylint**: Code analysis
- **Flake8**: Style guide enforcement
- **Black**: Code formatting
- **mypy**: Static type checking
- **pytest**: Test runner
- **isort**: Import sorting

### Go
- **golint/golangci-lint**: Code linting
- **gofmt**: Code formatting
- **go vet**: Code correctness
- **go test**: Test runner

### Ruby
- **RuboCop**: Code analysis and formatting
- **Reek**: Code smell detection

### Rust
- **clippy**: Linting
- **rustfmt**: Formatting
- **cargo test**: Test runner

### Shell Scripts
- **shellcheck**: Shell script linting
- **shfmt**: Shell script formatting

### Markdown/Documentation
- **markdownlint**: Markdown style checking
- **write-good**: Grammar and prose linting
- **vale**: Prose linting with custom styles

### JSON/YAML
- **jsonlint**: JSON validation
- **yamllint**: YAML validation

### Docker
- **hadolint**: Dockerfile linting

### CSS/SCSS
- **stylelint**: CSS/SCSS linting
- **prettier**: Formatting

## Workflow

When this skill is invoked, follow this comprehensive validation workflow:

### 1. **Identify Validation Targets**

Ask the user what they want to validate, or automatically detect from context:
- Specific files or directories
- Recently modified files
- All files in a project
- Staged git changes
- Generated output from previous tasks

### 2. **Detect File Types and Available Tools**

For each file or directory:
- Detect file extensions and types
- Check which validation tools are installed
- Look for project-specific configuration files (.eslintrc, .prettierrc, pyproject.toml, etc.)
- Identify package.json scripts that might run validators

### 3. **Check Tool Availability**

Before running validators, check which tools are available:

```bash
# Example checks
command -v eslint >/dev/null 2>&1 && echo "ESLint: available"
command -v pylint >/dev/null 2>&1 && echo "Pylint: available"
command -v prettier >/dev/null 2>&1 && echo "Prettier: available"
```

If tools are missing but needed:
- Check if they're available as project dependencies (in node_modules, venv, etc.)
- Suggest installation commands if not found
- Offer to install them if user confirms

### 4. **Run Validators**

Execute appropriate validators based on file types:

#### For JavaScript/TypeScript:
```bash
# ESLint
npx eslint [files] --format=stylish

# Prettier check
npx prettier --check [files]

# TypeScript
npx tsc --noEmit

# Tests
npm test
```

#### For Python:
```bash
# Pylint
pylint [files] --output-format=text

# Flake8
flake8 [files]

# Black check
black --check [files]

# mypy
mypy [files]

# pytest
pytest -v
```

#### For Markdown:
```bash
# markdownlint
markdownlint [files]

# write-good
write-good [files]
```

#### For Shell Scripts:
```bash
# shellcheck
shellcheck [files]
```

### 5. **Parse and Categorize Results**

Organize validation results by severity:
- **Errors**: Critical issues that must be fixed
- **Warnings**: Issues that should be reviewed
- **Info/Style**: Suggestions for improvement

For each issue, capture:
- File path and line number
- Rule/check that failed
- Description of the issue
- Suggested fix (if available)

### 6. **Present Results to User**

Format results clearly and concisely:

```
Validation Results for [file/directory]:

✗ ERRORS (3)
  src/app.ts:42:5 - 'variable' is assigned but never used (no-unused-vars)
  src/utils.ts:15:12 - Missing semicolon (semi)

⚠ WARNINGS (2)
  src/config.js:8:1 - Line exceeds 100 characters (max-len)

ℹ INFO (1)
  README.md:23 - Use contractions sparingly (write-good)

Summary: 3 errors, 2 warnings, 1 info
```

Group by file if multiple files were validated.

### 7. **Offer Auto-Fix Options**

If validators support auto-fixing, offer to apply fixes:

```bash
# ESLint auto-fix
npx eslint [files] --fix

# Prettier auto-fix
npx prettier --write [files]

# Black auto-fix
black [files]

# Go format
gofmt -w [files]
```

Ask user:
- "Would you like me to auto-fix the [N] issues that can be automatically corrected?"
- Show which issues can be auto-fixed vs. which require manual intervention

### 8. **Apply Fixes (if approved)**

If user approves auto-fixes:
1. Run auto-fix commands
2. Re-run validators to confirm fixes
3. Show before/after comparison
4. Report any remaining issues that need manual fixes

### 9. **Manual Fix Assistance**

For issues that can't be auto-fixed:
- Explain each issue clearly
- Show the problematic code with context
- Suggest specific corrections
- Offer to make the changes if user approves

### 10. **Final Validation**

After all fixes are applied:
- Run validators one more time
- Confirm all critical issues are resolved
- Provide summary of changes made
- Suggest next steps (commit, test, etc.)

## Special Cases

### Running Tests
When validation includes running tests:
- Run the appropriate test command (npm test, pytest, go test, etc.)
- Parse test results for failures
- Show failing test names and error messages
- Offer to help fix failing tests

### Configuration-Based Validation
If project has custom validation configs:
- Respect .eslintrc, .prettierrc, pyproject.toml, etc.
- Don't suggest conflicting rules
- Maintain project's existing code style

### CI/CD Integration
Check for CI/CD validation scripts:
- Look for .github/workflows, .gitlab-ci.yml, etc.
- Suggest running the same checks locally
- Ensure local validation matches CI requirements

## Error Handling

### Tool Not Found
```
⚠ ESLint not found. Would you like me to:
  1. Install it as a dev dependency: npm install -D eslint
  2. Skip ESLint validation
  3. Use a different linter
```

### Validation Failures
If validators fail to run:
- Check for syntax errors in config files
- Verify tool versions are compatible
- Suggest debugging steps

### Large Number of Issues
If >50 issues found:
- Show summary statistics by category
- Ask if user wants to see all issues or just errors
- Suggest focusing on critical errors first
- Offer to fix issues in batches

## Best Practices

1. **Always run validators before committing**: Catch issues early
2. **Respect project conventions**: Use existing configs
3. **Fix errors before warnings**: Prioritize critical issues
4. **Auto-fix when safe**: Use auto-fix for formatting/style
5. **Manual review for logic**: Don't auto-fix semantic issues
6. **Run tests after fixes**: Ensure fixes don't break functionality
7. **Incremental validation**: Validate as you write, not just at the end

## Examples

### Example 1: Validate a Single File
```
User: "Validate the code I just wrote in src/app.ts"

Actions:
1. Detect file type: TypeScript
2. Check for ESLint, Prettier, TypeScript compiler
3. Run validators:
   - npx eslint src/app.ts
   - npx prettier --check src/app.ts
   - npx tsc --noEmit src/app.ts
4. Present results with line numbers and descriptions
5. Offer auto-fix for formatting issues
6. Manually address logic issues
```

### Example 2: Validate Before Commit
```
User: "Validate all my changes before I commit"

Actions:
1. Get list of staged files: git diff --cached --name-only
2. Group files by type (JS, Python, Markdown, etc.)
3. Run appropriate validators for each type
4. Show combined results
5. Auto-fix formatting issues if approved
6. Confirm all errors resolved before allowing commit
```

### Example 3: Full Project Validation
```
User: "Run all validators on the entire project"

Actions:
1. Look for package.json scripts (lint, test, format)
2. Run project-level commands (npm run lint, npm test)
3. Check for CI/CD configs and run same checks
4. Generate comprehensive validation report
5. Prioritize errors by severity and file
6. Create action plan for fixing issues
```

### Example 4: Document Validation
```
User: "Check this README.md for issues"

Actions:
1. Run markdownlint for structure/syntax
2. Run write-good for grammar and readability
3. Check for broken links
4. Verify code blocks have language tags
5. Present issues with suggestions
6. Offer to fix markdown formatting issues
```

## Integration with Development Workflow

### Pre-commit Hook Integration
Suggest setting up pre-commit hooks to run validators automatically:

```bash
# Example .git/hooks/pre-commit
#!/bin/bash
npm run lint
npm test
```

### Editor Integration
Recommend editor extensions for real-time validation:
- VS Code: ESLint, Prettier, Pylint extensions
- Configure format-on-save
- Enable inline error highlighting

### Continuous Validation
During development sessions:
- Validate after significant code changes
- Run quick checks frequently
- Run full validation before major commits
- Always validate before creating pull requests

## Advanced Features

### Custom Validation Rules
Support custom validation scripts:
- Look for validate.sh, check.sh, or similar scripts
- Run custom validation commands from package.json
- Support project-specific quality gates

### Validation Profiles
Maintain different validation levels:
- **Quick**: Basic syntax and formatting
- **Standard**: Linting and type checking
- **Thorough**: Full suite including tests and integration checks
- **CI**: Match exactly what CI/CD runs

### Incremental Validation
For large projects:
- Validate only changed files
- Use git diff to identify changes
- Cache validation results
- Re-run only affected validators

### Parallel Validation
Run multiple validators concurrently:
- Execute independent validators in parallel
- Aggregate results when all complete
- Improve validation speed for large projects

## Output Formats

### Terminal Output (Default)
Colorized, human-readable format with symbols and clear grouping

### JSON Output
For integration with other tools:
```json
{
  "summary": {
    "errors": 3,
    "warnings": 2,
    "info": 1
  },
  "results": [
    {
      "file": "src/app.ts",
      "line": 42,
      "column": 5,
      "severity": "error",
      "rule": "no-unused-vars",
      "message": "'variable' is assigned but never used"
    }
  ]
}
```

### Markdown Report
For documentation or issue tracking:
```markdown
# Validation Report

**Date**: 2025-11-18
**Files Checked**: 15
**Total Issues**: 6

## Summary
- ✗ Errors: 3
- ⚠ Warnings: 2
- ℹ Info: 1

## Issues by File
...
```

## Troubleshooting

### Common Issues

**Validators hanging or taking too long:**
- Check for large files or directories
- Exclude node_modules, venv, build directories
- Use .eslintignore, .prettierignore files

**Conflicting rules between tools:**
- Configure tools to work together
- Disable conflicting rules in one tool
- Use consistent config files

**False positives:**
- Add ignore comments for specific lines
- Configure rules to match project needs
- Update rule configurations in config files

**Tool version mismatches:**
- Use exact versions in package.json
- Document required tool versions
- Consider using Docker for consistent environments

## Summary

The Output Validator skill provides comprehensive, automated quality checking for code and documents. It:
- ✓ Detects and runs appropriate validators automatically
- ✓ Presents clear, actionable feedback
- ✓ Offers automated fixes when possible
- ✓ Integrates with existing development workflows
- ✓ Supports multiple languages and file types
- ✓ Helps maintain consistent code quality

**When to use this skill:**
- After writing new code
- Before committing changes
- When refactoring
- Before creating pull requests
- During code reviews
- When onboarding to a new project
- To enforce project quality standards