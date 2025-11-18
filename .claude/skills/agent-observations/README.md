# Agent Observations Skill

A Claude Code skill that enables transparent, observation-driven development by recording intermediate reasoning, asking clarifying questions, and sharing chain-of-thought processes.

## Overview

The Agent Observations skill helps Claude Code work more transparently and accurately by:

- **Recording observations**: Documenting intermediate findings and partial results
- **Asking clarifying questions**: Proactively identifying and resolving ambiguities
- **Chain-of-thought injection**: Making reasoning visible to users and other agents
- **Memory persistence**: Storing observations for future reference and continuity
- **Transparency**: Ensuring tasks are understood correctly before implementation

## Installation

This skill is located in `.claude/skills/agent-observations/` and should be automatically discovered by Claude Code.

## Usage

### Invoking the Skill

Use any of these commands to activate the skill:

```
/agent-observations
/observe
/clarify
/reasoning
```

Or simply ask Claude Code to use the skill:
```
"Please use the agent-observations skill to help me with this task"
```

### When to Use

This skill is particularly valuable for:

1. **Ambiguous requirements**: When task descriptions are vague or open to interpretation
2. **Complex debugging**: When investigating issues requires hypothesis testing
3. **Architectural decisions**: When multiple valid approaches exist
4. **Learning codebases**: When exploring unfamiliar code
5. **Collaborative work**: When reasoning needs to be shared with team members
6. **High-stakes changes**: When mistakes would be costly

### Example Scenarios

#### Scenario 1: Ambiguous Feature Request

**User**: "Add a search feature"

**With skill**: Claude will ask about search scope, UI/UX preferences, performance requirements, and data sources before implementing.

**Without skill**: Claude might implement a search feature that doesn't match expectations.

---

#### Scenario 2: Debugging Investigation

**User**: "Fix the performance issue"

**With skill**: Claude will:
- Document initial observations (slow API, large payload, etc.)
- Record hypotheses and test results
- Share reasoning about root cause
- Propose solution with trade-offs
- Ask for confirmation before implementing

**Without skill**: Claude might jump to a solution that addresses symptoms rather than root cause.

---

#### Scenario 3: Architecture Decision

**User**: "Refactor the authentication system"

**With skill**: Claude will:
- Analyze current architecture
- Document observations about pain points
- Present multiple refactoring approaches
- Explain trade-offs of each approach
- Ask which constraints matter most (security, performance, maintainability)

**Without skill**: Claude might choose an approach based on assumptions about priorities.

## Observation Memory Structure

The skill creates a `.claude/observations/` directory with:

```
.claude/observations/
├── observations.json          # Structured observation log
├── reasoning-log.md          # Human-readable chain-of-thought
├── clarifications.md         # Questions asked and answers received
├── task-understanding.md     # Evolving understanding of current task
└── archive/                  # Completed task observations
    └── YYYY-MM-DD-task-name/
```

### Observation Format

Each observation includes:

- **Timestamp**: When the observation was made
- **Type**: discovery, assumption, uncertainty, finding, or result
- **Content**: What was observed
- **Confidence**: High, medium, or low
- **Implications**: What it means for the task
- **Next steps**: How to act on the information

### Example Observation Entry

```json
{
  "timestamp": "2025-11-18T10:30:00Z",
  "observation_type": "finding",
  "content": "API endpoint /users/search returns all user fields including sensitive data (email, phone) even when only name is needed",
  "confidence": "high",
  "implications": "Over-fetching data causes slow response times and potential security concern",
  "next_steps": "Implement field selection parameter or use GraphQL"
}
```

## Key Features

### 1. Ambiguity Detection

The skill automatically identifies common ambiguity patterns:

- Vague requirements ("make it better")
- Multiple valid interpretations ("update the UI")
- Unstated assumptions ("add authentication")
- Scope uncertainty ("improve performance")
- Context-dependent terms ("the file", "the function")

### 2. Structured Clarification

Questions are organized by priority:

- **Critical**: Blocks progress if unanswered
- **Important**: Significantly affects approach
- **Optional**: Improves solution but not essential

### 3. Chain-of-Thought Documentation

Reasoning is shared in clear, structured format:

- Current understanding
- Observations so far
- Reasoning process
- Uncertainties
- Proposed next steps
- Questions for clarification

### 4. Progressive Refinement

Understanding evolves through cycles of:

1. Observe (gather information)
2. Reason (analyze and hypothesize)
3. Clarify (ask questions)
4. Refine (update understanding)
5. Act (implement with confidence)

## Integration with Claude Code Tools

The skill integrates seamlessly with:

- **TodoWrite**: Track observations as part of task progress
- **Task**: Delegate observation sub-tasks to specialized agents
- **Read/Write**: Persist observations to disk
- **Grep/Glob**: Discover related code during observation
- **Bash**: Run experiments to test hypotheses

## Best Practices

### Do's ✅

- **Be explicit about confidence**: "I'm 80% certain this is X, but it could be Y"
- **Show your work**: Don't just state conclusions, show the reasoning path
- **Update as you learn**: Revise understanding when new information emerges
- **Prioritize questions**: Help users know what's critical vs. nice-to-have
- **Link to code**: Use `file.js:42` references in observations
- **Time-box investigation**: Ask for help if stuck rather than spiraling
- **Acknowledge uncertainty**: "I don't have enough information to determine X"

### Don'ts ❌

- **Don't assume**: State assumptions explicitly or ask questions
- **Don't hide reasoning**: Jump to solutions without showing exploration
- **Don't ask binary questions**: Provide context and trade-offs
- **Don't be vague**: "Something seems wrong" → "Function X at file.js:42 returns null when input is Y"
- **Don't record everything**: Focus on decision-relevant observations

## Configuration

### Skill Metadata

Located in `skill.json`:

```json
{
  "name": "agent-observations",
  "description": "Records agent observations, intermediate reasoning, and asks clarifying questions when input is ambiguous.",
  "aliases": ["observe", "clarify", "reasoning"],
  "location": "user"
}
```

### Customization

You can customize the skill by editing `prompt.md` to:

- Add domain-specific observation patterns
- Modify question templates
- Change observation file structure
- Add integration with external tools
- Customize confidence thresholds

## Examples

### Example 1: Before and After

**Before (without skill)**:
```
User: Fix the bug in checkout
Claude: I've updated the checkout validation logic in checkout.js
User: That's not the bug I meant...
```

**After (with skill)**:
```
User: Fix the bug in checkout
Claude: I'll investigate the checkout process. First, let me clarify:

## Questions
1. What's the specific bug? (error message, incorrect behavior, etc.)
2. When does it occur? (always, specific conditions, certain users?)
3. Any error logs available?

## Initial Observations
I've found:
- Checkout code in: /src/components/checkout/
- 3 potential issues mentioned in code comments
- Last modified: 2 weeks ago

Once you clarify the specific bug, I'll document my investigation
and propose a fix.
```

### Example 2: Complex Task Breakdown

**User**: "Optimize the application"

**Claude's Observation-Driven Response**:
```markdown
## Initial Task Analysis

**My Understanding**: You want to improve application performance.

**Ambiguities Identified**:
- Which aspects? (load time, runtime performance, memory usage, bundle size)
- Which user flows? (initial load, specific features, all interactions)
- Target metrics? (what's the goal - 2x faster, specific millisecond target)
- Constraints? (acceptable trade-offs in code complexity, bundle size)

## Initial Observations

I've analyzed the codebase:

**Findings**:
1. Bundle size: 2.3MB (Confidence: High)
   - Implication: Slow initial load on 3G connections

2. Unoptimized images: 15 PNGs, no lazy loading (Confidence: High)
   - Implication: Unnecessary bandwidth usage

3. No code splitting: Single bundle (Confidence: High)
   - Implication: Users download code for features they may not use

**Questions**:

**Critical**:
1. What performance problem are users experiencing?
2. What's the priority: initial load, interaction speed, or both?

**Important**:
3. Are there specific pages/features that need optimization first?
4. What's acceptable bundle size increase for better UX?

**Optional**:
5. Should we add performance monitoring?
6. Any budget for CDN or image optimization services?

Please answer the critical questions, and I'll create a tailored
optimization plan with specific, measurable improvements.
```

## Troubleshooting

### Skill Not Loading

Check that:
1. File is located at `.claude/skills/agent-observations/prompt.md`
2. `skill.json` exists in the same directory
3. JSON syntax is valid

### Too Many Questions

If Claude asks too many questions:
- Provide more context upfront
- Say "use your best judgment for non-critical decisions"
- Adjust the skill prompt to reduce question threshold

### Not Enough Clarification

If Claude doesn't ask enough questions:
- Explicitly say "use agent-observations skill"
- Make request more open-ended
- Ask "what would you need to know to do this well?"

## Contributing

To improve this skill:

1. Add domain-specific patterns to `prompt.md`
2. Create reusable observation templates
3. Share examples of successful clarifications
4. Document edge cases and how to handle them

## License

This skill is part of the ClaudeCodeFrameWork project.

## Related Skills

- **session-start-hook**: Configure project startup
- Other skills can be created to complement observation-driven development

## Support

For issues or questions about this skill:
1. Check the examples in `prompt.md`
2. Review observation logs in `.claude/observations/`
3. Open an issue in the project repository

---

**Remember**: The goal isn't to ask permission for every decision, but to ensure correct understanding and transparent reasoning. Good observations and clarifications save time by preventing rework.
