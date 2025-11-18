"""
Agent Pulse - Proactive AI Assistant System

A ChatGPT Pulse-inspired system that proactively analyzes conversations,
conducts research, and delivers personalized updates to help users stay
on top of their tasks, opportunities, and interests.
"""

__version__ = "1.0.0"
__author__ = "Claude Code Framework"

from .core.orchestrator import PulseOrchestrator
from .core.config import PulseConfig
from .agents.conversation_analyzer import ConversationAnalyzer
from .agents.research_agent import ResearchAgent
from .agents.opportunity_finder import OpportunityFinder
from .agents.problem_solver import ProblemSolver
from .storage.memory_store import MemoryStore
from .storage.preferences import PreferenceManager
from .generators.card_generator import UpdateCardGenerator

__all__ = [
    "PulseOrchestrator",
    "PulseConfig",
    "ConversationAnalyzer",
    "ResearchAgent",
    "OpportunityFinder",
    "ProblemSolver",
    "MemoryStore",
    "PreferenceManager",
    "UpdateCardGenerator",
]
