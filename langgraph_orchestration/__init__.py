"""
LangGraph Agent Orchestration Framework

This module provides a stateful, graph-based agent orchestration framework
using LangGraph. It integrates with the existing ClaudeCodeFramework agent
and skill systems to enable complex multi-agent workflows.

Key Features:
- Stateful agent workflows with persistent state management
- Graph-based workflow definition with conditional routing
- Integration with existing BaseAgent and Skill systems
- Support for parallel and sequential agent execution
- Checkpointing and recovery capabilities
- Human-in-the-loop workflows

Components:
- state: State management classes for agent workflows
- nodes: Agent node definitions and execution logic
- graph_builder: Utilities for constructing LangGraph workflows
- integration: Integration layer with existing framework
- checkpoints: State persistence and recovery
"""

from .state import AgentState, WorkflowState, MessageState, StateManager, Message, MessageRole
from .nodes import AgentNode, SkillNode, RouterNode, ToolNode, HumanInputNode, AggregatorNode
from .graph_builder import GraphBuilder, WorkflowGraph
from .integration import LangGraphAgentOrchestrator

__all__ = [
    # State management
    "AgentState",
    "WorkflowState",
    "MessageState",
    "StateManager",
    "Message",
    "MessageRole",

    # Node types
    "AgentNode",
    "SkillNode",
    "RouterNode",
    "ToolNode",
    "HumanInputNode",
    "AggregatorNode",

    # Graph construction
    "GraphBuilder",
    "WorkflowGraph",

    # Orchestrator
    "LangGraphAgentOrchestrator",
]

__version__ = "1.0.0"
