# Basic Usage Examples

## Example 1: Simple Variable Replacement

**Template:**
```
Hello {user_name}, welcome to {project_name}!
```

**Variables:**
- `user_name` = "Alice"
- `project_name` = "Claude Code"

**Result:**
```
Hello Alice, welcome to Claude Code!
```

---

## Example 2: Optional Variables with Defaults

**Template:**
```
Generate a {report_type:monthly} report for {department}.
Format: {format:PDF}
```

**Provided Variables:**
- `department` = "Engineering"

**Result:**
```
Generate a monthly report for Engineering.
Format: PDF
```

*Note: `report_type` and `format` used their default values*

---

## Example 3: Missing Required Variable (Error Case)

**Template:**
```
Review code in {file_path} by {reviewer_name}.
```

**Provided Variables:**
- `file_path` = "src/app.js"

**Result:**
```
⚠️  Missing Required Variables:
- {reviewer_name}: The name of the code reviewer

Please provide these values to continue.
```

*Process stops until user provides the missing variable*

---

## Example 4: Code Review Workflow

**User Request:**
"Use the code-review template to review my authentication module"

**Step 1: Load Template**
```
templates/code-review.txt
```

**Step 2: Extract Variables**
Required:
- `file_path`
- `code_content`
- `focus_areas`

Optional (with defaults):
- `reviewer_name:Team`
- `style_guide:standard`
- `severity_level:all`

**Step 3: Gather from Context**
- `file_path` = "src/auth/authentication.js" (inferred from "authentication module")
- `code_content` = (read from file)
- `focus_areas` = "authentication security" (inferred from context)

**Step 4: Validate**
All required variables present ✓

**Step 5: Fill Template**
```
Please review the following code from src/auth/authentication.js:

## Review Criteria
Focus on: authentication security
Style Guide: standard coding practices
Severity Level: all issues

## Code to Review
[... actual code content ...]

## Expected Output
Provide a detailed review covering:
1. Code quality and best practices
2. Potential bugs or errors
3. Performance considerations
4. Security vulnerabilities
5. Readability and maintainability

Reviewer: Development Team
```

---

## Example 5: Summarization with Custom Parameters

**User Request:**
"Summarize this documentation for executives, max 200 words"

**Template:** `templates/summarization.txt`

**Variables Gathered:**
- `content` = (documentation content)
- `content_type` = "documentation"
- `max_length` = "200" (from user request)
- `target_audience` = "executives" (from user request)
- `focus` = "key points" (default)

**Filled Template:**
```
Summarize the following documentation:

## Content
[... documentation content ...]

## Summarization Parameters
- Maximum Length: 200 words
- Target Audience: executives
- Focus: key points and main takeaways

## Output Format
Provide:
1. Executive summary (2-3 sentences)
2. Main points (bullet list)
3. Key takeaways
4. Recommendations (if applicable)
```

---

## Example 6: Bug Investigation

**User Request:**
"Investigate the login timeout bug (high severity)"

**Template:** `templates/bug-report.txt`

**Interactive Gathering:**
```
Claude: I need more information to fill the bug report template.

Missing required variables:
- bug_description: What happens during the login timeout?
- reproduction_steps: How can we reproduce this issue?

I can infer:
- severity: high (from your request)

Please provide the missing details.
```

**User Provides:**
```
Description: Users are logged out after 30 seconds of inactivity
Steps:
1. Log in to the application
2. Wait 30 seconds without interaction
3. Try to navigate - user is logged out
```

**Filled Template:**
```
## Bug Report
**Description**: Users are logged out after 30 seconds of inactivity

**Severity**: high
**Affected Component**: to be determined
**User Impact**: moderate

## Reproduction Steps
1. Log in to the application
2. Wait 30 seconds without interaction
3. Try to navigate - user is logged out

## Investigation Tasks
Please investigate and provide:
1. Root cause analysis
2. Affected code locations
3. Potential fix approaches
4. Risk assessment for each fix
5. Recommended solution

## Additional Context
No additional context provided
```

---

## Example 7: Creating Custom Templates

**User Request:**
"Create a template for database migration reviews"

**Process:**
1. Discuss with user what variables are needed
2. Create new template file
3. Save to `templates/db-migration-review.txt`
4. Document required and optional variables
5. Provide example usage

**Custom Template Created:**
```
# Database Migration Review Template
# Required variables: migration_name, migration_type, affected_tables
# Optional variables: rollback_plan:TBD, impact:low, downtime:none

Review migration: {migration_name}
Type: {migration_type}
Affected Tables: {affected_tables}

Impact Assessment: {impact:low}
Downtime Required: {downtime:none expected}
Rollback Plan: {rollback_plan:To be determined}

Please review for:
1. Data integrity risks
2. Performance impact
3. Rollback safety
4. Index optimization
```

---

## Key Takeaways

1. **Always validate** required variables before filling
2. **Use defaults wisely** for optional variables
3. **Gather context** from user messages, file paths, and previous conversation
4. **Ask for clarification** when required variables are missing
5. **Document templates** with clear variable lists
6. **Provide feedback** on which defaults were used
