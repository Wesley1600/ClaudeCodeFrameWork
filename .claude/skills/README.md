# Claude Code Skills

This directory contains skills for Claude Code that use progressive disclosure to optimize context window usage.

## Structure

```
.claude/skills/
├── README.md                          # This file
├── progressive-disclosure/            # Meta-skill for managing progressive disclosure
│   └── skill.md
└── [other-skills]/                    # Additional skills
    └── skill.md
```

## Progressive Disclosure

Skills are structured in three levels:

1. **Metadata** (Always loaded) - ~500 tokens
   - Skill name and description
   - Triggers and keywords
   - Dependencies

2. **Instructions** (Loaded when relevant) - ~3K tokens
   - How to use the skill
   - When to apply it
   - Basic examples

3. **Resources** (Loaded when critical) - ~15K tokens
   - Detailed algorithms
   - Complex examples
   - Edge cases and troubleshooting

## Creating a New Skill

Use the template from `progressive-disclosure/skill.md` (Appendix A) to create new skills.

Key requirements:

1. **Mark sections clearly:**
   ```markdown
   <!-- LEVEL: METADATA -->
   ## Metadata
   ...

   <!-- LEVEL: INSTRUCTIONS -->
   ## Instructions
   ...

   <!-- LEVEL: RESOURCES -->
   ## Resources
   ...
   ```

2. **Include required metadata fields:**
   - Skill Name
   - Type
   - Version
   - Purpose
   - Triggers
   - Dependencies
   - Context Cost
   - Complexity

3. **Self-contained levels:**
   - Each level should be readable on its own
   - Higher levels build on lower levels
   - Don't reference content from higher levels in lower levels

## Usage

The progressive disclosure meta-skill automatically:

1. **Analyzes** user queries for relevance
2. **Scores** each skill based on keyword match, topic similarity, task type, and complexity
3. **Loads** appropriate levels based on relevance scores:
   - Score < 0.2: Skip
   - Score 0.2-0.5: Load metadata
   - Score 0.5-0.8: Load instructions
   - Score 0.8+: Load full resources
4. **Manages** context window budget
5. **Upgrades** skill levels dynamically if heavily used

## Best Practices

### For Skill Authors

- **Keep metadata concise:** Every token counts when multiple skills are loaded
- **Make instructions actionable:** Focus on the "how" and "when"
- **Put complexity in resources:** Save heavy content for when it's needed
- **Test at each level:** Ensure each level is useful standalone
- **Use clear triggers:** Help the relevance scoring find your skill

### For Skill Users (Claude Code)

- **Start conservative:** Load metadata first, upgrade if needed
- **Monitor usage:** Track which skills are actually referenced in responses
- **Respect budget:** Don't load full resources for low-priority skills
- **Cache aggressively:** Parsing is expensive, reuse loaded content
- **Measure effectiveness:** Track tokens saved vs. quality impact

## Context Window Budget

With 200K token context window:

```
Reserved for task execution: ~60-80K tokens
  - User query & history: 10-20K
  - Code being edited: 20-40K
  - Tool outputs: 10-30K
  - Response generation: 10-20K

Available for skills: ~100-120K tokens

Recommended allocation:
  - 5-10 high-relevance skills (full resources): ~100K tokens
  - 10-20 medium-relevance skills (instructions): ~30-60K tokens
  - 20-30 low-relevance skills (metadata): ~10-15K tokens
```

## Skill Types

Common skill categories:

- **Implementation:** Writing new code, adding features
- **Debugging:** Finding and fixing bugs, error analysis
- **Optimization:** Performance improvements, refactoring
- **Analysis:** Understanding code, architectural review
- **Testing:** Writing tests, validation
- **Documentation:** Creating docs, comments
- **Integration:** Connecting systems, APIs
- **Data Processing:** ETL, transformations
- **Machine Learning:** Training, inference, evaluation

## Example: UMAP Optimization Skill

See how a skill would be structured for this codebase:

```markdown
# UMAP Optimization

<!-- LEVEL: METADATA -->
## Metadata

**Skill Name:** UMAP Optimization
**Type:** optimization
**Version:** 1.0.0
**Purpose:** Optimize UMAP implementations for large-scale datasets
**Triggers:** umap, optimize, performance, scale, large dataset, embedding
**Dependencies:** None
**Context Cost:** Medium
**Complexity:** 0.7

**Quick Summary:**
Provides optimization strategies for UMAP-based embedding systems, including
cluster caching, FAISS integration, and batch processing improvements.

---

<!-- LEVEL: INSTRUCTIONS -->
## Instructions

### When to Use
- Dataset size > 10,000 samples
- Training time exceeds acceptable threshold
- Memory usage is too high
- Need to scale to production workloads

### Key Optimizations
1. **Cluster Caching:** Reuse k-means clusters across steps
2. **FAISS Integration:** Replace torch.cdist with FAISS for large N
3. **Batch Processing:** Optimize edge batch sizes
4. **Mixed Precision:** Use AMP for GPU acceleration

---

<!-- LEVEL: RESOURCES -->
## Resources

### Detailed Implementation

[Full algorithms, code examples, benchmarks...]
```

## Metrics

Track progressive disclosure effectiveness:

- **Efficiency Score:** Ratio of tokens at lower levels (higher is better)
- **Upgrade Rate:** How often skills need to be upgraded (lower is better)
- **Cache Hit Rate:** How often cached content is reused (higher is better)
- **Relevance Accuracy:** Do loaded skills actually get used? (track references)

## Version History

- **v1.0.0** (2025-11-18): Initial progressive disclosure implementation

## Contributing

When adding new skills:

1. Follow the template structure
2. Test at each disclosure level
3. Measure token counts (metadata ~500, instructions ~3K, resources ~15K)
4. Verify triggers match actual use cases
5. Document dependencies clearly

## License

Skills are part of the Claude Code Framework and follow the same license as the main project.
