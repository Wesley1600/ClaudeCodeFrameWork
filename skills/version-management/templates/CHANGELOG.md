# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Features that have been added but not yet released

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in upcoming releases

### Removed
- Features that have been removed

### Fixed
- Bug fixes

### Security
- Security improvements or vulnerability fixes

---

## [1.0.0] - YYYY-MM-DD

### Added
- Initial release
- Core functionality implementation
- Basic documentation

### Changed
- N/A (initial release)

### Fixed
- N/A (initial release)

---

## Template Instructions

When adding a new version, follow this format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature A
- New feature B

### Changed
- Modified behavior of feature C
- Updated documentation for D

### Deprecated
- Feature E will be removed in version X+1.0.0

### Removed
- Removed deprecated feature F

### Fixed
- Fixed bug in feature G (#issue-number)
- Corrected typo in documentation

### Security
- Fixed security vulnerability in feature H (CVE-YYYY-XXXXX)
```

### Version Numbering Guide

Given a version number MAJOR.MINOR.PATCH, increment the:

1. **MAJOR** version when you make incompatible API changes
2. **MINOR** version when you add functionality in a backward compatible manner
3. **PATCH** version when you make backward compatible bug fixes

### Categories Guide

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Now removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

### Best Practices

1. **Keep entries concise**: One line per change when possible
2. **Use present tense**: "Add feature" not "Added feature"
3. **Link to issues**: Reference issue/PR numbers when applicable
4. **Group related changes**: Keep related items together
5. **Date format**: Use ISO 8601 (YYYY-MM-DD)
6. **Keep unreleased section**: Always maintain an [Unreleased] section
7. **Add comparison links**: Link version tags for easy diff viewing

### Example with Links

```markdown
## [1.2.0] - 2025-11-18

### Added
- New rollback safety checks ([#123](https://github.com/org/repo/pull/123))
- Automatic backup creation before destructive operations

### Changed
- Improved error messages in validator ([#124](https://github.com/org/repo/pull/124))
- Updated documentation structure

### Fixed
- Rollback file permission issues ([#125](https://github.com/org/repo/issues/125))
- Changelog formatting errors

[1.2.0]: https://github.com/org/repo/compare/v1.1.0...v1.2.0
```

### Comparison Links

Add at the bottom of the file:

```markdown
[Unreleased]: https://github.com/org/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/org/repo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/org/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/org/repo/releases/tag/v1.0.0
```
