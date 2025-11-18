# Version Management Skill

Professional version control for Claude Code skills, prompts, and documents.

## Quick Start

### 1. Initialize Version Management

```bash
cd ~/.claude/skills/your-skill-name
../../version-management/scripts/version_manager.sh init . 0.1.0
```

This creates:
- `.versions/` directory for version storage
- `CHANGELOG.md` for tracking changes
- Initial version snapshot at `v0.1.0`

### 2. Create a New Version

After making changes to your skill:

```bash
../../version-management/scripts/version_manager.sh create . 1.0.0 "Initial stable release"
```

### 3. List All Versions

```bash
../../version-management/scripts/version_manager.sh list .
```

Output:
```
Version History for skill at: .
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERSION    | DATE                 | DESCRIPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v0.1.0     | 2025-11-18 10:00     | Initial version
v1.0.0     | 2025-11-18 12:00     | Initial stable release
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. Show Version Details

```bash
../../version-management/scripts/version_manager.sh show . 1.0.0
```

### 5. Rollback to Previous Version

If something goes wrong:

```bash
../../version-management/scripts/version_manager.sh rollback . 1.0.0
```

This will:
- Create a backup of current state
- Restore all files from version `v1.0.0`
- Update metadata

### 6. Calculate Next Version

```bash
# Bump from 1.0.0 to 1.1.0 (minor)
../../version-management/scripts/version_manager.sh bump 1.0.0 minor

# Bump from 1.0.0 to 2.0.0 (major)
../../version-management/scripts/version_manager.sh bump 1.0.0 major

# Bump from 1.0.0 to 1.0.1 (patch)
../../version-management/scripts/version_manager.sh bump 1.0.0 patch
```

## Installation

### For Individual Skills

1. Copy the version-management skill to your Claude skills directory:

```bash
cp -r skills/version-management ~/.claude/skills/
```

2. Initialize version management for any existing skill:

```bash
cd ~/.claude/skills/your-skill
../version-management/scripts/version_manager.sh init . 0.1.0
```

### For Project-Based Skills

If you're developing skills in a git repository:

```bash
# Clone or copy the version-management skill
cd your-project/skills
git clone <repo-url> version-management
# or
cp -r /path/to/version-management .
```

## Directory Structure

After initialization, your skill will have:

```
your-skill/
├── SKILL.md                    # Current version
├── scripts/                    # Current scripts
├── templates/                  # Current templates
└── .versions/                  # Version history
    ├── CHANGELOG.md            # Change log
    ├── v0.1.0/                 # Version 0.1.0
    │   ├── SKILL.md
    │   ├── scripts/
    │   ├── templates/
    │   └── metadata.json
    ├── v1.0.0/                 # Version 1.0.0
    │   ├── SKILL.md
    │   ├── scripts/
    │   ├── templates/
    │   └── metadata.json
    └── backup-20251118-120000/ # Rollback backup
        ├── SKILL.md
        └── scripts/
```

## Usage Examples

### Example 1: Version a New Skill

```bash
# Create new skill
mkdir ~/.claude/skills/code-reviewer
cd ~/.claude/skills/code-reviewer

# Create SKILL.md
cat > SKILL.md <<EOF
---
name: code-reviewer
description: Reviews code for quality and best practices
---
# Code Reviewer Skill
...
EOF

# Initialize version management
../version-management/scripts/version_manager.sh init . 0.1.0

# Work on the skill...
# When ready for release:
../version-management/scripts/version_manager.sh create . 1.0.0 "Initial stable release"
```

### Example 2: Update Existing Skill

```bash
cd ~/.claude/skills/your-skill

# Make changes to SKILL.md
vim SKILL.md

# Create new version
../version-management/scripts/version_manager.sh create . 1.1.0 "Added new features"

# Update changelog manually
vim .versions/CHANGELOG.md
```

### Example 3: Recover from Bad Update

```bash
cd ~/.claude/skills/your-skill

# Oh no, v1.1.0 has bugs!
# List versions to see what's available
../version-management/scripts/version_manager.sh list .

# Rollback to last stable version
../version-management/scripts/version_manager.sh rollback . 1.0.0

# Fix issues, then create patch version
../version-management/scripts/version_manager.sh create . 1.0.1 "Fixed bugs from v1.1.0"
```

### Example 4: Compare Versions

```bash
# Show details of two versions
../version-management/scripts/version_manager.sh show . 1.0.0
../version-management/scripts/version_manager.sh show . 1.1.0

# Use diff to compare SKILL.md
diff .versions/v1.0.0/SKILL.md .versions/v1.1.0/SKILL.md

# Or use git if in a repo
git diff v1.0.0..v1.1.0 -- .
```

## Workflow Integration

### With Git

The version manager integrates with git:

```bash
# Create version (automatically creates git tag)
./version_manager.sh create . 1.0.0 "Release version 1.0.0"

# List git tags
git tag -l "v*"

# Push tags to remote
git push origin --tags

# Checkout specific version
git checkout v1.0.0
```

### With Claude Code Hooks

You can automate versioning in Claude Code hooks:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/skills/version-management/scripts/check_versions.sh"
          }
        ]
      }
    ]
  }
}
```

## Changelog Maintenance

### Manual Updates

Edit `.versions/CHANGELOG.md`:

```markdown
## [1.1.0] - 2025-11-18

### Added
- New validation features
- Improved error handling

### Changed
- Updated documentation

### Fixed
- Bug in rollback mechanism
```

### Automated Updates

The version manager automatically:
- Creates initial changelog
- Adds version headers
- Includes timestamps

You should manually:
- Add detailed change entries
- Categorize changes (Added/Changed/Fixed)
- Add links to issues/PRs

## Best Practices

### When to Version

✅ **Do version when:**
- Adding major features
- Making breaking changes
- Before deploying to production
- After significant testing
- Completing milestones

❌ **Don't version for:**
- Typo fixes
- Comment updates
- Whitespace changes

### Version Numbering

- **Patch (1.0.0 → 1.0.1)**: Bug fixes, typos
- **Minor (1.0.0 → 1.1.0)**: New features, backward compatible
- **Major (1.0.0 → 2.0.0)**: Breaking changes

### Changelog Writing

- **Be concise**: One line per change
- **Be specific**: "Fix rollback permission bug" not "Fix bug"
- **Link issues**: Reference GitHub issues/PRs
- **Use categories**: Added/Changed/Fixed/Removed
- **Date consistently**: Use ISO 8601 (YYYY-MM-DD)

## Troubleshooting

### Version Already Exists

```bash
# Error: Version v1.0.0 already exists
# Solution: Use different version number
./version_manager.sh create . 1.0.1 "Patch release"
```

### Missing jq Command

```bash
# Error: jq: command not found
# Solution: Install jq
apt-get install jq  # Debian/Ubuntu
brew install jq     # macOS
```

### Rollback Failed

```bash
# Check backup directory
ls .versions/backup-*/

# Manually restore
cp .versions/backup-20251118-120000/SKILL.md .
```

### Git Tag Conflicts

```bash
# Error: tag 'v1.0.0' already exists
# Solution: Delete and recreate tag
git tag -d v1.0.0
./version_manager.sh create . 1.0.0 "Recreate tag"
```

## Advanced Usage

### Batch Version Creation

```bash
# Version multiple skills
for skill in ~/.claude/skills/*/; do
    cd "$skill"
    ../version-management/scripts/version_manager.sh create . 1.0.0 "Batch release"
done
```

### Export Version Archive

```bash
# Create tarball of specific version
tar -czf skill-v1.0.0.tar.gz .versions/v1.0.0/

# Create zip archive
zip -r skill-v1.0.0.zip .versions/v1.0.0/
```

### Version Comparison Script

```bash
#!/bin/bash
# compare_versions.sh
v1="$1"
v2="$2"

echo "Comparing $v1 to $v2:"
diff -u ".versions/$v1/SKILL.md" ".versions/$v2/SKILL.md"
```

## API Reference

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize version management | `init . 0.1.0` |
| `create` | Create new version | `create . 1.0.0 "Description"` |
| `list` | List all versions | `list .` |
| `show` | Show version details | `show . 1.0.0` |
| `rollback` | Rollback to version | `rollback . 1.0.0` |
| `bump` | Calculate next version | `bump 1.0.0 minor` |
| `help` | Show help | `help` |

### Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `3`: Version not found
- `4`: Validation failed

## Dependencies

Required:
- `bash` (4.0+)
- `jq` (for JSON parsing)
- `git` (optional, for git integration)

Optional:
- `diff` (for version comparison)
- `tar`/`zip` (for archiving)

## Contributing

To improve this skill:

1. Make your changes
2. Test thoroughly
3. Update documentation
4. Create new version
5. Update changelog

```bash
# After making changes
./scripts/version_manager.sh create . 1.1.0 "Your improvements"
```

## License

This skill is part of the Claude Code framework.

## Support

For issues or questions:
- Check the troubleshooting section
- Review SKILL.md for detailed documentation
- Consult Claude Code documentation
- Open an issue in the repository

## Version History

See `.versions/CHANGELOG.md` for complete version history.
