"""Skill loader for loading skill configurations from files.

This module provides functionality to load skill definitions from YAML/JSON
files and register them in the skill registry.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class SkillLoader:
    """Loads skill configurations from files.

    Supports loading individual skills or batch loading from directories.

    Attributes:
        skills_dir: Default directory for skill configurations

    Example:
        >>> loader = SkillLoader("skills/examples/")
        >>> skill_config = loader.load("skill_nlp_001.yaml")
        >>> all_skills = loader.load_all()
    """

    def __init__(self, skills_dir: Optional[str] = None):
        """Initialize the skill loader.

        Args:
            skills_dir: Directory containing skill configuration files.
                       Defaults to 'skills/examples' in current directory.
        """
        if skills_dir is None:
            skills_dir = "skills/examples"

        self.skills_dir = Path(skills_dir)

        if not self.skills_dir.exists():
            logger.warning(f"Skills directory does not exist: {self.skills_dir}")
            self.skills_dir.mkdir(parents=True, exist_ok=True)

    def load(self, filename: str) -> Dict[str, Any]:
        """Load a single skill configuration from file.

        Args:
            filename: Name of skill configuration file (YAML or JSON)

        Returns:
            Skill configuration dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid

        Example:
            >>> loader = SkillLoader()
            >>> config = loader.load("text_analyzer.yaml")
        """
        file_path = self.skills_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Skill file not found: {file_path}")

        return self._load_file(file_path)

    def load_all(self) -> List[Dict[str, Any]]:
        """Load all skill configurations from the skills directory.

        Returns:
            List of skill configuration dictionaries

        Example:
            >>> loader = SkillLoader()
            >>> all_skills = loader.load_all()
            >>> print(f"Loaded {len(all_skills)} skills")
        """
        skills = []

        # Load YAML files
        for yaml_file in self.skills_dir.glob("*.yaml"):
            try:
                config = self._load_file(yaml_file)
                skills.append(config)
                logger.info(f"Loaded skill from {yaml_file.name}")
            except Exception as e:
                logger.error(f"Failed to load {yaml_file.name}: {e}")

        # Load JSON files
        for json_file in self.skills_dir.glob("*.json"):
            try:
                config = self._load_file(json_file)
                skills.append(config)
                logger.info(f"Loaded skill from {json_file.name}")
            except Exception as e:
                logger.error(f"Failed to load {json_file.name}: {e}")

        return skills

    def load_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Load all skills matching a specific category.

        Args:
            category: Category name to filter by

        Returns:
            List of skill configurations in the specified category

        Example:
            >>> loader = SkillLoader()
            >>> nlp_skills = loader.load_by_category("nlp")
        """
        all_skills = self.load_all()
        return [
            skill for skill in all_skills
            if skill.get('category') == category
        ]

    def save(
        self,
        skill_config: Dict[str, Any],
        filename: Optional[str] = None,
        format: str = 'yaml'
    ) -> str:
        """Save a skill configuration to file.

        Args:
            skill_config: Skill configuration dictionary
            filename: Output filename (auto-generated if not provided)
            format: Output format ('yaml' or 'json')

        Returns:
            Path to saved file

        Example:
            >>> loader = SkillLoader()
            >>> config = {"skill_id": "skill_001", "name": "TestSkill"}
            >>> path = loader.save(config)
        """
        # Generate filename if not provided
        if filename is None:
            skill_id = skill_config.get('skill_id', 'unnamed_skill')
            ext = 'yaml' if format == 'yaml' else 'json'
            filename = f"{skill_id}.{ext}"

        output_path = self.skills_dir / filename

        # Save file
        with open(output_path, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(skill_config, f, indent=2)
            else:
                yaml.dump(
                    skill_config,
                    f,
                    default_flow_style=False,
                    sort_keys=False
                )

        logger.info(f"Saved skill configuration to {output_path}")
        return str(output_path)

    @staticmethod
    def _load_file(file_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file.

        Args:
            file_path: Path to configuration file

        Returns:
            Loaded configuration dictionary

        Raises:
            ValueError: If file format is not supported
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix == '.json':
                return json.load(f)
            elif file_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                raise ValueError(
                    f"Unsupported file format: {file_path.suffix}. "
                    "Use .yaml, .yml, or .json"
                )

    def list_available(self) -> List[str]:
        """List all available skill configuration files.

        Returns:
            List of skill configuration filenames

        Example:
            >>> loader = SkillLoader()
            >>> files = loader.list_available()
            >>> print(f"Available skills: {', '.join(files)}")
        """
        files = []

        for yaml_file in self.skills_dir.glob("*.yaml"):
            files.append(yaml_file.name)

        for json_file in self.skills_dir.glob("*.json"):
            files.append(json_file.name)

        return sorted(files)


def load_skill(
    filename: str,
    skills_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function to load a single skill configuration.

    Args:
        filename: Skill configuration filename
        skills_dir: Directory containing skill files

    Returns:
        Skill configuration dictionary

    Example:
        >>> config = load_skill("text_analyzer.yaml")
    """
    loader = SkillLoader(skills_dir)
    return loader.load(filename)


def load_all_skills(skills_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """Convenience function to load all skill configurations.

    Args:
        skills_dir: Directory containing skill files

    Returns:
        List of skill configuration dictionaries

    Example:
        >>> all_skills = load_all_skills()
        >>> for skill in all_skills:
        ...     print(f"Loaded: {skill['name']}")
    """
    loader = SkillLoader(skills_dir)
    return loader.load_all()
