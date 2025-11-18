"""Skill registry for managing and accessing skills.

This module provides the SkillRegistry class for registering, retrieving,
and managing skills within the agent framework.
"""

from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import logging


logger = logging.getLogger(__name__)


class SkillRegistry:
    """Central registry for managing skills.

    The registry maintains a catalog of available skills, their metadata,
    and references to their implementations or templates.

    Attributes:
        skills: Dictionary mapping skill_id to skill configuration
        categories: Dictionary organizing skills by category

    Example:
        >>> registry = SkillRegistry()
        >>> registry.register(
        ...     skill_id="skill_nlp_001",
        ...     skill_config={"name": "TextAnalyzer", "category": "nlp"}
        ... )
        >>> skill = registry.get("skill_nlp_001")
    """

    def __init__(self):
        """Initialize an empty skill registry."""
        self._skills: Dict[str, Dict[str, Any]] = {}
        self._categories: Dict[str, List[str]] = {}
        self._executors: Dict[str, Callable] = {}

    def register(
        self,
        skill_id: str,
        skill_config: Dict[str, Any],
        executor: Optional[Callable] = None
    ) -> None:
        """Register a skill with the registry.

        Args:
            skill_id: Unique skill identifier
            skill_config: Skill configuration dictionary containing:
                - name: Skill name
                - description: Skill description
                - category: Skill category
                - inputs: Input specifications
                - outputs: Output specifications
                - metadata: Additional metadata
            executor: Optional callable that executes the skill

        Raises:
            ValueError: If skill_id already exists or config is invalid

        Example:
            >>> registry = SkillRegistry()
            >>> config = {
            ...     "name": "TextAnalyzer",
            ...     "description": "Analyzes text",
            ...     "category": "nlp"
            ... }
            >>> registry.register("skill_nlp_001", config)
        """
        if skill_id in self._skills:
            raise ValueError(f"Skill '{skill_id}' is already registered")

        # Validate required fields
        required_fields = ['name', 'description', 'category']
        for field in required_fields:
            if field not in skill_config:
                raise ValueError(
                    f"Skill config missing required field: '{field}'"
                )

        # Store skill configuration
        self._skills[skill_id] = skill_config.copy()
        self._skills[skill_id]['skill_id'] = skill_id

        # Organize by category
        category = skill_config['category']
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(skill_id)

        # Store executor if provided
        if executor:
            self._executors[skill_id] = executor

        logger.info(f"Registered skill: {skill_id} (category: {category})")

    def unregister(self, skill_id: str) -> None:
        """Remove a skill from the registry.

        Args:
            skill_id: Skill identifier to remove

        Raises:
            KeyError: If skill_id doesn't exist
        """
        if skill_id not in self._skills:
            raise KeyError(f"Skill '{skill_id}' not found in registry")

        # Remove from category index
        category = self._skills[skill_id]['category']
        if category in self._categories:
            self._categories[category].remove(skill_id)
            if not self._categories[category]:
                del self._categories[category]

        # Remove skill and executor
        del self._skills[skill_id]
        if skill_id in self._executors:
            del self._executors[skill_id]

        logger.info(f"Unregistered skill: {skill_id}")

    def get(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a skill's configuration by ID.

        Args:
            skill_id: Skill identifier

        Returns:
            Skill configuration dictionary, or None if not found

        Example:
            >>> registry = SkillRegistry()
            >>> config = registry.get("skill_nlp_001")
        """
        return self._skills.get(skill_id)

    def get_executor(self, skill_id: str) -> Optional[Callable]:
        """Retrieve a skill's executor function.

        Args:
            skill_id: Skill identifier

        Returns:
            Executor callable, or None if not registered

        Example:
            >>> executor = registry.get_executor("skill_nlp_001")
            >>> if executor:
            ...     result = executor(input_data)
        """
        return self._executors.get(skill_id)

    def execute(self, skill_id: str, **kwargs) -> Any:
        """Execute a skill with provided arguments.

        Args:
            skill_id: Skill identifier
            **kwargs: Arguments to pass to skill executor

        Returns:
            Result from skill execution

        Raises:
            KeyError: If skill not found
            ValueError: If skill has no executor

        Example:
            >>> result = registry.execute(
            ...     "skill_nlp_001",
            ...     text="Hello world"
            ... )
        """
        if skill_id not in self._skills:
            raise KeyError(f"Skill '{skill_id}' not found in registry")

        executor = self._executors.get(skill_id)
        if not executor:
            raise ValueError(f"Skill '{skill_id}' has no executor registered")

        logger.debug(f"Executing skill: {skill_id}")
        return executor(**kwargs)

    def list_skills(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[str]:
        """List all registered skill IDs, optionally filtered.

        Args:
            category: Filter by category
            tag: Filter by tag in metadata

        Returns:
            List of skill IDs

        Example:
            >>> # List all skills
            >>> all_skills = registry.list_skills()
            >>> # List NLP skills
            >>> nlp_skills = registry.list_skills(category="nlp")
            >>> # List skills with 'analysis' tag
            >>> analysis_skills = registry.list_skills(tag="analysis")
        """
        if category:
            return self._categories.get(category, []).copy()

        if tag:
            filtered = []
            for skill_id, config in self._skills.items():
                tags = config.get('metadata', {}).get('tags', [])
                if tag in tags:
                    filtered.append(skill_id)
            return filtered

        return list(self._skills.keys())

    def list_categories(self) -> List[str]:
        """List all available skill categories.

        Returns:
            List of category names

        Example:
            >>> categories = registry.list_categories()
            >>> print(f"Available categories: {', '.join(categories)}")
        """
        return list(self._categories.keys())

    def search(
        self,
        query: str,
        search_fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search for skills matching a query.

        Args:
            query: Search query string
            search_fields: Fields to search in (default: ['name', 'description'])

        Returns:
            List of matching skill configurations

        Example:
            >>> results = registry.search("text analysis")
            >>> for skill in results:
            ...     print(f"Found: {skill['name']}")
        """
        if search_fields is None:
            search_fields = ['name', 'description']

        query_lower = query.lower()
        results = []

        for skill_id, config in self._skills.items():
            for field in search_fields:
                value = config.get(field, '')

                if isinstance(value, str) and query_lower in value.lower():
                    results.append(config.copy())
                    break
                elif isinstance(value, list):
                    if any(query_lower in str(item).lower() for item in value):
                        results.append(config.copy())
                        break

        return results

    def get_dependencies(self, skill_id: str) -> List[str]:
        """Get list of skill_ids that a skill depends on.

        Args:
            skill_id: Skill identifier

        Returns:
            List of dependency skill_ids

        Example:
            >>> deps = registry.get_dependencies("skill_advanced_001")
            >>> print(f"Dependencies: {deps}")
        """
        skill = self.get(skill_id)
        if not skill:
            return []

        return skill.get('metadata', {}).get('dependencies', [])

    def validate_dependencies(self, skill_id: str) -> Tuple[bool, List[str]]:
        """Validate that all dependencies for a skill are registered.

        Args:
            skill_id: Skill identifier

        Returns:
            Tuple of (all_valid, missing_dependencies)

        Example:
            >>> is_valid, missing = registry.validate_dependencies("skill_001")
            >>> if not is_valid:
            ...     print(f"Missing dependencies: {missing}")
        """
        dependencies = self.get_dependencies(skill_id)
        missing = [
            dep for dep in dependencies
            if dep not in self._skills
        ]

        return (len(missing) == 0, missing)

    def get_skill_count(self) -> int:
        """Get total number of registered skills.

        Returns:
            Number of registered skills

        Example:
            >>> count = registry.get_skill_count()
            >>> print(f"Total skills: {count}")
        """
        return len(self._skills)

    def clear(self) -> None:
        """Remove all skills from the registry.

        Example:
            >>> registry.clear()
        """
        self._skills.clear()
        self._categories.clear()
        self._executors.clear()
        logger.info("Cleared all skills from registry")

    def export_catalog(self) -> Dict[str, Any]:
        """Export the complete skill catalog.

        Returns:
            Dictionary containing all skills and metadata

        Example:
            >>> catalog = registry.export_catalog()
            >>> import json
            >>> with open('catalog.json', 'w') as f:
            ...     json.dump(catalog, f)
        """
        return {
            'skills': self._skills.copy(),
            'categories': self._categories.copy(),
            'total_skills': len(self._skills),
            'total_categories': len(self._categories),
        }

    def __len__(self) -> int:
        """Return number of registered skills."""
        return len(self._skills)

    def __contains__(self, skill_id: str) -> bool:
        """Check if a skill is registered."""
        return skill_id in self._skills

    def __repr__(self) -> str:
        """String representation of the registry."""
        return (
            f"SkillRegistry(skills={len(self._skills)}, "
            f"categories={len(self._categories)})"
        )


# Add missing import
from typing import Tuple
