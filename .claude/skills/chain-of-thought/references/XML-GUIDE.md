# XML Tag Conventions for Chain of Thought

## Purpose

This guide explains the proper use of XML tags for chain of thought reasoning, based on Claude's native capabilities and best practices for structured output.

---

## Core Tags

### `<thinking>` and `</thinking>`

**Purpose:** Contains the model's internal reasoning process, working through problems step-by-step before providing a final answer.

**When to use:**
- Breaking down complex problems
- Evaluating multiple options
- Planning implementation steps
- Debugging and error analysis
- Reflecting on decisions

**Characteristics:**
- Can contain raw, unpolished reasoning
- May include false starts and corrections
- Markdown formatting supported
- Can be nested with sections

**Example:**
```xml
<thinking>
Let me analyze this problem step by step.

First, what do we know?
- Input: array of numbers
- Goal: find the median

Options:
1. Sort and pick middle - O(n log n)
2. Quickselect - O(n) average case

Given the requirement for efficiency with large datasets, quickselect is better.

Wait, do we need the median repeatedly? If so, we should sort once and reuse.
Checking requirements... yes, median is called multiple times.

Decision: Sort once, O(n log n), then O(1) for each median lookup.
</thinking>
```

### `<answer>` and `</answer>`

**Purpose:** Contains the final, polished response to the user's query.

**When to use:**
- After completing reasoning in `<thinking>`
- For the user-facing output
- When you have a clear, actionable response

**Characteristics:**
- Should be clear and concise
- Well-formatted and professional
- Directly addresses the user's question
- May include code, explanations, or recommendations

**Example:**
```xml
<answer>
For this use case, I recommend sorting the array once and reusing it:

```javascript
class MedianFinder {
  constructor(numbers) {
    this.sorted = [...numbers].sort((a, b) => a - b);
  }

  getMedian() {
    const mid = Math.floor(this.sorted.length / 2);
    if (this.sorted.length % 2 === 0) {
      return (this.sorted[mid - 1] + this.sorted[mid]) / 2;
    }
    return this.sorted[mid];
  }
}
```

Time complexity: O(n log n) for initialization, O(1) for each median query.
</answer>
```

---

## Alternative and Extended Tags

### `<reflection>` (Advanced)

**Purpose:** Explicit self-reflection on reasoning quality, assumptions, or potential errors.

**When to use:**
- When questioning your own reasoning
- Checking for logical errors
- Validating assumptions
- Considering alternative perspectives

**Example:**
```xml
<thinking>
Initial plan: Use a hash map to store frequencies.

<reflection>
Wait, is a hash map the right choice here?
- Pro: O(1) lookup
- Con: Uses more memory than an array
- Question: What's the range of values?

If values are 0-100, an array would be more efficient.
Let me reconsider...
</reflection>

Updated plan: Check value range first, then choose data structure.
</thinking>
```

### `<plan>` (Advanced)

**Purpose:** Specifically demarcates planning sections within thinking blocks.

**When to use:**
- Breaking down implementation into steps
- Outlining approach before execution
- Creating task lists

**Example:**
```xml
<thinking>
<plan>
1. Set up database schema
2. Create API endpoints
3. Implement authentication
4. Add validation logic
5. Write tests
6. Deploy to staging
</plan>

Let me start with step 1...
</thinking>
```

### `<observation>` (Advanced)

**Purpose:** Recording factual observations from code, logs, or data.

**When to use:**
- Analyzing code structure
- Reading log files
- Examining data patterns

**Example:**
```xml
<thinking>
<observation>
Looking at the error logs:
- All failures occur between 2am-3am
- Error code: ECONNREFUSED
- Affected service: database
</observation>

Hypothesis: Scheduled maintenance window causes connection drops.
</thinking>
```

---

## Nesting and Structure

### Markdown Inside XML

You can use full markdown formatting inside XML tags:

```xml
<thinking>
## Problem Analysis

### Option 1: Breadth-First Search
- **Pros:** Finds shortest path
- **Cons:** Higher memory usage

### Option 2: Depth-First Search
- **Pros:** Lower memory
- **Cons:** May not find shortest path

**Decision:** Use BFS because finding the shortest path is critical.
</thinking>
```

### Nested Sections

For complex reasoning, nest sections with markdown headers:

```xml
<thinking>
# Phase 1: Understanding

## Requirements
- [Requirement 1]
- [Requirement 2]

## Constraints
- [Constraint 1]
- [Constraint 2]

# Phase 2: Design

## Architecture Options
[Analysis]

## Decision
[Chosen approach]

# Phase 3: Implementation Planning

## Steps
1. [Step 1]
2. [Step 2]
</thinking>
```

---

## Best Practices

### 1. Separate Concerns

**Don't mix thinking and answer:**
```xml
<!-- Bad -->
<thinking>
Let me figure this out... okay, the answer is X because Y.

So here's the solution: [code]
</thinking>
```

**Do this:**
```xml
<!-- Good -->
<thinking>
Let me figure this out...
- Analysis: [reasoning]
- Conclusion: X because Y
</thinking>

<answer>
Here's the solution:
[code]
</answer>
```

### 2. Show Work, Not Just Conclusions

**Weak thinking:**
```xml
<thinking>
The bug is on line 45. I should fix it.
</thinking>
```

**Strong thinking:**
```xml
<thinking>
Looking for the bug...

Checking error message: "undefined is not a function"
Stack trace points to: line 45

Line 45 code:
```javascript
result.map(x => x * 2)
```

Wait, what is `result`? Tracing back...
Line 40: `const result = fetchData()`

Issue: `fetchData()` might return null/undefined
The code assumes `result` is always an array

Root cause: Missing null check before calling .map()

Fix: Add guard clause or default value
</thinking>
```

### 3. Use Headings for Long Reasoning

```xml
<thinking>
## Step 1: Understand Requirements
[Analysis]

## Step 2: Evaluate Options
### Option A
[Details]

### Option B
[Details]

## Step 3: Make Decision
[Reasoning]

## Step 4: Plan Implementation
[Steps]
</thinking>
```

### 4. Correct Errors Inline

If you make a mistake during reasoning, fix it in the thinking block:

```xml
<thinking>
Initial thought: Use a Set for fast lookup.

Wait, that won't work because we need to preserve order.

Correction: Use an array and keep track of seen items separately.
Actually, even better: Use a Map to preserve insertion order AND get O(1) lookup.

Final decision: Map
</thinking>
```

### 5. Keep Answer Blocks Concise

The `<answer>` should be focused and user-friendly:

```xml
<answer>
Use the following approach:

```javascript
const uniqueOrdered = [...new Map(items.map(item => [item.id, item])).values()];
```

This preserves insertion order while removing duplicates based on `id`.
</answer>
```

---

## Common Patterns

### Pattern 1: Problem-Solution

```xml
<thinking>
Problem: [description]
Constraints: [limitations]
Approach: [method]
Verification: [how to validate]
</thinking>

<answer>
[Solution]
</answer>
```

### Pattern 2: Analysis-Recommendation

```xml
<thinking>
## Current State
[What exists now]

## Issues
[Problems identified]

## Options
[Alternatives considered]

## Recommendation
[Chosen path and why]
</thinking>

<answer>
I recommend [X] because [concise reasoning].

[Implementation details]
</answer>
```

### Pattern 3: Multi-Step Planning

```xml
<thinking>
## Phase 1: Research
[Findings]

## Phase 2: Design
[Architecture]

## Phase 3: Implementation Plan
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Phase 4: Validation
[How to verify success]
</thinking>

<answer>
I'll implement this in three steps:

1. **[Step 1]** - [description]
2. **[Step 2]** - [description]
3. **[Step 3]** - [description]

Starting with step 1...
</answer>
```

### Pattern 4: Iterative Refinement

```xml
<thinking>
## Initial Idea
[First approach]

## Issues with Initial Idea
[Problems found]

## Refined Approach
[Improved version]

## Final Validation
[Checking the refined approach]
✓ Meets requirements
✓ Handles edge cases
✓ Performant
</thinking>

<answer>
[Refined solution]
</answer>
```

---

## XML Tag Dos and Don'ts

### Do:
- ✅ Use `<thinking>` for all reasoning and problem-solving
- ✅ Use `<answer>` for final, user-facing responses
- ✅ Include markdown formatting for readability
- ✅ Show your work, including false starts and corrections
- ✅ Structure long thinking blocks with headers
- ✅ Separate distinct phases of reasoning

### Don't:
- ❌ Put user-facing content in `<thinking>` tags
- ❌ Put internal reasoning in `<answer>` tags
- ❌ Skip thinking for complex problems
- ❌ Make thinking blocks messy and unstructured
- ❌ Repeat the same information in both tags
- ❌ Use thinking as a way to "show off" - be genuine

---

## Integration with Claude Code

In the Claude Code framework, chain of thought reasoning enables:

### 1. Transparent Decision Making
Users can see why you chose a particular approach.

### 2. Debuggable Reasoning
When something goes wrong, the thinking block shows where reasoning diverged.

### 3. Improved Accuracy
Step-by-step reasoning reduces errors compared to direct answers.

### 4. Learning and Improvement
Thinking blocks create a record of decision-making patterns.

### 5. Multi-Agent Coordination
Agents can share reasoning with each other for better collaboration.

---

## Example: Full Workflow

User asks: "Why is my React component re-rendering so much?"

```xml
<thinking>
## Initial Analysis
User reports: excessive re-renders in React component

Need to understand:
1. What triggers re-renders in React?
   - State changes
   - Prop changes
   - Parent re-renders
   - Context changes

2. Common causes of excessive re-renders:
   - New object/array references in render
   - Inline function definitions
   - Missing memo/useMemo/useCallback
   - Context provider value changes

## Information Gathering
I should ask to see the component code to diagnose.

Actually, wait - let me check if they provided code already...
[Checking context]

No code provided yet. I'll need to ask for it.

## Response Strategy
1. Explain common causes
2. Ask for code
3. Provide diagnostic steps
</thinking>

<answer>
React components re-render excessively usually due to:

1. **New object references on each render**
   ```jsx
   // Bad: new object every render
   <Child config={{theme: 'dark'}} />

   // Good: stable reference
   const config = useMemo(() => ({theme: 'dark'}), []);
   <Child config={config} />
   ```

2. **Inline function definitions**
   ```jsx
   // Bad: new function every render
   <button onClick={() => handleClick(id)}>

   // Good: memoized callback
   const onClick = useCallback(() => handleClick(id), [id]);
   <button onClick={onClick}>
   ```

3. **Parent component re-renders**
   - If parent re-renders, children re-render too
   - Fix: Use `React.memo()` for expensive children

Could you share your component code? I'll identify the specific cause.
</answer>
```

---

## Summary

- Use `<thinking>` for reasoning, `<answer>` for final output
- Structure thinking with markdown for clarity
- Show your work, including corrections
- Keep answers concise and user-focused
- Apply patterns appropriate to the task type

These conventions make AI reasoning transparent, debuggable, and effective.
