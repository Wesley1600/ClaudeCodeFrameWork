# Error Handling Skill

A comprehensive skill for wrapping tool calls with robust error handling, retry logic, and fallback behaviors.

## Overview

This skill provides a framework for handling tool failures gracefully, including:
- Error detection and classification
- Automatic retry with exponential backoff
- Fallback strategies for common failures
- Error logging and reporting
- Human escalation when appropriate
- Recovery mechanisms

## Error Classification

### Retryable Errors
Errors that should be automatically retried:
- Network timeouts
- Temporary connection failures
- Rate limiting (429 errors)
- Transient API errors (5xx status codes)
- Lock/resource busy errors
- Git push/pull failures due to network

### Non-Retryable Errors
Errors that need immediate attention:
- Authentication failures (401, 403)
- Not found errors (404)
- Invalid input/syntax errors
- Permission denied errors
- File system corruption
- Resource exhausted (disk full)

### Critical Errors
Errors requiring human escalation:
- Data corruption detected
- Security vulnerabilities found
- Multiple consecutive retry failures
- Unexpected state changes
- Tool malfunction patterns

## Retry Strategy

### Exponential Backoff Configuration
```
Max retries: 4
Base delay: 2 seconds
Backoff pattern: 2s, 4s, 8s, 16s
Max total wait: 30 seconds
```

### Retry Decision Logic
1. **Classify error type** - Determine if error is retryable
2. **Check retry count** - Ensure we haven't exceeded max attempts
3. **Apply backoff delay** - Wait before next attempt
4. **Log retry attempt** - Record attempt number and reason
5. **Execute retry** - Attempt operation again
6. **Success check** - Verify operation completed successfully

## Tool-Specific Error Handling

### Bash Tool Errors

**Network Operations (git, npm, curl, wget)**
```
Error Pattern: "Connection timed out", "Could not resolve host"
Strategy: Retry up to 4 times with exponential backoff
Fallback: Suggest checking network connectivity or using alternative mirror
Escalation: After 4 failures, ask user to verify network/proxy settings
```

**File System Errors**
```
Error Pattern: "No space left on device", "Permission denied"
Strategy: No retry - immediate escalation
Fallback: Suggest disk cleanup or permission fixes
Escalation: Provide specific error details and remediation steps
```

### Read/Write/Edit Tool Errors

**File Not Found**
```
Error Pattern: "ENOENT: no such file or directory"
Strategy: Verify path, search for similar files
Fallback: Search codebase for likely location
Escalation: Ask user to confirm expected file location
```

**Permission Errors**
```
Error Pattern: "EACCES: permission denied"
Strategy: Check file permissions, suggest chmod if appropriate
Fallback: Attempt read-only operations if write fails
Escalation: Request user intervention for permission changes
```

**File Lock Errors**
```
Error Pattern: "EBUSY: resource busy or locked"
Strategy: Retry 2-3 times with 1-second delay
Fallback: Suggest closing other processes or using force flag
Escalation: After retries, ask user to check for locking processes
```

### Grep/Glob Tool Errors

**Pattern Errors**
```
Error Pattern: "Invalid regex", "Malformed pattern"
Strategy: No retry - fix pattern
Fallback: Simplify pattern, escape special characters
Escalation: Show corrected pattern to user
```

**Timeout Errors**
```
Error Pattern: Operation timeout on large searches
Strategy: Retry with narrower scope or type filters
Fallback: Use multiple targeted searches instead of one broad search
Escalation: Suggest alternative search strategies
```

### WebFetch/WebSearch Errors

**Network Errors**
```
Error Pattern: "ETIMEDOUT", "ECONNREFUSED", "DNS resolution failed"
Strategy: Retry up to 3 times with 4-second backoff
Fallback: Try alternative URLs or cached content
Escalation: After retries, report network issue and continue with available data
```

**Rate Limiting**
```
Error Pattern: "429 Too Many Requests"
Strategy: Wait for rate limit reset, then retry once
Fallback: Use cached results if available
Escalation: Inform user of rate limit and delay required
```

**Redirect Handling**
```
Error Pattern: "Redirect to different host"
Strategy: Automatically follow redirect with new WebFetch call
Fallback: None needed - this is expected behavior
Escalation: None
```

### Git Operations Errors

**Push Failures**
```
Error Pattern: "failed to push", "rejected", "non-fast-forward"
Strategy:
  - For network errors: Retry up to 4 times with exponential backoff
  - For merge conflicts: Pull and rebase, then retry
  - For authentication: Escalate immediately
Fallback: Attempt fetch first, then pull, then push
Escalation: After network retries fail, ask user to check credentials/network
```

**Merge Conflicts**
```
Error Pattern: "CONFLICT", "automatic merge failed"
Strategy: No automatic retry
Fallback: Stash changes, pull, reapply, then resolve
Escalation: Present conflict details and ask for resolution strategy
```

## Error Logging Format

Log all errors with the following structure:

```
[ERROR] <Timestamp>
Tool: <tool_name>
Operation: <operation_description>
Error Type: <retryable|non-retryable|critical>
Error Message: <full_error_message>
Attempt: <current_attempt>/<max_attempts>
Retry: <yes|no>
Fallback: <fallback_strategy_used>
Status: <resolved|escalated|retrying>
```

## Implementation Pattern

When executing tool calls that may fail, follow this pattern:

### 1. Pre-Execution Check
- Validate inputs before tool call
- Check prerequisites (file exists, network available, etc.)
- Verify permissions and access

### 2. Execution with Error Capture
- Execute tool call
- Capture full error details if it fails
- Classify error type immediately

### 3. Error Analysis
- Determine if error is retryable
- Check retry count and limits
- Identify appropriate fallback strategy

### 4. Retry or Fallback
- If retryable and under limit:
  - Log retry attempt
  - Apply exponential backoff delay
  - Execute retry
- If non-retryable:
  - Apply fallback strategy
  - Log fallback action

### 5. Escalation Decision
- If all retries exhausted: escalate with full context
- If critical error: escalate immediately
- If fallback fails: escalate with both primary and fallback errors
- Provide clear, actionable information to user

### 6. Recovery
- After successful retry: log success and continue
- After successful fallback: inform user of alternative approach used
- After escalation: wait for user guidance before proceeding

## Example Usage Scenarios

### Scenario 1: Git Push with Network Error

```
Attempt 1: git push -u origin branch
Error: "Connection timed out"
Classification: Retryable (network error)
Action: Wait 2 seconds, retry

Attempt 2: git push -u origin branch
Error: "Connection timed out"
Classification: Retryable (network error)
Action: Wait 4 seconds, retry

Attempt 3: git push -u origin branch
Success: Pushed successfully
Log: "Git push succeeded after 3 attempts (network recovery)"
```

### Scenario 2: File Read with Lock Error

```
Attempt 1: Read file.txt
Error: "EBUSY: resource busy or locked"
Classification: Retryable (temporary lock)
Action: Wait 1 second, retry

Attempt 2: Read file.txt
Error: "EBUSY: resource busy or locked"
Classification: Retryable (temporary lock)
Action: Wait 2 seconds, retry

Attempt 3: Read file.txt
Error: "EBUSY: resource busy or locked"
Classification: Escalate
Action: Inform user - "file.txt appears to be locked by another process. Please close any applications that might be using this file."
```

### Scenario 3: Grep Pattern Error with Fallback

```
Attempt 1: Grep pattern "function\s+\w+(*args)"
Error: "Invalid regex - unmatched parenthesis"
Classification: Non-retryable (syntax error)
Fallback: Simplify pattern to "function.*args"
Action: Execute with corrected pattern

Attempt 2: Grep pattern "function.*args"
Success: Found 23 matches
Log: "Original pattern was invalid, used simplified pattern instead"
Inform user: "Note: I simplified the regex pattern to avoid syntax errors"
```

### Scenario 4: WebFetch with Rate Limiting

```
Attempt 1: WebFetch https://api.example.com/docs
Error: "429 Too Many Requests - Retry after 60 seconds"
Classification: Retryable (rate limit)
Action: Wait 60 seconds, retry once

Attempt 2: WebFetch https://api.example.com/docs
Success: Retrieved content
Log: "WebFetch succeeded after rate limit wait"
Inform user: "Note: Had to wait 60 seconds due to rate limiting"
```

### Scenario 5: Multiple Tool Failures - Escalation

```
Attempt 1: Edit config.json (change setting)
Error: "EACCES: permission denied"
Classification: Non-retryable (permissions)
Fallback: Try Read instead to show current content

Attempt 2: Read config.json
Error: "EACCES: permission denied"
Classification: Critical (both read and write failed)
Escalation: "Unable to access config.json due to permission errors.
             Both read and write operations failed.
             Current file permissions: -rw------- (owner only)
             Suggested fix: Run 'chmod 644 config.json' or run Claude Code with appropriate permissions.
             Would you like me to suggest alternative approaches?"
```

## Best Practices

1. **Always validate inputs** before executing tool calls
2. **Classify errors immediately** to determine appropriate response
3. **Log all retry attempts** for debugging and transparency
4. **Use appropriate backoff** - don't hammer failing services
5. **Provide context** when escalating to users
6. **Suggest solutions** when errors occur
7. **Fail gracefully** - never leave operations in inconsistent state
8. **Learn from patterns** - if same error occurs repeatedly, adjust strategy
9. **Communicate clearly** - tell user what went wrong and what you're doing about it
10. **Don't hide errors** - always inform user of significant issues

## Anti-Patterns to Avoid

1. ❌ Retrying non-retryable errors (wasting time)
2. ❌ Infinite retry loops (blocking progress)
3. ❌ Hiding errors from users (lack of transparency)
4. ❌ Retrying without backoff (hammering services)
5. ❌ Giving up without trying fallbacks
6. ❌ Escalating without providing context
7. ❌ Continuing silently after critical errors
8. ❌ Using same strategy for all error types
9. ❌ Ignoring error patterns and root causes
10. ❌ Failing to clean up after partial failures

## Integration with Existing Workflows

This error handling skill should be applied:

- **During git operations** - Push, pull, fetch failures
- **During file operations** - Read, write, edit operations
- **During network operations** - WebFetch, WebSearch, API calls
- **During build/test operations** - npm, pytest, compile commands
- **During search operations** - Grep, Glob, find operations
- **During any operation** that interacts with external systems

## Monitoring and Improvement

Track these metrics to improve error handling:

- **Retry success rate** - How often do retries succeed?
- **Time to recovery** - How long do retries take?
- **Escalation rate** - How often do we need human help?
- **Error patterns** - What errors occur most frequently?
- **Fallback effectiveness** - Do fallback strategies work?

Use this data to refine retry limits, backoff timing, and fallback strategies.

## Summary

When using this skill:

1. **Wrap all risky tool calls** in error handling logic
2. **Classify errors** to determine correct response
3. **Retry intelligently** with exponential backoff
4. **Use fallbacks** when primary approach fails
5. **Escalate clearly** when human intervention needed
6. **Log everything** for debugging and improvement
7. **Communicate** what's happening to the user
8. **Recover gracefully** and continue work when possible

This ensures robust, reliable tool execution that handles failures gracefully and keeps users informed.
