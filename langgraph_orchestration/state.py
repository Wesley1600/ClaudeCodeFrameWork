"""
State Management for LangGraph Agent Orchestration

This module defines state classes for managing data flow through
agent workflows in LangGraph.
"""

from typing import TypedDict, Annotated, Sequence, Dict, Any, Optional, List
from operator import add
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class MessageRole(Enum):
    """Message roles in agent conversations."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """Represents a message in an agent conversation."""
    role: MessageRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "role": self.role.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        )


class AgentState(TypedDict):
    """
    Base state for agent workflows.

    This is the fundamental state structure passed between nodes in the graph.
    The 'messages' field uses the add reducer to append new messages.
    """
    messages: Annotated[Sequence[Dict[str, Any]], add]
    current_agent: str
    context: Dict[str, Any]
    intermediate_results: Dict[str, Any]


class WorkflowState(TypedDict):
    """
    Extended state for complex multi-agent workflows.

    Includes additional fields for workflow management, routing,
    and cross-agent communication.
    """
    # Core message flow
    messages: Annotated[Sequence[Dict[str, Any]], add]

    # Workflow metadata
    workflow_id: str
    current_step: str
    previous_step: Optional[str]
    next_step: Optional[str]

    # Agent tracking
    current_agent: str
    agent_stack: List[str]  # Track agent call hierarchy
    completed_agents: List[str]

    # State and context
    context: Dict[str, Any]
    shared_memory: Dict[str, Any]
    intermediate_results: Dict[str, Any]

    # Routing and control
    routing_decision: Optional[str]
    loop_count: int
    max_loops: int

    # Error handling
    errors: List[Dict[str, Any]]
    retry_count: int

    # Skill execution
    active_skills: List[str]
    skill_results: Dict[str, Any]


class MessageState(TypedDict):
    """
    Simple message-based state for conversational agents.

    Minimal state focusing on message history and basic context.
    """
    messages: Annotated[Sequence[Dict[str, Any]], add]
    context: Dict[str, Any]


class StateManager:
    """
    Manages state operations and transitions in agent workflows.

    Provides utilities for state validation, transformation, and persistence.
    """

    @staticmethod
    def create_initial_state(
        workflow_id: str,
        initial_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        max_loops: int = 10
    ) -> WorkflowState:
        """
        Create an initial workflow state.

        Args:
            workflow_id: Unique identifier for the workflow
            initial_message: Optional initial user message
            context: Optional initial context data
            max_loops: Maximum number of workflow loops allowed

        Returns:
            Initialized WorkflowState
        """
        messages = []
        if initial_message:
            msg = Message(
                role=MessageRole.USER,
                content=initial_message
            )
            messages.append(msg.to_dict())

        return WorkflowState(
            messages=messages,
            workflow_id=workflow_id,
            current_step="start",
            previous_step=None,
            next_step=None,
            current_agent="",
            agent_stack=[],
            completed_agents=[],
            context=context or {},
            shared_memory={},
            intermediate_results={},
            routing_decision=None,
            loop_count=0,
            max_loops=max_loops,
            errors=[],
            retry_count=0,
            active_skills=[],
            skill_results={}
        )

    @staticmethod
    def add_message(
        state: WorkflowState,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowState:
        """
        Add a message to the state.

        Args:
            state: Current workflow state
            role: Role of the message sender
            content: Message content
            metadata: Optional metadata

        Returns:
            Updated state
        """
        msg = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )

        # Create a new state with the added message
        new_state = state.copy()
        new_state["messages"] = list(state["messages"]) + [msg.to_dict()]
        return new_state

    @staticmethod
    def update_context(
        state: WorkflowState,
        updates: Dict[str, Any]
    ) -> WorkflowState:
        """
        Update the context in the state.

        Args:
            state: Current workflow state
            updates: Dictionary of context updates

        Returns:
            Updated state
        """
        new_state = state.copy()
        new_state["context"] = {**state["context"], **updates}
        return new_state

    @staticmethod
    def record_agent_execution(
        state: WorkflowState,
        agent_name: str,
        result: Any
    ) -> WorkflowState:
        """
        Record the execution of an agent.

        Args:
            state: Current workflow state
            agent_name: Name of the executed agent
            result: Agent execution result

        Returns:
            Updated state
        """
        new_state = state.copy()
        new_state["completed_agents"] = list(state["completed_agents"]) + [agent_name]
        new_state["intermediate_results"] = {
            **state["intermediate_results"],
            agent_name: result
        }
        return new_state

    @staticmethod
    def record_error(
        state: WorkflowState,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowState:
        """
        Record an error in the state.

        Args:
            state: Current workflow state
            error: Exception that occurred
            context: Optional error context

        Returns:
            Updated state
        """
        error_record = {
            "type": type(error).__name__,
            "message": str(error),
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }

        new_state = state.copy()
        new_state["errors"] = list(state["errors"]) + [error_record]
        new_state["retry_count"] = state["retry_count"] + 1
        return new_state

    @staticmethod
    def should_continue(state: WorkflowState) -> bool:
        """
        Check if the workflow should continue.

        Args:
            state: Current workflow state

        Returns:
            True if workflow should continue, False otherwise
        """
        # Check loop limit
        if state["loop_count"] >= state["max_loops"]:
            return False

        # Check for terminal errors
        if len(state["errors"]) > 5:  # Too many errors
            return False

        return True

    @staticmethod
    def get_latest_message(state: WorkflowState) -> Optional[Message]:
        """
        Get the latest message from the state.

        Args:
            state: Current workflow state

        Returns:
            Latest message or None
        """
        if not state["messages"]:
            return None

        return Message.from_dict(state["messages"][-1])

    @staticmethod
    def get_messages_by_role(
        state: WorkflowState,
        role: MessageRole
    ) -> List[Message]:
        """
        Get all messages with a specific role.

        Args:
            state: Current workflow state
            role: Message role to filter by

        Returns:
            List of messages with the specified role
        """
        return [
            Message.from_dict(msg)
            for msg in state["messages"]
            if msg["role"] == role.value
        ]
