# Web Fetch Skill - Technical Reference

## Overview

This document provides technical implementation details, edge cases, and advanced usage patterns for the web-fetch skill.

## WebFetch Tool API

### Function Signature

```typescript
WebFetch(
  url: string,              // Required: fully-formed valid URL
  prompt: string,           // Required: analysis instructions
  allowed_domains?: string[], // Optional: whitelist domains
  blocked_domains?: string[]  // Optional: blacklist domains
)
```

### Parameters

#### url (required)
- **Type**: string (URI format)
- **Constraints**:
  - Must be fully-formed (include protocol)
  - HTTP automatically upgraded to HTTPS
  - Must be user-provided or from search results
  - Cannot be generated or guessed
- **Valid**: `https://example.com/page`
- **Invalid**: `example.com/page` (missing protocol)

#### prompt (required)
- **Type**: string
- **Purpose**: Describes what information to extract
- **Best practices**:
  - Be specific and actionable
  - Focus on desired output format
  - Include context if needed
  - Avoid vague requests

#### allowed_domains (optional)
- **Type**: array of strings
- **Behavior**: Only domains in this list can be fetched
- **Use case**: Restricting to official documentation
- **Example**: `["docs.python.org", "peps.python.org"]`
- **Mutually exclusive with**: `blocked_domains`

#### blocked_domains (optional)
- **Type**: array of strings
- **Behavior**: Domains in this list cannot be fetched
- **Use case**: Avoiding unreliable sources
- **Example**: `["spam-site.com", "malware-domain.net"]`
- **Mutually exclusive with**: `allowed_domains`

### Return Behavior

- **Success**: Returns processed content (HTML→Markdown + analysis)
- **Redirect**: Returns special redirect message with new URL
- **Failure**: Returns error message
- **Large content**: May be summarized automatically
- **Cached**: 15-minute self-cleaning cache for same URL

## Security Architecture

### Data Exfiltration Prevention

The max_uses limit prevents malicious attempts to exfiltrate data through web requests:

#### Attack Vector
An attacker could try to:
1. Encode sensitive data in URL parameters
2. Make repeated requests to external server
3. Exfiltrate information via HTTP logs

#### Mitigation Strategy
```
Max Uses Limit:
├── Default: 10 fetches/conversation
├── Warning: 7 fetches (70% threshold)
├── Hard Stop: 10 fetches (requires approval)
└── Reset: Only on new conversation
```

#### Implementation Pseudocode
```python
fetch_count = 0
MAX_USES = 10
WARN_THRESHOLD = 7

def web_fetch_with_tracking(url, prompt, **kwargs):
    global fetch_count

    # Check limit
    if fetch_count >= MAX_USES:
        user_approval = ask_user("Fetch limit reached. Continue?")
        if not user_approval:
            return "Fetch cancelled by user"

    # Warn at threshold
    if fetch_count == WARN_THRESHOLD:
        notify_user(f"Approaching limit ({fetch_count}/{MAX_USES})")

    # Execute fetch
    result = WebFetch(url, prompt, **kwargs)
    fetch_count += 1

    return result
```

### URL Validation

Never generate URLs to prevent:
- Accessing unintended resources
- Data exfiltration through crafted URLs
- Privacy violations

**Acceptable URL sources:**
1. Direct user input: "Fetch https://example.com"
2. Search results: URLs returned by WebSearch
3. Local files: URLs found in code/docs (with confirmation)

**Unacceptable URL sources:**
1. Generated from patterns
2. Inferred from partial input
3. Assumed from context
4. Constructed from templates

## Domain Filtering Implementation

### Whitelist Approach (allowed_domains)

**When to use:**
- Restricting to official documentation
- Corporate security policies
- High-trust sources only

**Example scenarios:**
```python
# Scenario 1: Python documentation only
WebFetch(
    url="https://docs.python.org/3/library/asyncio.html",
    prompt="Explain asyncio event loop",
    allowed_domains=["docs.python.org", "peps.python.org"]
)

# Scenario 2: Academic research only
WebFetch(
    url="https://arxiv.org/pdf/2301.12345.pdf",
    prompt="Extract methodology",
    allowed_domains=["arxiv.org", "scholar.google.com", "ieee.org"]
)

# Scenario 3: Corporate intranet
WebFetch(
    url="https://wiki.company.com/engineering/guides",
    prompt="List all deployment guides",
    allowed_domains=["wiki.company.com", "docs.company.com"]
)
```

### Blacklist Approach (blocked_domains)

**When to use:**
- Avoiding known unreliable sources
- Blocking competitors
- Preventing access to problematic sites

**Example scenarios:**
```python
# Scenario 1: Avoid content farms
WebFetch(
    url="https://quality-source.com/article",
    prompt="Analyze this tutorial",
    blocked_domains=["spam-site.com", "low-quality-blog.net"]
)

# Scenario 2: Research without opinion pieces
WebFetch(
    url="https://news-site.com/tech-analysis",
    prompt="Extract factual information",
    blocked_domains=["opinion-blog.com", "editorial-site.com"]
)
```

### Filter Validation

**Priority order:**
1. If `allowed_domains` specified → only those domains allowed
2. If `blocked_domains` specified → all except those domains allowed
3. If both specified → ERROR (mutually exclusive)
4. If neither specified → all domains allowed (default)

## Advanced Usage Patterns

### Pattern 1: Comparative Analysis

Fetch multiple sources and synthesize:

```markdown
Task: Compare error handling in Python vs Rust

Steps:
1. WebFetch(
     "https://docs.python.org/3/tutorial/errors.html",
     "Explain Python exception handling with examples",
     allowed_domains=["docs.python.org"]
   ) → fetch_count = 1

2. WebFetch(
     "https://doc.rust-lang.org/book/ch09-00-error-handling.html",
     "Explain Rust error handling with Result and Option types",
     allowed_domains=["doc.rust-lang.org"]
   ) → fetch_count = 2

3. Synthesize comparison table:
   | Aspect | Python | Rust |
   |--------|--------|------|
   | Model  | Exceptions | Result/Option |
   | ...    | ...    | ... |
```

### Pattern 2: Research Pipeline

Search → Filter → Fetch → Analyze:

```markdown
Task: Research best practices for API authentication

Steps:
1. WebSearch("API authentication best practices 2024")
   → Returns 10 results

2. Present results to user
   → User selects 3 relevant URLs

3. Sequential fetches:
   For each URL:
   - WebFetch(url, "Extract authentication methods and security considerations")
   - fetch_count += 1
   - Accumulate findings

4. Synthesize comprehensive guide from all sources
```

### Pattern 3: Deep Dive Analysis

Fetch, analyze, then fetch related resources:

```markdown
Task: Understand a complex technical concept

Steps:
1. WebFetch(main_article_url,
     "Extract main concepts, related topics, and references"
   ) → fetch_count = 1

2. Identify 2-3 key related topics from references

3. Ask user: "I found references to X, Y, Z. Should I fetch those too?"

4. If approved:
   For each related topic:
   - WebFetch(related_url, "Explain this related concept")
   - fetch_count += 1

5. Build comprehensive understanding with cross-references
```

### Pattern 4: PDF Document Chain

Fetch and analyze academic papers with citations:

```markdown
Task: Analyze ML paper and key citations

Steps:
1. WebFetch("https://arxiv.org/pdf/main-paper.pdf",
     "Extract abstract, methods, results, and top 3 cited papers"
   ) → fetch_count = 1

2. User reviews, selects citation #2 to explore

3. WebFetch("https://arxiv.org/pdf/cited-paper.pdf",
     "Extract methodology relevant to [main paper's approach]"
   ) → fetch_count = 2

4. Compare and contrast methodologies
```

## Edge Cases and Solutions

### Edge Case 1: Redirect Chain

**Problem**: URL redirects multiple times
**Solution**:
```
1. First WebFetch returns redirect to URL_2
2. Inform user: "Redirected to URL_2. Fetching..."
3. Second WebFetch(URL_2) → fetch_count = 2
4. If URL_2 also redirects, inform user and ask to continue
5. Track each redirect as separate fetch
```

### Edge Case 2: Fetch Limit During Multi-Fetch Operation

**Problem**: Reach limit mid-way through comparative analysis
**Solution**:
```
Scenario: Comparing 5 frameworks, limit is 10, currently at 8

1. Fetch framework 1 → count = 9
2. Fetch framework 2 → count = 10 (limit reached)
3. Stop and inform user: "Reached limit after 2/5 frameworks"
4. Options:
   a) Present partial analysis
   b) Ask to continue (with approval)
   c) Save remaining URLs for next conversation
```

### Edge Case 3: Invalid URL After Redirect

**Problem**: Redirect leads to broken/invalid URL
**Solution**:
```
1. WebFetch returns redirect to invalid URL
2. Detect failure (not just redirect)
3. Inform user: "Redirect failed - destination unavailable"
4. Don't count failed fetch against limit (only successful fetches)
5. Suggest alternative approach
```

### Edge Case 4: Domain Filter Conflict

**Problem**: User-provided URL blocked by filter
**Solution**:
```
User: "Fetch https://medium.com/article"
(but blocked_domains includes medium.com)

Response:
1. Detect conflict before fetching
2. Inform user: "URL blocked by domain filter"
3. Ask: "Override filter for this fetch?"
4. If yes: fetch without filter, count = +1
5. If no: suggest alternative source
```

### Edge Case 5: Extremely Large Content

**Problem**: Fetching very large page/PDF
**Solution**:
```
1. WebFetch tool auto-summarizes large content
2. Receive summarized version
3. Inform user: "Content was large - received summary"
4. If user needs more detail:
   - Suggest specific section to re-fetch
   - Or use more targeted prompt
5. Each attempt counts as separate fetch
```

### Edge Case 6: Dynamic/JavaScript Content

**Problem**: Content requires JavaScript execution
**Solution**:
```
1. WebFetch returns HTML without JS-rendered content
2. Detect missing expected content
3. Inform user: "Page may require JavaScript"
4. Alternatives:
   a) Suggest searching for static version
   b) Suggest API endpoint if available
   c) Suggest cached/archive version
```

## Performance Considerations

### Caching Strategy

- **Duration**: 15 minutes
- **Behavior**: Self-cleaning (automatic expiration)
- **Benefit**: Faster response for repeated URLs
- **Trade-off**: May show stale content for rapidly updating pages

**When cache helps:**
```
1. User: "Fetch example.com/docs"
   → Fetches and caches, count = 1

2. User: "Can you explain section 3 from that page?"
   → Uses cache, count = 1 (not incremented)

3. 20 minutes later...
   → Cache expired, new fetch needed
```

### Parallel vs Sequential Fetches

**Sequential (recommended):**
```
For each URL in [url1, url2, url3]:
    result = WebFetch(url, prompt)
    fetch_count += 1
    analyze(result)
    present_to_user()
```

**Parallel (not recommended):**
```
# Don't do this - harder to track and analyze
results = parallel_map(urls, lambda url: WebFetch(url, prompt))
fetch_count += len(urls)
```

**Reasoning**: Sequential allows incremental presentation and better user control.

## Error Handling Reference

| Error Type | Detection | Response | Count Impact |
|------------|-----------|----------|--------------|
| Invalid URL format | Before fetch | Ask user to verify | No change |
| Domain blocked | Before fetch | Notify, ask override | No change |
| Redirect | Tool response | Follow with approval | +1 per fetch |
| 404 Not Found | Tool response | Inform user, suggest alternatives | +1 |
| 403 Forbidden | Tool response | May need authentication | +1 |
| Timeout | Tool response | Suggest retry or alternative | +1 |
| Content too large | Tool response | Receive summary | +1 |
| Limit reached | Before fetch | Require approval | +0 (pending) |

## Testing Scenarios

### Test 1: Basic Fetch
```
Input: User provides single URL
Expected: Fetch succeeds, count = 1
Verify: Content returned and analyzed
```

### Test 2: Domain Whitelist
```
Input: URL + allowed_domains list
Expected: Only whitelisted domains work
Verify: Other domains rejected pre-fetch
```

### Test 3: Limit Enforcement
```
Input: 11 fetch requests
Expected: Warning at 7, stop at 10
Verify: Requires approval for 11th
```

### Test 4: Redirect Handling
```
Input: URL that redirects
Expected: Detect redirect, fetch new URL
Verify: Both URLs counted separately
```

### Test 5: PDF Processing
```
Input: PDF URL
Expected: Extracts text and visual content
Verify: Returns page-by-page analysis
```

### Test 6: Cache Behavior
```
Input: Same URL twice within 15 min
Expected: Second fetch uses cache
Verify: Count only incremented once
```

## Integration Examples

### With Summarization Skill
```
1. WebFetch(article_url, "Extract full content")
2. Pass to summarization skill
3. Return concise summary
```

### With Code Review Skill
```
1. WebFetch(github_url, "Extract code examples")
2. Pass to code review skill
3. Analyze code quality and patterns
```

### With Learning Path Creation
```
1. WebSearch("learn topic X")
2. WebFetch top 3 tutorial URLs
3. Synthesize learning path with:
   - Beginner → Intermediate → Advanced
   - Resources from fetched content
```

## Troubleshooting Guide

| Symptom | Cause | Solution |
|---------|-------|----------|
| "Cannot fetch URL" | URL generated, not provided | Only use user-provided URLs |
| "Domain blocked" | Conflicts with filter | Review/adjust domain filters |
| "Limit reached" | 10 fetches completed | Get user approval or start new session |
| "Redirect loop" | Site configuration issue | Try alternative URL/archive |
| "Empty content" | JavaScript required | Find static alternative |
| "Summary only" | Content too large | Use more specific prompt/section |

## Best Practices Checklist

Before each WebFetch:
- [ ] URL is from valid source (user/search/file)
- [ ] Prompt is specific and actionable
- [ ] fetch_count checked against limit
- [ ] Domain filters appropriate for task
- [ ] User aware of what will be fetched
- [ ] Ready to handle redirect if occurs
- [ ] Plan for analyzing results
- [ ] Consider if cache may apply

After each WebFetch:
- [ ] Increment fetch_count
- [ ] Check if approaching limit (warn at 7)
- [ ] Analyze results thoroughly
- [ ] Present findings clearly
- [ ] Determine if additional fetches needed
- [ ] Update user on progress

## Configuration Recommendations

### Conservative Settings (High Security)
```
max_uses: 5
warn_threshold: 3
allowed_domains: ["docs.python.org", "trusted-site.com"]
require_approval: true (for all fetches)
```

### Balanced Settings (Recommended)
```
max_uses: 10
warn_threshold: 7
domain_filtering: case-by-case
require_approval: false (until limit)
```

### Research-Intensive Settings
```
max_uses: 20
warn_threshold: 15
blocked_domains: ["spam-site.com", ...]
require_approval: false (until limit)
```

## API Limits and Rate Limiting

**WebFetch Tool Limits:**
- No explicit rate limit per se
- max_uses enforced at skill level
- Respect site-specific robots.txt
- 15-minute cache reduces redundant requests

**Site-Specific Considerations:**
- Some sites block automated requests
- Academic sites (arXiv) usually allow
- News sites may have paywalls
- APIs may have separate rate limits

## Future Enhancements

Potential improvements:
1. **Dynamic limit adjustment** based on task type
2. **Persistent fetch history** across conversations
3. **Smart caching** with content change detection
4. **Batch fetch optimization** for multiple URLs
5. **Domain reputation scoring** for auto-filtering
6. **Integration hooks** for custom post-processing

---

## Quick Reference Card

```
╔════════════════════════════════════════════════════════╗
║             WEB FETCH SKILL QUICK REFERENCE             ║
╠════════════════════════════════════════════════════════╣
║ Basic Usage:                                            ║
║   WebFetch(url, prompt)                                 ║
║                                                         ║
║ With Whitelist:                                         ║
║   WebFetch(url, prompt, allowed_domains=[...])          ║
║                                                         ║
║ With Blacklist:                                         ║
║   WebFetch(url, prompt, blocked_domains=[...])          ║
║                                                         ║
║ Limits:                                                 ║
║   • Default: 10 fetches/conversation                    ║
║   • Warning: 7 fetches (70%)                            ║
║   • Requires approval: 11+ fetches                      ║
║                                                         ║
║ URL Sources (Valid):                                    ║
║   ✓ User-provided                                       ║
║   ✓ Search results                                      ║
║   ✓ Local files (confirmed)                             ║
║   ✗ Generated/guessed                                   ║
║                                                         ║
║ Supported Content:                                      ║
║   • HTML (converted to Markdown)                        ║
║   • PDF (text + visual extraction)                      ║
║   • Cached (15-minute TTL)                              ║
║                                                         ║
║ Error Handling:                                         ║
║   • Redirects: Follow with new fetch (+1 count)         ║
║   • Failures: Don't retry auto (still counts)           ║
║   • Large content: Auto-summarized                      ║
╚════════════════════════════════════════════════════════╝
```
