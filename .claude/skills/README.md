# Claude Code Skills

This directory contains custom skills for Claude Code to enhance its capabilities.

## Available Skills

### Error Handling Skill (`error-handling.md`)

A comprehensive framework for wrapping tool calls with robust error handling, retry logic, and fallback behaviors.

**Use this skill when:**
- Executing operations that may fail due to network issues
- Working with git operations (push, pull, fetch)
- Performing file I/O that may encounter locks or permissions
- Making web requests that may timeout or rate limit
- Any operation where graceful failure handling is important

**Key features:**
- Automatic error classification (retryable vs non-retryable)
- Exponential backoff retry logic
- Tool-specific fallback strategies
- Structured error logging
- Clear escalation paths for human intervention

**How to activate:**
Claude Code automatically uses skills when relevant. For explicit activation:
```
Use the error-handling skill to execute this git push with retry logic
```

## Creating Custom Skills

To create a new skill:

1. Create a markdown file in `.claude/skills/`
2. Document the skill's purpose and usage
3. Provide clear examples and patterns
4. Include decision trees for when to use the skill

## Skill Best Practices

- **Specific and actionable** - Provide clear steps
- **Include examples** - Show real usage scenarios
- **Define scope** - Be clear about when to use the skill
- **Error handling** - Always consider what can go wrong
- **User communication** - Guide how to inform users

## Integration

Skills are automatically available to Claude Code when placed in this directory. Reference them by name or topic in your prompts.
