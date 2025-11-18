"""
Skill Registry - Discovery and Management System

Provides automatic skill discovery, registration, and retrieval.
"""

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
import logging

from .base_skill import BaseSkill, SkillMetadata


logger = logging.getLogger(__name__)


class SkillRegistry:
    """
    Central registry for all available skills.

    Provides:
    - Automatic discovery of skills in a directory
    - Manual registration of skill classes
    - Skill instantiation with configuration
    - Querying skills by name, tag, or capability
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
