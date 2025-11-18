# Claude Skills - Best Practices Guide

This document provides comprehensive guidelines for creating effective and maintainable Claude Skills.

## 1. Skill Structure

### Directory Organization

Follow this recommended structure:

```
my-skill/
├── SKILL.md                    # Core skill definition (required)
├── scripts/                    # Helper scripts
│   ├── main.py
│   ├── helpers.py
│   └── setup.sh
├── references/                 # Documentation
│   ├── best-practices.md
│   ├── api-reference.md
│   └── troubleshooting.md
├── assets/                     # Templates and examples
│   ├── templates/
│   │   ├── default-template.txt
│   │   └── advanced-template.txt
│   └── examples/
│       ├── example-input.json
│       └── example-output.json
└── README.md                   # Optional: detailed documentation
```

### Key Principles

- **Single Responsibility**: Each skill should have one primary purpose
- **Modularity**: Design skills to compose well with other skills
- **Progressive Disclosure**: Keep SKILL.md concise; put detailed docs elsewhere
- **Self-Contained**: Include all resources needed to operate the skill

## 2. SKILL.md Format

### Required Frontmatter

```yaml
---
name: skill-name
description: Clear, concise description of what the skill does
---
```

### Recommended Sections

1. **Skill Name (H1)** - Main heading matching the SKILL.md filename
2. **Purpose** - What problem does this skill solve?
3. **When to Use** - Specific use cases and scenarios
4. **Key Features** - What makes this skill useful
5. **Instructions** - How Claude should behave when using the skill
6. **Guidelines** - Important rules to follow
7. **Examples** - Concrete usage patterns
8. **Resources** - Links to helper files and documentation
9. **Support** - How to get help or report issues

### Example SKILL.md Structure

```markdown
---
name: my-skill
description: Brief, clear description
---

# My Skill Name

[Keep introduction concise - max 2-3 sentences]

## Purpose

[Explain what problem this solves]

## When to Use

- Use case 1
- Use case 2
- Use case 3

## Key Features

1. Feature 1 - brief description
2. Feature 2 - brief description
3. Feature 3 - brief description

## Instructions

[Clear steps for Claude to follow]

## Guidelines

- Guideline 1
- Guideline 2
- Guideline 3

## Examples

### Example 1
[Show input and expected output]

### Example 2
[Another realistic example]

## Resources

- [Documentation](./references/guide.md)
- [Helper Scripts](./scripts/)
- [Templates](./assets/templates/)

## Support

[How to get help with this skill]
```

## 3. Content Guidelines

### Conciseness

- **Keep SKILL.md under 5,000 words** to avoid overwhelming Claude's context
- Use clear, direct language
- Remove unnecessary fluff or verbose explanations
- Let helper resources contain detailed information

### Clarity

- Use active voice
- Define technical terms on first use
- Include examples for complex concepts
- Organize with clear headers and bullet points

### Specificity

- Provide concrete examples with inputs and outputs
- Be explicit about expected behavior
- Highlight edge cases and limitations
- Specify any prerequisites or dependencies

## 4. Helper Scripts Best Practices

### Python Scripts

- Add docstrings to all functions
- Use type hints for function parameters and returns
- Handle errors gracefully with informative messages
- Follow PEP 8 style guidelines
- Include a `if __name__ == "__main__":` block for testing

### Bash Scripts

- Add comments explaining complex logic
- Use meaningful variable names
- Source utilities in a standardized location
- Include error handling
- Make scripts executable (`chmod +x`)

### Universal

- Document all functions and their parameters
- Provide usage examples
- Handle missing dependencies gracefully
- Log errors clearly for debugging
- Make scripts modular and reusable

## 5. Examples and Documentation

### Example Quality

- **Realistic**: Use genuine use cases, not artificial scenarios
- **Complete**: Show input, process, and output
- **Varied**: Include basic and advanced examples
- **Documented**: Explain what each example demonstrates

### Example Format

```markdown
### Example: Create a User Profile

**Input:**
```json
{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "role": "admin"
}
```

**Process:**
1. Validate the input data
2. Generate a profile ID
3. Create database record

**Output:**
```json
{
  "id": "prof_123abc",
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "role": "admin",
  "created_at": "2024-01-15T10:30:00Z"
}
```
```

## 6. Resource Files

### Templates

- Provide ready-to-use templates for common tasks
- Include both minimal and comprehensive examples
- Document template variables and how to customize them
- Name templates clearly: `template-basic.txt`, `template-advanced.json`

### References

- Write supporting documentation in separate files
- Focus on detailed information that's too much for SKILL.md
- Link clearly from SKILL.md to relevant references
- Include API documentation, configuration guides, etc.

### Assets

- Keep binary files and example data in the `assets/` directory
- Organize by type: `examples/`, `templates/`, `images/`, etc.
- Document all asset files
- Include sample data for testing

## 7. Testing Your Skill

### Before Publishing

- [ ] SKILL.md frontmatter is correct (name and description)
- [ ] All referenced files exist and are properly formatted
- [ ] Example inputs and outputs are accurate
- [ ] Helper scripts are executable and tested
- [ ] No broken links in documentation
- [ ] Content is concise and clear
- [ ] Guideline are specific and actionable

### Testing with Claude

1. Activate the skill
2. Test basic usage patterns from examples
3. Test edge cases and error conditions
4. Verify resource loading works correctly
5. Check that Claude follows all guidelines
6. Validate output format and quality

## 8. Common Mistakes to Avoid

❌ **Too verbose** - Keep SKILL.md focused and concise
❌ **Unclear instructions** - Be specific about expected behavior
❌ **Missing examples** - Always include concrete use cases
❌ **Broken links** - Test all references to helper files
❌ **No error handling** - Anticipate and address common problems
❌ **Poor organization** - Use consistent structure across skills
❌ **Vague guidelines** - Make rules specific and actionable
❌ **Missing dependencies** - Document all prerequisites

## 9. Version Control

### Commit Messages

```
feat: Add new template for API documentation

- Include headers and parameter documentation
- Add examples for common endpoints
- Update SKILL.md with new template reference
```

### Changelog Format

```markdown
## [1.2.0] - 2024-01-15

### Added
- New template for API documentation
- Support for OpenAPI 3.1 specifications

### Fixed
- Markdown formatting in examples
- Broken reference links
```

## 10. Skill Composition

### Working with Multiple Skills

Skills can work together when:
- They have complementary purposes
- Output of one feeds into another
- They follow consistent conventions
- They document their interfaces clearly

### Design for Composition

- Document input/output formats clearly
- Use standard data formats (JSON, Markdown, CSV)
- Avoid tight coupling between skills
- Make skills idempotent where possible

## Resources

- [Claude Code Skills Documentation](https://docs.claude.com/claude-code/skills)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Best Practices Guide](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
