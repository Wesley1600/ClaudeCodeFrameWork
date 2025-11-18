# Claude Code Skills

This directory contains custom skills for Claude Code that use progressive disclosure to optimize context window usage.

## Structure

```
.claude/skills/
├── README.md                          # This file
├── progressive-disclosure/            # Meta-skill for managing progressive disclosure
│   └── skill.md
├── umap-optimization/                 # UMAP-specific optimization skill
│   └── skill.md
├── automated-ui-testing.md            # UI testing automation skill
├── batch-processing.md                # Batch processing skill
├── error-handling.md                  # Error handling framework skill
├── scenario-simulation/               # Scenario modeling and decision analysis
│   ├── SKILL.md
│   ├── README.md
│   ├── QUICK_START.md
│   ├── examples/
│   └── templates/
├── summarization/                     # Text summarization skill
│   └── SKILL.md
└── [other-skills]/                    # Additional skills
    └── skill.md
```

## Progressive Disclosure

Skills are structured in three levels to optimize context window usage:

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

## Available Skills

### Progressive Disclosure Meta-Skill (`progressive-disclosure/skill.md`)

Manages the progressive disclosure of skill content based on task relevance.

**Use this skill when:**
- Building or managing the skill system itself
- Optimizing context window usage
- Understanding how skills are loaded

**Key features:**
- Relevance scoring algorithm
- Context window budget management
- Dynamic level upgrading
- Skill dependency resolution

---

### UMAP Optimization Skill (`umap-optimization/skill.md`)

Provides optimization strategies for UMAP-based embedding systems.

**Use this skill when:**
- Training is too slow (> 5 min for N < 10K)
- Dataset size > 10,000 samples
- Memory usage exceeds GPU capacity
- Deploying UMAP models to production

**Key features:**
- Cluster caching (10x speedup)
- FAISS integration (100x+ for large N)
- Mixed precision training (2x speedup)
- Numerical stability enhancements

---

### Automated UI Testing Skill (`automated-ui-testing.md`)

A comprehensive skill for automating web application testing using headless browsers (Playwright, Puppeteer, or Selenium).

**Type:** Testing
**Triggers:** UI testing, web testing, playwright, puppeteer, selenium, e2e testing, test automation, QA, quality assurance, regression testing

**Use this skill when:**
- Testing web application functionality (forms, authentication, navigation)
- Performing quality assurance and regression testing
- Setting up end-to-end test automation
- Validating responsive design across devices
- Testing accessibility compliance
- Implementing visual regression testing
- Creating CI/CD test pipelines

**Key features:**
- Complete testing infrastructure setup
- Test script generation for common scenarios
- Page Object Model implementation
- API mocking and network interception
- Screenshot and video capture on failures
- Comprehensive test reporting
- CI/CD integration templates
- Support for multiple browsers and viewports

**How to activate:**
```
"Set up automated UI testing for my React app"
"Create tests for the login flow"
"Test the shopping cart functionality"
```

---

### Batch Processing Skill (`batch-processing.md`)

A comprehensive skill for executing batch operations efficiently, reducing overhead and maintaining consistent processing across multiple similar tasks.

**Type:** Data Processing
**Triggers:** batch processing, bulk operations, process multiple files, batch execution, parallel processing, bulk refactoring, batch script execution

**Use this skill when:**
- Processing multiple files (PDFs, images, text files, code files)
- Running multiple scripts or tests
- Applying the same transformation across multiple files
- Bulk data processing operations
- Mass code refactoring or migrations
- Executing similar tasks repeatedly

**Key features:**
- Intelligent parallel vs sequential processing strategies
- Comprehensive error handling (continues on failure)
- Progress tracking via todo lists
- Detailed success/failure reporting with statistics
- Resource-aware processing with safety checks
- Support for various file types and operations
- Hybrid batch processing for large datasets

**How to activate:**
```
"Process all PDF files in the /docs folder and extract text"
"Run all test files in the tests/ directory"
"Apply eslint fixes to all JavaScript files in src/"
"Convert all PNG images in /images to JPEG format"
```

---

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
```
Use the error-handling skill to execute this git push with retry logic
```

---

### Scenario Simulation Skill (`scenario-simulation/SKILL.md`)

A comprehensive skill for modeling different scenarios, creating decision trees, running simulations, and analyzing impacts.

**Use this skill when:**
- Making business decisions (pricing, hiring, investments)
- Planning technical architecture (scaling, migrations)
- Assessing risks and mitigation strategies
- Forecasting outcomes under uncertainty
- Comparing multiple options or strategies

**Key features:**
- Multi-scenario analysis (best/worst/expected cases)
- Decision tree creation and visualization
- Monte Carlo simulations
- Sensitivity analysis
- Python and TypeScript implementation templates

**How to activate:**
```
Use the scenario simulation skill to model launching a new product
```

### Summarization Skill (`summarization/SKILL.md`)

Condenses long documents, conversation logs, or transcripts into concise summaries.

**Use this skill when:**
- Processing long documents or articles
- Summarizing conversation histories
- Creating executive summaries
- Extracting key points from verbose content
- Different detail levels needed

**Key features:**
- Multiple output formats (bullet points, paragraphs, executive summary)
- Customizable detail levels
- Supports retrieval from memory/files
- Focus on key insights and actionable items

**How to activate:**
```
Use the summarization skill to summarize this document
```

---

## Creating a New Skill

### Progressive Disclosure Format (Recommended)

Use the template from `progressive-disclosure/skill.md` (Appendix A) to create new skills with three-tier structure:

```markdown
# Skill Name

<!-- LEVEL: METADATA -->
## Metadata

**Skill Name:** [Name]
**Type:** [implementation|debugging|optimization|etc.]
**Version:** [Semantic version]
**Purpose:** [One-line description]
**Triggers:** [Comma-separated keywords]
**Dependencies:** [List of required skills, if any]
**Context Cost:** [Low|Medium|High]
**Complexity:** [0.0-1.0 scale]

**Quick Summary:**
[2-3 sentence overview]

---

<!-- LEVEL: INSTRUCTIONS -->
## Instructions

### When to Use This Skill
[Describe scenarios]

### Basic Workflow
1. [Step 1]
2. [Step 2]
3. [Step 3]

---

<!-- LEVEL: RESOURCES -->
## Resources

### Detailed Implementation
[Comprehensive guide]
```

### Simple Format (Alternative)

For simpler skills, create a markdown file directly in `.claude/skills/`:

1. Create a markdown file in `.claude/skills/`
2. Document the skill's purpose and usage
3. Provide clear examples and patterns
4. Include decision trees for when to use the skill
5. Add an entry to this README

### Subdirectory Format (For Complex Skills)

For skills with multiple files (templates, examples, docs):

1. Create a subdirectory in `.claude/skills/`
2. Add `SKILL.md` as the main skill definition
3. Include `README.md` for detailed documentation
4. Add `examples/` and `templates/` as needed
5. Follow the progressive disclosure levels in `SKILL.md`

See `scenario-simulation/` for a complete example.

## Best Practices

### For Skill Authors

- **Keep metadata concise:** Every token counts when multiple skills are loaded
- **Make instructions actionable:** Focus on the "how" and "when"
- **Put complexity in resources:** Save heavy content for when it's needed
- **Test at each level:** Ensure each level is useful standalone
- **Use clear triggers:** Help the relevance scoring find your skill
- **Specific and actionable:** Provide clear steps
- **Include examples:** Show real usage scenarios
- **Define scope:** Be clear about when to use the skill
- **Error handling:** Always consider what can go wrong
- **User communication:** Guide how to inform users

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
- **Testing:** Writing tests, validation, QA
- **Documentation:** Creating docs, comments
- **Integration:** Connecting systems, APIs
- **Data Processing:** ETL, transformations, batch processing
- **Machine Learning:** Training, inference, evaluation
- **Decision Support:** Scenario modeling, option evaluation
- **Content Processing:** Summarization, extraction, transformation

## Metrics

Track progressive disclosure effectiveness:

- **Efficiency Score:** Ratio of tokens at lower levels (higher is better)
- **Upgrade Rate:** How often skills need to be upgraded (lower is better)
- **Cache Hit Rate:** How often cached content is reused (higher is better)
- **Relevance Accuracy:** Do loaded skills actually get used? (track references)

## Version History

- **v1.3.0** (2025-11-18): Added Scenario Simulation and Summarization skills
- **v1.2.0** (2025-11-18): Added Batch Processing Skill
- **v1.1.0** (2025-11-18): Added Automated UI Testing Skill
- **v1.0.0** (2025-11-18): Initial progressive disclosure implementation

## Integration

Skills are automatically available to Claude Code when placed in this directory. Reference them by name or topic in your prompts.

## Contributing

When adding new skills:

1. Follow the template structure (progressive disclosure format recommended)
2. Test at each disclosure level
3. Measure token counts (metadata ~500, instructions ~3K, resources ~15K)
4. Verify triggers match actual use cases
5. Document dependencies clearly
6. Add entry to this README under "Available Skills"

## Additional Resources

- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference guide (if available)
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Detailed usage guide (if available)
- Individual skill documentation files for detailed instructions

## License

Skills are part of the Claude Code Framework and follow the same license as the main project.
