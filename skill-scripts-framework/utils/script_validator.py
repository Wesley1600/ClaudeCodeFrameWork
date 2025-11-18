#!/usr/bin/env python3
"""
Script Validator Utility

Validates skill scripts for common issues and best practices.
"""

import json
import os
import stat
import sys
from pathlib import Path
from typing import List, Dict, Any


class ValidationResult:
    """Result of a validation check."""

    def __init__(self, severity: str, message: str, file: str = None):
        self.severity = severity  # "error", "warning", "info"
        self.message = message
        self.file = file

    def __str__(self):
        prefix = {
            "error": "❌ ERROR",
            "warning": "⚠️  WARNING",
            "info": "ℹ️  INFO"
        }.get(self.severity, "")

        if self.file:
            return f"{prefix}: {self.file}: {self.message}"
        return f"{prefix}: {self.message}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "severity": self.severity,
            "message": self.message,
            "file": self.file
        }


class ScriptValidator:
    """Validates skill scripts."""

    def __init__(self, skill_root: Path):
        """
        Initialize validator.

        Args:
            skill_root: Root directory of the skill
        """
        self.skill_root = Path(skill_root)
        self.scripts_dir = self.skill_root / "scripts"
        self.results: List[ValidationResult] = []

    def validate_all(self) -> List[ValidationResult]:
        """
        Run all validation checks.

        Returns:
            List of validation results
        """
        self.results = []

        self._check_structure()
        self._check_skill_md()
        self._check_python_scripts()
        self._check_bash_scripts()
        self._check_permissions()
        self._check_best_practices()

        return self.results

    def _check_structure(self):
        """Check directory structure."""
        # Check if SKILL.md exists
        skill_md = self.skill_root / "SKILL.md"
        if not skill_md.exists():
            self.results.append(ValidationResult(
                "error",
                "SKILL.md not found",
                str(self.skill_root)
            ))

        # Check if scripts directory exists
        if not self.scripts_dir.exists():
            self.results.append(ValidationResult(
                "error",
                "scripts/ directory not found",
                str(self.skill_root)
            ))
            return

        # Check for at least one script
        python_scripts = list(self.scripts_dir.glob("**/*.py"))
        bash_scripts = list(self.scripts_dir.glob("**/*.sh"))

        if not python_scripts and not bash_scripts:
            self.results.append(ValidationResult(
                "warning",
                "No Python or Bash scripts found in scripts/",
                str(self.scripts_dir)
            ))

    def _check_skill_md(self):
        """Check SKILL.md content."""
        skill_md = self.skill_root / "SKILL.md"
        if not skill_md.exists():
            return

        content = skill_md.read_text()

        # Check for template placeholders
        if "[" in content and "]" in content:
            self.results.append(ValidationResult(
                "warning",
                "SKILL.md contains template placeholders [...]",
                "SKILL.md"
            ))

        # Check for script references
        if "scripts/" not in content and "python" not in content.lower() and "bash" not in content.lower():
            self.results.append(ValidationResult(
                "warning",
                "SKILL.md doesn't reference any scripts",
                "SKILL.md"
            ))

        # Check size (should be concise)
        if len(content) > 10000:
            self.results.append(ValidationResult(
                "warning",
                f"SKILL.md is large ({len(content)} bytes). Consider moving details to README.md",
                "SKILL.md"
            ))

    def _check_python_scripts(self):
        """Check Python scripts."""
        python_scripts = list(self.scripts_dir.glob("**/*.py"))

        for script in python_scripts:
            relative_path = script.relative_to(self.skill_root)

            # Check shebang
            first_line = script.read_text().split('\n')[0]
            if not first_line.startswith('#!'):
                self.results.append(ValidationResult(
                    "info",
                    "Missing shebang line (#!/usr/bin/env python3)",
                    str(relative_path)
                ))

            # Check for main guard
            content = script.read_text()
            if '__main__' not in content:
                self.results.append(ValidationResult(
                    "warning",
                    "Missing if __name__ == '__main__': guard",
                    str(relative_path)
                ))

            # Check for basic error handling
            if 'try:' not in content and 'except' not in content:
                self.results.append(ValidationResult(
                    "warning",
                    "No exception handling found",
                    str(relative_path)
                ))

    def _check_bash_scripts(self):
        """Check Bash scripts."""
        bash_scripts = list(self.scripts_dir.glob("**/*.sh"))

        for script in bash_scripts:
            relative_path = script.relative_to(self.skill_root)
            content = script.read_text()

            # Check shebang
            first_line = content.split('\n')[0]
            if not first_line.startswith('#!/'):
                self.results.append(ValidationResult(
                    "error",
                    "Missing shebang line (#!/usr/bin/env bash)",
                    str(relative_path)
                ))

            # Check for error handling
            if 'set -e' not in content:
                self.results.append(ValidationResult(
                    "warning",
                    "Missing 'set -e' for error handling",
                    str(relative_path)
                ))

            # Check for undefined variable handling
            if 'set -u' not in content:
                self.results.append(ValidationResult(
                    "info",
                    "Missing 'set -u' for undefined variable handling",
                    str(relative_path)
                ))

    def _check_permissions(self):
        """Check file permissions."""
        python_scripts = list(self.scripts_dir.glob("**/*.py"))
        bash_scripts = list(self.scripts_dir.glob("**/*.sh"))

        for script in python_scripts + bash_scripts:
            relative_path = script.relative_to(self.skill_root)
            file_stat = script.stat()

            # Check if executable
            if not file_stat.st_mode & stat.S_IXUSR:
                self.results.append(ValidationResult(
                    "warning",
                    "Script is not executable (run: chmod +x)",
                    str(relative_path)
                ))

    def _check_best_practices(self):
        """Check for best practices."""
        # Check for README.md
        readme = self.skill_root / "README.md"
        if not readme.exists():
            self.results.append(ValidationResult(
                "info",
                "No README.md found (recommended for developer documentation)",
                str(self.skill_root)
            ))

        # Check for allowed-tools.json
        allowed_tools = self.skill_root / "allowed-tools.json"
        if allowed_tools.exists():
            try:
                data = json.loads(allowed_tools.read_text())
                if "allowed_tools" not in data:
                    self.results.append(ValidationResult(
                        "warning",
                        "allowed-tools.json missing 'allowed_tools' key",
                        "allowed-tools.json"
                    ))
            except json.JSONDecodeError:
                self.results.append(ValidationResult(
                    "error",
                    "allowed-tools.json is not valid JSON",
                    "allowed-tools.json"
                ))

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return any(r.severity == "error" for r in self.results)

    def print_results(self):
        """Print validation results."""
        for result in self.results:
            print(result)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate skill scripts")
    parser.add_argument("skill_root", help="Root directory of the skill")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    validator = ScriptValidator(args.skill_root)
    results = validator.validate_all()

    if args.json:
        output = {
            "valid": not validator.has_errors(),
            "results": [r.to_dict() for r in results]
        }
        print(json.dumps(output, indent=2))
    else:
        validator.print_results()

        print(f"\n{'='*50}")
        if validator.has_errors():
            print("❌ Validation failed with errors")
            sys.exit(1)
        else:
            print("✅ Validation passed")
            sys.exit(0)


if __name__ == "__main__":
    main()
