# Version Management Skill

A comprehensive skill for managing versions of Claude Code skills, prompts, and documents using git-based version control.

## Features

- **Semantic Versioning**: Follow semver (MAJOR.MINOR.PATCH) standards
- **Git-Based**: Leverage git tags for reliable version tracking
- **Changelog Management**: Automatically generate and maintain changelogs
- **Rollback Support**: Safely revert to previous versions
- **Version Comparison**: Diff between versions to understand changes
- **Metadata Tracking**: Store version metadata in `.version` files

## Quick Start

### Using the Skill in Claude Code

Simply invoke the `version-management` skill when you need to:

```
User: "I want to create v1.0.0 of my custom skill"
Claude: [Activates version-management skill and guides through versioning]
```

### Using Helper Scripts

Two helper scripts are provided for manual operations:

#### 1. Bash Script (`version.sh`)

```bash
# Initialize version management for a skill
.claude/skills/version-management/scripts/version.sh init my-skill

# List all versions
.claude/skills/version-management/scripts/version.sh list

# List versions for specific skill
.claude/skills/version-management/scripts/version.sh list my-skill

# Create a new version tag
.claude/skills/version-management/scripts/version.sh tag my-skill 1.2.3

# Rollback to previous version
.claude/skills/version-management/scripts/version.sh rollback my-skill 1.2.0

# Compare two versions
.claude/skills/version-management/scripts/version.sh diff my-skill 1.2.0 1.2.3

# Generate changelog from commits
.claude/skills/version-management/scripts/version.sh changelog my-skill

# Show current version
.claude/skills/version-management/scripts/version.sh current my-skill
```

#### 2. Python Script (`version_manager.py`)

```bash
# List all skills with versions
python3 .claude/skills/version-management/scripts/version_manager.py list

# List versions for specific skill
python3 .claude/skills/version-management/scripts/version_manager.py list my-skill

# Show current version
python3 .claude/skills/version-management/scripts/version_manager.py current my-skill

# Suggest next version
python3 .claude/skills/version-management/scripts/version_manager.py suggest my-skill --type minor

# Generate changelog entry
python3 .claude/skills/version-management/scripts/version_manager.py changelog my-skill 1.2.3

# Validate skill structure
python3 .claude/skills/version-management/scripts/version_manager.py validate my-skill

# Compare two versions
python3 .claude/skills/version-management/scripts/version_manager.py compare my-skill 1.2.0 1.2.3
```

## Workflow Examples

### Creating Your First Version

```bash
# 1. Navigate to your skill
cd .claude/skills/my-skill

# 2. Initialize version management
../../version-management/scripts/version.sh init my-skill

# This creates:
# - CHANGELOG.md with initial entry
# - .version file with metadata
# - Git commit and tag for v0.1.0
```

### Releasing a New Version

```bash
# 1. Make your changes to SKILL.md or scripts
# Edit files...

# 2. Commit your changes
git add .
git commit -m "feat: add new feature X"

# 3. Generate changelog entry
python3 ../../version-management/scripts/version_manager.py changelog my-skill 1.1.0

# 4. Update CHANGELOG.md with the generated entry
# Edit CHANGELOG.md...

# 5. Create the version tag
../../version-management/scripts/version.sh tag my-skill 1.1.0

# 6. Push to remote (optional)
git push origin skill/my-skill/v1.1.0
```

### Rolling Back After Issues

```bash
# 1. Identify the problem version
../../version-management/scripts/version.sh list my-skill

# 2. Rollback to stable version
../../version-management/scripts/version.sh rollback my-skill 1.0.0

# 3. Update CHANGELOG.md to document the rollback
# Edit CHANGELOG.md to add rollback entry...

# 4. Commit the rollback documentation
git add CHANGELOG.md
git commit -m "docs: document rollback to v1.0.0 due to regression"
```

## Directory Structure

When version management is initialized, your skill will have:

```
.claude/skills/my-skill/
├── SKILL.md              # Main skill definition (versioned)
├── CHANGELOG.md          # Version history (versioned)
├── .version              # Current version metadata
├── scripts/              # Helper scripts (versioned)
│   └── utilities.sh
└── resources/            # Additional resources (versioned)
    └── templates/
```

## Version Metadata (.version file)

The `.version` file stores structured metadata:

```json
{
  "name": "my-skill",
  "version": "1.2.3",
  "released": "2025-11-18",
  "stable": true,
  "deprecated": false,
  "dependencies": {
    "min_claude_version": "4.0"
  }
}
```

## Changelog Format

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format:

```markdown
# Changelog

## [1.2.3] - 2025-11-18

### Added
- New feature X for better Y

### Changed
- Improved performance of Z

### Fixed
- Bug where A caused B

### Security
- Updated dependency to fix CVE-XXXX
```

## Conventional Commits

Use conventional commit format for automatic changelog generation:

- `feat:` - New features (MINOR bump)
- `fix:` - Bug fixes (PATCH bump)
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Maintenance tasks
- `security:` - Security fixes (PATCH bump)
- `BREAKING CHANGE:` - Breaking changes (MAJOR bump)

Example:
```bash
git commit -m "feat: add support for async operations"
git commit -m "fix: resolve race condition in handler"
git commit -m "docs: update usage examples"
```

## Semantic Versioning Guidelines

- **MAJOR** (X.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.X.0): New features, backwards-compatible additions
- **PATCH** (0.0.X): Bug fixes, backwards-compatible fixes

## Integration with Claude Code

When using this skill through Claude Code:

1. **Automatic Detection**: Claude detects when version management is needed
2. **Guided Workflow**: Step-by-step guidance through versioning process
3. **Error Recovery**: Automatic rollback suggestions when issues occur
4. **Change Analysis**: Automatic comparison between versions
5. **Validation**: Checks for proper skill structure and metadata

## Best Practices

1. **Always test before tagging** - Verify the skill works correctly
2. **Update CHANGELOG.md** - Document all changes clearly
3. **Use semantic versioning** - Follow semver standards
4. **Create backups** - Tag backups before major changes
5. **Commit often** - Small, focused commits are easier to track
6. **Tag immediately** - Don't delay tagging after completing a version
7. **Push tags** - Share versions with team via remote repository

## Troubleshooting

### Tag Already Exists

```bash
# Delete local tag
git tag -d skill/my-skill/v1.2.3

# Delete remote tag
git push origin :refs/tags/skill/my-skill/v1.2.3

# Recreate with correct version
../../version-management/scripts/version.sh tag my-skill 1.2.3
```

### Lost Changelog

```bash
# Reconstruct from git history
git log --tags --simplify-by-decoration --pretty="format:%ai %d %s"
```

### Restore from Backup

```bash
# List backup tags
git tag -l "skill/my-skill/backup-*"

# Restore from backup
git checkout skill/my-skill/backup-20251118-143000 -- .
```

## Advanced Usage

### Creating Version Branches

For long-term support of multiple versions:

```bash
# Create branch for v1.x maintenance
git checkout -b skill/my-skill/v1.x skill/my-skill/v1.2.3

# Make fixes on the branch
git commit -m "fix: backport security fix"
git tag -a "skill/my-skill/v1.2.4" -m "Security patch for v1.x"
```

### Bulk Operations

```bash
# List all skills with their current versions
for skill in .claude/skills/*/; do
    name=$(basename "$skill")
    python3 .claude/skills/version-management/scripts/version_manager.py current "$name" 2>/dev/null
done

# Validate all skills
for skill in .claude/skills/*/; do
    name=$(basename "$skill")
    echo "Validating $name..."
    python3 .claude/skills/version-management/scripts/version_manager.py validate "$name"
done
```

## Contributing

To improve this version management skill:

1. Fork/branch from current version
2. Make improvements
3. Test thoroughly
4. Update CHANGELOG.md
5. Submit with clear version bump rationale

## License

This skill is part of the Claude Code Framework and follows the same license.

## Support

For issues or questions:
- Check the troubleshooting section
- Review SKILL.md for detailed instructions
- Consult git documentation for advanced operations

---

**Version**: 1.0.0
**Last Updated**: 2025-11-18
**Maintained by**: Claude Code Framework
