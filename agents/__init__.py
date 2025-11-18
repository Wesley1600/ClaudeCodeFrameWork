"""Agent system for the framework."""

from .base_agent import BaseAgent, AgentConfig
from .registry import AgentRegistry

__all__ = [
    'BaseAgent',
    'AgentConfig',
    'AgentRegistry',
]
