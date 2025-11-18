"""Metadata management utilities for agents and skills.

This module provides functionality for loading, saving, and managing
metadata for agent and skill configurations.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class MetadataManager:
    """Manages metadata for agents and skills.

    Handles loading, saving, and querying metadata from YAML/JSON files,
    with support for caching and batch operations.

    Attributes:
        metadata_dir: Directory containing metadata files
        cache: In-memory cache of loaded metadata

    Example:
        >>> manager = MetadataManager("metadata/")
        >>> agent_meta = manager.get_agent_metadata("agent_001")
        >>> skill_meta = manager.get_skill_metadata("skill_nlp_001")
    """

    def __init__(self, metadata_dir: Optional[str] = None):
        """Initialize the metadata manager.

        Args:
            metadata_dir: Path to directory containing metadata files.
                         Defaults to 'metadata' in current directory.
        """
        if metadata_dir is None:
            metadata_dir = "metadata"

        self.metadata_dir = Path(metadata_dir)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.metadata_dir / "agents").mkdir(exist_ok=True)
        (self.metadata_dir / "skills").mkdir(exist_ok=True)

        # In-memory cache
        self.cache: Dict[str, Dict[str, Any]] = {
            'agents': {},
            'skills': {}
        }

    def get_agent_metadata(
        self,
        agent_id: str,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a specific agent.

        Args:
            agent_id: Agent identifier
            use_cache: If True, use cached metadata if available

        Returns:
            Agent metadata dictionary, or None if not found

        Example:
            >>> manager = MetadataManager()
            >>> metadata = manager.get_agent_metadata("agent_research_v1")
        """
        # Check cache first
        if use_cache and agent_id in self.cache['agents']:
            return self.cache['agents'][agent_id]

        # Try to load from file
        agent_file = self.metadata_dir / "agents" / f"{agent_id}.yaml"

        if not agent_file.exists():
            # Try JSON format
            agent_file = self.metadata_dir / "agents" / f"{agent_id}.json"

        if agent_file.exists():
            metadata = self._load_file(agent_file)
            # Cache it
            self.cache['agents'][agent_id] = metadata
            return metadata

        return None

    def get_skill_metadata(
        self,
        skill_id: str,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for a specific skill.

        Args:
            skill_id: Skill identifier
            use_cache: If True, use cached metadata if available

        Returns:
            Skill metadata dictionary, or None if not found

        Example:
            >>> manager = MetadataManager()
            >>> metadata = manager.get_skill_metadata("skill_nlp_textanalyzer_001")
        """
        # Check cache first
        if use_cache and skill_id in self.cache['skills']:
            return self.cache['skills'][skill_id]

        # Try to load from file
        skill_file = self.metadata_dir / "skills" / f"{skill_id}.yaml"

        if not skill_file.exists():
            # Try JSON format
            skill_file = self.metadata_dir / "skills" / f"{skill_id}.json"

        if skill_file.exists():
            metadata = self._load_file(skill_file)
            # Cache it
            self.cache['skills'][skill_id] = metadata
            return metadata

        return None

    def save_agent_metadata(
        self,
        agent_id: str,
        metadata: Dict[str, Any],
        format: str = 'yaml'
    ) -> str:
        """Save agent metadata to file.

        Args:
            agent_id: Agent identifier
            metadata: Metadata dictionary
            format: Output format ('yaml' or 'json')

        Returns:
            Path to saved file

        Example:
            >>> manager = MetadataManager()
            >>> metadata = {"id": "agent_001", "name": "TestAgent"}
            >>> path = manager.save_agent_metadata("agent_001", metadata)
        """
        ext = 'yaml' if format == 'yaml' else 'json'
        output_file = self.metadata_dir / "agents" / f"{agent_id}.{ext}"

        self._save_file(output_file, metadata, format)

        # Update cache
        self.cache['agents'][agent_id] = metadata

        return str(output_file)

    def save_skill_metadata(
        self,
        skill_id: str,
        metadata: Dict[str, Any],
        format: str = 'yaml'
    ) -> str:
        """Save skill metadata to file.

        Args:
            skill_id: Skill identifier
            metadata: Metadata dictionary
            format: Output format ('yaml' or 'json')

        Returns:
            Path to saved file

        Example:
            >>> manager = MetadataManager()
            >>> metadata = {"skill_id": "skill_001", "name": "TestSkill"}
            >>> path = manager.save_skill_metadata("skill_001", metadata)
        """
        ext = 'yaml' if format == 'yaml' else 'json'
        output_file = self.metadata_dir / "skills" / f"{skill_id}.{ext}"

        self._save_file(output_file, metadata, format)

        # Update cache
        self.cache['skills'][skill_id] = metadata

        return str(output_file)

    def list_agents(self) -> List[str]:
        """List all available agent IDs.

        Returns:
            List of agent IDs

        Example:
            >>> manager = MetadataManager()
            >>> agents = manager.list_agents()
            >>> print(f"Found {len(agents)} agents")
        """
        agents_dir = self.metadata_dir / "agents"
        agent_ids = []

        for file_path in agents_dir.glob("*.yaml"):
            agent_ids.append(file_path.stem)

        for file_path in agents_dir.glob("*.json"):
            if file_path.stem not in agent_ids:
                agent_ids.append(file_path.stem)

        return sorted(agent_ids)

    def list_skills(self, category: Optional[str] = None) -> List[str]:
        """List all available skill IDs, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of skill IDs

        Example:
            >>> manager = MetadataManager()
            >>> nlp_skills = manager.list_skills(category="nlp")
        """
        skills_dir = self.metadata_dir / "skills"
        skill_ids = []

        for file_path in skills_dir.glob("*.yaml"):
            skill_id = file_path.stem

            # Filter by category if specified
            if category:
                metadata = self.get_skill_metadata(skill_id)
                if metadata and metadata.get('category') == category:
                    skill_ids.append(skill_id)
            else:
                skill_ids.append(skill_id)

        for file_path in skills_dir.glob("*.json"):
            skill_id = file_path.stem
            if skill_id in skill_ids:
                continue

            # Filter by category if specified
            if category:
                metadata = self.get_skill_metadata(skill_id)
                if metadata and metadata.get('category') == category:
                    skill_ids.append(skill_id)
            else:
                skill_ids.append(skill_id)

        return sorted(skill_ids)

    def search_skills(
        self,
        query: str,
        search_fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search skills by keyword in specified fields.

        Args:
            query: Search query string
            search_fields: Fields to search in (default: ['name', 'description', 'tags'])

        Returns:
            List of matching skill metadata dictionaries

        Example:
            >>> manager = MetadataManager()
            >>> results = manager.search_skills("text analysis")
        """
        if search_fields is None:
            search_fields = ['name', 'description', 'tags']

        query_lower = query.lower()
        results = []

        for skill_id in self.list_skills():
            metadata = self.get_skill_metadata(skill_id)
            if not metadata:
                continue

            # Search in specified fields
            for field in search_fields:
                value = metadata.get(field, '')

                # Handle different field types
                if isinstance(value, str):
                    if query_lower in value.lower():
                        results.append(metadata)
                        break
                elif isinstance(value, list):
                    # For tags and other lists
                    if any(query_lower in str(item).lower() for item in value):
                        results.append(metadata)
                        break
                elif isinstance(value, dict):
                    # For nested metadata
                    tags = value.get('tags', [])
                    if any(query_lower in str(tag).lower() for tag in tags):
                        results.append(metadata)
                        break

        return results

    def validate_skill_references(
        self,
        agent_metadata: Dict[str, Any]
    ) -> List[str]:
        """Validate that all skill references in agent metadata exist.

        Args:
            agent_metadata: Agent metadata dictionary

        Returns:
            List of invalid skill_ids (empty if all valid)

        Example:
            >>> manager = MetadataManager()
            >>> agent_meta = {"skills": ["skill_001", "skill_999"]}
            >>> invalid = manager.validate_skill_references(agent_meta)
        """
        available_skills = set(self.list_skills())
        agent_skills = agent_metadata.get('skills', [])

        invalid_skills = [
            skill_id for skill_id in agent_skills
            if skill_id not in available_skills
        ]

        return invalid_skills

    def clear_cache(self) -> None:
        """Clear the metadata cache."""
        self.cache = {
            'agents': {},
            'skills': {}
        }

    @staticmethod
    def _load_file(file_path: Path) -> Dict[str, Any]:
        """Load metadata from YAML or JSON file.

        Args:
            file_path: Path to file

        Returns:
            Loaded metadata dictionary
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix == '.json':
                return json.load(f)
            else:
                return yaml.safe_load(f)

    @staticmethod
    def _save_file(
        file_path: Path,
        data: Dict[str, Any],
        format: str = 'yaml'
    ) -> None:
        """Save metadata to YAML or JSON file.

        Args:
            file_path: Path to file
            data: Data to save
            format: Output format ('yaml' or 'json')
        """
        # Convert datetime objects to strings
        serializable_data = MetadataManager._make_serializable(data)

        with open(file_path, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(serializable_data, f, indent=2)
            else:
                yaml.dump(
                    serializable_data,
                    f,
                    default_flow_style=False,
                    sort_keys=False
                )

    @staticmethod
    def _make_serializable(obj: Any) -> Any:
        """Convert object to JSON/YAML serializable format.

        Args:
            obj: Object to convert

        Returns:
            Serializable version of object
        """
        if isinstance(obj, datetime):
            return obj.isoformat() + 'Z'
        elif isinstance(obj, dict):
            return {k: MetadataManager._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [MetadataManager._make_serializable(item) for item in obj]
        else:
            return obj
