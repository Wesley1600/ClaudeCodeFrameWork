# Agent Observations - Quick Reference Guide

## Quick Decision Tree

```
User request received
│
├─ Is request clear and unambiguous?
│  ├─ YES → Confirm understanding briefly, proceed
│  └─ NO → Use observation mode ⬇️
│
├─ Does request have multiple valid interpretations?
│  └─ YES → List interpretations, ask which is correct
│
├─ Are there unstated assumptions?
│  └─ YES → State assumptions explicitly, ask for confirmation
│
├─ Is scope unclear?
│  └─ YES → List what you think is in/out of scope, ask for confirmation
│
└─ Are success criteria ambiguous?
   └─ YES → Propose success criteria, ask if they match expectations
```

---

## Common Ambiguity Patterns & Responses

### Pattern 1: Vague Action Verbs

**User says**: "Improve the performance"

**Response template**:
```markdown
I'd like to clarify what performance improvements matter most:

**Options**:
1. Faster initial load time
2. Quicker interaction/response time
3. Better memory usage
4. Smaller bundle size

**Questions**:
- Which user action feels slow?
- What's the current metric and target?
- Any specific threshold? (e.g., "load under 2s")

This helps me focus on the right optimizations.
```

---

### Pattern 2: "The" (Ambiguous References)

**User says**: "Update the component"

**Response template**:
```markdown
I found several components in the codebase:

1. UserProfile component (src/components/UserProfile.jsx)
2. UserSettings component (src/components/UserSettings.jsx)
3. UserCard component (src/components/UserCard.jsx)

**Question**: Which component should I update?

**Also**: What kind of update? (design, functionality, bug fix, refactoring)
```

---

### Pattern 3: Scope Uncertainty

**User says**: "Add authentication"

**Response template**:
```markdown
I'll add authentication. Let me confirm the scope:

**My understanding**:
- Add user login/logout
- Protect certain routes/pages
- Store auth state

**Questions**:
**Critical**:
1. Auth method? (Email/password, OAuth, social login, magic link)
2. Protect which routes/features specifically?

**Important**:
3. Password reset functionality needed?
4. "Remember me" feature?
5. Session timeout duration?

**Optional**:
6. Two-factor authentication?
7. Email verification for new users?
```

---

### Pattern 4: Quality Terms

**User says**: "Make the code better"

**Response template**:
```markdown
"Better" can mean different things. Which matters most?

**Options**:
1. **Performance**: Faster execution
2. **Readability**: Easier to understand
3. **Maintainability**: Easier to modify
4. **Reliability**: Fewer bugs, better error handling
5. **Testability**: Better test coverage
6. **Security**: Fewer vulnerabilities

**Current observations**:
[List specific issues you found]

**Question**: Which aspect should I prioritize, or is it a combination?
```

---

### Pattern 5: Feature Requests Without Context

**User says**: "Add a search feature"

**Response template**:
```markdown
I'll add search functionality. Let me clarify the requirements:

**Critical questions** (affect architecture):
1. **What's searchable?** (users, products, posts, all content)
2. **Where does search happen?** (backend API or frontend filtering)
3. **Search type?** (real-time/as-you-type or on-submit)

**Important questions** (affect UX):
4. Results display? (full items, previews, or just titles)
5. Pagination? (how many results per page)
6. Filters needed? (date, category, etc.)

**Optional enhancements**:
7. Autocomplete/suggestions?
8. Search history?
9. Advanced operators (AND/OR)?

Answering 1-3 will let me start; the rest improves the experience.
```

---

## Quick Templates by Task Type

### Debugging Tasks

```markdown
## Debugging: [Issue Description]

**Observations**:
1. Symptom: [What's happening]
2. Expected: [What should happen]
3. Frequency: Always / Sometimes / Rare
4. Environment: [Where it occurs]

**Hypotheses**:
1. [Hypothesis 1] - Confidence: [%]
2. [Hypothesis 2] - Confidence: [%]

**Next steps**:
1. Test hypothesis 1 by [action]
2. If that's not it, check [alternative]

**Questions**:
- When did this start happening?
- Any recent changes to [related area]?
- Can you reproduce it consistently?
```

---

### Feature Implementation

```markdown
## Feature: [Feature Name]

**Understanding**:
[What the feature should do in one sentence]

**In scope**:
- [Item 1]
- [Item 2]

**Out of scope** (confirm):
- [Item 1]
- [Item 2]

**Questions**:
1. [Critical question about core functionality]
2. [Important question about UX]
3. [Optional question about enhancements]

**Proposed approach**:
[High-level strategy]

Proceed? Or any adjustments?
```

---

### Refactoring Tasks

```markdown
## Refactoring: [Component/Module]

**Current issues observed**:
1. [Issue 1] - Impact: [Why it matters]
2. [Issue 2] - Impact: [Why it matters]

**Proposed changes**:
1. [Change 1]
   - Benefit: [What improves]
   - Risk: [What could break]

2. [Change 2]
   - Benefit: [What improves]
   - Risk: [What could break]

**Questions**:
1. Is backward compatibility required?
2. Should this be incremental or all-at-once?
3. What's the priority: readability vs. performance?

**Testing strategy**:
[How to ensure nothing breaks]
```

---

### Investigation Tasks

```markdown
## Investigation: [Topic]

**Goal**: [What you're trying to learn]

**Approach**:
1. First, check [location/file]
2. Then, analyze [aspect]
3. Finally, test [hypothesis]

**Will report back with**:
- Findings: [What exists]
- Patterns: [How it's structured]
- Recommendations: [What to do]
- Open questions: [What's unclear]

**Timeline**: [How long this might take]

Should I proceed with this approach?
```

---

## Observation Recording - Quick Format

### During Investigation

```markdown
## [TIMESTAMP] - [What you're doing]

**Observation**: [What you found]
**Confidence**: High/Medium/Low
**Implication**: [What this means]
**Next**: [What to do with this info]
```

### At Decision Points

```markdown
## Decision: [Topic]

**Options**:
A) [Option A] - Pros: [X] / Cons: [Y]
B) [Option B] - Pros: [X] / Cons: [Y]

**Recommendation**: [Choice] because [rationale]

**Trade-off**: Accepting [loss] for [gain]

Agree?
```

---

## Confidence Level Guide

| Level | % | When to Use | What to Do |
|-------|---|-------------|------------|
| **High** | 80-100% | Clear requirements, validated approach | Proceed with implementation |
| **Medium** | 50-79% | Some assumptions, minor uncertainties | State assumptions, ask optional questions |
| **Low** | 20-49% | Multiple interpretations, key unknowns | Ask critical questions before proceeding |
| **Very Low** | 0-19% | Request is unclear or contradictory | Must clarify before any work |

---

## Question Priority Framework

### Critical (Must answer before proceeding)
- Blocks all progress
- Wrong answer = wrong solution
- Affects core architecture
- **Example**: "Should this be real-time or batch processing?"

### Important (Significantly affects approach)
- Can proceed with assumption
- Wrong answer = rework needed
- Affects implementation details
- **Example**: "Should we cache results?"

### Optional (Nice to know)
- Can use best judgment
- Wrong answer = minor adjustment
- Affects polish and UX
- **Example**: "Should animation be 200ms or 300ms?"

---

## When NOT to Over-Clarify

**DON'T ask about**:
- Standard best practices (just apply them)
- Obvious implementation details
- Common conventions (follow existing patterns)
- Trivial styling choices (use good judgment)

**DO ask about**:
- Business logic and rules
- Non-obvious user expectations
- Performance/security trade-offs
- Anything with multiple valid approaches

---

## Red Flags - Always Clarify

🚩 **User uses**: "just", "simply", "obviously"
   → Often indicates complexity they're not seeing

🚩 **Multiple stakeholders** mentioned
   → May have conflicting requirements

🚩 **Past failed attempts** mentioned
   → Need to understand what went wrong

🚩 **Words like**: "better", "faster", "cleaner"
   → Subjective; need concrete criteria

🚩 **"Similar to X"** references
   → Need to know which aspects to copy

🚩 **Technical debt** context
   → Need to understand constraints

---

## Communication Patterns

### Show Understanding Before Questioning

✅ **Good**:
```
My understanding: You want [summary].

Questions:
1. [Question]
2. [Question]
```

❌ **Bad**:
```
What do you mean?
```

---

### Provide Context for Questions

✅ **Good**:
```
I found two approaches. A is faster but harder to maintain.
B is cleaner but slightly slower.

Which matters more: speed or maintainability?
```

❌ **Bad**:
```
Should I use A or B?
```

---

### State Assumptions Explicitly

✅ **Good**:
```
I'm assuming users can only edit their own posts, not others'.
Let me know if that's wrong.
```

❌ **Bad**:
```
I added edit functionality.
```

---

## File Naming for Observations

### Convention

```
.claude/observations/
├── YYYY-MM-DD_task-name/
│   ├── observations.json
│   ├── reasoning-log.md
│   ├── clarifications.md
│   └── task-understanding.md
```

### Example

```
.claude/observations/
├── 2025-11-18_add-search-feature/
│   ├── observations.json
│   ├── reasoning-log.md
│   ├── clarifications.md
│   └── task-understanding.md
└── 2025-11-17_fix-checkout-bug/
    └── [archived files]
```

---

## Integration with TodoWrite

```markdown
**Todo**: Implement user authentication

**Observation Note**:
- Clarified: OAuth with Google/GitHub
- Scope: Login/logout only, not registration
- Confidence: 95%
- See: .claude/observations/2025-11-18_add-auth/
```

---

## Quick Decision: Use Observation Mode?

```
YES if:
- Uncertainty > 20%
- Multiple interpretations exist
- High-stakes change
- Ambiguous requirements
- User new to project
- Complex task

NO if:
- Simple, clear request
- Standard task
- Following existing pattern
- Confidence > 90%
- Trivial change
```

---

## Keyboard Shortcuts (Conceptual)

| Action | Quick Command | Output |
|--------|---------------|--------|
| Ask clarifying question | `/clarify` | Structured question template |
| Record observation | `/observe` | Timestamped observation entry |
| Show reasoning | `/reasoning` | Chain-of-thought documentation |
| Check understanding | `/understanding` | Current task interpretation |

---

## Success Indicators

**You're doing it right when**:
✅ User says "yes, exactly!" to clarifications
✅ No rework needed after implementation
✅ User feels heard and informed
✅ Confidence increases through conversation
✅ Questions are specific and actionable
✅ Observations help future debugging

**You might be overdoing it when**:
⚠️ User gets frustrated with questions
⚠️ You ask more than 5 questions at once
⚠️ You ask about trivial decisions
⚠️ You delay obvious simple tasks
⚠️ You record every tiny detail

---

## Remember

> "Clarify the ambiguous, state the assumed, record the observed."

**Three core actions**:
1. **When uncertain** → Ask
2. **When assuming** → State
3. **When learning** → Record

**The goal**: Build shared understanding that leads to the right solution the first time.
