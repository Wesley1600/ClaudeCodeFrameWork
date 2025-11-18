# Changelog

All notable changes to the version-management skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Planned
- Automatic changelog generation from git commits
- Support for multiple changelog formats
- Integration with CI/CD pipelines
- Version comparison visualizations

## [1.0.0] - 2025-11-18
### Added
- Initial release of version-management skill
- Git-based version tagging system
- Changelog management with Keep a Changelog format
- Rollback operations with automatic backups
- Semantic versioning support (MAJOR.MINOR.PATCH)
- Version comparison and history viewing
- Helper script (version-utils.sh) with commands:
  - `tag`: Create version tags
  - `list`: List all versions
  - `compare`: Compare versions
  - `rollback`: Safe rollback with backups
  - `init`: Initialize version tracking
  - `report`: Generate version reports
  - `update-skill`: Update SKILL.yaml version field
- Comprehensive documentation in SKILL.md
- Emergency recovery procedures
- Best practices and guidelines
- Integration with skills directory structure

### Documentation
- SKILL.md with detailed instructions and examples
- SKILL.yaml with metadata
- CHANGELOG.md following Keep a Changelog format
- Inline help in version-utils.sh script
- User interaction examples

### Features
- Track changes to SKILL.md, scripts, and resources
- Store detailed changelogs for each version
- Create annotated git tags for releases
- Roll back to previous versions when errors occur
- Compare different versions
- Generate version reports
- Colored terminal output for better readability
- Interactive confirmations for destructive operations
- Automatic backup creation before rollbacks
