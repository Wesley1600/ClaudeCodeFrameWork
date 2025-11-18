# Version Management Skill

A comprehensive skill for managing versions of skills, prompts, and documents using git-based version control.

## Overview

This skill enables systematic version management with:

- **Version Tagging**: Create semantic version tags (v1.0.0, v2.1.3, etc.)
- **Changelog Management**: Maintain structured changelogs following Keep a Changelog format
- **Rollback Operations**: Safely restore previous versions with automatic backups
- **Change Tracking**: Monitor changes to SKILL.md, scripts, and resources
- **Version Comparison**: Compare different versions and view changes
- **History Reporting**: Generate detailed version reports

## Quick Start

### Using with Claude Code

Activate the skill in a conversation:

```
Use the version-management skill to create version 1.1.0 of my-skill
```

Claude will:
1. Review changes since the last version
2. Update CHANGELOG.md with new entries
3. Update the version field in SKILL.yaml
4. Commit the changes
5. Create a git tag for the release

### Using the Helper Script

The `version-utils.sh` script provides command-line utilities:

```bash
# List all versions
.claude/skills/version-management/version-utils.sh list

# Create a new version tag
.claude/skills/version-management/version-utils.sh tag v1.2.0 "Added feature X"

# Compare versions
.claude/skills/version-management/version-utils.sh compare v1.0.0 v1.1.0

# Rollback to previous version
.claude/skills/version-management/version-utils.sh rollback v1.0.0 .claude/skills/my-skill

# Initialize version tracking for a new skill
.claude/skills/version-management/version-utils.sh init .claude/skills/new-skill

# Generate version report
.claude/skills/version-management/version-utils.sh report .claude/skills/my-skill

# Update version in SKILL.yaml
.claude/skills/version-management/version-utils.sh update-skill .claude/skills/my-skill 1.2.0
```

## File Structure

```
.claude/skills/version-management/
├── SKILL.yaml           # Skill metadata and configuration
├── SKILL.md             # Main skill instructions for Claude
├── CHANGELOG.md         # Version history of this skill
├── README.md            # This file
└── version-utils.sh     # Helper script for version operations
```

## Semantic Versioning

This skill follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** version (X.0.0): Incompatible API changes or breaking changes
- **MINOR** version (1.X.0): New features, backwards-compatible
- **PATCH** version (1.0.X): Bug fixes, backwards-compatible

### Examples

- `v1.0.0` → `v1.0.1`: Fixed typo in documentation
- `v1.0.1` → `v1.1.0`: Added new rollback feature
- `v1.1.0` → `v2.0.0`: Changed command interface (breaking change)

## Common Workflows

### Creating a New Release

1. Make changes to your skill
2. Test thoroughly
3. Update CHANGELOG.md with changes
4. Update version in SKILL.yaml
5. Commit changes
6. Create version tag
7. (Optional) Push to remote

### Rolling Back After Issues

1. Identify the problematic version
2. Choose a stable version to rollback to
3. Create automatic backup of current state
4. Perform rollback
5. Test the rolled-back version
6. Commit and tag as a new patch version

### Viewing Version History

1. List all version tags
2. View CHANGELOG.md
3. Compare specific versions to see differences
4. Generate detailed version reports

## Best Practices

1. **Always test before tagging** - Ensure functionality works before creating a release
2. **Write meaningful commit messages** - Explain why, not just what changed
3. **Keep CHANGELOG.md updated** - Update it before creating version tags
4. **Use annotated tags** - Provide context with tag messages
5. **Create backups before rollbacks** - Automatic in the helper script
6. **Follow semantic versioning** - Communicate change impact clearly
7. **Document breaking changes** - Clearly mark incompatible changes

## Integration with Skills

When managing skill versions:

### Track These Files

- `SKILL.yaml` - Metadata and version number
- `SKILL.md` - Skill instructions
- `*.sh`, `*.py` - Helper scripts
- `resources/*` - Supporting files
- `CHANGELOG.md` - Version history
- `README.md` - Documentation

### Before Each Release

1. Update `version` field in SKILL.yaml
2. Add entry to CHANGELOG.md
3. Test all functionality
4. Create git tag matching SKILL.yaml version

### When Rolling Back

1. Note the rollback in CHANGELOG.md
2. Consider creating a patch version
3. Test the rolled-back version
4. Communicate the rollback

## Changelog Format

This skill uses the [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [1.1.0] - 2025-11-18
### Added
- New features

### Changed
- Updates to existing functionality

### Deprecated
- Features marked for removal

### Removed
- Deleted features

### Fixed
- Bug fixes

### Security
- Security patches
```

## Emergency Recovery

If something goes wrong:

```bash
# View all recent operations
git reflog

# Recover to any previous state (replace N with step from reflog)
git reset --hard HEAD@{N}

# Or create a recovery branch
git checkout -b emergency-recovery HEAD@{N}
```

Git never truly deletes committed data - recovery is almost always possible!

## Requirements

- Git (version 2.0+)
- Bash (for version-utils.sh script)
- A git repository

## Examples

### Example 1: New Feature Release

```bash
# Make changes to skill
vim .claude/skills/my-skill/SKILL.md

# Update changelog
vim .claude/skills/my-skill/CHANGELOG.md

# Update version in SKILL.yaml
.claude/skills/version-management/version-utils.sh update-skill .claude/skills/my-skill 1.2.0

# Commit changes
git add .claude/skills/my-skill/
git commit -m "Add new feature to my-skill"

# Create version tag
.claude/skills/version-management/version-utils.sh tag v1.2.0 "Release v1.2.0: New feature X"
```

### Example 2: Quick Rollback

```bash
# Rollback to previous stable version (includes automatic backup)
.claude/skills/version-management/version-utils.sh rollback v1.1.0 .claude/skills/my-skill

# Review the changes
git diff --staged

# Commit the rollback
git commit -m "Rollback my-skill to v1.1.0 due to bug in v1.2.0"

# Tag as patch version
.claude/skills/version-management/version-utils.sh tag v1.1.1 "Hotfix: Rollback to v1.1.0"
```

### Example 3: Version Comparison

```bash
# Compare two versions
.claude/skills/version-management/version-utils.sh compare v1.0.0 v1.2.0 .claude/skills/my-skill

# Generate detailed report
.claude/skills/version-management/version-utils.sh report .claude/skills/my-skill > version-report.md
```

## Troubleshooting

### Tag Already Exists

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag (if pushed)
git push origin :refs/tags/v1.0.0

# Recreate tag
.claude/skills/version-management/version-utils.sh tag v1.0.0 "Corrected tag"
```

### Rollback Caused Conflicts

```bash
# Abort the rollback
git checkout HEAD -- .

# Or manually resolve conflicts
git status
# Edit conflicting files
git add <resolved-files>
git commit
```

### Lost Changes

```bash
# Find lost commits
git reflog

# Recover lost work
git checkout <commit-hash>
git checkout -b recovery-branch
```

## License

Part of Claude Code Framework - see repository license.

## Version

Current version: **1.0.0**

See [CHANGELOG.md](./CHANGELOG.md) for version history.

## Contributing

To improve this skill:

1. Make changes
2. Test thoroughly
3. Update CHANGELOG.md
4. Update version in SKILL.yaml
5. Follow the versioning practices this skill documents!

---

**Maintained by**: Claude Code Framework
**Last Updated**: 2025-11-18
