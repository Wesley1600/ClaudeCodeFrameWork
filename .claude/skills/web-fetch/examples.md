# Web Fetch Skill - Examples

This document provides practical, real-world examples of using the web-fetch skill.

## Example 1: Fetching Documentation

### Scenario
User wants to understand Python's asyncio library.

### Conversation
```
User: Can you fetch the Python asyncio documentation and explain the event loop?

Claude:
I'll fetch the official Python asyncio documentation to explain the event loop.

[Executes:]
WebFetch(
    url="https://docs.python.org/3/library/asyncio-eventloop.html",
    prompt="Explain what an event loop is, how it works, and provide key usage patterns with code examples"
)

[Fetch count: 1/10]

[After receiving results:]
The asyncio event loop is the core of Python's asynchronous programming model. Here's what I learned from the official documentation:

**What is an Event Loop?**
The event loop is the central execution device that manages and distributes the execution of async tasks and callbacks. It runs in a single thread and coordinates all asynchronous operations.

**How it Works:**
1. The event loop continuously checks for tasks ready to run
2. Executes ready tasks until they hit an `await` point
3. Switches to other ready tasks while waiting
4. Handles I/O events and callbacks
5. Repeats until all tasks complete

**Key Usage Pattern:**
```python
import asyncio

async def main():
    await asyncio.sleep(1)
    print('Done')

# Run the event loop
asyncio.run(main())
```

Would you like me to fetch more specific information about any particular aspect of asyncio?
```

### Key Points
- ✅ Used user-provided URL (implicit - official docs)
- ✅ Specific prompt targeting the user's question
- ✅ Tracked fetch count (1/10)
- ✅ Presented clear, structured results
- ✅ Offered follow-up options

---

## Example 2: Research with WebSearch Integration

### Scenario
User wants to research Rust error handling best practices.

### Conversation
```
User: Find and analyze the best articles about Rust error handling.

Claude:
I'll search for articles on Rust error handling and then fetch the most relevant ones.

[Executes:]
WebSearch(query="Rust error handling best practices 2024")

[After receiving search results:]
I found several excellent resources. Here are the top results:

1. "Error Handling in Rust" - Official Rust Book (doc.rust-lang.org)
2. "Rust Error Handling Patterns" - blog.burntsushi.net
3. "The ? Operator and Error Propagation" - rust-lang.org
4. "Custom Error Types in Rust" - fettblog.eu
5. "anyhow vs thiserror: Which to Use?" - dev.to

I recommend fetching #1 (Official Rust Book) and #2 (Andrew Gallant's blog) for comprehensive coverage. Should I proceed?

User: Yes, fetch both.

Claude:
I'll fetch both articles now.

[Executes:]
WebFetch(
    url="https://doc.rust-lang.org/book/ch09-00-error-handling.html",
    prompt="Extract and explain: 1) Result and Option types, 2) the ? operator, 3) best practices for error handling, 4) code examples",
    allowed_domains=["doc.rust-lang.org", "rust-lang.org"]
)
[Fetch count: 1/10]

WebFetch(
    url="https://blog.burntsushi.net/rust-error-handling",
    prompt="Extract: 1) error handling patterns, 2) library recommendations (anyhow, thiserror), 3) real-world examples, 4) common pitfalls",
    allowed_domains=["blog.burntsushi.net"]
)
[Fetch count: 2/10]

[After receiving both results:]
I've analyzed both resources. Here's a comprehensive guide to Rust error handling:

## Result and Option Types

**From Official Rust Book:**
- `Result<T, E>` for operations that can fail
- `Option<T>` for values that may be absent
- Pattern matching for explicit handling

**Code example:**
```rust
fn read_file(path: &str) -> Result<String, io::Error> {
    fs::read_to_string(path)
}

match read_file("data.txt") {
    Ok(contents) => println!("{}", contents),
    Err(e) => eprintln!("Error: {}", e),
}
```

## The ? Operator

**From both sources:**
The `?` operator propagates errors up the call stack:

```rust
fn process() -> Result<(), Box<dyn Error>> {
    let data = read_file("data.txt")?;  // Returns error if fails
    let parsed = parse_data(&data)?;     // Chains error handling
    Ok(())
}
```

## Library Recommendations

**From Andrew Gallant's blog:**

1. **anyhow**: For applications (flexible error handling)
```rust
use anyhow::{Context, Result};

fn app_logic() -> Result<()> {
    let config = load_config()
        .context("Failed to load config")?;
    Ok(())
}
```

2. **thiserror**: For libraries (structured error types)
```rust
use thiserror::Error;

#[derive(Error, Debug)]
enum MyError {
    #[error("IO error: {0}")]
    Io(#[from] io::Error),

    #[error("Parse error: {0}")]
    Parse(String),
}
```

## Best Practices

1. Use `Result` for recoverable errors
2. Use `panic!` only for bugs/invariants
3. Provide context with error messages
4. Use `?` operator for clean error propagation
5. In libraries: define custom error types
6. In applications: use `anyhow` for convenience

Would you like me to fetch more specific information about any of these topics?
```

### Key Points
- ✅ Combined WebSearch + WebFetch workflow
- ✅ Asked user which results to fetch (didn't assume)
- ✅ Applied domain filtering for security
- ✅ Fetched sequentially with tracking (2/10)
- ✅ Synthesized findings from multiple sources
- ✅ Presented comprehensive, structured analysis

---

## Example 3: PDF Research Paper Analysis

### Scenario
User wants to analyze a machine learning research paper.

### Conversation
```
User: Can you analyze this paper and summarize the key contributions? https://arxiv.org/pdf/2103.14030.pdf

Claude:
I'll fetch and analyze this ML research paper from arXiv.

[Executes:]
WebFetch(
    url="https://arxiv.org/pdf/2103.14030.pdf",
    prompt="Extract and summarize: 1) Paper title and authors, 2) Abstract/main contribution, 3) Methodology and approach, 4) Key experimental results, 5) Conclusions and future work, 6) Top 3 cited references"
)
[Fetch count: 1/10]

[After receiving PDF content:]
# Paper Analysis: [Paper Title]

## Title and Authors
**Title:** "Learning Transferable Visual Models From Natural Language Supervision"
**Authors:** Alec Radford, et al. (OpenAI)
**Published:** 2021

## Main Contribution
This paper introduces CLIP (Contrastive Language-Image Pre-training), a neural network that learns visual concepts from natural language supervision. Key innovation: training on 400 million (image, text) pairs from the internet rather than fixed classification labels.

## Methodology
**Approach:**
1. Contrastive pre-training on image-text pairs
2. Joint embedding space for images and text
3. Zero-shot transfer to downstream tasks
4. No task-specific fine-tuning required

**Architecture:**
- Image encoder: Vision Transformer (ViT) or ResNet
- Text encoder: Transformer
- Contrastive loss function aligns embeddings

## Key Results
- Zero-shot CLIP matches supervised ResNet-50 on ImageNet
- Robust to distribution shift (superior generalization)
- Competitive with task-specific models across 30+ datasets
- Efficient: learns from web-scale noisy data

## Conclusions
1. Natural language supervision enables flexible, generalizable visual learning
2. Zero-shot transfer competitive with supervised approaches
3. Scalability: performance improves with model and data size
4. Opens path for more general-purpose vision systems

## Top Cited References
1. "Attention Is All You Need" (Vaswani et al.) - Transformer architecture
2. "An Image is Worth 16x16 Words" (Dosovitskiy et al.) - Vision Transformer
3. "SimCLR" (Chen et al.) - Contrastive learning framework

**Analysis:**
This is a foundational paper in multi-modal learning. CLIP's key insight is using natural language as a supervision signal, which provides much richer information than traditional labels. The zero-shot capability is particularly impressive - the model can classify images into arbitrary categories it wasn't explicitly trained on.

Would you like me to:
1. Fetch any of the cited references for deeper understanding?
2. Search for follow-up papers that build on CLIP?
3. Look for code implementations or tutorials?
```

### Key Points
- ✅ PDF URL directly from user
- ✅ Structured prompt for academic content
- ✅ Comprehensive extraction (abstract, methods, results, citations)
- ✅ Clear presentation with sections
- ✅ Offered relevant follow-up actions

---

## Example 4: Approaching Fetch Limit

### Scenario
User conducting extensive research, approaching the fetch limit.

### Conversation
```
User: I need to compare authentication methods across 10 different frameworks.

Claude:
I understand you want to compare authentication approaches across 10 frameworks. Before we start, I should mention that the default fetch limit is 10 per conversation to prevent unintended data access.

For your task, I'll need to fetch documentation for each framework. Let me proceed efficiently:

1. Which 10 frameworks would you like me to analyze?
2. Should I focus on specific aspects (OAuth, JWT, sessions, etc.)?

User: Django, Flask, Express, FastAPI, Spring Boot, Laravel, Rails, ASP.NET, Phoenix, Gin. Focus on JWT and OAuth support.

Claude:
Perfect. I'll fetch JWT and OAuth documentation for each framework. Let me start:

[Executes for each framework:]
1. Django: WebFetch(...) [Fetch: 1/10]
2. Flask: WebFetch(...) [Fetch: 2/10]
3. Express: WebFetch(...) [Fetch: 3/10]
4. FastAPI: WebFetch(...) [Fetch: 4/10]
5. Spring Boot: WebFetch(...) [Fetch: 5/10]
6. Laravel: WebFetch(...) [Fetch: 6/10]
7. Rails: WebFetch(...) [Fetch: 7/10]

⚠️ **Note:** Approaching fetch limit (7/10). Continuing with remaining 3...

8. ASP.NET: WebFetch(...) [Fetch: 8/10]
9. Phoenix: WebFetch(...) [Fetch: 9/10]
10. Gin: WebFetch(...) [Fetch: 10/10]

✅ **Fetch limit reached (10/10)** - All frameworks analyzed.

[After collecting all data:]
# Authentication Comparison: 10 Web Frameworks

## JWT Support Summary

| Framework | Native Support | Library | Ease of Use |
|-----------|----------------|---------|-------------|
| Django | Via package | djangorestframework-simplejwt | ⭐⭐⭐⭐ |
| Flask | Via extension | Flask-JWT-Extended | ⭐⭐⭐⭐⭐ |
| Express | Via middleware | jsonwebtoken | ⭐⭐⭐⭐⭐ |
| FastAPI | Via dependency | python-jose | ⭐⭐⭐⭐⭐ |
| Spring Boot | Built-in | Spring Security + JWT | ⭐⭐⭐ |
| Laravel | Via package | tymon/jwt-auth | ⭐⭐⭐⭐ |
| Rails | Via gem | jwt | ⭐⭐⭐⭐ |
| ASP.NET | Built-in | JwtBearer | ⭐⭐⭐ |
| Phoenix | Via library | Guardian | ⭐⭐⭐⭐ |
| Gin | Via middleware | jwt-go | ⭐⭐⭐⭐⭐ |

## OAuth Support Summary

| Framework | OAuth 2.0 | Social Login | Provider Library |
|-----------|-----------|--------------|------------------|
| Django | ✅ | ✅ | django-allauth |
| Flask | ✅ | ✅ | Authlib |
| Express | ✅ | ✅ | Passport.js |
| FastAPI | ✅ | ✅ | Authlib |
| Spring Boot | ✅ | ✅ | Spring Security OAuth |
| Laravel | ✅ | ✅ | Socialite |
| Rails | ✅ | ✅ | OmniAuth |
| ASP.NET | ✅ | ✅ | IdentityServer |
| Phoenix | ✅ | ✅ | Ueberauth |
| Gin | ✅ | ✅ | goth |

## Recommendations by Use Case

**Fastest Setup (JWT):**
1. FastAPI - Excellent docs, minimal boilerplate
2. Express - Simple middleware pattern
3. Flask - Flask-JWT-Extended is very intuitive

**Best Enterprise OAuth:**
1. Spring Boot - Comprehensive, battle-tested
2. ASP.NET - Native Microsoft integration
3. Django - Mature ecosystem

**Detailed Implementation Guides:**
[Presents framework-specific implementation patterns extracted from each fetch]

---

**Note:** We've reached the fetch limit (10/10) for this conversation. If you need additional information, we can:
1. Start a new conversation to reset the counter
2. I can analyze based on what I've already fetched
3. You can adjust the limit if needed for research tasks

What would you like to do next?
```

### Key Points
- ✅ Warned user about fetch limit upfront
- ✅ Efficient fetching (one per framework)
- ✅ Clear progress tracking (X/10 after each fetch)
- ✅ Warning at 7/10 threshold
- ✅ Notification when limit reached
- ✅ Comprehensive synthesis of all fetched data
- ✅ Explained options when limit reached

---

## Example 5: Domain Filtering for Security

### Scenario
Corporate user wants to fetch only from approved internal documentation.

### Conversation
```
User: I need to fetch our company's deployment guides. Only fetch from wiki.company.com and docs.company.com for security reasons.

Claude:
Understood. I'll restrict fetches to only your approved internal domains: wiki.company.com and docs.company.com.

What specific deployment guide would you like me to fetch?

User: Start with https://wiki.company.com/engineering/kubernetes-deploy

Claude:
I'll fetch the Kubernetes deployment guide from your internal wiki with domain restrictions applied.

[Executes:]
WebFetch(
    url="https://wiki.company.com/engineering/kubernetes-deploy",
    prompt="Extract: 1) Prerequisites, 2) Step-by-step deployment process, 3) Configuration requirements, 4) Common troubleshooting steps",
    allowed_domains=["wiki.company.com", "docs.company.com"]
)
[Fetch count: 1/10]

[After receiving content:]
# Kubernetes Deployment Guide (Internal)

## Prerequisites
- kubectl v1.28+ installed
- Access to company-k8s cluster
- ServiceAccount with deployment permissions
- Docker images in company registry

## Deployment Process

**Step 1: Configure kubectl context**
```bash
kubectl config use-context company-prod
kubectl get nodes  # Verify access
```

**Step 2: Apply manifests**
```bash
kubectl apply -f deployments/
kubectl apply -f services/
kubectl apply -f ingress/
```

**Step 3: Verify deployment**
```bash
kubectl get pods -n your-namespace
kubectl logs deployment/your-app
```

## Configuration Requirements
[Details from internal guide...]

## Troubleshooting
[Common issues and solutions...]

The guide also references https://docs.company.com/k8s-troubleshooting. Would you like me to fetch that as well? (Domain is approved)

User: Yes, fetch the troubleshooting guide.

Claude:
[Executes:]
WebFetch(
    url="https://docs.company.com/k8s-troubleshooting",
    prompt="Extract all troubleshooting scenarios, error messages, and resolution steps",
    allowed_domains=["wiki.company.com", "docs.company.com"]
)
[Fetch count: 2/10]

[After receiving content:]
# Kubernetes Troubleshooting Guide (Internal)

## Common Issues
[Detailed troubleshooting from internal docs...]

---

Both guides fetched successfully with domain restrictions active. All fetches limited to:
✅ wiki.company.com
✅ docs.company.com

If I encounter any links to external domains, I'll notify you before attempting to fetch them.
```

### Key Points
- ✅ Applied allowed_domains filter from the start
- ✅ Only fetched from approved corporate domains
- ✅ Asked before fetching additional URLs
- ✅ Verified domain compliance explicitly
- ✅ Would reject external domains automatically

---

## Example 6: Handling Redirects

### Scenario
User provides URL that redirects to different domain.

### Conversation
```
User: Fetch this article: https://bit.ly/rust-async-guide

Claude:
I'll fetch the article from that URL.

[Executes:]
WebFetch(
    url="https://bit.ly/rust-async-guide",
    prompt="Explain Rust async programming concepts and patterns"
)

[WebFetch returns redirect message:]
"Redirect detected: https://bit.ly/rust-async-guide → https://tokio.rs/tokio/tutorial

Claude:
The short URL redirects to https://tokio.rs/tokio/tutorial (the official Tokio tutorial). Should I fetch the content from the redirect destination?

User: Yes, go ahead.

Claude:
[Executes:]
WebFetch(
    url="https://tokio.rs/tokio/tutorial",
    prompt="Extract and explain: 1) Introduction to Tokio, 2) Core concepts (runtime, tasks, async/await), 3) Key examples and patterns",
    allowed_domains=["tokio.rs"]
)
[Fetch count: 2/10] (both redirect and destination counted)

[After receiving content:]
# Tokio Tutorial Summary

## Introduction
Tokio is an asynchronous runtime for Rust that provides:
- Multi-threaded, work-stealing task scheduler
- Async I/O backed by the OS event queue (epoll, kqueue, IOCP)
- Async TCP/UDP sockets, timers, and channels

## Core Concepts

**1. Runtime:**
The Tokio runtime executes async code:
```rust
#[tokio::main]
async fn main() {
    println!("Hello from Tokio!");
}
```

**2. Tasks:**
Lightweight threads of execution:
```rust
tokio::spawn(async {
    // Runs concurrently
});
```

**3. Async/Await:**
[Details from tutorial...]

---

Note: Followed redirect from bit.ly → tokio.rs. Total fetches: 2/10 (initial + redirect).
```

### Key Points
- ✅ Detected redirect automatically
- ✅ Informed user about destination
- ✅ Asked for confirmation before following
- ✅ Counted both as separate fetches
- ✅ Applied domain filter to final destination
- ✅ Transparent about redirect handling

---

## Example 7: Efficient Multi-Source Research

### Scenario
User wants to learn a new concept from multiple perspectives.

### Conversation
```
User: I want to understand Docker multi-stage builds. Find and compare explanations from official docs and community tutorials.

Claude:
I'll help you understand Docker multi-stage builds by fetching both official documentation and a highly-rated community tutorial.

**Plan:**
1. Fetch official Docker docs on multi-stage builds
2. Fetch a well-regarded community tutorial
3. Synthesize both perspectives

Let me start:

[Executes:]
WebFetch(
    url="https://docs.docker.com/build/building/multi-stage/",
    prompt="Extract: 1) What multi-stage builds are, 2) Why they're useful, 3) Syntax and structure, 4) Complete example, 5) Best practices",
    allowed_domains=["docs.docker.com"]
)
[Fetch count: 1/10]

[After first fetch:]
**From Official Docs:**
Multi-stage builds use multiple FROM statements in a Dockerfile, allowing you to:
- Copy artifacts between stages
- Reduce final image size
- Separate build-time and runtime dependencies

Example:
```dockerfile
# Stage 1: Build
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN go build -o main .

# Stage 2: Runtime
FROM alpine:latest
COPY --from=builder /app/main /main
CMD ["/main"]
```

Now fetching community perspective:

[Executes:]
WebSearch("Docker multi-stage builds tutorial")
[Finds highly-rated tutorial on dev.to]

WebFetch(
    url="https://dev.to/author/docker-multistage-guide",
    prompt="Extract: 1) Real-world use cases, 2) Practical examples, 3) Common pitfalls, 4) Performance tips, 5) Comparison with single-stage"
)
[Fetch count: 2/10]

[After second fetch:]
**From Community Tutorial:**
Real-world benefits:
- Image size: 1.2GB → 15MB (Python app example)
- Security: No build tools in production image
- Speed: Cached layers optimize rebuild time

Common pitfalls:
- Forgetting to name stages (use AS)
- Copying unnecessary files between stages
- Not leveraging BuildKit features

# Synthesized Understanding

## What Are Multi-Stage Builds?
[Combined explanation from both sources]

## Why Use Them?
**Official perspective:** Separate concerns, reduce size
**Community perspective:** Real-world 80x size reduction examples

## Complete Example (Best Practices from Both Sources)
```dockerfile
# Stage 1: Dependencies
FROM node:18 AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:18-alpine
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/index.js"]
```

## Key Insights

**From Official Docs:**
- Use numbered stages or names
- COPY --from=<stage> to transfer artifacts
- Each FROM starts fresh

**From Community:**
- Alpine for minimal runtime images
- Cache dependencies separately
- Security: fewer attack vectors

**Comparison Table:**
| Aspect | Single-Stage | Multi-Stage |
|--------|--------------|-------------|
| Image Size | ~1GB | ~15MB |
| Build Tools in Prod | Yes ❌ | No ✅ |
| Security Surface | Large | Minimal |
| Build Time | Fast | Slightly slower |

## When to Use Multi-Stage Builds
1. Compiled languages (Go, Rust, C++)
2. Frontend builds (npm run build)
3. Any app with build-time vs runtime dependencies
4. Production deployments (size matters)

This synthesis combines the official technical specification with real-world practical insights. The community tutorial's before/after examples really demonstrate the dramatic size reduction possible.

Fetches used: 2/10. Would you like me to:
1. Find Dockerfile examples for specific languages?
2. Fetch information about advanced multi-stage patterns?
3. Look up BuildKit-specific optimizations?
```

### Key Points
- ✅ Strategic fetching (official + community)
- ✅ Combined WebSearch + WebFetch
- ✅ Synthesized multiple perspectives
- ✅ Presented comparison table
- ✅ Provided complete practical examples
- ✅ Tracked fetches (2/10)
- ✅ Offered relevant follow-ups

---

## Example 8: Fetch Limit Exceeded - Handling

### Scenario
User conducting very extensive research exceeds the limit.

### Conversation
```
User: I need to analyze 15 different CI/CD platforms. Fetch documentation for each.

Claude:
I understand you want to analyze 15 CI/CD platforms. However, the fetch limit is 10 per conversation to prevent unintended data access.

**Options:**
1. **Prioritize**: Select the top 10 platforms to analyze now
2. **Two-phase**: Fetch 10 now, then continue in new conversation for remaining 5
3. **Increase limit**: If this is an authorized research task, we can proceed with user approval beyond 10

Which approach works best for you?

User: Let's do the top 10 first. GitHub Actions, GitLab CI, Jenkins, CircleCI, Travis CI, Azure Pipelines, Bitbucket Pipelines, Drone, TeamCity, Bamboo.

Claude:
Perfect. I'll fetch documentation for these 10 platforms focusing on key features, pricing, and integration capabilities.

[Proceeds to fetch 10 platforms...]
[After 10 fetches:] ✅ Fetch limit reached (10/10)

[Presents comprehensive comparison of all 10 platforms]

Now, for the remaining 5 platforms (Buildkite, Semaphore, Codefresh, ArgoCD, Tekton), we have two options:

1. **New Conversation**: Start fresh with reset counter
2. **Proceed with Approval**: I can continue fetching beyond the limit with your explicit approval

If you choose option 2, please confirm: "Yes, continue fetching beyond limit for research purposes."

User: Yes, continue fetching beyond limit for research purposes.

Claude:
Thank you for the approval. Continuing with the remaining 5 platforms...

⚠️ **Fetching beyond standard limit with user approval**

[Executes:]
WebFetch(url for Buildkite...)
[Fetch count: 11/15 - BEYOND LIMIT with approval]

[Executes:]
WebFetch(url for Semaphore...)
[Fetch count: 12/15 - BEYOND LIMIT with approval]

[Continues through all 15...]

✅ **All 15 platforms analyzed** (10 standard + 5 with approval)

[Presents comprehensive comparison of all 15 CI/CD platforms]

For future extensive research tasks, consider:
- Starting a new conversation after 10 fetches
- Using the search-first, selective-fetch strategy
- Requesting limit adjustment at the start if known large task
```

### Key Points
- ✅ Warned user about limit upfront
- ✅ Offered multiple approaches
- ✅ Required explicit approval to exceed
- ✅ Clear notation when beyond limit
- ✅ Tracked all fetches transparently (11/15, 12/15, etc.)
- ✅ Completed comprehensive analysis
- ✅ Provided guidance for future similar tasks

---

## Summary of Best Practices from Examples

### 1. URL Handling
- ✅ Always use user-provided or search-returned URLs
- ✅ Handle redirects explicitly with user notification
- ✅ Apply domain filtering when security matters
- ❌ Never generate or guess URLs

### 2. Fetch Tracking
- ✅ Track count after every fetch (X/10)
- ✅ Warn at threshold (7/10)
- ✅ Require approval beyond limit
- ✅ Be transparent about count status

### 3. Prompt Quality
- ✅ Specific, structured prompts (numbered points)
- ✅ Target user's actual question
- ✅ Request examples and practical guidance
- ❌ Avoid vague "tell me about" prompts

### 4. Workflow Efficiency
- ✅ Search first, fetch selectively
- ✅ Ask user which results to fetch
- ✅ Synthesize multiple sources
- ✅ Present structured, scannable results

### 5. User Communication
- ✅ Explain what you're fetching and why
- ✅ Show progress (fetch count)
- ✅ Offer relevant follow-ups
- ✅ Be transparent about limits and redirects

### 6. Security
- ✅ Apply domain filters for corporate/sensitive scenarios
- ✅ Never bypass filters without approval
- ✅ Track fetches to prevent exfiltration
- ✅ Respect user-defined security boundaries

---

## Quick Reference: Example Scenarios

| User Request | Strategy | Fetches | Key Technique |
|--------------|----------|---------|---------------|
| "Fetch this URL" | Direct fetch | 1 | Simple WebFetch |
| "Research topic X" | Search → selective fetch | 2-3 | WebSearch integration |
| "Compare A vs B" | Fetch both → synthesize | 2 | Comparative analysis |
| "Analyze this PDF" | PDF fetch → structured extract | 1 | Academic content prompt |
| "10+ sources" | Prioritize or get approval | 10+ | Limit management |
| "Internal docs only" | Domain whitelist | Variable | allowed_domains filter |
| "Best tutorial" | Search → user selects → fetch | 2 | User-guided selection |
| "Deep dive" | Main → related → synthesis | 3-5 | Progressive exploration |

These examples demonstrate the web-fetch skill in realistic scenarios, showcasing proper URL handling, fetch tracking, domain filtering, and security-conscious usage patterns.
