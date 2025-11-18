# Error Handling Skill - Usage Guide

## Quick Start

To use the error handling skill with Claude Code, simply reference it in your prompts:

```
Use the error-handling skill to push my changes to git
```

or more implicitly:

```
Push my changes with retry logic in case of network issues
```

Claude will automatically apply the error handling patterns defined in the skill.

## Common Use Cases

### 1. Git Operations

**Pushing code with network retry:**
```
I need to push my changes to the remote repository.
Use error handling with retry logic for network issues.
```

Claude will:
- Attempt git push
- Retry up to 4 times with exponential backoff on network errors
- Log each retry attempt
- Escalate if all retries fail

**Pulling with conflict resolution:**
```
Pull latest changes and handle any conflicts
```

Claude will:
- Attempt git pull
- Handle merge conflicts with appropriate fallback
- Escalate for manual resolution if needed

### 2. File Operations

**Reading files with lock handling:**
```
Read config.json and handle any file lock issues
```

Claude will:
- Attempt to read the file
- Retry if file is temporarily locked
- Suggest solutions if permission denied
- Provide fallback options

**Editing with permission handling:**
```
Update the configuration file, handling any permission errors gracefully
```

Claude will:
- Check file permissions first
- Attempt edit operation
- Suggest permission fixes if needed
- Try read-only operation as fallback

### 3. Network Operations

**Web fetching with retry:**
```
Fetch the documentation from https://example.com/docs with retry logic
```

Claude will:
- Attempt WebFetch
- Retry on timeout or connection errors
- Handle rate limiting appropriately
- Follow redirects automatically

**API calls with rate limit handling:**
```
Search for recent Python tutorials, handling rate limits
```

Claude will:
- Execute WebSearch
- Wait for rate limit reset if hit
- Continue with available results if repeated failures

### 4. Build and Test Operations

**Running tests with retry:**
```
Run the test suite, retrying if there are transient failures
```

Claude will:
- Execute test command
- Identify transient vs real failures
- Retry transient failures
- Report persistent failures for investigation

## Invoking Specific Error Handling Strategies

### Exponential Backoff Retry

For operations that may have temporary failures:

```
Execute npm install with exponential backoff retry (up to 4 attempts)
```

Configuration used:
- Max retries: 4
- Delays: 2s, 4s, 8s, 16s
- Total max wait: 30s

### Fallback Strategies

For operations with alternative approaches:

```
Search for the authentication module.
If initial search fails, try broader patterns.
```

Claude will:
1. Try specific search first
2. Fall back to broader search if no results
3. Try multiple search strategies
4. Report what worked

### Immediate Escalation

For operations requiring human decision:

```
Attempt to modify system configuration.
Escalate immediately if permission denied.
```

Claude will:
- Not retry permission errors
- Provide clear error context
- Suggest solutions
- Wait for user guidance

## Error Classification Examples

### Retryable Errors

These errors trigger automatic retry:

```
- "Connection timed out"
- "ETIMEDOUT"
- "Network unreachable"
- "Resource temporarily unavailable"
- "429 Too Many Requests"
- "503 Service Unavailable"
- "EBUSY: resource busy or locked"
```

### Non-Retryable Errors

These errors use fallback or escalate:

```
- "404 Not Found"
- "ENOENT: no such file"
- "Invalid syntax"
- "Permission denied"
- "401 Unauthorized"
- "Invalid regex pattern"
```

### Critical Errors

These errors escalate immediately:

```
- "Data corruption detected"
- "Security vulnerability found"
- "Unexpected state change"
- "System malfunction"
```

## Monitoring and Logging

The skill provides structured logging for all errors:

```
[ERROR] 2025-11-18T10:30:45Z
Tool: Bash
Operation: git push -u origin feature-branch
Error Type: retryable
Error Message: Connection timed out
Attempt: 2/4
Retry: yes
Fallback: none
Status: retrying
```

After resolution:

```
[INFO] 2025-11-18T10:30:53Z
Operation: git push -u origin feature-branch
Status: Success after 3 attempts
Total time: 8 seconds
Recovery: Automatic (network recovery)
```

## Best Practices

### DO:

✅ **Specify retry requirements for critical operations**
```
Push the code to production with full retry logic
```

✅ **Request error context when things fail**
```
If the build fails, show me full error logs
```

✅ **Use fallback strategies for flexible operations**
```
Find the configuration file, checking common locations if not found
```

✅ **Ask for escalation on ambiguous errors**
```
If you encounter permission errors, ask me before proceeding
```

### DON'T:

❌ **Don't retry operations that should fail fast**
```
Bad: "Keep retrying the database migration until it works"
Good: "Attempt database migration, escalate if it fails"
```

❌ **Don't hide errors**
```
Bad: "Run tests and ignore failures"
Good: "Run tests, report all failures, retry only transient ones"
```

❌ **Don't retry without limits**
```
Bad: "Keep trying to push until successful"
Good: "Try pushing up to 4 times, then ask for help"
```

## Advanced Patterns

### Conditional Retry

```
Execute the deployment script.
Retry on network errors but not on validation errors.
```

### Progressive Fallback

```
Try to read from primary cache, then secondary cache, then database.
```

### Partial Success Handling

```
Process all files in the directory.
Log failures but continue processing remaining files.
Report summary at the end.
```

### Recovery After Failure

```
If the git push fails after retries:
1. Check branch status
2. Verify remote connectivity
3. Suggest alternative approaches
4. Ask before force pushing
```

## Integration with Workflows

### CI/CD Pipeline

```
Run the full CI pipeline:
1. Run tests (retry transient failures)
2. Build project (retry network issues during dependency fetch)
3. Deploy (escalate on any deployment failures)

Handle each step with appropriate error strategy.
```

### Code Review Process

```
Fetch PR #123 details (with retry on network errors)
Run linter on changed files (no retry on lint errors)
Run tests on affected code (retry on infrastructure failures)
Provide review summary
```

### Development Workflow

```
Pull latest changes (retry on network issues)
Run local tests (no retry on test failures)
Fix any issues
Commit and push (retry on network issues)
```

## Troubleshooting

### "Too many retries, operation still failing"

**Possible causes:**
- Network issue is persistent, not transient
- Service is down, not just slow
- Rate limiting is too strict

**Solution:**
- Check network connectivity
- Verify service status
- Wait longer before retrying
- Use alternative endpoint

### "Fallback not working"

**Possible causes:**
- Fallback has same dependency as primary
- Error affects both strategies

**Solution:**
- Use truly independent fallback
- Escalate for human decision

### "Errors not being retried"

**Possible causes:**
- Error classified as non-retryable
- Retry limit already reached

**Solution:**
- Check error classification
- Adjust retry limits if appropriate
- Verify error is truly transient

## Examples from Real Scenarios

### Scenario: Deploying to production

```
User: Deploy the application to production

Claude: I'll deploy with comprehensive error handling:

1. Running pre-deployment checks...
   ✓ Tests passed
   ✓ Build successful

2. Pushing to production branch...
   ⚠ Network timeout (attempt 1/4)
   ⏳ Waiting 2 seconds...
   ⚠ Network timeout (attempt 2/4)
   ⏳ Waiting 4 seconds...
   ✓ Push successful (attempt 3/4)

3. Triggering deployment...
   ✓ Deployment started
   ✓ Health checks passed

Deployment completed successfully after handling network issues.
Total time: 3 minutes 15 seconds
```

### Scenario: Large refactoring task

```
User: Rename the function getUserData to fetchUserProfile across the codebase

Claude: I'll perform this refactoring with error handling:

1. Searching for all occurrences...
   ✓ Found 47 occurrences in 12 files

2. Updating files with edit operations...
   ✓ Updated file 1/12: src/api/users.ts
   ✓ Updated file 2/12: src/components/Profile.tsx
   ⚠ File locked: src/utils/cache.ts (attempt 1/3)
   ⏳ Waiting 1 second...
   ✓ Updated file 3/12: src/utils/cache.ts
   ...
   ✓ All 12 files updated successfully

3. Running tests to verify...
   ✓ All tests pass

Refactoring completed successfully with 1 retry needed for locked file.
```

## Reference

For full error handling specification, see [error-handling.md](error-handling.md)

For Python implementation examples, see [error_handling_example.py](../error_handling_example.py)
