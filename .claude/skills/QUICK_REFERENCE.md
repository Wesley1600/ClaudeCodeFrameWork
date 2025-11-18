# Error Handling Skill - Quick Reference

## TL;DR

This skill wraps tool calls with try/catch logic, retry mechanisms, and fallback strategies.

## How to Use

**Explicit invocation:**
```
Use the error-handling skill to execute this operation
```

**Implicit (Claude auto-applies when relevant):**
```
Push my changes to git (handles network errors automatically)
```

## Error Types

| Type | Behavior | Examples |
|------|----------|----------|
| **Retryable** | Auto-retry with backoff | Network timeout, resource busy, rate limits |
| **Non-Retryable** | Use fallback or escalate | 404, syntax errors, permission denied |
| **Critical** | Immediate escalation | Data corruption, security issues |

## Retry Configuration

```
Max retries: 4
Backoff delays: 2s, 4s, 8s, 16s
Total max wait: 30s
```

## Common Scenarios

### Git Push
```
Operation: git push
Network error → Retry up to 4x with backoff
Auth error → Escalate immediately
Merge conflict → Pull and retry
```

### File Operations
```
Operation: Read/Write/Edit
File locked → Retry 2-3x with 1s delay
Permission denied → Suggest chmod, escalate
Not found → Search for file, ask user
```

### Web Requests
```
Operation: WebFetch/WebSearch
Timeout → Retry up to 3x with 4s backoff
Rate limit (429) → Wait for reset, retry once
Redirect → Auto-follow with new request
```

## Error Log Format

```
[ERROR] 2025-11-18T10:30:45Z
Tool: <tool_name>
Operation: <description>
Error Type: <retryable|non-retryable|critical>
Attempt: <N/M>
Retry: <yes|no>
Status: <resolved|escalated|retrying>
```

## Decision Tree

```
Error occurs
    ├─ Critical? → ESCALATE immediately
    ├─ Retryable?
    │   ├─ Under retry limit?
    │   │   ├─ Yes → RETRY with backoff
    │   │   └─ No → Try FALLBACK or ESCALATE
    │   └─ No → Try FALLBACK or ESCALATE
    └─ Success → LOG and CONTINUE
```

## Example Usage

```python
# In prompts to Claude:
"Push the code with retry logic for network issues"
"Read config.json and handle file locks gracefully"
"Fetch documentation with timeout handling"
"Deploy with comprehensive error handling at each step"
```

## Files

- `error-handling.md` - Full specification
- `USAGE_GUIDE.md` - Detailed examples and patterns
- `README.md` - Skills directory overview
- `../error_handling_example.py` - Python implementation

## Key Principles

1. Classify before acting
2. Retry intelligently (not infinitely)
3. Use fallbacks when possible
4. Escalate with context
5. Log everything
6. Communicate clearly
7. Fail gracefully

## When to Use

- Any operation that might fail transiently
- Network-dependent operations
- File I/O with potential locks
- Multi-step workflows
- Production deployments
- Any critical operation

## When NOT to Use

- Operations that should fail fast
- User input validation (fail immediately)
- Logic errors (fix, don't retry)
- Operations with side effects (unless idempotent)
