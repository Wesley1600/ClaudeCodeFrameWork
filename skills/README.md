# Claude Code Skills Collection

This directory contains custom skills for Claude Code that extend its capabilities with specialized workflows and automation.

## Available Skills

### Output Validator

**Location:** `skills/output-validator/`

**Description:** A comprehensive skill that validates code, documents, and configurations against quality standards using linters, formatters, type checkers, and test runners.

**Key Features:**
- Automatic file type detection
- Multi-language support (JavaScript, TypeScript, Python, Go, Rust, Ruby, Shell, etc.)
- Document validation (Markdown, JSON, YAML)
- Auto-fix capabilities for formatting and style issues
- Integration with project-specific configurations
- Clear, categorized issue reporting (errors, warnings, info)
- Support for custom validation workflows

**Use Cases:**
- Validate code after writing
- Check code quality before committing
- Run full project validation
- Verify documentation formatting
- Enforce code quality standards
- Pre-commit hook validation

**Quick Start:**
```bash
# Install the skill (copy to user's .claude directory)
cp -r skills/output-validator ~/.claude/skills/

# Use in Claude Code
/skill output-validator

# Or simply ask
"Validate my code"
"Check this file for errors"
```

See [output-validator/README.md](output-validator/README.md) for full documentation.

## Installation

### Installing Skills Locally

To install any skill in this collection to your local Claude Code environment:

```bash
# Install a specific skill
cp -r skills/[skill-name] ~/.claude/skills/

# Install all skills
cp -r skills/* ~/.claude/skills/
```

### Creating Your Own Skills

Skills are stored in `~/.claude/skills/[skill-name]/` with the following structure:

```
skill-name/
├── SKILL.md          # Skill definition and instructions (required)
├── README.md         # User documentation (optional)
└── examples/         # Example files and scripts (optional)
```

**SKILL.md Format:**
```markdown
---
name: skill-name
description: Brief description of what the skill does and when to use it
---

# Skill Title

[Detailed instructions for Claude to follow when executing this skill]
```

## Skill Development Guidelines

When creating new skills:

1. **Clear Purpose** - Each skill should have a focused, well-defined purpose
2. **Comprehensive Documentation** - Include detailed instructions in SKILL.md
3. **User Guide** - Provide a README.md for end users
4. **Examples** - Include example files and scripts when applicable
5. **Error Handling** - Guide Claude to handle errors gracefully
6. **Tool Detection** - Check for required tools and suggest installation
7. **Workflow Steps** - Break complex tasks into clear, numbered steps
8. **Best Practices** - Include guidance on when and how to use the skill

## Contributing

To contribute a new skill to this collection:

1. Create a new directory in `skills/`
2. Add SKILL.md with YAML front-matter and instructions
3. Add README.md with user documentation
4. Include examples if applicable
5. Test the skill thoroughly
6. Submit a pull request

## Resources

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills)
- [Creating Custom Skills Guide](https://docs.claude.com/en/docs/claude-code/skills/creating-skills)

## License

These skills are provided as examples and templates for use with Claude Code. Feel free to modify and adapt them for your needs.

---

**Note:** Skills in this directory are reference implementations. Install them to `~/.claude/skills/` to use them with Claude Code.