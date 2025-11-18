# Common Variables Reference

This document lists commonly used variables across templates and their typical meanings.

## General Context Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `user_name` | String | Name of the user | "Alice Johnson" |
| `date` | String | Current date | "2025-11-18" |
| `project_name` | String | Name of the project | "Claude Code" |
| `task_name` | String | Name of the current task | "Authentication Refactor" |

## File & Code Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `file_path` | String | Path to file being analyzed | "src/components/Header.tsx" |
| `file_name` | String | Name of file without path | "Header.tsx" |
| `code_content` | String/Block | Actual code content | "function foo() {...}" |
| `function_name` | String | Name of function | "calculateTotal" |
| `class_name` | String | Name of class | "UserController" |
| `component_name` | String | Name of component | "Header" |
| `line_number` | Number | Line number reference | "42" |

## Review & Analysis Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `reviewer_name` | String | Name of reviewer | "Engineering Team" |
| `review_type` | String | Type of review | "security audit" |
| `focus_areas` | String | What to focus on | "performance, security" |
| `severity_level` | String | Issue severity | "high, medium, low" |
| `analysis_type` | String | Type of analysis | "performance analysis" |
| `style_guide` | String | Coding style guide | "Google Style Guide" |

## Documentation Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `content` | String/Block | Content to process | "Full documentation text" |
| `content_type` | String | Type of content | "API documentation" |
| `target_audience` | String | Intended audience | "developers" |
| `max_length` | Number | Maximum output length | "500" |
| `format` | String | Output format | "markdown" |

## Bug & Issue Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `bug_description` | String | Bug description | "Login fails on Safari" |
| `reproduction_steps` | String/List | How to reproduce | "1. Open Safari\n2. ..." |
| `severity` | String | Bug severity | "critical" |
| `affected_component` | String | Which component | "AuthService" |
| `user_impact` | String | Impact on users | "Cannot log in" |
| `expected_behavior` | String | What should happen | "Login succeeds" |
| `actual_behavior` | String | What actually happens | "Error message shown" |

## Testing Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `test_type` | String | Type of test | "unit test" |
| `coverage_target` | Number | Coverage percentage | "80" |
| `test_framework` | String | Testing framework | "Jest" |
| `test_file` | String | Test file path | "src/__tests__/auth.test.js" |

## Report Variables

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `report_type` | String | Type of report | "monthly" |
| `department` | String | Department name | "Engineering" |
| `time_period` | String | Time period | "Q4 2024" |
| `metrics` | String/List | Metrics to include | "velocity, quality, bugs" |

## Optional Variable Defaults

Common default values for optional variables:

```
{tone:professional}
{format:markdown}
{max_length:500}
{severity:medium}
{impact:moderate}
{priority:normal}
{status:pending}
{confidence:medium}
{verbosity:detailed}
{include_examples:yes}
{style_guide:standard coding practices}
{target_audience:general}
{output_format:structured}
```

## Variable Naming Conventions

### Good Variable Names
- Descriptive: `{analysis_type}` not `{type}`
- Lowercase: `{user_name}` not `{UserName}`
- Underscores: `{max_length}` not `{maxLength}` or `{max-length}`
- Specific: `{code_file_path}` not `{path}`

### Bad Variable Names
- Too short: `{x}`, `{val}`, `{tmp}`
- Too generic: `{data}`, `{info}`, `{stuff}`
- Wrong case: `{UserName}`, `{PROJECT_NAME}`
- Special chars: `{user-name}`, `{user.name}`

## Context Extraction Patterns

### From User Messages
```
"Review the header component" → {component_name} = "header"
"Use John as the reviewer" → {reviewer_name} = "John"
"Make it brief" → {max_length} = "200"
"High priority bug" → {severity} = "high"
```

### From File Paths
```
File: src/components/auth/LoginForm.tsx
→ {file_path} = "src/components/auth/LoginForm.tsx"
→ {file_name} = "LoginForm.tsx"
→ {component_name} = "LoginForm"
→ {module_name} = "auth"
```

### From Code Context
```
Reviewing function: async calculateTotal(items) { ... }
→ {function_name} = "calculateTotal"
→ {is_async} = "yes"
→ {parameter_count} = "1"
```

### From Git Context
```
Current branch: feature/user-auth
→ {branch_name} = "feature/user-auth"
→ {feature_name} = "user-auth"

Latest commit: "Fix login bug"
→ {commit_message} = "Fix login bug"
```

## Variable Validation

### Type Validation
- **Strings**: Any text value
- **Numbers**: Validate numeric format (e.g., `{max_length}` should be a number)
- **Enums**: Check against allowed values (e.g., `{severity}` in [low, medium, high, critical])
- **Paths**: Validate file path format
- **Dates**: Validate date format (ISO 8601 recommended)

### Content Validation
- **Email**: Check email format for `{email}` variables
- **URLs**: Validate URL format for `{url}` variables
- **Code blocks**: Preserve formatting for `{code_content}`
- **Lists**: Handle comma-separated or newline-separated lists

### Security Validation
For potentially sensitive contexts:
- Escape special characters in `{user_input}` variables
- Validate file paths don't escape project directory
- Sanitize SQL/code injection risks
- Warn on potentially unsafe patterns

## Custom Variable Definitions

When creating templates, document your variables:

```
# Custom Template Name
# Required variables: var1, var2, var3
# Optional variables: var4:default1, var5:default2
#
# Variable Descriptions:
# - var1: Description of what this represents
# - var2: Description of what this represents
# - var3: Description of what this represents
# - var4: Description (default: default1)
# - var5: Description (default: default2)
```

This helps users understand what values to provide.
