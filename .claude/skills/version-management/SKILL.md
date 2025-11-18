---
name: Version Management
description: Track versions, tag releases, maintain changelogs, and rollback skills, prompts, and documents
version: "1.0.0"
author: Claude Code Framework
tags:
  - version-control
  - changelog
  - rollback
  - git
---

# Version Management Skill

This skill provides comprehensive version management for skills, prompts, and documents in Claude Code. It leverages git under the hood to track changes, create tagged releases, maintain changelogs, and enable rollbacks.

## Core Capabilities

1. **Version Tracking**: Track changes to SKILL.md, scripts, and resource files
2. **Release Tagging**: Create semantic versioned releases with tags
3. **Changelog Management**: Automatically generate and maintain changelogs
4. **Rollback Support**: Safely revert to previous versions when errors occur
5. **Diff Analysis**: Compare versions to understand changes

## Usage Instructions

### 1. Initialize Version Management for a Skill

When the user asks to initialize version management for a skill:

```bash
# Navigate to the skill directory
cd .claude/skills/[skill-name]

# Initialize git tracking if not already done
git add SKILL.md
git commit -m "Initialize [skill-name] v0.1.0"
git tag -a "skill/[skill-name]/v0.1.0" -m "Initial version of [skill-name]"

# Create initial CHANGELOG.md
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - YYYY-MM-DD

### Added
- Initial version of the skill
- Core functionality implemented
EOF
```

### 2. Create a New Version Release

When the user wants to tag a new release:

**Steps:**
1. Review changes since last release
2. Determine version bump (major.minor.patch)
3. Update CHANGELOG.md with changes
4. Commit changes
5. Create git tag
6. Push tag to remote (if applicable)

**Example workflow:**

```bash
# 1. Review changes
cd .claude/skills/[skill-name]
git log --oneline $(git describe --tags --abbrev=0)..HEAD

# 2. Update CHANGELOG.md (manual or assisted)
# Add new version section with date and changes

# 3. Commit the changelog
git add CHANGELOG.md
git commit -m "Update changelog for v[X.Y.Z]"

# 4. Create version tag
git tag -a "skill/[skill-name]/v[X.Y.Z]" -m "Release v[X.Y.Z]: [brief description]"

# 5. Push changes and tags
git push origin HEAD
git push origin "skill/[skill-name]/v[X.Y.Z]"
```

### 3. Rollback to Previous Version

When the user reports errors or wants to revert:

**Steps:**
1. List available versions
2. Identify target version
3. Create backup of current state
4. Revert to target version
5. Test and verify

**Example workflow:**

```bash
# 1. List available versions for the skill
cd .claude/skills/[skill-name]
git tag -l "skill/[skill-name]/*"

# 2. View differences
git diff skill/[skill-name]/v[OLD] skill/[skill-name]/v[NEW]

# 3. Create backup tag of current state
git tag -a "skill/[skill-name]/backup-$(date +%Y%m%d-%H%M%S)" -m "Backup before rollback"

# 4. Rollback specific files to target version
git checkout "skill/[skill-name]/v[TARGET]" -- SKILL.md
# Rollback any other files as needed
git checkout "skill/[skill-name]/v[TARGET]" -- [script-file]

# 5. Commit the rollback
git add .
git commit -m "Rollback to v[TARGET] due to [reason]"

# 6. Update CHANGELOG
# Add entry documenting the rollback
```

### 4. Compare Versions

When analyzing changes between versions:

```bash
cd .claude/skills/[skill-name]

# Compare two versions
git diff skill/[skill-name]/v[OLD]..skill/[skill-name]/v[NEW]

# Show what changed in a specific version
git show skill/[skill-name]/v[VERSION]

# View changelog for a version
git show skill/[skill-name]/v[VERSION]:CHANGELOG.md
```

### 5. List All Versioned Skills

```bash
# Show all skill version tags
git tag -l "skill/*/v*"

# Show tags with dates and messages
git tag -l "skill/*/v*" --format='%(refname:short)%09%(creatordate:short)%09%(contents:subject)'
```

## Semantic Versioning Guidelines

Use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** (X.0.0): Incompatible changes, complete rewrites, breaking changes
- **MINOR** (0.X.0): New features, backwards-compatible functionality additions
- **PATCH** (0.0.X): Bug fixes, documentation updates, minor improvements

## Changelog Format

Each changelog entry should include:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features or capabilities

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in future versions

### Removed
- Features that have been removed

### Fixed
- Bug fixes

### Security
- Security-related changes
```

## Directory Structure for Versioned Skills

```
.claude/skills/[skill-name]/
├── SKILL.md              # Main skill definition (versioned)
├── CHANGELOG.md          # Version history (versioned)
├── scripts/              # Helper scripts (versioned)
│   ├── setup.sh
│   └── utilities.py
├── resources/            # Additional resources (versioned)
│   ├── templates/
│   └── data/
└── .version              # Current version metadata (optional)
```

## Workflow Examples

### Example 1: Bug Fix Release

```
User: "The skill has a bug in the regex pattern. Can you fix it and create a patch release?"

Steps:
1. Fix the bug in SKILL.md
2. Add entry to CHANGELOG.md under new [X.Y.Z+1] section in ### Fixed
3. Commit: "Fix regex pattern bug in skill validation"
4. Tag: skill/[name]/v[X.Y.Z+1]
5. Confirm fix works
```

### Example 2: Rollback After Breaking Change

```
User: "The new version is causing errors. Roll back to the previous stable version."

Steps:
1. git tag -l "skill/[name]/*" to list versions
2. Identify last stable version (e.g., v1.2.0)
3. Create backup tag of current state
4. git checkout skill/[name]/v1.2.0 -- SKILL.md [other-files]
5. Commit rollback with explanation
6. Update CHANGELOG.md documenting the rollback
```

### Example 3: Major Version Upgrade

```
User: "Rewrite the skill with a completely new approach for v2.0.0"

Steps:
1. Make breaking changes to SKILL.md
2. Update all affected scripts and resources
3. Create comprehensive CHANGELOG.md entry for v2.0.0
4. Document migration guide in changelog
5. Commit all changes
6. Tag: skill/[name]/v2.0.0
7. Consider keeping v1.x branch for legacy support
```

## Advanced Features

### Version Metadata File

Optionally create a `.version` file to track metadata:

```json
{
  "name": "skill-name",
  "version": "1.2.3",
  "released": "2025-11-18",
  "stable": true,
  "deprecated": false,
  "dependencies": {
    "min_claude_version": "4.0"
  }
}
```

### Automated Changelog Generation

Generate changelog entries from git commits:

```bash
# Get commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"- %s (%h)"

# Categorize by conventional commits
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"%s" | \
  grep -E "^(feat|fix|docs|refactor|test|chore):" | \
  sed 's/^feat:/### Added\n-/g' | \
  sed 's/^fix:/### Fixed\n-/g'
```

### Diff Summary

Provide a summary when creating new versions:

```bash
# Lines changed
git diff --stat skill/[name]/v[OLD]..skill/[name]/v[NEW]

# File changes
git diff --name-status skill/[name]/v[OLD]..skill/[name]/v[NEW]
```

## Error Recovery

If version management encounters errors:

1. **Corrupted tags**: Remove and recreate
   ```bash
   git tag -d skill/[name]/v[X.Y.Z]
   git push origin :refs/tags/skill/[name]/v[X.Y.Z]
   # Recreate correctly
   ```

2. **Lost changelog**: Reconstruct from git history
   ```bash
   git log --tags --simplify-by-decoration --pretty="format:%ai %d %s"
   ```

3. **Conflicting versions**: Use backup tags to resolve
   ```bash
   git tag -l "skill/[name]/backup-*"
   ```

## Best Practices

1. **Always test before tagging**: Verify the skill works before creating a release
2. **Write descriptive changelog entries**: Future you will thank you
3. **Use conventional commits**: Makes automation easier
4. **Tag immediately after release**: Don't delay tagging
5. **Keep backups**: Create backup tags before major changes
6. **Document breaking changes**: Be explicit about compatibility
7. **Version everything together**: Tag all related files in one release
8. **Push tags to remote**: Ensure team has access to versions

## Integration with Claude Code

When Claude Code loads skills, it can optionally:

1. Check version compatibility
2. Warn about deprecated skills
3. Auto-update to stable versions
4. Suggest rollback if errors detected
5. Display changelog on skill updates

## Summary

This version management skill provides a robust, git-based system for tracking, releasing, and managing versions of Claude Code skills. It ensures that you can:

- Confidently experiment with new features
- Quickly rollback when issues arise
- Maintain a clear history of changes
- Collaborate with version awareness
- Document evolution over time

When assisting users, always:
1. Confirm current version first
2. Create backups before major changes
3. Update changelogs thoroughly
4. Test before tagging
5. Communicate version changes clearly
