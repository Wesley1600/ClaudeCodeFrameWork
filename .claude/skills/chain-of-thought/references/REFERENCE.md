# Chain of Thought - Extended Reference

## Advanced Patterns and Real-World Examples

This document provides in-depth examples and advanced patterns for chain of thought reasoning.

---

## Table of Contents

1. [Multi-Turn Reasoning](#multi-turn-reasoning)
2. [Hierarchical Thinking](#hierarchical-thinking)
3. [Collaborative Reasoning](#collaborative-reasoning)
4. [Error Recovery Patterns](#error-recovery-patterns)
5. [Domain-Specific Templates](#domain-specific-templates)
6. [Performance Optimization](#performance-optimization)

---

## Multi-Turn Reasoning

When a task spans multiple interactions, maintain continuity by referencing previous thinking.

### Example: Iterative Bug Investigation

**Turn 1:**
```xml
<thinking>
## Initial Investigation
User reports: API returning 500 errors intermittently

Hypothesis 1: Database connection timeout
- Check: connection pool settings
- Evidence needed: error logs

Hypothesis 2: Race condition in concurrent requests
- Check: request handling logic
- Evidence needed: timing patterns

Next step: Examine error logs to narrow down
</thinking>

<answer>
Let me check the error logs to understand the pattern of failures.
</answer>
```

**Turn 2 (after reading logs):**
```xml
<thinking>
## Previous Context
Turn 1: Identified two hypotheses (DB timeout vs race condition)

## New Evidence
Error logs show:
- All failures happen during high traffic (>100 req/sec)
- Error message: "Cannot read property 'data' of undefined"
- Stack trace points to requestHandler.js:45

## Updated Analysis
This is NOT a database issue. It's a race condition.
- Line 45 accesses request.body.data
- High traffic suggests concurrent modification
- The undefined suggests request object is being mutated

## Root Cause
Likely cause: shared mutable state in request handler

## Next Action
Examine requestHandler.js:45 and check for global state
</thinking>

<answer>
The error logs reveal this is a race condition, not a database issue. All failures occur during high traffic when accessing `request.body.data`. Let me examine the request handler code.
</answer>
```

**Turn 3 (after reading code):**
```xml
<thinking>
## Investigation History
- Turn 1: Formed hypotheses
- Turn 2: Logs pointed to race condition
- Turn 3: Found the bug

## The Bug
Line 42-45 in requestHandler.js:
```javascript
let currentRequest = request; // PROBLEM: shared reference
processAsync(() => {
  return currentRequest.body.data; // undefined when overwritten
});
```

The `currentRequest` variable is overwritten by concurrent requests!

## Solution
Capture the data value immediately:
```javascript
const requestData = request.body.data; // immutable capture
processAsync(() => {
  return requestData; // safe
});
```

## Validation
This explains:
- Why it only fails under high traffic
- Why the error is intermittent
- Why the request object appears undefined
</thinking>

<answer>
Found the bug! The request handler uses a shared mutable reference that gets overwritten during concurrent requests. Here's the fix:

```javascript
// Before (buggy):
let currentRequest = request;
processAsync(() => {
  return currentRequest.body.data; // undefined during concurrent requests
});

// After (fixed):
const requestData = request.body.data;
processAsync(() => {
  return requestData; // immutable, safe
});
```

This captures the data immediately before async processing, preventing race conditions.
</answer>
```

---

## Hierarchical Thinking

For complex tasks, use nested thinking levels to organize reasoning.

### Example: System Architecture Design

```xml
<thinking>
# Level 1: High-Level Strategy

## Goal
Design a scalable e-commerce platform for 1M+ users

## Major Components
1. Frontend (web + mobile)
2. API Gateway
3. Backend services
4. Data layer
5. Infrastructure

# Level 2: Component Deep-Dive

## 2.1 Frontend Architecture

### Requirements Analysis
- Web: React (existing team expertise)
- Mobile: React Native (code sharing)
- State management: Redux vs Context API

### Decision Process
React Native enables 70% code reuse
- Pro: faster development
- Pro: consistent UX
- Con: some platform-specific features harder
- Decision: Use React Native with native modules for complex features

## 2.2 Backend Services

### Service Boundaries
Option A: Monolith with modules
Option B: Microservices from day 1
Option C: Modular monolith → gradual extraction

### Evaluation
Current team: 5 developers
Timeline: 6 months to MVP
Growth plan: 2x team size in year 2

Analysis:
- Microservices (Option B) = overkill for team size
- Pure monolith (Option A) = future pain
- Hybrid (Option C) = best balance

Decision: Modular monolith with clear service boundaries

### Critical Services to Isolate
1. Authentication (high security, stable)
2. Payment processing (PCI compliance, isolated)
3. Product catalog (high read, cacheable)
4. Order management (core business logic)

# Level 3: Implementation Details

## 3.1 Data Layer Design

### Database Selection
Products catalog:
- Read-heavy (90% reads)
- Semi-structured data (variants, attributes)
- Search requirements
→ PostgreSQL + Elasticsearch

Orders:
- ACID requirements
- Relational (orders → items → products)
→ PostgreSQL

Sessions/Cache:
- High throughput
- Ephemeral
→ Redis

## 3.2 API Gateway Strategy

### Requirements
- Rate limiting
- Authentication
- Request routing
- Response caching

### Options
Kong vs NGINX vs AWS API Gateway

Decision Matrix:
- Kong: feature-rich, self-hosted
- NGINX: lightweight, requires custom plugins
- AWS API Gateway: managed, AWS-specific

Given AWS infrastructure → AWS API Gateway
Reasoning: reduces operational burden, native integration

# Level 4: Risk Assessment

## Identified Risks

Risk 1: Database scaling at 1M users
- Mitigation: Read replicas + caching strategy
- Validation: Load testing at 100K user simulation

Risk 2: Frontend bundle size
- Mitigation: Code splitting, lazy loading
- Validation: Bundle analysis, performance budgets

Risk 3: Payment processing downtime
- Mitigation: Retry logic, fallback processor
- Validation: Chaos engineering tests

# Level 5: Final Validation

## Checklist
✓ Meets scalability requirements (1M+ users)
✓ Team can implement (existing skills)
✓ Within timeline (6 months)
✓ Costs reasonable (AWS tier estimate: $5K/month initial)
✓ Security addressed (PCI compliance, auth)
✓ Monitoring planned (CloudWatch, Sentry)

## Risks Accepted
- Some rework needed when extracting microservices later
- AWS vendor lock-in (acceptable trade-off for speed)

## Open Questions
- [ ] CDN strategy (CloudFront vs Cloudflare)
- [ ] CI/CD tooling (GitHub Actions vs CircleCI)
→ Can be decided during implementation
</thinking>

<answer>
## E-Commerce Platform Architecture

### Frontend
- **Web + Mobile**: React + React Native (70% code sharing)
- **State**: Redux for complex state, Context API for simple cases

### Backend
- **Pattern**: Modular monolith (clear service boundaries for future extraction)
- **Language**: Node.js (team expertise)
- **Key modules**: Auth, Payments, Products, Orders

### Data Layer
- **Primary DB**: PostgreSQL (orders, users, products)
- **Search**: Elasticsearch (product catalog)
- **Cache**: Redis (sessions, frequently accessed data)

### Infrastructure
- **Cloud**: AWS
- **API Gateway**: AWS API Gateway (managed, rate limiting, auth)
- **Hosting**: ECS (containerized services)
- **CDN**: TBD (CloudFront vs Cloudflare)

### Scalability Strategy
1. Database read replicas for read-heavy workloads
2. Redis caching layer
3. CDN for static assets
4. Horizontal scaling via ECS auto-scaling

### Timeline
- Months 1-2: Core services (auth, products, orders)
- Months 3-4: Frontend + payment integration
- Months 5-6: Testing, optimization, launch prep

### Cost Estimate
Initial: ~$5K/month (scales with usage)

### Next Steps
1. Set up AWS infrastructure (VPC, RDS, ECS)
2. Create service templates and repository structure
3. Implement authentication module (foundation)
</answer>
```

---

## Collaborative Reasoning

When multiple agents or perspectives are involved, use thinking blocks to coordinate.

### Example: Code Review Discussion

**Agent 1 (Reviewer):**
```xml
<thinking>
## Code Review: Authentication Module

### Security Analysis
Line 45: Password hashing
```javascript
const hash = md5(password);
```
🚨 CRITICAL: MD5 is cryptographically broken!

Recommendation: Use bcrypt or argon2

### Performance Analysis
Line 78: Database query in loop
```javascript
for (user of users) {
  await db.getUserPermissions(user.id);
}
```
⚠️ N+1 query problem, will cause performance issues

Recommendation: Batch query or use JOIN

### Code Quality
- Good: Clear variable names
- Good: Error handling present
- Issue: No input validation on line 23

## Severity Assessment
1. MD5 usage: BLOCKER (security)
2. N+1 queries: MAJOR (performance)
3. Missing validation: MINOR (correctness)

## Recommendation
Request changes before merge
</thinking>

<answer>
### Review: Request Changes

**BLOCKER - Security Issue:**
Line 45 uses MD5 for password hashing. MD5 is cryptographically broken and vulnerable to rainbow table attacks.

**Fix:** Use bcrypt:
```javascript
const hash = await bcrypt.hash(password, 10);
```

**MAJOR - Performance Issue:**
Line 78 has N+1 query problem that will cause slowdowns with many users.

**Fix:** Batch the query:
```javascript
const userIds = users.map(u => u.id);
const permissions = await db.getUserPermissionsBatch(userIds);
```

**MINOR - Input Validation:**
Line 23 should validate email format before processing.

Please address the security and performance issues before merging.
</answer>
```

**Agent 2 (Developer):**
```xml
<thinking>
## Reviewing Feedback

### Blocker: MD5 → bcrypt
Agree this is critical. However, considerations:
- We have 100K existing users with MD5 hashes
- Can't just switch without migration strategy

Migration plan:
1. Add `hash_version` field to users table
2. New users get bcrypt (version 2)
3. Existing users keep MD5 temporarily (version 1)
4. On next login, rehash with bcrypt and update version
5. After 90 days, force password reset for remaining MD5 users

This allows gradual migration without breaking existing users.

### Major: N+1 queries
Good catch. However:
- `getUserPermissionsBatch` doesn't exist yet
- Need to implement it or use JOIN

Checking schema... permissions table has user_id foreign key.
Better approach: JOIN in the original query

```javascript
const usersWithPermissions = await db.query(`
  SELECT users.*, permissions.*
  FROM users
  LEFT JOIN permissions ON users.id = permissions.user_id
  WHERE users.id IN (?)
`, userIds);
```

### Minor: Email validation
Agree. Will add validator.isEmail() check.

## Updated Implementation Plan
1. Implement hash migration strategy (MD5 → bcrypt)
2. Refactor query to use JOIN
3. Add email validation
4. Add tests for all three fixes
</thinking>

<answer>
Thanks for the thorough review! I agree with all points. Here's my implementation plan:

**1. MD5 → bcrypt (with migration strategy):**
I'll implement a gradual migration to avoid breaking existing users:
- Add `hash_version` field to track hash type
- New registrations use bcrypt immediately
- Existing users rehash on next login
- Force reset after 90 days for holdouts

**2. N+1 fix (using JOIN):**
I'll refactor to use a JOIN instead of separate queries:
```javascript
const usersWithPermissions = await db.query(`
  SELECT users.*, permissions.*
  FROM users
  LEFT JOIN permissions ON users.id = permissions.user_id
  WHERE users.id IN (?)
`, userIds);
```

**3. Email validation:**
Adding `validator.isEmail()` check on line 23.

I'll push these fixes with tests shortly. ETA: 2 hours.
</answer>
```

---

## Error Recovery Patterns

When things go wrong, use thinking blocks to diagnose and adapt.

### Example: Build Failure Recovery

```xml
<thinking>
## Build Attempt 1

Command: `npm run build`

Error:
```
Module not found: Error: Can't resolve './utils/helper'
```

## Diagnosis
The import path is broken. Let me check:
- Does the file exist?
- Is the path correct?
- Case sensitivity issue?

Checking file system...
Found: `src/utils/Helper.js` (capital H)
Import: `import { foo } from './utils/helper'` (lowercase h)

Root cause: Case mismatch (Linux is case-sensitive, local dev on Mac was case-insensitive)

## Solution
Fix import to match actual filename

## Build Attempt 2

Command: `npm run build`

Error:
```
TypeError: Cannot read property 'map' of undefined
  at ProductList.jsx:23
```

## New Diagnosis
Runtime error during build (SSR?). Checking ProductList.jsx:23...

Line 23: `products.map(p => ...)`

The `products` prop is undefined. This is happening during build, so it's SSR.

Root cause: Component assumes `products` exists but doesn't handle undefined case

## Solution
Add default props or guard:
```javascript
const { products = [] } = props;
```

## Build Attempt 3

Command: `npm run build`

Result: ✓ SUCCESS

## Reflection
Two issues fixed:
1. Case sensitivity in imports (development env difference)
2. Missing prop defaults for SSR

Learning: Always test builds on Linux before deploying (or use Docker for consistency)
</thinking>

<answer>
Build fixed! Two issues resolved:

1. **Import case mismatch**: `./utils/helper` → `./utils/Helper` (Linux is case-sensitive)
2. **SSR prop handling**: Added default for `products` prop in ProductList

The build now passes. To prevent future issues, consider using Docker for development to match the production environment's case sensitivity.
</answer>
```

---

## Domain-Specific Templates

### Template: Algorithm Design

```xml
<thinking>
## Problem Statement
Input: [description]
Output: [description]
Constraints: [limitations]

## Examples
Example 1:
Input: [sample input]
Expected Output: [sample output]

Example 2:
Input: [edge case]
Expected Output: [expected result]

## Approach Analysis

### Brute Force
Algorithm: [description]
Time Complexity: O(?)
Space Complexity: O(?)
Pros: [advantages]
Cons: [disadvantages]

### Optimized Approach 1
Algorithm: [description]
Time Complexity: O(?)
Space Complexity: O(?)
Pros: [advantages]
Cons: [disadvantages]

### Optimized Approach 2
Algorithm: [description]
Time Complexity: O(?)
Space Complexity: O(?)
Pros: [advantages]
Cons: [disadvantages]

## Decision
Chosen: [approach]
Reasoning: [why this one]

## Implementation Plan
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Edge Cases to Handle
- [Edge case 1]
- [Edge case 2]
- [Edge case 3]

## Verification Strategy
- [Test case 1]
- [Test case 2]
- [Complexity verification]
</thinking>

<answer>
[Implementation with explanation]
</answer>
```

### Template: API Design

```xml
<thinking>
## Requirements
Functional:
- [Requirement 1]
- [Requirement 2]

Non-functional:
- Performance: [target]
- Security: [requirements]
- Scalability: [requirements]

## API Design Options

### RESTful Approach
Endpoints:
- GET /resource
- POST /resource
- PUT /resource/:id
- DELETE /resource/:id

Pros: [advantages]
Cons: [disadvantages]

### GraphQL Approach
Schema:
```graphql
type Resource {
  id: ID!
  field1: String
  field2: Int
}
```

Pros: [advantages]
Cons: [disadvantages]

## Decision
Approach: [chosen design]
Reasoning: [justification]

## Endpoint Specification
[Detailed endpoint design]

## Security Considerations
- Authentication: [method]
- Authorization: [method]
- Rate limiting: [strategy]
- Input validation: [strategy]

## Error Handling
- 400: [scenarios]
- 401: [scenarios]
- 403: [scenarios]
- 404: [scenarios]
- 500: [scenarios]

## Documentation Plan
- OpenAPI/Swagger spec
- Usage examples
- Error codes reference
</thinking>

<answer>
[API specification with examples]
</answer>
```

### Template: Database Schema Design

```xml
<thinking>
## Data Requirements
Entities:
- [Entity 1] with attributes [list]
- [Entity 2] with attributes [list]

Relationships:
- [Entity 1] → [Entity 2]: [type]

## Access Patterns
Query 1: [description] - frequency: [high/medium/low]
Query 2: [description] - frequency: [high/medium/low]

## Normalization Analysis
Current form: [1NF/2NF/3NF]
Trade-offs:
- Normalized: [pros/cons]
- Denormalized: [pros/cons]

Decision: [approach and why]

## Index Strategy
Index 1: [columns] - justification: [query pattern]
Index 2: [columns] - justification: [query pattern]

## Schema Draft
```sql
CREATE TABLE entity1 (
  id PRIMARY KEY,
  ...
);
```

## Migration Strategy
- [Step 1]
- [Step 2]

## Performance Validation
- Expected table size: [estimate]
- Query performance target: [target]
- Index overhead: [acceptable?]
</thinking>

<answer>
[Final schema with migration script]
</answer>
```

---

## Performance Optimization

When thinking blocks get large, optimize for clarity without sacrificing depth.

### Guideline: Use Headings and Lists

**Instead of:**
```xml
<thinking>
So I need to figure out if we should use option A or option B. Option A has the advantage of being faster but it's more complex to implement and maintain. Option B is slower but it's simpler. Looking at our requirements, we need good performance but the team is small so maintenance matters. Also considering that this is an MVP so we want to ship quickly. Taking all of this into account I think option B makes more sense because...
</thinking>
```

**Do this:**
```xml
<thinking>
## Options Comparison

### Option A
Pros:
- Faster performance
Cons:
- Complex implementation
- High maintenance burden

### Option B
Pros:
- Simple implementation
- Low maintenance
Cons:
- Slower performance

## Context
- Small team (3 developers)
- MVP timeline (3 months)
- Performance: important but not critical

## Decision
Choose Option B
Reasoning: Simplicity and speed to market outweigh performance gains for MVP
</thinking>
```

### Guideline: Reference Instead of Repeating

**Instead of:**
```xml
<thinking>
## Turn 5
So in turn 1 we discussed X and Y, then in turn 2 we found Z, and in turn 3 we discovered A, and in turn 4 we learned B, so now...
</thinking>
```

**Do this:**
```xml
<thinking>
## Context (from turns 1-4)
- Identified issue: race condition
- Root cause: shared mutable state
- Attempted fix: immutable variables

## New Information (Turn 5)
[Focus on what's new]
</thinking>
```

---

## Summary

Chain of thought reasoning is most powerful when:
- Thinking is structured and organized
- Each step builds on previous insights
- Reflection enables course correction
- Final answers are clear and actionable

Use these patterns as starting points and adapt them to your specific needs.
