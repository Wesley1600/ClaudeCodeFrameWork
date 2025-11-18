# Prompt Templating Skill

A Claude Code skill for creating consistent, reusable prompts with dynamic variable substitution.

## Overview

This skill enables you to:
- Create prompt templates with placeholders like `{variable_name}`
- Fill templates with values from task context
- Validate required variables before execution
- Use default values for optional variables
- Maintain consistent prompt styles across tasks

## Quick Start

### Using a Built-in Template

```
You: Use the code-review template to review src/auth.js for security issues

Claude: [Uses prompt-templating skill]
- Loads templates/code-review.txt
- Extracts required variables
- Fills in from context:
  - file_path = "src/auth.js"
  - focus_areas = "security issues"
  - code_content = [reads from file]
- Applies defaults for optional variables
- Outputs filled template
```

### Creating a Custom Template

```
You: Create a summarization template for my weekly reports

Claude: [Uses prompt-templating skill]
- Asks what variables you need
- Creates custom template
- Saves to templates/
- Shows example usage
```

## Features

### ✓ Variable Substitution
Replace `{placeholders}` with actual values from context

### ✓ Required Variable Validation
Warns if critical variables are missing:
```
⚠️  Missing Required Variables:
- {user_name}: Name of the user
- {file_path}: Path to file being analyzed

Please provide these values to continue.
```

### ✓ Optional Variables with Defaults
```
{severity:medium}        → Uses "medium" if not provided
{format:markdown}        → Uses "markdown" if not provided
{max_length:500}         → Uses "500" if not provided
```

### ✓ Context-Aware
Automatically extracts variables from:
- User messages
- File paths and content
- Previous conversation
- Git context
- Code being analyzed

## Directory Structure

```
.claude/skills/prompt-templating/
├── SKILL.md                    # Main skill instructions
├── README.md                   # This file
├── templates/                  # Pre-built templates
│   ├── code-review.txt
│   ├── summarization.txt
│   ├── analysis.txt
│   └── bug-report.txt
├── examples/                   # Usage examples
│   └── basic-usage.md
└── reference/                  # Documentation
    ├── variables.md            # Common variables reference
    └── template-syntax.md      # Syntax guide
```

## Built-in Templates

### code-review.txt
Review code with configurable focus areas and style guides.

**Required:** `file_path`, `code_content`, `focus_areas`
**Optional:** `reviewer_name`, `style_guide`, `severity_level`

### summarization.txt
Summarize documents with target audience and length constraints.

**Required:** `content`, `content_type`
**Optional:** `max_length`, `target_audience`, `focus`

### analysis.txt
General-purpose analysis template.

**Required:** `subject`, `analysis_type`
**Optional:** `depth`, `format`, `include_examples`

### bug-report.txt
Investigate bugs with structured format.

**Required:** `bug_description`, `reproduction_steps`
**Optional:** `severity`, `affected_component`, `user_impact`

## Template Syntax

### Basic Variable
```
{variable_name}
```
Required if not provided.

### Optional Variable with Default
```
{variable_name:default_value}
```
Uses default if not provided.

### Escaping Literal Braces
```
\{not_a_variable\}
```
Outputs: `{not_a_variable}`

## Example Usage

### Example 1: Code Review
```
Template: templates/code-review.txt

User provides:
- File: "src/components/Header.tsx"
- Focus: "React hooks usage"

Skill fills:
- {file_path} = "src/components/Header.tsx"
- {code_content} = [reads file content]
- {focus_areas} = "React hooks usage"
- {reviewer_name} = "Team" (default)
- {style_guide} = "standard coding practices" (default)

Result: Complete code review prompt ready to use
```

### Example 2: Document Summary
```
Template: templates/summarization.txt

User provides:
- Content: [documentation text]
- Type: "API documentation"
- Audience: "frontend developers"
- Max length: "300 words"

Skill fills:
- {content} = [documentation text]
- {content_type} = "API documentation"
- {target_audience} = "frontend developers"
- {max_length} = "300 words"

Result: Customized summarization prompt
```

### Example 3: Missing Variables
```
Template: templates/bug-report.txt

User provides:
- "Investigate the timeout issue"

Required but missing:
- {bug_description} - needs detail
- {reproduction_steps} - needs steps

Skill warns:
⚠️  Missing Required Variables:
- {bug_description}: Detailed description of the bug
- {reproduction_steps}: Steps to reproduce the issue

Please provide these values to continue.

User provides missing info, skill continues
```

## Creating Custom Templates

### Template File Format

```
# Template Name
# Required variables: var1, var2
# Optional variables: var3:default3, var4:default4

[Your template content with {variables}]
```

### Example Custom Template

```
# Pull Request Template
# Required: pr_title, changes_summary
# Optional: related_issue:none, breaking_changes:no

## {pr_title}

### Summary
{changes_summary}

### Related Issue
{related_issue:None}

### Breaking Changes
{breaking_changes:No breaking changes}

### Checklist
- [ ] Tests added
- [ ] Documentation updated
- [ ] Reviewed by team
```

## Common Variables

See `reference/variables.md` for complete list.

**General:**
- `{user_name}`, `{project_name}`, `{date}`

**File & Code:**
- `{file_path}`, `{code_content}`, `{function_name}`

**Review:**
- `{reviewer_name}`, `{focus_areas}`, `{severity}`

**Documentation:**
- `{content}`, `{target_audience}`, `{max_length}`

## Best Practices

### 1. Descriptive Variable Names
```
Good: {analysis_type}, {max_word_count}
Bad:  {type}, {max}
```

### 2. Sensible Defaults
```
Good: {format:markdown}, {severity:medium}
Bad:  {format:?}, {severity:unknown}
```

### 3. Document Templates
Include header comment listing:
- Required variables
- Optional variables with defaults
- Example usage

### 4. Validate Early
Check for missing required variables BEFORE filling template.

### 5. Preserve Context
Keep templates focused on structure, let context provide details.

## Workflow

1. **Identify Need** - User requests templated prompt
2. **Load Template** - From `templates/` or custom path
3. **Parse Variables** - Extract `{variables}` from template
4. **Gather Values** - From user, context, files
5. **Validate** - Check all required variables present
6. **Warn if Missing** - Stop and ask user for missing values
7. **Fill Template** - Replace placeholders with values
8. **Output** - Return completed prompt

## Advanced Features (Optional)

### Conditional Sections
```
{?if:variable_name}
Include this only if variable_name is provided
{?endif}
```

### List Iteration
```
{?foreach:item in items}
- {item}
{?endforeach}
```

**Note:** These are optional enhancements. Basic replacement is the core functionality.

## Files Reference

- **SKILL.md** - Main skill instructions for Claude
- **README.md** - This documentation
- **templates/*.txt** - Pre-built prompt templates
- **examples/basic-usage.md** - Usage examples
- **reference/variables.md** - Common variables guide
- **reference/template-syntax.md** - Complete syntax reference

## Getting Help

1. See `examples/basic-usage.md` for practical examples
2. See `reference/template-syntax.md` for syntax details
3. See `reference/variables.md` for common variables
4. Check existing templates in `templates/` for patterns

## Version

**v1.0.0** - Initial release

## License

Part of Claude Code skills collection.
