"""
Unit tests for LangGraph Agent Orchestration Framework
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_orchestration import (
    LangGraphAgentOrchestrator,
    GraphBuilder,
    AgentNode,
    SkillNode,
    ToolNode,
    RouterNode,
    StateManager,
    WorkflowState,
    MessageRole,
    Message
)
from agents.base_agent import BaseAgent, AgentConfig
from skills.base_skill import BaseSkill, SkillContext, SkillMetadata


# Test Fixtures

class TestSkill(BaseSkill):
    """Simple test skill."""

    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="test_skill",
            description="Test skill for unit tests"
        )

    def execute(self, context: SkillContext, **kwargs) -> str:
        input_data = kwargs.get("input", "")
        return f"Processed: {input_data}"


class ErrorSkill(BaseSkill):
    """Skill that raises an error."""

    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="error_skill",
            description="Skill that raises an error"
        )

    def execute(self, context: SkillContext, **kwargs) -> str:
        raise ValueError("Test error")


def create_test_agent(agent_id="test_agent_001"):
    """Create a test agent."""
    config = AgentConfig(
        id=agent_id,
        name="Test Agent",
        version="1.0.0",
        description="Test agent for unit tests",
        skills=["test_skill"]
    )
    return BaseAgent(config)


# Tests for StateManager

class TestStateManager:
    """Test StateManager functionality."""

    def test_create_initial_state(self):
        """Test initial state creation."""
        state = StateManager.create_initial_state(
            workflow_id="test_001",
            initial_message="Hello",
            context={"key": "value"},
            max_loops=5
        )

        assert state["workflow_id"] == "test_001"
        assert len(state["messages"]) == 1
        assert state["messages"][0]["content"] == "Hello"
        assert state["context"]["key"] == "value"
        assert state["max_loops"] == 5
        assert state["loop_count"] == 0

    def test_add_message(self):
        """Test adding messages to state."""
        state = StateManager.create_initial_state(workflow_id="test_002")

        state = StateManager.add_message(
            state,
            MessageRole.ASSISTANT,
            "Response message",
            metadata={"test": True}
        )

        assert len(state["messages"]) == 1
        assert state["messages"][0]["role"] == "assistant"
        assert state["messages"][0]["content"] == "Response message"
        assert state["messages"][0]["metadata"]["test"] is True

    def test_update_context(self):
        """Test updating context."""
        state = StateManager.create_initial_state(
            workflow_id="test_003",
            context={"a": 1}
        )

        state = StateManager.update_context(state, {"b": 2, "c": 3})

        assert state["context"]["a"] == 1
        assert state["context"]["b"] == 2
        assert state["context"]["c"] == 3

    def test_record_agent_execution(self):
        """Test recording agent execution."""
        state = StateManager.create_initial_state(workflow_id="test_004")

        state = StateManager.record_agent_execution(
            state,
            "test_agent",
            {"result": "success"}
        )

        assert "test_agent" in state["completed_agents"]
        assert state["intermediate_results"]["test_agent"]["result"] == "success"

    def test_record_error(self):
        """Test error recording."""
        state = StateManager.create_initial_state(workflow_id="test_005")

        error = ValueError("Test error")
        state = StateManager.record_error(state, error, {"node": "test"})

        assert len(state["errors"]) == 1
        assert state["errors"][0]["type"] == "ValueError"
        assert state["errors"][0]["message"] == "Test error"
        assert state["retry_count"] == 1

    def test_get_latest_message(self):
        """Test getting latest message."""
        state = StateManager.create_initial_state(
            workflow_id="test_006",
            initial_message="First"
        )

        state = StateManager.add_message(state, MessageRole.ASSISTANT, "Second")
        state = StateManager.add_message(state, MessageRole.USER, "Third")

        latest = StateManager.get_latest_message(state)
        assert latest is not None
        assert latest.content == "Third"
        assert latest.role == MessageRole.USER

    def test_get_messages_by_role(self):
        """Test filtering messages by role."""
        state = StateManager.create_initial_state(workflow_id="test_007")

        state = StateManager.add_message(state, MessageRole.USER, "User 1")
        state = StateManager.add_message(state, MessageRole.ASSISTANT, "Assistant 1")
        state = StateManager.add_message(state, MessageRole.USER, "User 2")

        user_messages = StateManager.get_messages_by_role(state, MessageRole.USER)
        assert len(user_messages) == 2
        assert user_messages[0].content == "User 1"
        assert user_messages[1].content == "User 2"


# Tests for Nodes

class TestNodes:
    """Test node functionality."""

    def test_tool_node(self):
        """Test ToolNode execution."""
        def test_function(state):
            return "Tool executed"

        node = ToolNode("test_tool", test_function, "Test tool")
        state = StateManager.create_initial_state(workflow_id="test_008")

        result = node(state)

        assert "test_tool" in result["intermediate_results"]
        assert result["intermediate_results"]["test_tool"] == "Tool executed"

    def test_skill_node(self):
        """Test SkillNode with BaseSkill."""
        skill = TestSkill()
        node = SkillNode(
            "test_skill_node",
            lambda: skill,
            "Test skill node"
        )

        state = StateManager.create_initial_state(
            workflow_id="test_009",
            initial_message="test input"
        )

        result = node(state)

        assert "test_skill_node" in result["active_skills"]
        assert "test_skill_node" in result["skill_results"]


# Tests for GraphBuilder

class TestGraphBuilder:
    """Test GraphBuilder functionality."""

    def test_add_node(self):
        """Test adding nodes to graph."""
        builder = GraphBuilder("test_graph")

        def node_fn(state):
            return state

        builder.add_node("node1", ToolNode("node1", node_fn))

        assert "node1" in builder.nodes

    def test_simple_chain(self):
        """Test building a simple sequential chain."""
        def node1_fn(state):
            return state

        def node2_fn(state):
            return state

        builder = GraphBuilder("chain_test")
        builder.add_node("node1", ToolNode("node1", node1_fn))
        builder.add_node("node2", ToolNode("node2", node2_fn))
        builder.add_edge("node1", "node2")
        builder.set_entry_point("node1")
        builder.add_finish_edge("node2")

        workflow = builder.build()
        assert workflow is not None
        assert workflow.name == "chain_test"


# Tests for LangGraphAgentOrchestrator

class TestLangGraphAgentOrchestrator:
    """Test LangGraphAgentOrchestrator functionality."""

    def test_register_agent(self):
        """Test agent registration."""
        orchestrator = LangGraphAgentOrchestrator()
        agent = create_test_agent()

        orchestrator.register_agent(agent)

        assert agent.config.id in orchestrator.agents
        assert orchestrator.list_agents() == [agent.config.id]

    def test_register_skill(self):
        """Test skill registration."""
        orchestrator = LangGraphAgentOrchestrator()
        skill = TestSkill()

        orchestrator.register_skill(skill)

        assert skill.name in orchestrator.skills
        assert orchestrator.list_skills() == [skill.name]

    def test_create_skill_workflow(self):
        """Test creating skill workflow."""
        orchestrator = LangGraphAgentOrchestrator()
        skill1 = TestSkill()

        orchestrator.register_skill(skill1, "skill1")

        workflow = orchestrator.create_skill_workflow(
            workflow_name="test_workflow",
            skill_sequence=["skill1"]
        )

        assert workflow is not None
        assert "test_workflow" in orchestrator.workflows
        assert orchestrator.list_workflows() == ["test_workflow"]

    def test_get_workflow(self):
        """Test retrieving workflow."""
        orchestrator = LangGraphAgentOrchestrator()
        skill = TestSkill()

        orchestrator.register_skill(skill, "skill1")
        workflow = orchestrator.create_skill_workflow(
            "my_workflow",
            ["skill1"]
        )

        retrieved = orchestrator.get_workflow("my_workflow")
        assert retrieved is workflow


# Tests for Message

class TestMessage:
    """Test Message class."""

    def test_message_creation(self):
        """Test creating a message."""
        msg = Message(
            role=MessageRole.USER,
            content="Test message",
            metadata={"key": "value"}
        )

        assert msg.role == MessageRole.USER
        assert msg.content == "Test message"
        assert msg.metadata["key"] == "value"

    def test_message_to_dict(self):
        """Test message serialization."""
        msg = Message(
            role=MessageRole.ASSISTANT,
            content="Response"
        )

        data = msg.to_dict()

        assert data["role"] == "assistant"
        assert data["content"] == "Response"
        assert "timestamp" in data

    def test_message_from_dict(self):
        """Test message deserialization."""
        data = {
            "role": "user",
            "content": "Test",
            "metadata": {},
            "timestamp": "2024-01-01T00:00:00"
        }

        msg = Message.from_dict(data)

        assert msg.role == MessageRole.USER
        assert msg.content == "Test"


# Integration Tests

class TestIntegration:
    """Integration tests for the full framework."""

    def test_end_to_end_skill_workflow(self):
        """Test complete skill workflow execution."""
        orchestrator = LangGraphAgentOrchestrator()

        # Register multiple skills
        skill1 = TestSkill()
        orchestrator.register_skill(skill1, "skill1")

        # Create workflow
        workflow = orchestrator.create_skill_workflow(
            workflow_name="e2e_test",
            skill_sequence=["skill1"]
        )

        # Run workflow
        result = workflow.run(
            initial_input="test input",
            context={"test": True}
        )

        # Verify results
        assert result is not None
        assert result["workflow_id"].startswith("e2e_test")
        assert result["context"]["test"] is True
        assert len(result["messages"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
