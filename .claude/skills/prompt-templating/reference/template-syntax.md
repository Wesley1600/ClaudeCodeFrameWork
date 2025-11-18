# Template Syntax Guide

Complete reference for the prompt templating syntax.

## Basic Syntax

### Simple Variable
```
{variable_name}
```
- Replaced with the value of `variable_name`
- If not provided and no default, treated as required
- Variable names: lowercase, alphanumeric, underscore only

**Examples:**
```
Hello {user_name}!
Review file: {file_path}
Analysis type: {analysis_type}
```

### Optional Variable with Default
```
{variable_name:default_value}
```
- If `variable_name` not provided, uses `default_value`
- Default value can contain spaces, but not colons
- For colons in defaults, see escaping section

**Examples:**
```
Tone: {tone:professional}
Maximum length: {max_length:500 words}
Format: {output_format:markdown with code blocks}
```

## Variable Naming Rules

### Valid Names
```
{user_name}        ✓ Lowercase with underscore
{file_path}        ✓ Descriptive
{analysis_type}    ✓ Multi-word with underscore
{max_length}       ✓ Clear meaning
{severity1}        ✓ Numbers allowed
{component_name_v2}✓ Complex but valid
```

### Invalid Names
```
{UserName}         ✗ Capital letters
{user-name}        ✗ Hyphens not allowed
{user.name}        ✗ Dots not allowed
{user name}        ✗ Spaces not allowed
{user@name}        ✗ Special characters
{2fast}            ✗ Cannot start with number
```

### Regex Pattern
```regex
^[a-z][a-z0-9_]*$
```
- Must start with lowercase letter
- Can contain lowercase letters, digits, underscores
- No spaces, no special characters

## Escaping

### Literal Braces
To include literal `{` or `}` in output:
```
Use \{this\} to show braces literally
```
Output:
```
Use {this} to show braces literally
```

### Colons in Default Values
For defaults containing colons, use quotes:
```
{timestamp:"2024-01-15 10:30:00"}
{url:"https://example.com"}
```

Or escape:
```
{timestamp:2024-01-15 10\:30\:00}
```

## Whitespace Handling

### No Spaces in Braces
```
{variable_name}     ✓ Correct
{ variable_name }   ✗ Invalid
{ variable_name}    ✗ Invalid
{variable_name }    ✗ Invalid
```

### Whitespace in Values
Whitespace outside braces is preserved:
```
Hello {name},

Welcome to {project}!
```

If `name = "Alice"` and `project = "Claude"`:
```
Hello Alice,

Welcome to Claude!
```

### Indentation Preservation
Template indentation is preserved:
```
class {class_name}:
    def {method_name}(self):
        return {return_value}
```

## Multi-line Variables

### Content Blocks
Variables can contain multi-line content:
```
Code to review:
{code_content}
```

If `code_content` is:
```python
def hello():
    print("world")
```

Result:
```
Code to review:
def hello():
    print("world")
```

### Preserving Formatting
Original formatting in variable values is preserved:
- Line breaks
- Indentation
- Spacing

## Default Value Syntax

### Simple Defaults
```
{severity:medium}
{format:markdown}
{max_lines:100}
```

### Defaults with Spaces
```
{reviewer_name:Engineering Team}
{style_guide:Google Python Style Guide}
{focus:key points and takeaways}
```

### Defaults with Special Characters
```
{separator:, }              (comma-space)
{bullet:• }                 (bullet point)
{format:markdown with **bold**}
```

### Empty Defaults
```
{optional_note:}            (empty string)
{additional_context:None}   (explicit "None")
```

## Variable Extraction

### From Template to Variable List

Template:
```
Review {file_path} for {issue_type}.
Severity: {severity:medium}
Assigned to: {assignee}
```

Extracted variables:
- **Required**: `file_path`, `issue_type`, `assignee`
- **Optional**: `severity` (default: "medium")

### Parsing Algorithm
```
1. Find all {text} patterns
2. For each pattern:
   a. Check for colon (:)
   b. If colon present:
      - Left of colon = variable name
      - Right of colon = default value
      - Mark as optional
   c. If no colon:
      - Entire text = variable name
      - Mark as required
3. Validate variable names
4. Build variable list
```

## Advanced Patterns

### Nested Defaults (Not Supported)
```
{var1:{var2:default}}  ✗ Not supported
```

Use separate variables instead:
```
{var1:default1}
{var2:default2}
```

### Conditional Inclusion (Optional Enhancement)
Basic templates don't support conditionals, but can be added:
```
{?if:show_advanced}
Advanced section here
{?endif}
```

This is an optional enhancement. Start with basic replacement.

### Lists (Optional Enhancement)
```
{?foreach:item in items}
- {item}
{?endforeach}
```

Also optional. Start with basic functionality.

## Common Patterns

### Code Review Template
```
# Review: {file_path}
Reviewer: {reviewer_name:Team}
Focus: {focus_areas}

{code_content}

Check for:
- {check1:bugs}
- {check2:performance}
- {check3:security}
```

### Analysis Template
```
Analyze {subject} for {purpose}.

Depth: {analysis_depth:detailed}
Format: {output_format:structured markdown}

Provide:
1. {section1:Overview}
2. {section2:Detailed Analysis}
3. {section3:Recommendations}
```

### Report Template
```
# {report_type:Monthly} Report
Department: {department}
Period: {time_period}

Metrics:
{metrics_content}

Summary: {summary:To be generated}
```

## Validation Rules

### Variable Name Validation
```python
import re

def is_valid_variable_name(name):
    pattern = r'^[a-z][a-z0-9_]*$'
    return re.match(pattern, name) is not None

# Valid
is_valid_variable_name("user_name")      # True
is_valid_variable_name("file_path")      # True

# Invalid
is_valid_variable_name("UserName")       # False
is_valid_variable_name("user-name")      # False
is_valid_variable_name("2fast")          # False
```

### Template Validation
Before filling:
1. Extract all variables
2. Validate each variable name
3. Check for required variables
4. Warn if any required variable missing
5. Only proceed if all required variables have values

## Error Messages

### Invalid Variable Name
```
⚠️  Warning: Invalid variable name at line 5
Found: {User-Name}
Expected: {user_name}
Variable names must be lowercase with underscores only.
```

### Missing Required Variable
```
❌ Error: Missing required variable
Variable: {file_path}
Description: Path to the file to analyze
Please provide this value to continue.
```

### Malformed Syntax
```
⚠️  Warning: Malformed placeholder at line 3
Found: {variable name with spaces}
Spaces are not allowed in variable names.
Did you mean: {variable_name_with_underscores}?
```

## Best Practices

### 1. Use Descriptive Names
```
Good: {analysis_type}, {target_audience}, {max_word_count}
Bad:  {type}, {audience}, {max}
```

### 2. Provide Sensible Defaults
```
Good: {format:markdown}, {severity:medium}, {verbose:no}
Bad:  {format:fmt}, {severity:?}, {verbose:0}
```

### 3. Document Required vs Optional
At top of template:
```
# Required: file_path, analysis_type
# Optional: format:markdown, depth:detailed
```

### 4. Group Related Variables
```
# File Variables
{file_path}
{file_name}
{file_type}

# Review Variables
{reviewer_name:Team}
{review_type:general}
{severity:all levels}
```

### 5. Consistent Naming Scheme
Pick a convention and stick to it:
```
# Good (consistent)
{user_name}
{user_email}
{user_role}

# Bad (inconsistent)
{userName}
{user_email}
{UserRole}
```

## Template File Format

### Recommended Structure
```
# Template Name
# Required variables: var1, var2
# Optional variables: var3:default3, var4:default4
#
# Description: What this template does
# Use case: When to use this template
#
# Example usage:
#   var1 = "example1"
#   var2 = "example2"

[Template content here with {variables}]
```

### File Extension
- `.txt` - Plain text templates
- `.md` - Markdown templates
- `.template` - Generic templates

All formats work the same way.

## Summary

**Key Points:**
1. Variables: `{name}` for required, `{name:default}` for optional
2. Names: lowercase, alphanumeric, underscores only
3. No spaces inside braces
4. Validate before filling
5. Preserve formatting and indentation
6. Warn on missing required variables

**Processing Order:**
1. Parse template
2. Extract variables
3. Validate names
4. Check for required variables
5. Gather values
6. Warn if missing
7. Fill template
8. Return result
