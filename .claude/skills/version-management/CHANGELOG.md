# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-18

### Added
- Initial version of the version management skill
- SKILL.md with comprehensive documentation on version management workflows
- Bash helper script (version.sh) for common version operations
  - Initialize version management for skills
  - List versions and tags
  - Create new version tags
  - Rollback to previous versions
  - Compare versions with diff
  - Generate changelog entries
  - Show current version
- Python helper script (version_manager.py) for advanced operations
  - Semantic version parsing and comparison
  - Automated changelog generation from conventional commits
  - Version metadata management
  - Skill structure validation
  - Detailed version comparison
- README.md with usage examples and best practices
- Example greeter skill demonstrating version management
- Support for semantic versioning (MAJOR.MINOR.PATCH)
- Git-based version tracking with tags
- Changelog management following Keep a Changelog format
- Version metadata tracking with .version files
- Rollback capabilities with automatic backup creation
- Conventional commits support for automated changelog generation
