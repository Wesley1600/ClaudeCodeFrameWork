"""
Skill Registry and Catalog - Multi-level Management System

Provides both orchestration-level skill management (SkillRegistry)
and configuration-level skill cataloging (SkillCatalog).
"""

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Type, Any, Callable, Tuple
import logging

from .base_skill import BaseSkill, SkillMetadata


logger = logging.getLogger(__name__)


class SkillRegistry:
    """
    Central registry for orchestration skills.

    Provides:
    - Automatic discovery of BaseSkill classes
    - Manual registration of skill classes
    - Skill instantiation with configuration
    - Querying skills by name, tag, or capability
    - Dependency resolution
    """

    def __init__(self):
        self._skills: Dict[str, Type[BaseSkill]] = {}
        self._metadata_cache: Dict[str, SkillMetadata] = {}

    def register(self, skill_class: Type[BaseSkill], override: bool = False) -> None:
        """
        Register a skill class.

        Args:
            skill_class: Skill class (must inherit from BaseSkill)
            override: Whether to override existing skill with same name
        """
        if not issubclass(skill_class, BaseSkill):
            raise TypeError(f"{skill_class} must inherit from BaseSkill")

        # Create a temporary instance to get metadata
        temp_instance = skill_class()
        skill_name = temp_instance.name

        if skill_name in self._skills and not override:
            raise ValueError(
                f"Skill '{skill_name}' already registered. "
                f"Use override=True to replace."
            )

        self._skills[skill_name] = skill_class
        self._metadata_cache[skill_name] = temp_instance.metadata

        logger.info(f"Registered skill: {skill_name}")

    def unregister(self, skill_name: str) -> None:
        """Remove a skill from the registry"""
        if skill_name in self._skills:
            del self._skills[skill_name]
            del self._metadata_cache[skill_name]
            logger.info(f"Unregistered skill: {skill_name}")

    def get_skill_class(self, name: str) -> Optional[Type[BaseSkill]]:
        """Get skill class by name"""
        return self._skills.get(name)

    def create_skill(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> BaseSkill:
        """
        Instantiate a skill by name.

        Args:
            name: Skill name
            config: Configuration dictionary to pass to skill constructor

        Returns:
            Instantiated skill

        Raises:
            ValueError: If skill not found
        """
        skill_class = self.get_skill_class(name)

        if skill_class is None:
            raise ValueError(
                f"Skill '{name}' not found. Available skills: {self.list_skills()}"
            )

        return skill_class(config=config)

    def list_skills(self) -> List[str]:
        """Get list of all registered skill names"""
        return sorted(self._skills.keys())

    def get_metadata(self, name: str) -> Optional[SkillMetadata]:
        """Get metadata for a skill"""
        return self._metadata_cache.get(name)

    def search_by_tag(self, tag: str) -> List[str]:
        """Find all skills with a specific tag"""
        results = []
        for name, metadata in self._metadata_cache.items():
            if tag in metadata.tags:
                results.append(name)
        return results

    def discover_skills(self, package_or_path: str) -> int:
        """
        Automatically discover and register skills from a package or directory.

        Args:
            package_or_path: Python package name or directory path

        Returns:
            Number of skills discovered and registered
        """
        discovered = 0

        # Check if it's a file path
        path = Path(package_or_path)
        if path.exists() and path.is_dir():
            discovered = self._discover_from_directory(path)
        else:
            # Try as a package name
            try:
                discovered = self._discover_from_package(package_or_path)
            except ImportError as e:
                logger.error(f"Could not import package {package_or_path}: {e}")

        logger.info(f"Discovered {discovered} skills from {package_or_path}")
        return discovered

    def _discover_from_package(self, package_name: str) -> int:
        """Discover skills from a Python package"""
        discovered = 0

        try:
            package = importlib.import_module(package_name)
        except ImportError:
            logger.error(f"Could not import package: {package_name}")
            return 0

        # Iterate through all modules in the package
        if hasattr(package, '__path__'):
            for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                full_module_name = f"{package_name}.{module_name}"
                try:
                    module = importlib.import_module(full_module_name)
                    discovered += self._register_skills_from_module(module)
                except Exception as e:
                    logger.warning(f"Error loading module {full_module_name}: {e}")

        return discovered

    def _discover_from_directory(self, directory: Path) -> int:
        """Discover skills from a directory"""
        discovered = 0

        for py_file in directory.glob("**/*.py"):
            if py_file.name.startswith("_"):
                continue

            # Convert path to module name
            rel_path = py_file.relative_to(directory.parent)
            module_name = str(rel_path.with_suffix("")).replace("/", ".")

            try:
                module = importlib.import_module(module_name)
                discovered += self._register_skills_from_module(module)
            except Exception as e:
                logger.warning(f"Error loading {py_file}: {e}")

        return discovered

    def _register_skills_from_module(self, module) -> int:
        """Register all skill classes found in a module"""
        discovered = 0

        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip the base classes themselves
            if obj is BaseSkill:
                continue

            # Check if it's a BaseSkill subclass
            if issubclass(obj, BaseSkill) and obj.__module__ == module.__name__:
                try:
                    self.register(obj, override=False)
                    discovered += 1
                except Exception as e:
                    logger.warning(f"Could not register {name}: {e}")

        return discovered

    def get_dependency_order(self, skill_names: List[str]) -> List[str]:
        """
        Resolve skill dependencies and return execution order.

        Args:
            skill_names: List of skill names to order

        Returns:
            Ordered list of skill names respecting dependencies

        Raises:
            ValueError: If circular dependency detected
        """
        # Build dependency graph
        deps_map = {}
        for name in skill_names:
            metadata = self.get_metadata(name)
            if metadata:
                deps_map[name] = [d for d in metadata.dependencies if d in skill_names]
            else:
                deps_map[name] = []

        # Topological sort
        ordered = []
        visited = set()
        visiting = set()

        def visit(node: str):
            if node in visited:
                return
            if node in visiting:
                raise ValueError(f"Circular dependency detected involving {node}")

            visiting.add(node)
            for dep in deps_map.get(node, []):
                visit(dep)
            visiting.remove(node)
            visited.add(node)
            ordered.append(node)

        for name in skill_names:
            visit(name)

        return ordered

    def __repr__(self) -> str:
        return f"<SkillRegistry(skills={len(self._skills)})>"


# Global registry instance
_global_registry = SkillRegistry()


def get_global_registry() -> SkillRegistry:
    """Get the global skill registry instance"""
    return _global_registry


class SkillCatalog:
    """Configuration-based skill catalog for agent framework.

    The catalog maintains skill configurations, metadata,
    and references to their implementations or templates.
    This is separate from SkillRegistry which manages BaseSkill classes.

    Attributes:
        skills: Dictionary mapping skill_id to skill configuration
        categories: Dictionary organizing skills by category

    Example:
        >>> catalog = SkillCatalog()
        >>> catalog.register(
        ...     skill_id="skill_nlp_001",
        ...     skill_config={"name": "TextAnalyzer", "category": "nlp"}
        ... )
        >>> skill = catalog.get("skill_nlp_001")
    """

    def __init__(self):
        """Initialize an empty skill catalog."""
        self._skills: Dict[str, Dict[str, Any]] = {}
        self._categories: Dict[str, List[str]] = {}
        self._executors: Dict[str, Callable] = {}

    def register(
        self,
        skill_id: str,
        skill_config: Dict[str, Any],
        executor: Optional[Callable] = None
    ) -> None:
        """Register a skill with the catalog.

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
            >>> catalog = SkillCatalog()
            >>> config = {
            ...     "name": "TextAnalyzer",
            ...     "description": "Analyzes text",
            ...     "category": "nlp"
            ... }
            >>> catalog.register("skill_nlp_001", config)
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
        """Remove a skill from the catalog.

        Args:
            skill_id: Skill identifier to remove

        Raises:
            KeyError: If skill_id doesn't exist
        """
        if skill_id not in self._skills:
            raise KeyError(f"Skill '{skill_id}' not found in catalog")

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
            >>> catalog = SkillCatalog()
            >>> config = catalog.get("skill_nlp_001")
        """
        return self._skills.get(skill_id)

    def get_executor(self, skill_id: str) -> Optional[Callable]:
        """Retrieve a skill's executor function.

        Args:
            skill_id: Skill identifier

        Returns:
            Executor callable, or None if not registered

        Example:
            >>> executor = catalog.get_executor("skill_nlp_001")
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
            >>> result = catalog.execute(
            ...     "skill_nlp_001",
            ...     text="Hello world"
            ... )
        """
        if skill_id not in self._skills:
            raise KeyError(f"Skill '{skill_id}' not found in catalog")

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
            >>> all_skills = catalog.list_skills()
            >>> # List NLP skills
            >>> nlp_skills = catalog.list_skills(category="nlp")
            >>> # List skills with 'analysis' tag
            >>> analysis_skills = catalog.list_skills(tag="analysis")
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
            >>> categories = catalog.list_categories()
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
            >>> results = catalog.search("text analysis")
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
            >>> deps = catalog.get_dependencies("skill_advanced_001")
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
            >>> is_valid, missing = catalog.validate_dependencies("skill_001")
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
            >>> count = catalog.get_skill_count()
            >>> print(f"Total skills: {count}")
        """
        return len(self._skills)

    def clear(self) -> None:
        """Remove all skills from the catalog.

        Example:
            >>> catalog.clear()
        """
        self._skills.clear()
        self._categories.clear()
        self._executors.clear()
        logger.info("Cleared all skills from catalog")

    def export_catalog(self) -> Dict[str, Any]:
        """Export the complete skill catalog.

        Returns:
            Dictionary containing all skills and metadata

        Example:
            >>> catalog_data = catalog.export_catalog()
            >>> import json
            >>> with open('catalog.json', 'w') as f:
            ...     json.dump(catalog_data, f)
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
        """String representation of the catalog."""
        return (
            f"SkillCatalog(skills={len(self._skills)}, "
            f"categories={len(self._categories)})"
        )
