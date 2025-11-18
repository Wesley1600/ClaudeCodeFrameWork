#!/usr/bin/env python3
"""
Advanced Version Management Utilities
Provides Python-based tools for skill version management
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ChangeType(Enum):
    """Types of changes in a changelog"""
    ADDED = "Added"
    CHANGED = "Changed"
    DEPRECATED = "Deprecated"
    REMOVED = "Removed"
    FIXED = "Fixed"
    SECURITY = "Security"


@dataclass
class Version:
    """Represents a semantic version"""
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other):
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other):
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)

    def __gt__(self, other):
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    def __ge__(self, other):
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)

    def __eq__(self, other):
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    @classmethod
    def parse(cls, version_string: str) -> 'Version':
        """Parse a version string like '1.2.3' or 'v1.2.3'"""
        version_string = version_string.lstrip('v')
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_string)
        if not match:
            raise ValueError(f"Invalid version format: {version_string}")
        return cls(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    def bump(self, level: str) -> 'Version':
        """Bump version by major, minor, or patch"""
        if level == 'major':
            return Version(self.major + 1, 0, 0)
        elif level == 'minor':
            return Version(self.major, self.minor + 1, 0)
        elif level == 'patch':
            return Version(self.major, self.minor, self.patch + 1)
        else:
            raise ValueError(f"Invalid bump level: {level}")


@dataclass
class SkillVersion:
    """Metadata about a skill version"""
    name: str
    version: Version
    tag: str
    date: str
    message: str
    commit: str

    def to_dict(self):
        return {
            'name': self.name,
            'version': str(self.version),
            'tag': self.tag,
            'date': self.date,
            'message': self.message,
            'commit': self.commit
        }


@dataclass
class VersionMetadata:
    """Skill version metadata from .version file"""
    name: str
    version: str
    released: str
    stable: bool
    deprecated: bool
    dependencies: Optional[Dict] = None

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


class VersionManager:
    """Manages versions for Claude Code skills"""

    def __init__(self, skills_dir: Path):
        self.skills_dir = Path(skills_dir)
        if not self.skills_dir.exists():
            raise ValueError(f"Skills directory not found: {skills_dir}")

    def _run_git(self, *args, cwd=None) -> str:
        """Run a git command and return output"""
        try:
            result = subprocess.run(
                ['git'] + list(args),
                cwd=cwd or self.skills_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e.stderr}")

    def get_skill_versions(self, skill_name: str) -> List[SkillVersion]:
        """Get all versions for a specific skill"""
        pattern = f"skill/{skill_name}/v*"
        tag_format = "%(refname:short)\t%(creatordate:short)\t%(contents:subject)\t%(objectname:short)"

        try:
            output = self._run_git('tag', '-l', pattern, '--sort=-version:refname', f'--format={tag_format}')
        except RuntimeError:
            return []

        versions = []
        for line in output.split('\n'):
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) < 4:
                continue

            tag, date, message, commit = parts[0], parts[1], parts[2], parts[3]

            # Extract version from tag
            version_match = re.search(r'/v(\d+\.\d+\.\d+)$', tag)
            if not version_match:
                continue

            version = Version.parse(version_match.group(1))

            versions.append(SkillVersion(
                name=skill_name,
                version=version,
                tag=tag,
                date=date,
                message=message,
                commit=commit
            ))

        return versions

    def get_all_skills(self) -> List[str]:
        """Get list of all skills"""
        skills = []
        for item in self.skills_dir.iterdir():
            if item.is_dir() and (item / 'SKILL.md').exists():
                skills.append(item.name)
        return sorted(skills)

    def get_current_version(self, skill_name: str) -> Optional[Version]:
        """Get current version of a skill"""
        skill_dir = self.skills_dir / skill_name
        version_file = skill_dir / '.version'

        if version_file.exists():
            try:
                with open(version_file) as f:
                    data = json.load(f)
                    return Version.parse(data['version'])
            except (json.JSONDecodeError, KeyError, ValueError):
                pass

        # Fallback to latest tag
        versions = self.get_skill_versions(skill_name)
        if versions:
            return versions[0].version

        return None

    def read_metadata(self, skill_name: str) -> Optional[VersionMetadata]:
        """Read version metadata from .version file"""
        skill_dir = self.skills_dir / skill_name
        version_file = skill_dir / '.version'

        if not version_file.exists():
            return None

        try:
            with open(version_file) as f:
                data = json.load(f)
                return VersionMetadata(**data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error reading metadata: {e}", file=sys.stderr)
            return None

    def write_metadata(self, skill_name: str, metadata: VersionMetadata):
        """Write version metadata to .version file"""
        skill_dir = self.skills_dir / skill_name
        version_file = skill_dir / '.version'

        with open(version_file, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)

    def suggest_next_version(self, skill_name: str, change_type: str = 'minor') -> Version:
        """Suggest next version based on current version and change type"""
        current = self.get_current_version(skill_name)
        if not current:
            return Version(0, 1, 0)

        return current.bump(change_type)

    def generate_changelog_entry(self, skill_name: str, version: Version) -> str:
        """Generate changelog entry from git commits since last version"""
        versions = self.get_skill_versions(skill_name)

        if not versions:
            return self._format_changelog_section(version, datetime.now().strftime('%Y-%m-%d'), {
                ChangeType.ADDED: ["Initial version of the skill"]
            })

        last_version = versions[0]
        # Path relative to skills_dir (which is .claude/skills)
        skill_path = skill_name

        # Get commits since last tag
        try:
            log_output = self._run_git(
                'log',
                f'{last_version.tag}..HEAD',
                '--pretty=format:%s',
                '--',
                skill_path
            )
        except RuntimeError:
            return ""

        if not log_output:
            return ""

        # Categorize commits
        changes = self._categorize_commits(log_output.split('\n'))

        return self._format_changelog_section(version, datetime.now().strftime('%Y-%m-%d'), changes)

    def _categorize_commits(self, commits: List[str]) -> Dict[ChangeType, List[str]]:
        """Categorize commits by type using conventional commits"""
        changes = {}

        for commit in commits:
            if not commit:
                continue

            # Try to match conventional commit format
            match = re.match(r'^(feat|fix|docs|refactor|test|chore|security|deprecate)(?:\(.*?\))?:\s*(.+)$', commit)

            if match:
                commit_type, message = match.groups()

                if commit_type == 'feat':
                    changes.setdefault(ChangeType.ADDED, []).append(message)
                elif commit_type == 'fix':
                    changes.setdefault(ChangeType.FIXED, []).append(message)
                elif commit_type == 'security':
                    changes.setdefault(ChangeType.SECURITY, []).append(message)
                elif commit_type == 'deprecate':
                    changes.setdefault(ChangeType.DEPRECATED, []).append(message)
                elif commit_type in ('refactor', 'docs'):
                    changes.setdefault(ChangeType.CHANGED, []).append(message)
            else:
                # Default to "Changed" for non-conventional commits
                changes.setdefault(ChangeType.CHANGED, []).append(commit)

        return changes

    def _format_changelog_section(self, version: Version, date: str, changes: Dict[ChangeType, List[str]]) -> str:
        """Format a changelog section"""
        lines = [f"## [{version}] - {date}", ""]

        for change_type in ChangeType:
            if change_type in changes:
                lines.append(f"### {change_type.value}")
                for change in changes[change_type]:
                    lines.append(f"- {change}")
                lines.append("")

        return '\n'.join(lines)

    def validate_skill(self, skill_name: str) -> List[str]:
        """Validate skill structure and return list of issues"""
        issues = []
        skill_dir = self.skills_dir / skill_name

        if not skill_dir.exists():
            issues.append(f"Skill directory does not exist: {skill_dir}")
            return issues

        if not (skill_dir / 'SKILL.md').exists():
            issues.append("SKILL.md not found")

        if not (skill_dir / 'CHANGELOG.md').exists():
            issues.append("CHANGELOG.md not found (recommended)")

        if not (skill_dir / '.version').exists():
            issues.append(".version file not found (recommended)")

        return issues

    def compare_versions(self, skill_name: str, v1: Version, v2: Version) -> Dict:
        """Compare two versions and return detailed diff"""
        tag1 = f"skill/{skill_name}/v{v1}"
        tag2 = f"skill/{skill_name}/v{v2}"

        try:
            # Get file changes (path relative to skills_dir)
            diff_stat = self._run_git('diff', '--stat', f'{tag1}..{tag2}', '--', skill_name)

            # Get detailed diff (path relative to skills_dir)
            diff_content = self._run_git('diff', f'{tag1}..{tag2}', '--', skill_name)

            return {
                'from_version': str(v1),
                'to_version': str(v2),
                'stat': diff_stat,
                'diff': diff_content,
                'files_changed': len([line for line in diff_stat.split('\n') if line.strip()])
            }
        except RuntimeError as e:
            return {'error': str(e)}


def main():
    """CLI interface for version management"""
    import argparse

    parser = argparse.ArgumentParser(description='Advanced skill version management')
    parser.add_argument('--skills-dir', default='.claude/skills', help='Skills directory')

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # List command
    list_parser = subparsers.add_parser('list', help='List skills and versions')
    list_parser.add_argument('skill', nargs='?', help='Specific skill name')

    # Current command
    current_parser = subparsers.add_parser('current', help='Show current version')
    current_parser.add_argument('skill', help='Skill name')

    # Suggest command
    suggest_parser = subparsers.add_parser('suggest', help='Suggest next version')
    suggest_parser.add_argument('skill', help='Skill name')
    suggest_parser.add_argument('--type', choices=['major', 'minor', 'patch'], default='minor')

    # Changelog command
    changelog_parser = subparsers.add_parser('changelog', help='Generate changelog entry')
    changelog_parser.add_argument('skill', help='Skill name')
    changelog_parser.add_argument('version', help='Version number')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate skill structure')
    validate_parser.add_argument('skill', help='Skill name')

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two versions')
    compare_parser.add_argument('skill', help='Skill name')
    compare_parser.add_argument('v1', help='First version')
    compare_parser.add_argument('v2', help='Second version')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        manager = VersionManager(args.skills_dir)

        if args.command == 'list':
            if args.skill:
                versions = manager.get_skill_versions(args.skill)
                for v in versions:
                    print(f"{v.tag}\t{v.date}\t{v.message}")
            else:
                skills = manager.get_all_skills()
                for skill in skills:
                    current = manager.get_current_version(skill)
                    print(f"{skill}: {current or 'no version'}")

        elif args.command == 'current':
            version = manager.get_current_version(args.skill)
            if version:
                print(f"Current version: {version}")
            else:
                print("No version found")
                sys.exit(1)

        elif args.command == 'suggest':
            next_version = manager.suggest_next_version(args.skill, args.type)
            print(f"Suggested next version: {next_version}")

        elif args.command == 'changelog':
            version = Version.parse(args.version)
            entry = manager.generate_changelog_entry(args.skill, version)
            print(entry)

        elif args.command == 'validate':
            issues = manager.validate_skill(args.skill)
            if issues:
                print("Issues found:")
                for issue in issues:
                    print(f"  - {issue}")
                sys.exit(1)
            else:
                print("Skill structure is valid")

        elif args.command == 'compare':
            v1 = Version.parse(args.v1)
            v2 = Version.parse(args.v2)
            result = manager.compare_versions(args.skill, v1, v2)

            if 'error' in result:
                print(f"Error: {result['error']}", file=sys.stderr)
                sys.exit(1)

            print(f"Comparing {result['from_version']} → {result['to_version']}")
            print(f"\nFiles changed: {result['files_changed']}")
            print("\nStats:")
            print(result['stat'])

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
