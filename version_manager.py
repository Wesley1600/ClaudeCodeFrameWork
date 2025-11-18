#!/usr/bin/env python3
"""
Version Management Utility for ClaudeCodeFrameWork

A specialized version management tool that:
- Records changes to templates, skills, or code
- Maintains a CHANGELOG.md file
- Interacts with Git repositories to commit updates and tag releases
- Supports semantic versioning (MAJOR.MINOR.PATCH)

Usage:
    python version_manager.py current                    # Show current version
    python version_manager.py bump [major|minor|patch]   # Bump version
    python version_manager.py add-change "description"   # Add change to unreleased
    python version_manager.py release                    # Create release from unreleased
    python version_manager.py tag                        # Create git tag for current version
    python version_manager.py status                     # Show unreleased changes
"""

__version__ = "1.0.0"
__author__ = "ClaudeCodeFrameWork"

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional, Tuple


@dataclass
class VersionInfo:
    """Semantic version information"""
    major: int
    minor: int
    patch: int

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def from_string(cls, version_str: str) -> 'VersionInfo':
        """Parse version string like '1.0.0'"""
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        return cls(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    def bump(self, bump_type: str) -> 'VersionInfo':
        """Create new version by bumping major, minor, or patch"""
        if bump_type == 'major':
            return VersionInfo(self.major + 1, 0, 0)
        elif bump_type == 'minor':
            return VersionInfo(self.major, self.minor + 1, 0)
        elif bump_type == 'patch':
            return VersionInfo(self.major, self.minor, self.patch + 1)
        else:
            raise ValueError(f"Invalid bump type: {bump_type}. Use major, minor, or patch")


@dataclass
class Change:
    """Represents a single change entry"""
    category: str  # Added, Changed, Deprecated, Removed, Fixed, Security, Performance
    description: str

    def to_markdown(self) -> str:
        return f"- {self.description}"


class VersionManager:
    """Manages version information and changelog"""

    # Files to track for version information
    VERSION_FILES = {
        'umap_analogy_engine.py': r'__version__\s*=\s*["\']([^"\']+)["\']',
        'version_manager.py': r'__version__\s*=\s*["\']([^"\']+)["\']',
    }

    # Valid change categories
    CATEGORIES = ['Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Security', 'Performance']

    def __init__(self, root_dir: Optional[Path] = None):
        """Initialize version manager

        Args:
            root_dir: Root directory of project (default: current directory)
        """
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self.changelog_path = self.root_dir / 'CHANGELOG.md'
        self.config_path = self.root_dir / '.version_config.json'
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load version management configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            'auto_commit': True,
            'auto_tag': False,
            'commit_template': 'chore: bump version to {version}',
            'tag_prefix': 'v',
            'track_files': list(self.VERSION_FILES.keys())
        }

    def _save_config(self):
        """Save version management configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_current_version(self) -> VersionInfo:
        """Get current version from main module"""
        main_file = self.root_dir / 'umap_analogy_engine.py'
        if not main_file.exists():
            raise FileNotFoundError(f"Main module not found: {main_file}")

        content = main_file.read_text()
        match = re.search(self.VERSION_FILES['umap_analogy_engine.py'], content)
        if not match:
            raise ValueError(f"Version not found in {main_file}")

        return VersionInfo.from_string(match.group(1))

    def update_version_in_files(self, new_version: VersionInfo):
        """Update version in all tracked files"""
        version_str = str(new_version)

        for filename, pattern in self.VERSION_FILES.items():
            filepath = self.root_dir / filename
            if not filepath.exists():
                print(f"Warning: {filename} not found, skipping")
                continue

            content = filepath.read_text()
            new_content = re.sub(
                pattern,
                f'__version__ = "{version_str}"',
                content
            )

            if content != new_content:
                filepath.write_text(new_content)
                print(f"✓ Updated version in {filename}")
            else:
                print(f"⚠ No version found in {filename}")

    def read_changelog(self) -> str:
        """Read current changelog content"""
        if not self.changelog_path.exists():
            raise FileNotFoundError(f"CHANGELOG.md not found at {self.changelog_path}")
        return self.changelog_path.read_text()

    def get_unreleased_changes(self) -> Dict[str, List[str]]:
        """Extract unreleased changes from CHANGELOG.md"""
        content = self.read_changelog()

        # Find unreleased section
        unreleased_match = re.search(
            r'## \[Unreleased\](.*?)(?=\n## \[|\Z)',
            content,
            re.DOTALL
        )

        if not unreleased_match:
            return {}

        unreleased_section = unreleased_match.group(1)
        changes = {}

        # Parse categories
        for category in self.CATEGORIES:
            category_match = re.search(
                f'### {category}(.*?)(?=\n### |\Z)',
                unreleased_section,
                re.DOTALL
            )
            if category_match:
                items = re.findall(r'^- (.+)$', category_match.group(1), re.MULTILINE)
                if items:
                    changes[category] = items

        return changes

    def add_change(self, category: str, description: str):
        """Add a change to the unreleased section

        Args:
            category: Change category (Added, Changed, Fixed, etc.)
            description: Description of the change
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}. Must be one of {self.CATEGORIES}")

        content = self.read_changelog()

        # Find unreleased section
        unreleased_match = re.search(
            r'(## \[Unreleased\].*?)(\n## \[)',
            content,
            re.DOTALL
        )

        if not unreleased_match:
            raise ValueError("Could not find [Unreleased] section in CHANGELOG.md")

        unreleased_section = unreleased_match.group(1)
        next_section = unreleased_match.group(2)

        # Check if category exists
        category_pattern = f'### {category}'
        if category_pattern in unreleased_section:
            # Add to existing category
            new_section = re.sub(
                f'(### {category}\n)',
                f'\\1- {description}\n',
                unreleased_section
            )
        else:
            # Add new category
            new_section = unreleased_section + f'\n### {category}\n- {description}\n'

        # Replace in content
        new_content = content.replace(
            unreleased_match.group(0),
            new_section + next_section
        )

        self.changelog_path.write_text(new_content)
        print(f"✓ Added change to {category}: {description}")

    def create_release(self, version: Optional[VersionInfo] = None, date: Optional[str] = None):
        """Create a release from unreleased changes

        Args:
            version: Version to release (default: current version)
            date: Release date in YYYY-MM-DD format (default: today)
        """
        if version is None:
            version = self.get_current_version()

        if date is None:
            date = datetime.date.today().isoformat()

        content = self.read_changelog()

        # Get unreleased changes
        unreleased_changes = self.get_unreleased_changes()
        if not unreleased_changes:
            print("⚠ No unreleased changes found")
            return

        # Build release section
        release_header = f'## [{version}] - {date}\n'
        release_body = ''

        for category in self.CATEGORIES:
            if category in unreleased_changes:
                release_body += f'\n### {category}\n'
                for change in unreleased_changes[category]:
                    release_body += f'- {change}\n'

        # Replace unreleased section with empty one and add new release
        new_content = re.sub(
            r'## \[Unreleased\].*?(\n## \[)',
            f'## [Unreleased]\n\n{release_header}{release_body}\\1',
            content,
            flags=re.DOTALL
        )

        # Update version links at bottom
        version_str = str(version)
        prev_version_match = re.search(r'\[(\d+\.\d+\.\d+)\]:', content)

        if prev_version_match:
            prev_version = prev_version_match.group(1)
            # Update unreleased link
            new_content = re.sub(
                r'\[Unreleased\]:.*',
                f'[Unreleased]: https://github.com/Wesley1600/ClaudeCodeFrameWork/compare/v{version_str}...HEAD',
                new_content
            )
            # Add new version link
            new_content = re.sub(
                r'(\[Unreleased\]:.*\n)',
                f'\\1[{version_str}]: https://github.com/Wesley1600/ClaudeCodeFrameWork/compare/v{prev_version}...v{version_str}\n',
                new_content
            )

        self.changelog_path.write_text(new_content)
        print(f"✓ Created release {version} in CHANGELOG.md")

    def bump_version(self, bump_type: str) -> VersionInfo:
        """Bump version and update files

        Args:
            bump_type: Type of bump (major, minor, patch)

        Returns:
            New version info
        """
        current = self.get_current_version()
        new_version = current.bump(bump_type)

        print(f"Bumping version: {current} → {new_version}")

        # Update version in files
        self.update_version_in_files(new_version)

        # Create release in changelog
        self.create_release(new_version)

        return new_version

    def create_git_tag(self, version: Optional[VersionInfo] = None, message: Optional[str] = None):
        """Create a git tag for the current version

        Args:
            version: Version to tag (default: current version)
            message: Tag message (default: "Release {version}")
        """
        if version is None:
            version = self.get_current_version()

        tag_name = f"{self.config.get('tag_prefix', 'v')}{version}"

        if message is None:
            message = f"Release {version}"

        try:
            # Check if tag already exists
            result = subprocess.run(
                ['git', 'tag', '-l', tag_name],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                check=True
            )

            if result.stdout.strip():
                print(f"⚠ Tag {tag_name} already exists")
                return

            # Create tag
            subprocess.run(
                ['git', 'tag', '-a', tag_name, '-m', message],
                cwd=self.root_dir,
                check=True
            )
            print(f"✓ Created git tag: {tag_name}")

            print(f"\nTo push the tag, run:")
            print(f"  git push origin {tag_name}")

        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create git tag: {e}")

    def commit_changes(self, version: VersionInfo, files: Optional[List[str]] = None):
        """Commit version changes to git

        Args:
            version: Version being committed
            files: Specific files to commit (default: all tracked files)
        """
        if files is None:
            files = [
                'CHANGELOG.md',
                *self.config.get('track_files', list(self.VERSION_FILES.keys()))
            ]

        commit_msg = self.config.get('commit_template', 'chore: bump version to {version}').format(
            version=version
        )

        try:
            # Add files
            subprocess.run(
                ['git', 'add'] + files,
                cwd=self.root_dir,
                check=True
            )

            # Commit
            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=self.root_dir,
                check=True
            )
            print(f"✓ Committed changes: {commit_msg}")

        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to commit changes: {e}")

    def show_status(self):
        """Show current version and unreleased changes"""
        print("=" * 60)
        print("VERSION MANAGEMENT STATUS")
        print("=" * 60)

        # Current version
        current = self.get_current_version()
        print(f"\nCurrent Version: {current}")

        # Unreleased changes
        unreleased = self.get_unreleased_changes()
        if unreleased:
            print("\nUnreleased Changes:")
            for category, changes in unreleased.items():
                print(f"\n  {category}:")
                for change in changes:
                    print(f"    - {change}")
        else:
            print("\nNo unreleased changes")

        print("\n" + "=" * 60)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Version Management Utility for ClaudeCodeFrameWork'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # current command
    subparsers.add_parser('current', help='Show current version')

    # bump command
    bump_parser = subparsers.add_parser('bump', help='Bump version')
    bump_parser.add_argument(
        'type',
        choices=['major', 'minor', 'patch'],
        help='Type of version bump'
    )
    bump_parser.add_argument(
        '--no-commit',
        action='store_true',
        help='Do not commit changes'
    )
    bump_parser.add_argument(
        '--tag',
        action='store_true',
        help='Create git tag after bump'
    )

    # add-change command
    change_parser = subparsers.add_parser('add-change', help='Add change to unreleased')
    change_parser.add_argument('description', help='Change description')
    change_parser.add_argument(
        '-c', '--category',
        choices=VersionManager.CATEGORIES,
        default='Changed',
        help='Change category (default: Changed)'
    )

    # release command
    release_parser = subparsers.add_parser('release', help='Create release from unreleased')
    release_parser.add_argument(
        '--no-commit',
        action='store_true',
        help='Do not commit changes'
    )

    # tag command
    tag_parser = subparsers.add_parser('tag', help='Create git tag for current version')
    tag_parser.add_argument('-m', '--message', help='Tag message')

    # status command
    subparsers.add_parser('status', help='Show version and unreleased changes')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize version manager
    vm = VersionManager()

    # Execute command
    try:
        if args.command == 'current':
            version = vm.get_current_version()
            print(f"Current version: {version}")

        elif args.command == 'bump':
            new_version = vm.bump_version(args.type)

            if not args.no_commit:
                vm.commit_changes(new_version)

            if args.tag:
                vm.create_git_tag(new_version)

        elif args.command == 'add-change':
            vm.add_change(args.category, args.description)

        elif args.command == 'release':
            vm.create_release()

            if not args.no_commit:
                version = vm.get_current_version()
                vm.commit_changes(version)

        elif args.command == 'tag':
            vm.create_git_tag(message=args.message)

        elif args.command == 'status':
            vm.show_status()

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
