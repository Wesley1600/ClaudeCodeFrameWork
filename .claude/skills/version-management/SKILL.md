# Version Management Skill

You are tasked with managing versions of skills, prompts, documents, and other resources using git-based version control.

## Core Responsibilities

1. **Version Tagging**: Create semantic version tags for skills and documents
2. **Changelog Management**: Maintain detailed changelogs for tracked resources
3. **Rollback Operations**: Restore previous versions when issues arise
4. **Change Tracking**: Monitor and record changes to SKILL.md, scripts, and resources

## Commands and Operations

### 1. Initialize Version Tracking

When the user wants to start tracking versions for a skill or document:

```bash
# Navigate to the skill/resource directory
cd .claude/skills/<skill-name>

# Initialize version tracking (if not already in git)
git add .
git commit -m "Initialize <skill-name> version tracking"

# Create initial version tag
git tag -a v1.0.0 -m "Initial release of <skill-name>"
```

### 2. Create a New Version/Release

When the user requests a new version release:

**Steps:**
1. Review changes since last version
2. Update CHANGELOG.md (create if doesn't exist)
3. Update version in SKILL.yaml
4. Commit changes
5. Create git tag with semantic version

**Example:**
```bash
# 1. Review changes
git diff v1.0.0..HEAD -- .claude/skills/<skill-name>/

# 2. Update CHANGELOG.md (you should do this)
# Add entry with date, version, and changes

# 3. Update SKILL.yaml version field
# Change: version: 1.0.0 -> version: 1.1.0

# 4. Commit the updates
git add .claude/skills/<skill-name>/
git commit -m "Release <skill-name> v1.1.0"

# 5. Create annotated tag
git tag -a v1.1.0 -m "Release v1.1.0: <summary of changes>"
```

### 3. View Version History

When the user wants to see version history:

```bash
# List all version tags for a skill
git tag -l "v*" --sort=-version:refname

# Show detailed tag information
git show v1.0.0

# View changelog for specific skill
cat .claude/skills/<skill-name>/CHANGELOG.md

# Show changes between versions
git log v1.0.0..v1.1.0 -- .claude/skills/<skill-name>/
```

### 4. Rollback to Previous Version

When the user needs to rollback due to errors or issues:

**IMPORTANT**: Always create a backup tag before rollback!

```bash
# 1. Create backup of current state
git tag -a backup-$(date +%Y%m%d-%H%M%S) -m "Backup before rollback"

# 2. View available versions
git tag -l "v*" --sort=-version:refname

# 3. Rollback specific files to a previous version
git checkout v1.0.0 -- .claude/skills/<skill-name>/

# 4. Review the rollback
git diff --staged

# 5. Commit the rollback
git commit -m "Rollback <skill-name> to v1.0.0 due to <reason>"

# 6. Optionally tag this as a new version
git tag -a v1.0.1 -m "Hotfix: Rollback to v1.0.0 state"
```

**Alternative - Full Repository Rollback:**
```bash
# For severe issues, reset entire repository (USE WITH CAUTION)
git reset --hard v1.0.0

# If already pushed, create a revert commit instead
git revert --no-commit <commit-hash>..HEAD
git commit -m "Revert to v1.0.0 state"
```

### 5. Maintain Changelog

For each version, create or update CHANGELOG.md in the skill directory:

**CHANGELOG.md Format:**
```markdown
# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- New features in development

## [1.1.0] - 2025-11-18
### Added
- New feature X for improved functionality
- Support for Y operation

### Changed
- Updated instruction clarity in SKILL.md
- Improved error handling in helper scripts

### Fixed
- Bug in rollback operation
- Edge case in version comparison

## [1.0.0] - 2025-11-01
### Added
- Initial release
- Core version management functionality
- Git-based tagging system
```

### 6. Track File Changes

Monitor specific files for changes:

```bash
# Show changes to SKILL.md
git log -p -- .claude/skills/<skill-name>/SKILL.md

# Show changes to all scripts in skill
git log --oneline -- .claude/skills/<skill-name>/*.sh

# Show who changed what and when
git blame .claude/skills/<skill-name>/SKILL.md

# Track file renames and moves
git log --follow -- .claude/skills/<skill-name>/SKILL.md
```

### 7. Compare Versions

When the user wants to compare different versions:

```bash
# Compare two specific versions
git diff v1.0.0..v1.1.0 -- .claude/skills/<skill-name>/

# Compare with specific focus
git diff v1.0.0..v1.1.0 -- .claude/skills/<skill-name>/SKILL.md

# Show summary statistics
git diff --stat v1.0.0..v1.1.0 -- .claude/skills/<skill-name>/

# Show word-level diff for better readability
git diff --word-diff v1.0.0..v1.1.0 -- .claude/skills/<skill-name>/SKILL.md
```

### 8. Export Version Information

Generate version reports:

```bash
# Create version report
cat > version-report.md << 'EOF'
# Version Report for <skill-name>

**Current Version:** $(git describe --tags --abbrev=0)
**Last Modified:** $(git log -1 --format=%cd -- .claude/skills/<skill-name>/)
**Total Versions:** $(git tag -l "v*" | wc -l)

## Recent Changes
$(git log -5 --oneline -- .claude/skills/<skill-name>/)

## Version Timeline
$(git tag -l "v*" --sort=-version:refname --format="%(refname:short) - %(creatordate:short) - %(subject)")
EOF
```

## Semantic Versioning Guidelines

Use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** (v2.0.0): Breaking changes, incompatible API changes
- **MINOR** (v1.1.0): New features, backwards-compatible
- **PATCH** (v1.0.1): Bug fixes, backwards-compatible

**Examples:**
- `v1.0.0` → `v1.0.1`: Fixed typo in SKILL.md
- `v1.0.1` → `v1.1.0`: Added new rollback feature
- `v1.1.0` → `v2.0.0`: Changed skill command interface (breaking)

## Best Practices

1. **Always create tags after significant changes**
2. **Write detailed commit messages** explaining why changes were made
3. **Update CHANGELOG.md** before creating version tags
4. **Test thoroughly** before tagging releases
5. **Create backups** before performing rollbacks
6. **Use annotated tags** (git tag -a) instead of lightweight tags
7. **Push tags to remote**: `git push --tags` (when ready)
8. **Document breaking changes** clearly in changelog

## Error Handling

### If version tag already exists:
```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag (if pushed)
git push origin :refs/tags/v1.0.0

# Recreate tag
git tag -a v1.0.0 -m "Corrected version tag"
```

### If rollback causes conflicts:
```bash
# Abort the rollback
git checkout --theirs .
# Or
git checkout --ours .

# Or manually resolve conflicts
git status
# Edit conflicting files
git add <resolved-files>
git commit
```

### If changes were lost:
```bash
# Find lost commits
git reflog

# Recover lost work
git checkout <commit-hash>
git checkout -b recovery-branch
```

## Integration with Skills

When managing skill versions specifically:

1. **Track these files closely:**
   - `SKILL.yaml` - metadata and version number
   - `SKILL.md` - skill instructions
   - `*.sh` - helper scripts
   - `resources/*` - any supporting files
   - `CHANGELOG.md` - version history

2. **Before each release:**
   - Update `version` field in SKILL.yaml
   - Update CHANGELOG.md with changes
   - Test all functionality
   - Create git tag matching SKILL.yaml version

3. **When rolling back a skill:**
   - Note the rollback in CHANGELOG.md
   - Consider if a patch version is needed
   - Test the rolled-back version
   - Communicate the rollback to users

## User Interaction Examples

### Example 1: Creating a new release
**User**: "Create version 1.2.0 of the version-management skill"

**You should:**
1. Review changes: `git diff v1.1.0..HEAD -- .claude/skills/version-management/`
2. Update CHANGELOG.md with new features/changes
3. Update version in SKILL.yaml to 1.2.0
4. Commit: `git commit -am "Release version-management v1.2.0"`
5. Tag: `git tag -a v1.2.0 -m "Release v1.2.0: Added feature X"`
6. Confirm with user

### Example 2: Rolling back
**User**: "The new version has errors, rollback to v1.1.0"

**You should:**
1. Create backup: `git tag -a backup-$(date +%Y%m%d-%H%M%S) -m "Backup before rollback"`
2. Checkout old version: `git checkout v1.1.0 -- .claude/skills/version-management/`
3. Update CHANGELOG.md noting the rollback
4. Commit: `git commit -m "Rollback version-management to v1.1.0 due to errors in v1.2.0"`
5. Tag as patch: `git tag -a v1.1.1 -m "Hotfix: Rollback to v1.1.0"`
6. Confirm with user and explain what was rolled back

### Example 3: Viewing version history
**User**: "Show me the version history of the authentication skill"

**You should:**
1. List tags: `git tag -l "v*" --sort=-version:refname`
2. Show changelog: `cat .claude/skills/authentication/CHANGELOG.md`
3. Summarize key versions and changes
4. Offer to show detailed diffs if needed

## Notes

- This skill uses git as the underlying version control system
- All operations preserve git history for full traceability
- Tags are the primary versioning mechanism
- CHANGELOG.md provides human-readable version history
- Rollbacks are safe and reversible with proper backup tags
- Skills are typically located in `.claude/skills/<skill-name>/`
- Always verify the git repository is in a clean state before major operations

## Emergency Recovery

If something goes wrong:

```bash
# View all recent operations
git reflog

# Recover to any previous state
git reset --hard HEAD@{n}  # where n is from reflog

# Or create a branch from any point
git checkout -b emergency-recovery HEAD@{n}
```

**Remember**: Git never truly deletes committed data. Recovery is almost always possible.
