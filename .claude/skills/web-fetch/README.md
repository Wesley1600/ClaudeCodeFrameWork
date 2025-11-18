# Web Fetch Skill

A Claude Code skill for safely retrieving and analyzing web content with built-in security controls.

## Overview

The web-fetch skill enables Claude to retrieve content from user-provided URLs or search results while implementing security measures to prevent data exfiltration. It handles domain filtering, usage limits, and proper URL validation.

## Features

- ✅ **Safe URL Handling**: Only uses user-provided or search-returned URLs (never generates URLs)
- ✅ **Domain Filtering**: Whitelist/blacklist capabilities for access control
- ✅ **Usage Limits**: Tracks fetches per conversation (default: 10) to prevent data exfiltration
- ✅ **PDF Support**: Automatically processes PDF documents
- ✅ **Redirect Handling**: Explicitly manages URL redirects with user awareness
- ✅ **Structured Analysis**: Guides Claude to extract and present information effectively

## Installation

This skill is included in the `.claude/skills/` directory and is automatically discovered by Claude Code.

### Directory Structure

```
.claude/skills/web-fetch/
├── SKILL.md          # Main skill definition with instructions
├── REFERENCE.md      # Technical implementation details
├── examples.md       # Practical usage examples
└── README.md         # This file
```

## Quick Start

### Basic Usage

```
User: Can you fetch and analyze https://example.com/article

Claude will:
1. Validate the URL (user-provided ✓)
2. Execute WebFetch with specific prompt
3. Track fetch count (1/10)
4. Analyze and present results
```

### With Domain Filtering

```
User: Fetch Python docs but only from docs.python.org

Claude will:
1. Apply allowed_domains filter
2. Fetch from approved domain only
3. Reject any external links automatically
```

### Research Workflow

```
User: Find and analyze articles about Rust async

Claude will:
1. WebSearch for relevant articles
2. Present results to user
3. Ask which to fetch (no assumptions)
4. Fetch approved URLs with tracking
5. Synthesize findings
```

## Security Controls

### 1. URL Validation
- ✅ User-provided URLs
- ✅ Search result URLs
- ✅ Local file URLs (with confirmation)
- ❌ Generated URLs (NEVER)
- ❌ Guessed URLs (NEVER)

### 2. Domain Filtering

**Whitelist (allowed_domains):**
```
Only fetch from approved domains:
["docs.python.org", "peps.python.org"]
```

**Blacklist (blocked_domains):**
```
Block specific domains:
["spam-site.com", "unreliable-source.net"]
```

### 3. Max Uses Tracking

**Default Limits:**
- Limit: 10 fetches/conversation
- Warning: 7 fetches (70% threshold)
- Hard stop: Requires approval at 10+

**Prevents:**
- Data exfiltration via repeated requests
- Unintended access to sensitive resources
- Excessive automated fetching

## Usage Patterns

### Pattern 1: Single URL Fetch
```markdown
User provides URL → Claude fetches → Analyzes → Presents results
Fetches: 1
```

### Pattern 2: Search + Selective Fetch
```markdown
Search for topic → Present results → User selects → Fetch selected → Synthesize
Fetches: 1-3 (selective)
```

### Pattern 3: Comparative Analysis
```markdown
Fetch source A → Fetch source B → Compare → Synthesize findings
Fetches: 2-4
```

### Pattern 4: Deep Research
```markdown
Main article → Related refs → User-approved deep dive → Comprehensive analysis
Fetches: 3-7
```

## When to Use This Skill

Use web-fetch when:
- ✅ User provides a specific URL to analyze
- ✅ Following up on WebSearch results
- ✅ Fetching documentation or tutorials
- ✅ Analyzing PDF research papers
- ✅ Comparing information across multiple sources
- ✅ Extracting structured data from web pages

Don't use when:
- ❌ URL would need to be generated/guessed
- ❌ Content is behind authentication
- ❌ User hasn't provided explicit URL
- ❌ Trying to access internal/private resources without authorization

## WebFetch Tool Parameters

```typescript
WebFetch(
  url: string,                    // Required: user-provided URL
  prompt: string,                 // Required: specific extraction instructions
  allowed_domains?: string[],     // Optional: whitelist
  blocked_domains?: string[]      // Optional: blacklist
)
```

## Files Description

### SKILL.md
The main skill file with:
- Metadata (name, description, version, allowed-tools)
- When to use this skill
- Security controls explanation
- Usage guidelines and workflows
- Error handling procedures
- Best practices and checklist

### REFERENCE.md
Technical implementation details:
- WebFetch API specification
- Security architecture
- Domain filtering implementation
- Advanced usage patterns
- Edge cases and solutions
- Performance considerations
- Troubleshooting guide

### examples.md
Real-world usage examples:
- Fetching documentation
- Research workflows
- PDF analysis
- Multi-source comparison
- Handling fetch limits
- Domain filtering scenarios
- Redirect management

## Best Practices

### ✅ Do

1. **Always** use user-provided or search-returned URLs
2. **Track** fetch count after every operation
3. **Warn** user at 70% of limit (7/10)
4. **Apply** domain filters when security matters
5. **Write** specific, actionable prompts
6. **Present** findings in structured format
7. **Offer** relevant follow-up options

### ❌ Don't

1. **Never** generate or guess URLs
2. **Never** bypass domain filters without approval
3. **Never** auto-fetch without user intent
4. **Never** exceed limits without explicit permission
5. **Never** use vague prompts ("tell me about this")
6. **Never** fetch sensitive/internal URLs without authorization

## Example Prompts

### Good Prompts ✓
```
"Extract installation instructions and list all dependencies"
"Summarize main argument and supporting evidence"
"List API endpoints with parameters and examples"
"Extract code examples showing async/await usage"
"Compare approach A vs approach B from these two sources"
```

### Poor Prompts ✗
```
"Tell me about this page" (too vague)
"What does this say?" (unclear goal)
"Read this" (no analysis specified)
"Everything" (overly broad)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot fetch URL" | Verify URL is user-provided, not generated |
| "Domain blocked" | Check domain filters, ask for override if needed |
| "Limit reached" | Get user approval or start new conversation |
| "Redirect detected" | Inform user, get approval to follow |
| "Empty content" | Page may require JavaScript - find alternative |
| "Content summarized" | Use more specific prompt or target specific section |

## Advanced Topics

### Redirect Handling
When a URL redirects:
1. WebFetch detects redirect
2. Returns redirect destination URL
3. Claude informs user
4. Asks for confirmation
5. Fetches destination (counts as +1)

### Fetch Limit Management
```
fetch_count = 0

After each WebFetch:
  fetch_count += 1

At 7: Warn user (approaching limit)
At 10: Require explicit approval
Beyond 10: Continue with documented approval
```

### Cache Behavior
- Duration: 15 minutes
- Self-cleaning (automatic expiration)
- Same URL within 15min = cached (no fetch count increment)
- After 15min = new fetch required

## Integration with Other Skills

Works well with:
- **summarization**: Fetch → summarize content
- **code-review**: Fetch → analyze code examples
- **research**: Multi-source information gathering
- **documentation**: Fetch official docs → extract specific info

## Version History

- **v1.0.0** (2024): Initial release
  - Basic WebFetch functionality
  - Domain filtering (whitelist/blacklist)
  - Max uses tracking
  - PDF support
  - Redirect handling

## Support

For issues or questions:
1. Check `REFERENCE.md` for technical details
2. Review `examples.md` for usage patterns
3. Consult Claude Code documentation
4. Report issues to skill maintainer

## License

Part of Claude Code Skills. See project license.

---

**Quick Reference:**

| Task | Fetches | Key Feature |
|------|---------|-------------|
| Single URL | 1 | Direct fetch |
| Search + fetch | 1-3 | WebSearch integration |
| Compare 2 sources | 2 | Synthesis |
| PDF analysis | 1 | Auto PDF processing |
| Deep research | 3-7 | Progressive exploration |
| Corporate docs | Variable | Domain whitelist |

**Remember**: Security through URL validation, domain filtering, and usage limits.
