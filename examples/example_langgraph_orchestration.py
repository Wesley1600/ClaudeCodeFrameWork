"""
Example: LangGraph Agent Orchestration

This example demonstrates how to use the LangGraph orchestration framework
to create complex multi-agent and multi-skill workflows.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, AgentConfig
from skills.base_skill import BaseSkill, SkillContext, SkillMetadata
from langgraph_orchestration import (
    LangGraphAgentOrchestrator,
    GraphBuilder,
    AgentNode,
    SkillNode,
    RouterNode,
    ToolNode,
    StateManager,
    WorkflowState,
    MessageRole
)


# Example 1: Simple Skill Definition
class GreetingSkill(BaseSkill):
    """Simple skill that generates greetings."""

    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="greeting_skill",
            description="Generates personalized greetings",
            version="1.0.0",
            tags=["nlp", "generation"]
        )

    def execute(self, context: SkillContext, **kwargs) -> str:
        name = kwargs.get("input", "there")
        return f"Hello, {name}! Welcome to the LangGraph orchestration framework."


class SummarizationSkill(BaseSkill):
    """Skill that creates summaries."""

    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="summarization_skill",
            description="Creates concise summaries of text",
            version="1.0.0",
            tags=["nlp", "summarization"]
        )

    def execute(self, context: SkillContext, **kwargs) -> str:
        text = kwargs.get("input", "")
        # Simple summarization (in real implementation, use LLM)
        words = text.split()[:10]  # Take first 10 words
        return f"Summary: {' '.join(words)}..."


class AnalysisSkill(BaseSkill):
    """Skill that performs analysis."""

    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="analysis_skill",
            description="Analyzes text for insights",
            version="1.0.0",
            tags=["analysis", "nlp"]
        )

    def execute(self, context: SkillContext, **kwargs) -> dict:
        text = kwargs.get("input", "")
        # Simple analysis
        return {
            "word_count": len(text.split()),
            "char_count": len(text),
            "has_question": "?" in text,
            "sentiment": "positive"  # Placeholder
        }


# Example 2: Create Agents
def create_research_agent() -> BaseAgent:
    """Create a research agent."""
    config = AgentConfig(
        id="research_agent_001",
        name="Research Agent",
        version="1.0.0",
        description="Performs research and gathers information",
        skills=["greeting_skill", "analysis_skill"],
        metadata={"type": "research", "domain": "general"}
    )
    return BaseAgent(config)


def create_writer_agent() -> BaseAgent:
    """Create a writer agent."""
    config = AgentConfig(
        id="writer_agent_001",
        name="Writer Agent",
        version="1.0.0",
        description="Creates written content",
        skills=["greeting_skill", "summarization_skill"],
        metadata={"type": "writer", "style": "professional"}
    )
    return BaseAgent(config)


# Example 3: Simple Sequential Workflow
def example_sequential_workflow():
    """Demonstrate a simple sequential workflow of skills."""
    print("\n" + "=" * 60)
    print("Example 1: Sequential Skill Workflow")
    print("=" * 60)

    # Create orchestrator
    orchestrator = LangGraphAgentOrchestrator(name="demo_orchestrator")

    # Register skills
    orchestrator.register_skill(GreetingSkill())
    orchestrator.register_skill(SummarizationSkill())
    orchestrator.register_skill(AnalysisSkill())

    # Create workflow
    workflow = orchestrator.create_skill_workflow(
        workflow_name="analyze_and_summarize",
        skill_sequence=["greeting_skill", "analysis_skill", "summarization_skill"]
    )

    # Run workflow
    result = workflow.run(
        initial_input="LangGraph enables powerful agent orchestration with state management and conditional routing!",
        context={"user": "Demo User"}
    )

    # Display results
    print("\nWorkflow completed!")
    print(f"Total messages: {len(result['messages'])}")
    print("\nMessage history:")
    for i, msg in enumerate(result["messages"]):
        print(f"{i+1}. [{msg['role']}]: {msg['content'][:100]}...")

    print(f"\nIntermediate results: {list(result.get('intermediate_results', {}).keys())}")


# Example 4: Agent Workflow
def example_agent_workflow():
    """Demonstrate a workflow with multiple agents."""
    print("\n" + "=" * 60)
    print("Example 2: Multi-Agent Workflow")
    print("=" * 60)

    # Create orchestrator
    orchestrator = LangGraphAgentOrchestrator(name="agent_orchestrator")

    # Create and register agents
    research_agent = create_research_agent()
    writer_agent = create_writer_agent()

    orchestrator.register_agent(research_agent)
    orchestrator.register_agent(writer_agent)

    # Create workflow
    workflow = orchestrator.create_agent_workflow(
        workflow_name="research_and_write",
        agent_sequence=["research_agent_001", "writer_agent_001"]
    )

    # Run workflow
    result = workflow.run(
        initial_input="What are the benefits of agent orchestration?",
        context={"project": "LangGraph Demo"}
    )

    # Display results
    print("\nAgent workflow completed!")
    print(f"Completed agents: {result.get('completed_agents', [])}")
    print(f"\nFinal context: {result.get('context', {})}")


# Example 5: Mixed Workflow (Agents + Skills)
def example_mixed_workflow():
    """Demonstrate a workflow combining agents and skills."""
    print("\n" + "=" * 60)
    print("Example 3: Mixed Agent & Skill Workflow")
    print("=" * 60)

    # Create orchestrator
    orchestrator = LangGraphAgentOrchestrator(name="mixed_orchestrator")

    # Register components
    orchestrator.register_agent(create_research_agent())
    orchestrator.register_skill(GreetingSkill())
    orchestrator.register_skill(AnalysisSkill())
    orchestrator.register_skill(SummarizationSkill())

    # Create mixed workflow
    workflow = orchestrator.create_mixed_workflow(
        workflow_name="comprehensive_pipeline",
        steps=[
            {"type": "skill", "id": "greeting_skill"},
            {"type": "agent", "id": "research_agent_001"},
            {"type": "skill", "id": "analysis_skill"},
            {"type": "skill", "id": "summarization_skill"}
        ]
    )

    # Run workflow
    result = workflow.run(
        initial_input="Agent orchestration frameworks",
        context={"priority": "high"}
    )

    # Display results
    print("\nMixed workflow completed!")
    print(f"Messages: {len(result['messages'])}")
    print(f"Active skills: {result.get('active_skills', [])}")


# Example 6: Custom Graph with Conditional Routing
def example_custom_graph():
    """Demonstrate building a custom graph with conditional routing."""
    print("\n" + "=" * 60)
    print("Example 4: Custom Graph with Conditional Routing")
    print("=" * 60)

    # Create a custom router function
    def route_by_sentiment(state: WorkflowState) -> str:
        """Route based on analysis results."""
        analysis = state.get("intermediate_results", {}).get("analysis_node", {})

        if isinstance(analysis, dict):
            sentiment = analysis.get("sentiment", "neutral")
            if sentiment == "positive":
                return "positive_path"
            elif sentiment == "negative":
                return "negative_path"

        return "neutral_path"

    # Create analysis tool
    def analyze_tool(state: WorkflowState) -> dict:
        latest = StateManager.get_latest_message(state)
        text = latest.content if latest else ""
        return {
            "sentiment": "positive" if "good" in text.lower() else "negative",
            "length": len(text)
        }

    # Build custom graph
    builder = GraphBuilder(name="conditional_workflow")

    # Add analysis node
    builder.add_node(
        "analysis_node",
        ToolNode("analysis_node", analyze_tool, "Analyze input")
    )
    builder.set_entry_point("analysis_node")

    # Add route-specific nodes
    builder.add_node(
        "positive_path",
        ToolNode(
            "positive_path",
            lambda s: "Great! Positive sentiment detected.",
            "Handle positive sentiment"
        )
    )

    builder.add_node(
        "negative_path",
        ToolNode(
            "negative_path",
            lambda s: "Understood. Addressing negative sentiment.",
            "Handle negative sentiment"
        )
    )

    builder.add_node(
        "neutral_path",
        ToolNode(
            "neutral_path",
            lambda s: "Neutral sentiment noted.",
            "Handle neutral sentiment"
        )
    )

    # Add conditional routing
    builder.add_conditional_edges(
        "analysis_node",
        route_by_sentiment,
        {
            "positive_path": "positive_path",
            "negative_path": "negative_path",
            "neutral_path": "neutral_path"
        }
    )

    # Add finish edges
    builder.add_finish_edge("positive_path")
    builder.add_finish_edge("negative_path")
    builder.add_finish_edge("neutral_path")

    # Build and run
    workflow = builder.build()
    result = workflow.run(
        initial_input="This is a good example of orchestration!"
    )

    print("\nConditional workflow completed!")
    print(f"Routing decision: {result.get('routing_decision', 'none')}")
    print(f"Messages: {len(result['messages'])}")


# Example 7: Workflow with State Management
def example_state_management():
    """Demonstrate advanced state management."""
    print("\n" + "=" * 60)
    print("Example 5: Advanced State Management")
    print("=" * 60)

    # Create initial state
    state = StateManager.create_initial_state(
        workflow_id="demo_workflow_001",
        initial_message="Let's track state through this workflow",
        context={"user": "Alice", "session_id": "123"},
        max_loops=5
    )

    print(f"Initial state created:")
    print(f"  Workflow ID: {state['workflow_id']}")
    print(f"  Messages: {len(state['messages'])}")
    print(f"  Context: {state['context']}")

    # Add messages
    state = StateManager.add_message(
        state,
        MessageRole.ASSISTANT,
        "Processing your request...",
        metadata={"step": 1}
    )

    state = StateManager.add_message(
        state,
        MessageRole.TOOL,
        "Analysis complete: 85% confidence",
        metadata={"tool": "analyzer", "confidence": 0.85}
    )

    # Update context
    state = StateManager.update_context(
        state,
        {"analysis_complete": True, "confidence": 0.85}
    )

    # Record agent execution
    state = StateManager.record_agent_execution(
        state,
        "analyzer_agent",
        {"status": "success", "findings": ["key1", "key2"]}
    )

    # Display final state
    print(f"\nFinal state:")
    print(f"  Messages: {len(state['messages'])}")
    print(f"  Context: {state['context']}")
    print(f"  Completed agents: {state['completed_agents']}")
    print(f"  Intermediate results: {list(state['intermediate_results'].keys())}")

    # Get latest message
    latest = StateManager.get_latest_message(state)
    print(f"\nLatest message:")
    print(f"  Role: {latest.role.value}")
    print(f"  Content: {latest.content}")


# Example 8: Streaming Workflow
def example_streaming_workflow():
    """Demonstrate streaming workflow execution."""
    print("\n" + "=" * 60)
    print("Example 6: Streaming Workflow Execution")
    print("=" * 60)

    # Create orchestrator
    orchestrator = LangGraphAgentOrchestrator(name="streaming_demo")

    # Register skills
    orchestrator.register_skill(GreetingSkill())
    orchestrator.register_skill(AnalysisSkill())

    # Create workflow
    workflow = orchestrator.create_skill_workflow(
        workflow_name="streaming_pipeline",
        skill_sequence=["greeting_skill", "analysis_skill"]
    )

    # Stream execution
    print("\nStreaming workflow execution:")
    print("-" * 40)

    for i, chunk in enumerate(workflow.stream(
        initial_input="Streaming example"
    )):
        print(f"\nChunk {i+1}:")
        print(f"  Keys: {list(chunk.keys())}")
        # Display current step
        for key, value in chunk.items():
            if isinstance(value, dict):
                print(f"  {key}: {value.get('current_step', 'N/A')}")

    print("\n" + "-" * 40)
    print("Streaming complete!")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("LangGraph Agent Orchestration Examples")
    print("=" * 60)

    try:
        # Run examples
        example_sequential_workflow()
        example_agent_workflow()
        example_mixed_workflow()
        example_custom_graph()
        example_state_management()
        example_streaming_workflow()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
