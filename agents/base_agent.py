"""Base agent class and configuration.

This module provides the foundational agent class that all specialized
agents inherit from, along with the AgentConfig dataclass for configuration.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for an agent.

    Attributes:
        id: Unique agent identifier
        name: Human-readable agent name
        version: Agent version
        description: Agent description
        skills: List of skill_ids the agent can use
        metadata: Additional metadata
        prompt_template: Optional prompt template reference
        parameters: Agent execution parameters
    """

    id: str
    name: str
    version: str
    description: str
    skills: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    prompt_template: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=lambda: {
        'temperature': 0.7,
        'max_tokens': 2000,
        'top_p': 0.9,
    })

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary.

        Returns:
            Dictionary representation of config
        """
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'skills': self.skills,
            'metadata': self.metadata,
            'prompt_template': self.prompt_template,
            'parameters': self.parameters,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfig':
        """Create config from dictionary.

        Args:
            data: Dictionary containing config data

        Returns:
            AgentConfig instance
        """
        return cls(
            id=data['id'],
            name=data['name'],
            version=data['version'],
            description=data['description'],
            skills=data.get('skills', []),
            metadata=data.get('metadata', {}),
            prompt_template=data.get('prompt_template'),
            parameters=data.get('parameters', {}),
        )


class BaseAgent:
    """Base class for all agents in the framework.

    Provides common functionality for agent initialization, skill management,
    and execution. Specialized agents should inherit from this class.

    Attributes:
        config: Agent configuration
        skill_registry: Reference to skill registry (if provided)

    Example:
        >>> config = AgentConfig(
        ...     id="agent_001",
        ...     name="TestAgent",
        ...     version="1.0.0",
        ...     description="A test agent",
        ...     skills=["skill_001", "skill_002"]
        ... )
        >>> agent = BaseAgent(config)
        >>> agent.initialize()
    """

    def __init__(
        self,
        config: AgentConfig,
        skill_registry: Optional[Any] = None
    ):
        """Initialize the agent.

        Args:
            config: Agent configuration
            skill_registry: Optional skill registry for skill access
        """
        self.config = config
        self.skill_registry = skill_registry
        self._initialized = False

        logger.info(
            f"Created agent: {config.name} (ID: {config.id}, "
            f"Version: {config.version})"
        )

    def initialize(self) -> None:
        """Initialize the agent and validate skills.

        Raises:
            ValueError: If required skills are not available
        """
        if self._initialized:
            logger.warning(f"Agent {self.config.id} already initialized")
            return

        # Validate skills if registry is available
        if self.skill_registry:
            missing_skills = []
            for skill_id in self.config.skills:
                if skill_id not in self.skill_registry:
                    missing_skills.append(skill_id)

            if missing_skills:
                raise ValueError(
                    f"Agent {self.config.id} requires skills that are not "
                    f"registered: {', '.join(missing_skills)}"
                )

            logger.info(
                f"Agent {self.config.id} validated {len(self.config.skills)} skills"
            )

        self._initialized = True
        logger.info(f"Agent {self.config.id} initialized successfully")

    def has_skill(self, skill_id: str) -> bool:
        """Check if agent has access to a specific skill.

        Args:
            skill_id: Skill identifier to check

        Returns:
            True if agent has the skill, False otherwise

        Example:
            >>> if agent.has_skill("skill_nlp_001"):
            ...     result = agent.execute_skill("skill_nlp_001", text="...")
        """
        return skill_id in self.config.skills

    def execute_skill(self, skill_id: str, **kwargs) -> Any:
        """Execute a skill with provided arguments.

        Args:
            skill_id: Skill identifier
            **kwargs: Arguments to pass to skill

        Returns:
            Result from skill execution

        Raises:
            ValueError: If agent doesn't have the skill or no registry
            RuntimeError: If agent not initialized

        Example:
            >>> result = agent.execute_skill(
            ...     "skill_nlp_001",
            ...     text="Hello world"
            ... )
        """
        if not self._initialized:
            raise RuntimeError(
                f"Agent {self.config.id} must be initialized before executing skills"
            )

        if not self.has_skill(skill_id):
            raise ValueError(
                f"Agent {self.config.id} does not have skill: {skill_id}"
            )

        if not self.skill_registry:
            raise ValueError(
                "No skill registry available for skill execution"
            )

        logger.debug(f"Agent {self.config.id} executing skill: {skill_id}")
        return self.skill_registry.execute(skill_id, **kwargs)

    def get_available_skills(self) -> List[str]:
        """Get list of skills available to this agent.

        Returns:
            List of skill_ids

        Example:
            >>> skills = agent.get_available_skills()
            >>> print(f"Agent has {len(skills)} skills")
        """
        return self.config.skills.copy()

    def add_skill(self, skill_id: str) -> None:
        """Add a skill to the agent's capabilities.

        Args:
            skill_id: Skill identifier to add

        Raises:
            ValueError: If skill already exists or not in registry

        Example:
            >>> agent.add_skill("skill_new_001")
        """
        if skill_id in self.config.skills:
            raise ValueError(f"Agent already has skill: {skill_id}")

        if self.skill_registry and skill_id not in self.skill_registry:
            raise ValueError(f"Skill not found in registry: {skill_id}")

        self.config.skills.append(skill_id)
        logger.info(f"Added skill {skill_id} to agent {self.config.id}")

    def remove_skill(self, skill_id: str) -> None:
        """Remove a skill from the agent's capabilities.

        Args:
            skill_id: Skill identifier to remove

        Raises:
            ValueError: If skill doesn't exist

        Example:
            >>> agent.remove_skill("skill_old_001")
        """
        if skill_id not in self.config.skills:
            raise ValueError(f"Agent does not have skill: {skill_id}")

        self.config.skills.remove(skill_id)
        logger.info(f"Removed skill {skill_id} from agent {self.config.id}")

    def update_parameters(self, **params) -> None:
        """Update agent execution parameters.

        Args:
            **params: Parameters to update (temperature, max_tokens, etc.)

        Example:
            >>> agent.update_parameters(temperature=0.8, max_tokens=4000)
        """
        self.config.parameters.update(params)
        logger.info(f"Updated parameters for agent {self.config.id}")

    def get_info(self) -> Dict[str, Any]:
        """Get agent information.

        Returns:
            Dictionary with agent details

        Example:
            >>> info = agent.get_info()
            >>> print(f"Agent: {info['name']}, Skills: {len(info['skills'])}")
        """
        return {
            'id': self.config.id,
            'name': self.config.name,
            'version': self.config.version,
            'description': self.config.description,
            'skills': self.config.skills,
            'skill_count': len(self.config.skills),
            'initialized': self._initialized,
            'metadata': self.config.metadata,
        }

    def __repr__(self) -> str:
        """String representation of the agent."""
        return (
            f"BaseAgent(id={self.config.id}, name={self.config.name}, "
            f"skills={len(self.config.skills)})"
        )
