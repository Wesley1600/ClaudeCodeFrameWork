# Claude Skills Examples and Templates

A comprehensive collection of Claude Skills templates and examples to help you understand how to create and structure your own custom skills.

## Overview

This directory contains:

1. **template-skill/** - The foundational template showing best practices and structure
2. **api-documentation/** - Example skill for creating API documentation
3. **data-analysis/** - Example skill for analyzing and visualizing data
4. **markdown-formatter/** - Example skill for formatting and validating Markdown

Each skill is self-contained with its own SKILL.md file, helper scripts, documentation, and examples.

## Quick Start

### 1. Understanding Skill Structure

Every Claude Skill consists of:

```
skill-name/
├── SKILL.md              # Core skill definition (required)
├── scripts/              # Helper scripts (optional)
│   ├── *.py
│   └── *.sh
├── references/           # Supporting documentation (optional)
│   └── *.md
└── assets/              # Templates and examples (optional)
    ├── templates/
    └── examples/
```

### 2. Key Files

**SKILL.md** - The heart of every skill. Contains:
- YAML frontmatter with `name` and `description`
- Clear purpose and use cases
- Specific instructions for Claude
- Guidelines and best practices
- Concrete examples
- Links to helper resources

### 3. Creating Your Own Skill

1. **Copy the template-skill directory**
   ```bash
   cp -r template-skill my-new-skill
   cd my-new-skill
   ```

2. **Edit SKILL.md** with your skill details:
   - Replace the frontmatter (name and description)
   - Write your specific instructions
   - Add examples for your use case
   - Link to your helper scripts

3. **Add helper scripts** (optional)
   - Python scripts for data processing
   - Bash scripts for automation
   - Any tools your skill needs

4. **Include documentation** (optional)
   - Best practices specific to your domain
   - API references
   - Configuration guides

5. **Test your skill** with Claude Code
   - Activate the skill
   - Test the examples
   - Verify helper scripts work
   - Refine instructions based on results

## Skills in This Repository

### 1. template-skill

The foundation for all other skills. Use this as a reference when creating new skills.

**Files:**
- `SKILL.md` - Complete skill template
- `scripts/helper.py` - Python utility functions
- `scripts/utilities.sh` - Bash utility functions
- `references/best-practices.md` - Comprehensive best practices guide
- `assets/templates/markdown-template.md` - Markdown document template
- `assets/examples/example-data.json` - Sample JSON data structure

**Use this to learn:**
- Proper SKILL.md structure
- How to organize helper files
- Best practices for skill development
- Example code patterns

### 2. api-documentation

Generate professional API documentation with examples, parameters, and error codes.

**Key Features:**
- REST and GraphQL API documentation
- OpenAPI specification generation
- Code examples in multiple languages
- Error codes and troubleshooting
- Request/response examples
- Authentication documentation

**When to use:**
- Documenting REST APIs
- Creating OpenAPI/Swagger specs
- Building developer guides
- Maintaining API references
- Creating SDK documentation

**Example usage:**
```
Activate api-documentation skill and help me create comprehensive documentation for our REST API with request/response examples.
```

### 3. data-analysis

Analyze datasets, create visualizations, and generate statistical reports.

**Key Features:**
- Exploratory data analysis (EDA)
- Statistical summaries
- Visualization generation
- Trend and pattern identification
- Anomaly detection
- Predictive modeling
- Professional reports

**When to use:**
- Understanding new datasets
- Creating data reports
- Finding trends and patterns
- Building dashboards
- Forecasting future values
- Identifying data quality issues

**Example usage:**
```
Use the data-analysis skill to analyze our customer data and create a visualization showing purchase patterns by region.
```

### 4. markdown-formatter

Format, validate, and optimize Markdown documents.

**Key Features:**
- Consistent formatting
- Syntax validation
- Automatic table of contents
- Linting and style checking
- Code block formatting
- Link validation
- Multiple export formats

**When to use:**
- Standardizing documentation
- Cleaning up Markdown files
- Creating professional READMEs
- Validating documentation syntax
- Converting between formats
- Enforcing style guides

**Example usage:**
```
Use the markdown-formatter skill to format this README, generate a table of contents, and ensure all links are valid.
```

## Best Practices Across All Skills

### 1. Structure

- Keep SKILL.md concise (under 5,000 words)
- Use progressive disclosure (detailed docs in separate files)
- Organize helper scripts logically
- Include examples that users can run

### 2. Clarity

- Write clear, specific instructions
- Use active voice and direct language
- Provide concrete examples with inputs and outputs
- Document all parameters and requirements

### 3. Completeness

- Include example data and templates
- Document error handling
- Explain edge cases and limitations
- Link to supporting documentation

### 4. Testing

- Verify all examples work correctly
- Test helper scripts in isolation
- Ensure links to resources are valid
- Check for missing dependencies

## Skill Patterns

### Pattern 1: Data Processing

Skills that transform or analyze data:
- **Input**: Raw data (CSV, JSON, database)
- **Processing**: Cleaning, filtering, aggregation
- **Output**: Processed data, statistics, visualizations

Example: data-analysis skill

### Pattern 2: Documentation Generation

Skills that create formatted documentation:
- **Input**: Content or specifications
- **Processing**: Formatting, validation, organization
- **Output**: Professional documents in various formats

Example: api-documentation, markdown-formatter skills

### Pattern 3: Code/Template Generation

Skills that generate code or templates:
- **Input**: Specifications or requirements
- **Processing**: Template substitution, code generation
- **Output**: Ready-to-use code or templates

Example: template-skill

### Pattern 4: Utility/Helper Skills

Skills that provide utility functions:
- **Input**: Various inputs depending on task
- **Processing**: Utility operations
- **Output**: Transformed data or results

## Common Scenarios

### Scenario 1: Create a New Skill for Your Team

1. Use `template-skill` as a starting point
2. Define your skill's purpose clearly
3. Write specific instructions for Claude
4. Add examples and helper scripts
5. Test with your team

### Scenario 2: Improve Existing Documentation

1. Activate `markdown-formatter` skill
2. Reference your documentation files
3. Ask for formatting improvements
4. Generate table of contents
5. Validate links

### Scenario 3: Document Your API

1. Activate `api-documentation` skill
2. Provide endpoint details
3. Get professional documentation
4. Include code examples
5. Generate OpenAPI spec

### Scenario 4: Analyze Business Data

1. Activate `data-analysis` skill
2. Upload your dataset
3. Get exploratory analysis
4. Create visualizations
5. Generate insights report

## File Organization Tips

### Keep Skills Modular

```
Each skill should:
- Have one primary purpose
- Be usable independently
- Work well with other skills
- Document its interfaces clearly
```

### Organize by Complexity

```
Simple Skills:
├── SKILL.md
└── assets/templates/

Medium Complexity:
├── SKILL.md
├── scripts/
└── assets/

Complex Skills:
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

### Version Your Skills

Track skill versions in:
- SKILL.md (add version field to frontmatter)
- references/changelog.md
- Git commit history

## Contributing

To add your own skill to this collection:

1. Create a new directory following the naming convention
2. Write a comprehensive SKILL.md file
3. Add helper scripts and documentation
4. Include example data
5. Test thoroughly
6. Document in this README

## Learning Resources

### For Skill Development

- Start with `template-skill/references/best-practices.md`
- Review the SKILL.md files in other example skills
- Read through helper scripts to see patterns
- Check the assets/examples/ directories

### For Specific Skills

- **API Documentation**: `api-documentation/SKILL.md`
- **Data Analysis**: `data-analysis/SKILL.md`
- **Markdown Formatting**: `markdown-formatter/SKILL.md`

### External Resources

- [Claude Code Skills Documentation](https://docs.claude.com/claude-code/skills)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)

## File Structure Reference

```
skills/
├── README.md (this file)
│
├── template-skill/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── helper.py
│   │   └── utilities.sh
│   ├── references/
│   │   └── best-practices.md
│   └── assets/
│       ├── templates/
│       │   └── markdown-template.md
│       └── examples/
│           └── example-data.json
│
├── api-documentation/
│   └── SKILL.md
│
├── data-analysis/
│   └── SKILL.md
│
└── markdown-formatter/
    └── SKILL.md
```

## Tips for Success

1. **Start Simple** - Begin with a clear, focused purpose
2. **Use Examples** - Show exactly what you want Claude to do
3. **Document Thoroughly** - Don't assume users will guess
4. **Test with Claude** - Actually use your skills with Claude Code
5. **Iterate** - Refine based on how Claude interprets your skill
6. **Share and Collect Feedback** - Improve based on team usage
7. **Keep Learning** - Review how others build skills

## Quick Reference

### SKILL.md Template

```markdown
---
name: your-skill-name
description: What this skill does in one clear sentence
---

# Your Skill Name

[One paragraph explaining the purpose]

## When to Use

- Use case 1
- Use case 2

## Key Features

1. Feature 1
2. Feature 2

## Instructions

[How Claude should behave when using this skill]

## Guidelines

- Guideline 1
- Guideline 2

## Examples

### Example 1
[Input and output example]

### Example 2
[Another example]

## Resources

- [Documentation](./references/)
- [Scripts](./scripts/)
- [Templates](./assets/templates/)

## Support

[How to get help]
```

## Support and Questions

For help with Claude Skills:

1. **Review this README** - Many answers are here
2. **Check the examples** - See how other skills are structured
3. **Read best practices** - Found in `template-skill/references/`
4. **Test incrementally** - Try small changes and verify they work
5. **Use Claude Code** - Activate skills and experiment

## License

These examples and templates are provided as-is for learning and use with Claude Code.

---

**Happy skill building! 🚀**
