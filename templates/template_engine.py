"""Template population engine for agents and skills.

This module provides the core template rendering functionality using Jinja2,
allowing dynamic population of agent and skill configurations with metadata.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import yaml

try:
    from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
except ImportError:
    raise ImportError(
        "Jinja2 is required for template population. "
        "Install it with: pip install jinja2"
    )


class TemplateType(Enum):
    """Types of templates supported by the engine."""
    AGENT = "agent"
    SKILL = "skill"
    PROMPT = "prompt"
    CONFIG = "config"


class TemplatePopulator:
    """Main template population engine.

    Handles loading and rendering of Jinja2 templates with metadata,
    ensuring correct field population for agent and skill configurations.

    Attributes:
        template_dir: Directory containing template files
        env: Jinja2 environment for template rendering

    Example:
        >>> populator = TemplatePopulator("templates/")
        >>> metadata = {
        ...     "name": "DataAnalyzer",
        ...     "skill_id": "skill_data_analyzer_001",
        ...     "description": "Analyzes data patterns"
        ... }
        >>> config = populator.populate_skill(metadata)
    """

    def __init__(self, template_dir: Optional[str] = None):
        """Initialize the template populator.

        Args:
            template_dir: Path to directory containing templates.
                         Defaults to 'templates/prompts' in the current directory.
        """
        if template_dir is None:
            # Default to templates/prompts directory
            base_path = Path(__file__).parent
            template_dir = str(base_path / "prompts")

        self.template_dir = Path(template_dir)

        # Create Jinja2 environment with custom settings
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

        # Add custom filters
        self.env.filters['timestamp'] = self._format_timestamp
        self.env.filters['capitalize_first'] = self._capitalize_first

    @staticmethod
    def _format_timestamp(dt: Optional[datetime] = None) -> str:
        """Format datetime as ISO 8601 string."""
        if dt is None:
            dt = datetime.utcnow()
        return dt.isoformat() + 'Z'

    @staticmethod
    def _capitalize_first(text: str) -> str:
        """Capitalize first letter of text."""
        return text[0].upper() + text[1:] if text else text

    def populate(
        self,
        template_name: str,
        metadata: Dict[str, Any],
        template_type: Optional[TemplateType] = None
    ) -> str:
        """Populate a template with provided metadata.

        Args:
            template_name: Name of template file (e.g., 'agent_template.j2')
            metadata: Dictionary containing template variables
            template_type: Optional type hint for template location

        Returns:
            Rendered template as string

        Raises:
            TemplateNotFound: If template file doesn't exist
            ValueError: If required metadata fields are missing
        """
        try:
            # Load and render template
            template = self.env.get_template(template_name)

            # Add default metadata if not provided
            enriched_metadata = self._enrich_metadata(metadata, template_type)

            # Render template
            rendered = template.render(**enriched_metadata)

            return rendered

        except TemplateNotFound as e:
            raise TemplateNotFound(
                f"Template '{template_name}' not found in {self.template_dir}"
            ) from e

    def _enrich_metadata(
        self,
        metadata: Dict[str, Any],
        template_type: Optional[TemplateType]
    ) -> Dict[str, Any]:
        """Enrich metadata with default values.

        Args:
            metadata: Original metadata dictionary
            template_type: Type of template being populated

        Returns:
            Enriched metadata dictionary
        """
        enriched = metadata.copy()

        # Add timestamp if not present
        if 'created_at' not in enriched:
            enriched['created_at'] = datetime.utcnow()

        # Add version if not present
        if 'version' not in enriched:
            enriched['version'] = '1.0.0'

        # Add template type
        if template_type:
            enriched['template_type'] = template_type.value

        return enriched

    def populate_agent(
        self,
        agent_metadata: Dict[str, Any],
        template_name: str = "agent_template.yaml.j2"
    ) -> str:
        """Populate an agent configuration template.

        Args:
            agent_metadata: Agent metadata including:
                - id: Unique agent identifier
                - name: Human-readable agent name
                - description: Agent description
                - skills: List of skill_ids this agent uses
                - metadata: Additional metadata (author, tags, etc.)
            template_name: Name of agent template file

        Returns:
            Populated YAML configuration as string

        Raises:
            ValueError: If required fields are missing

        Example:
            >>> metadata = {
            ...     "id": "agent_001",
            ...     "name": "ResearchAgent",
            ...     "description": "Conducts research tasks",
            ...     "skills": ["skill_search_001", "skill_analyze_001"]
            ... }
            >>> config = populator.populate_agent(metadata)
        """
        required_fields = ['id', 'name', 'description']
        self._validate_required_fields(agent_metadata, required_fields, 'agent')

        return self.populate(
            template_name,
            agent_metadata,
            TemplateType.AGENT
        )

    def populate_skill(
        self,
        skill_metadata: Dict[str, Any],
        template_name: str = "skill_template.yaml.j2"
    ) -> str:
        """Populate a skill configuration template.

        Args:
            skill_metadata: Skill metadata including:
                - skill_id: Unique skill identifier
                - name: Human-readable skill name
                - description: Skill description
                - category: Skill category (e.g., 'data', 'communication')
                - inputs: List of input specifications
                - outputs: List of output specifications
            template_name: Name of skill template file

        Returns:
            Populated YAML configuration as string

        Raises:
            ValueError: If required fields are missing

        Example:
            >>> metadata = {
            ...     "skill_id": "skill_analyzer_001",
            ...     "name": "TextAnalyzer",
            ...     "description": "Analyzes text patterns",
            ...     "category": "nlp"
            ... }
            >>> config = populator.populate_skill(metadata)
        """
        required_fields = ['skill_id', 'name', 'description']
        self._validate_required_fields(skill_metadata, required_fields, 'skill')

        return self.populate(
            template_name,
            skill_metadata,
            TemplateType.SKILL
        )

    def populate_prompt(
        self,
        prompt_metadata: Dict[str, Any],
        template_name: str
    ) -> str:
        """Populate a prompt template.

        Args:
            prompt_metadata: Prompt-specific metadata
            template_name: Name of prompt template file

        Returns:
            Populated prompt as string
        """
        return self.populate(
            template_name,
            prompt_metadata,
            TemplateType.PROMPT
        )

    def save_populated_template(
        self,
        output_path: str,
        populated_content: str
    ) -> None:
        """Save populated template to file.

        Args:
            output_path: Path where populated content should be saved
            populated_content: The rendered template content
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(populated_content)

    def populate_and_save_agent(
        self,
        agent_metadata: Dict[str, Any],
        output_path: str,
        template_name: str = "agent_template.yaml.j2"
    ) -> str:
        """Populate agent template and save to file.

        Args:
            agent_metadata: Agent metadata
            output_path: Where to save the populated config
            template_name: Template file name

        Returns:
            Path to saved file
        """
        content = self.populate_agent(agent_metadata, template_name)
        self.save_populated_template(output_path, content)
        return output_path

    def populate_and_save_skill(
        self,
        skill_metadata: Dict[str, Any],
        output_path: str,
        template_name: str = "skill_template.yaml.j2"
    ) -> str:
        """Populate skill template and save to file.

        Args:
            skill_metadata: Skill metadata
            output_path: Where to save the populated config
            template_name: Template file name

        Returns:
            Path to saved file
        """
        content = self.populate_skill(skill_metadata, template_name)
        self.save_populated_template(output_path, content)
        return output_path

    @staticmethod
    def _validate_required_fields(
        metadata: Dict[str, Any],
        required_fields: List[str],
        entity_type: str
    ) -> None:
        """Validate that required fields are present in metadata.

        Args:
            metadata: Metadata dictionary to validate
            required_fields: List of required field names
            entity_type: Type of entity (for error messages)

        Raises:
            ValueError: If any required field is missing
        """
        missing_fields = [
            field for field in required_fields
            if field not in metadata or not metadata[field]
        ]

        if missing_fields:
            raise ValueError(
                f"Missing required {entity_type} fields: {', '.join(missing_fields)}"
            )

    def list_available_templates(self, subdirectory: Optional[str] = None) -> List[str]:
        """List all available templates in the template directory.

        Args:
            subdirectory: Optional subdirectory to search in

        Returns:
            List of template file names
        """
        search_dir = self.template_dir
        if subdirectory:
            search_dir = search_dir / subdirectory

        if not search_dir.exists():
            return []

        templates = []
        for file_path in search_dir.rglob('*.j2'):
            rel_path = file_path.relative_to(self.template_dir)
            templates.append(str(rel_path))

        return sorted(templates)
