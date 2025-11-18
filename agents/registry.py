"""Agent registry for managing agent instances.

This module provides the AgentRegistry class for registering and managing
agent instances within the framework.
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentConfig
import logging

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Central registry for managing agents.

    Maintains a catalog of registered agents and provides methods for
    agent discovery and access.

    Attributes:
        agents: Dictionary mapping agent_id to agent instance

    Example:
        >>> registry = AgentRegistry()
        >>> config = AgentConfig(
        ...     id="agent_001",
        ...     name="TestAgent",
        ...     version="1.0.0",
        ...     description="Test agent"
        ... )
        >>> agent = BaseAgent(config)
        >>> registry.register(agent)
    """

    def __init__(self):
        """Initialize an empty agent registry."""
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """Register an agent instance.

        Args:
            agent: Agent instance to register

        Raises:
            ValueError: If agent ID already exists

        Example:
            >>> registry = AgentRegistry()
            >>> agent = BaseAgent(config)
            >>> registry.register(agent)
        """
        agent_id = agent.config.id

        if agent_id in self._agents:
            raise ValueError(f"Agent '{agent_id}' is already registered")

        self._agents[agent_id] = agent
        logger.info(f"Registered agent: {agent_id} ({agent.config.name})")

    def unregister(self, agent_id: str) -> None:
        """Remove an agent from the registry.

        Args:
            agent_id: Agent identifier to remove

        Raises:
            KeyError: If agent doesn't exist

        Example:
            >>> registry.unregister("agent_001")
        """
        if agent_id not in self._agents:
            raise KeyError(f"Agent '{agent_id}' not found in registry")

        agent_name = self._agents[agent_id].config.name
        del self._agents[agent_id]
        logger.info(f"Unregistered agent: {agent_id} ({agent_name})")

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """Retrieve an agent by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent instance, or None if not found

        Example:
            >>> agent = registry.get("agent_001")
            >>> if agent:
            ...     info = agent.get_info()
        """
        return self._agents.get(agent_id)

    def list_agents(self) -> List[str]:
        """List all registered agent IDs.

        Returns:
            List of agent IDs

        Example:
            >>> agent_ids = registry.list_agents()
            >>> print(f"Registered agents: {', '.join(agent_ids)}")
        """
        return list(self._agents.keys())

    def search_by_skill(self, skill_id: str) -> List[BaseAgent]:
        """Find all agents that have a specific skill.

        Args:
            skill_id: Skill identifier to search for

        Returns:
            List of agents with the specified skill

        Example:
            >>> agents = registry.search_by_skill("skill_nlp_001")
            >>> print(f"Found {len(agents)} agents with NLP skill")
        """
        matching_agents = []

        for agent in self._agents.values():
            if agent.has_skill(skill_id):
                matching_agents.append(agent)

        return matching_agents

    def search_by_name(self, name_pattern: str) -> List[BaseAgent]:
        """Find agents by name pattern.

        Args:
            name_pattern: Pattern to match in agent name (case-insensitive)

        Returns:
            List of matching agents

        Example:
            >>> agents = registry.search_by_name("Research")
            >>> for agent in agents:
            ...     print(agent.config.name)
        """
        pattern_lower = name_pattern.lower()
        matching_agents = []

        for agent in self._agents.values():
            if pattern_lower in agent.config.name.lower():
                matching_agents.append(agent)

        return matching_agents

    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agent instances.

        Returns:
            List of all agent instances

        Example:
            >>> all_agents = registry.get_all_agents()
            >>> for agent in all_agents:
            ...     print(agent.get_info())
        """
        return list(self._agents.values())

    def get_agent_count(self) -> int:
        """Get total number of registered agents.

        Returns:
            Number of registered agents

        Example:
            >>> count = registry.get_agent_count()
            >>> print(f"Total agents: {count}")
        """
        return len(self._agents)

    def clear(self) -> None:
        """Remove all agents from the registry.

        Example:
            >>> registry.clear()
        """
        self._agents.clear()
        logger.info("Cleared all agents from registry")

    def export_catalog(self) -> Dict[str, Any]:
        """Export catalog of all registered agents.

        Returns:
            Dictionary containing agent information

        Example:
            >>> catalog = registry.export_catalog()
            >>> import json
            >>> with open('agents.json', 'w') as f:
            ...     json.dump(catalog, f)
        """
        catalog = {
            'total_agents': len(self._agents),
            'agents': {}
        }

        for agent_id, agent in self._agents.items():
            catalog['agents'][agent_id] = agent.get_info()

        return catalog

    def __len__(self) -> int:
        """Return number of registered agents."""
        return len(self._agents)

    def __contains__(self, agent_id: str) -> bool:
        """Check if an agent is registered."""
        return agent_id in self._agents

    def __repr__(self) -> str:
        """String representation of the registry."""
        return f"AgentRegistry(agents={len(self._agents)})"
