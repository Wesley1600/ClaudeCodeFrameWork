# LangGraph Agent Orchestration Framework

A powerful, stateful agent orchestration framework built on LangGraph, seamlessly integrated with the ClaudeCodeFramework's BaseAgent and BaseSkill systems.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Core Concepts](#core-concepts)
6. [Architecture](#architecture)
7. [Usage Examples](#usage-examples)
8. [API Reference](#api-reference)
9. [Best Practices](#best-practices)
10. [Advanced Topics](#advanced-topics)

## Overview

The LangGraph Orchestration Framework provides a sophisticated system for building complex, stateful workflows with multiple agents and skills. It combines the power of LangGraph's state management and graph-based execution with the modularity of the existing agent and skill framework.

### Key Benefits

- **Stateful Workflows**: Maintain context and state across multiple agent interactions
- **Graph-Based Execution**: Define complex workflows with conditional routing and parallel execution
- **Seamless Integration**: Works directly with existing BaseAgent and BaseSkill implementations
- **Checkpointing**: Save and resume workflows at any point
- **Streaming Support**: Stream workflow execution for real-time monitoring
- **Type Safety**: Fully typed state management with TypedDict

## Features

### State Management
- Typed state with WorkflowState, AgentState, and MessageState
- Automatic message accumulation with role-based organization
- Context sharing across agents and skills
- Error tracking and recovery

### Node Types
- **AgentNode**: Execute BaseAgent instances
- **SkillNode**: Execute BaseSkill instances
- **RouterNode**: Conditional routing based on state
- **ToolNode**: Execute arbitrary functions
- **HumanInputNode**: Request human-in-the-loop input
- **AggregatorNode**: Combine results from parallel paths

### Graph Construction
- **GraphBuilder**: Fluent API for building workflows
- **Conditional Edges**: Route based on state conditions
- **Sequential Chains**: Simple linear workflows
- **Parallel Execution**: Execute multiple paths simultaneously
- **Loops and Cycles**: Implement iterative workflows

### Integration Layer
- **LangGraphAgentOrchestrator**: High-level orchestration API
- **FrameworkAgentNode**: Wraps BaseAgent for LangGraph
- **FrameworkSkillNode**: Wraps BaseSkill for LangGraph
- Automatic skill registry integration

## Installation

The framework is already installed as part of the setup:

```bash
pip install langgraph langchain langchain-core langchain-community
```

Dependencies are listed in `requirements.txt`:
- langgraph>=0.2.0
- langchain>=0.3.0
- langchain-core>=0.3.0
- langchain-community>=0.3.0

## Quick Start

### 1. Simple Skill Workflow

```python
from langgraph_orchestration import LangGraphAgentOrchestrator
from skills.base_skill import BaseSkill, SkillContext, SkillMetadata

# Define a skill
class GreetingSkill(BaseSkill):
    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="greeting",
            description="Generates greetings"
        )

    def execute(self, context: SkillContext, **kwargs) -> str:
        name = kwargs.get("input", "there")
        return f"Hello, {name}!"

# Create orchestrator
orchestrator = LangGraphAgentOrchestrator()

# Register skill
orchestrator.register_skill(GreetingSkill())

# Create workflow
workflow = orchestrator.create_skill_workflow(
    workflow_name="greeting_flow",
    skill_sequence=["greeting"]
)

# Run workflow
result = workflow.run(initial_input="World")
print(result["messages"][-1]["content"])  # "Hello, World!"
```

### 2. Multi-Agent Workflow

```python
from agents.base_agent import BaseAgent, AgentConfig

# Create agents
research_agent = BaseAgent(AgentConfig(
    id="research_001",
    name="Research Agent",
    version="1.0.0",
    description="Researches topics",
    skills=["search_skill", "summarize_skill"]
))

writer_agent = BaseAgent(AgentConfig(
    id="writer_001",
    name="Writer Agent",
    version="1.0.0",
    description="Writes content",
    skills=["writing_skill"]
))

# Register and create workflow
orchestrator = LangGraphAgentOrchestrator()
orchestrator.register_agent(research_agent)
orchestrator.register_agent(writer_agent)

workflow = orchestrator.create_agent_workflow(
    workflow_name="research_and_write",
    agent_sequence=["research_001", "writer_001"]
)

# Execute
result = workflow.run(initial_input="Write about quantum computing")
```

### 3. Custom Graph with Conditional Routing

```python
from langgraph_orchestration import GraphBuilder, ToolNode, RouterNode

def analyze(state):
    # Analysis logic
    return {"sentiment": "positive"}

def route_by_sentiment(state):
    sentiment = state["routing_decision"]
    return "positive_handler" if sentiment == "positive" else "negative_handler"

# Build graph
builder = GraphBuilder("conditional_flow")
builder.add_node("analyzer", ToolNode("analyzer", analyze))
builder.add_node("positive_handler", ToolNode("pos", lambda s: "Great!"))
builder.add_node("negative_handler", ToolNode("neg", lambda s: "Noted."))

builder.set_entry_point("analyzer")
builder.add_conditional_edges("analyzer", route_by_sentiment)
builder.add_finish_edge("positive_handler")
builder.add_finish_edge("negative_handler")

workflow = builder.build()
result = workflow.run(initial_input="I love this!")
```

## Core Concepts

### State

State is the central data structure that flows through the workflow. Three state types are available:

#### WorkflowState
The most comprehensive state for complex workflows:

```python
class WorkflowState(TypedDict):
    messages: Annotated[Sequence[Dict[str, Any]], add]  # Message history
    workflow_id: str                                     # Unique workflow ID
    current_step: str                                    # Current node
    current_agent: str                                   # Active agent
    context: Dict[str, Any]                             # Workflow context
    shared_memory: Dict[str, Any]                       # Cross-node memory
    intermediate_results: Dict[str, Any]                # Node results
    routing_decision: Optional[str]                     # Next route
    errors: List[Dict[str, Any]]                        # Error log
    # ... and more
```

#### AgentState
Simplified state for agent-focused workflows:

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[Dict[str, Any]], add]
    current_agent: str
    context: Dict[str, Any]
    intermediate_results: Dict[str, Any]
```

#### MessageState
Minimal state for conversational flows:

```python
class MessageState(TypedDict):
    messages: Annotated[Sequence[Dict[str, Any]], add]
    context: Dict[str, Any]
```

### Nodes

Nodes are the functional units that process state. Each node:
- Receives the current state
- Performs operations
- Returns updated state

Available node types:
- `AgentNode`: Executes agents
- `SkillNode`: Executes skills
- `RouterNode`: Routes based on conditions
- `ToolNode`: Executes custom functions
- `HumanInputNode`: Requests human input
- `AggregatorNode`: Combines parallel results

### Graphs

Graphs define the workflow structure:
- **Nodes**: Processing units
- **Edges**: Connections between nodes
- **Conditional Edges**: Dynamic routing
- **Entry Point**: Starting node
- **END**: Terminal state

### Messages

Messages track communication flow:

```python
@dataclass
class Message:
    role: MessageRole  # SYSTEM, USER, ASSISTANT, TOOL
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
```

## Architecture

### Component Hierarchy

```
LangGraphAgentOrchestrator
    ├── Registered Agents (BaseAgent)
    ├── Registered Skills (BaseSkill)
    └── Workflows (WorkflowGraph)
            ├── Compiled Graph
            ├── Nodes
            │   ├── FrameworkAgentNode
            │   ├── FrameworkSkillNode
            │   ├── RouterNode
            │   └── ToolNode
            └── Checkpointer
```

### Execution Flow

1. **Initialize**: Create orchestrator and register components
2. **Define**: Build workflow graph with nodes and edges
3. **Compile**: Build the graph into executable workflow
4. **Execute**: Run with initial state
5. **Stream**: Optionally stream execution steps
6. **Checkpoint**: Save state for resumption

## Usage Examples

### Example 1: Sequential Skill Pipeline

```python
# Create data processing pipeline
orchestrator = LangGraphAgentOrchestrator()

# Register skills
orchestrator.register_skill(ExtractSkill())
orchestrator.register_skill(TransformSkill())
orchestrator.register_skill(LoadSkill())

# Create ETL workflow
workflow = orchestrator.create_skill_workflow(
    workflow_name="etl_pipeline",
    skill_sequence=["extract", "transform", "load"]
)

# Execute
result = workflow.run(
    initial_input="data.csv",
    context={"database": "postgres://localhost/mydb"}
)
```

### Example 2: Mixed Agent-Skill Workflow

```python
orchestrator = LangGraphAgentOrchestrator()

# Register components
orchestrator.register_agent(research_agent)
orchestrator.register_skill(AnalysisSkill())
orchestrator.register_skill(ReportSkill())

# Create mixed workflow
workflow = orchestrator.create_mixed_workflow(
    workflow_name="research_report",
    steps=[
        {"type": "agent", "id": "research_agent"},
        {"type": "skill", "id": "analysis"},
        {"type": "skill", "id": "report"}
    ]
)

result = workflow.run(initial_input="Market trends 2024")
```

### Example 3: Conditional Workflow

```python
builder = GraphBuilder("approval_workflow")

# Define routing logic
def needs_approval(state):
    amount = state["context"].get("amount", 0)
    return "manager_review" if amount > 1000 else "auto_approve"

# Build graph
builder.add_node("check_amount", ToolNode("check", check_amount_fn))
builder.add_node("manager_review", ToolNode("review", review_fn))
builder.add_node("auto_approve", ToolNode("approve", approve_fn))

builder.set_entry_point("check_amount")
builder.add_conditional_edges("check_amount", needs_approval)
builder.add_finish_edge("manager_review")
builder.add_finish_edge("auto_approve")

workflow = builder.build()
```

### Example 4: Parallel Execution

```python
# Create parallel research workflow
builder = GraphBuilder("parallel_research")

# Add parallel research nodes
builder.add_node("web_search", ToolNode("web", web_search_fn))
builder.add_node("db_query", ToolNode("db", database_query_fn))
builder.add_node("api_call", ToolNode("api", api_call_fn))

# Add aggregator
builder.add_node("combine", AggregatorNode(
    "combine",
    aggregation_fn,
    source_nodes=["web_search", "db_query", "api_call"]
))

# Connect all research nodes to aggregator
builder.add_edge("web_search", "combine")
builder.add_edge("db_query", "combine")
builder.add_edge("api_call", "combine")

workflow = builder.build()
```

### Example 5: Streaming Execution

```python
workflow = orchestrator.create_skill_workflow(
    workflow_name="long_pipeline",
    skill_sequence=["step1", "step2", "step3", "step4"]
)

# Stream execution
print("Starting workflow...")
for chunk in workflow.stream(initial_input="process this"):
    # Each chunk contains state updates
    current_step = list(chunk.keys())[0]
    print(f"Completed: {current_step}")

print("Workflow complete!")
```

### Example 6: Checkpointing and Resume

```python
# Start workflow
workflow = orchestrator.get_workflow("long_running_task")
result = workflow.run(
    initial_input="Start processing",
    workflow_id="task_001"
)

# Later, resume from checkpoint
workflow_id = "task_001"
saved_state = workflow.get_state(workflow_id)

if saved_state:
    # Resume with new input
    final_result = workflow.resume(
        workflow_id=workflow_id,
        new_input="Continue processing"
    )
```

## API Reference

### LangGraphAgentOrchestrator

Main orchestration interface.

**Methods:**

- `register_agent(agent: BaseAgent) -> self`
- `register_skill(skill: BaseSkill, skill_id: Optional[str]) -> self`
- `create_agent_workflow(name: str, agent_sequence: List[str]) -> WorkflowGraph`
- `create_skill_workflow(name: str, skill_sequence: List[str]) -> WorkflowGraph`
- `create_mixed_workflow(name: str, steps: List[Dict]) -> WorkflowGraph`
- `run_workflow(name: str, input_message: str, context: Dict) -> WorkflowState`
- `get_workflow(name: str) -> Optional[WorkflowGraph]`
- `list_workflows() -> List[str]`
- `list_agents() -> List[str]`
- `list_skills() -> List[str]`

### WorkflowGraph

Compiled workflow ready for execution.

**Methods:**

- `run(initial_input: str, context: Dict, workflow_id: str, max_loops: int) -> WorkflowState`
- `stream(initial_input: str, context: Dict, workflow_id: str, max_loops: int) -> Iterator`
- `get_state(workflow_id: str) -> Optional[WorkflowState]`
- `resume(workflow_id: str, new_input: str) -> WorkflowState`
- `visualize(output_path: str) -> str`

### GraphBuilder

Fluent API for building graphs.

**Methods:**

- `add_node(name: str, node: BaseNode) -> self`
- `add_edge(from_node: str, to_node: str) -> self`
- `add_conditional_edges(source: str, router: Callable, path_map: Dict) -> self`
- `set_entry_point(node_name: str) -> self`
- `add_finish_edge(from_node: str) -> self`
- `build() -> WorkflowGraph`

### StateManager

Utilities for state management.

**Static Methods:**

- `create_initial_state(workflow_id, initial_message, context, max_loops) -> WorkflowState`
- `add_message(state, role, content, metadata) -> WorkflowState`
- `update_context(state, updates) -> WorkflowState`
- `record_agent_execution(state, agent_name, result) -> WorkflowState`
- `record_error(state, error, context) -> WorkflowState`
- `get_latest_message(state) -> Optional[Message]`
- `get_messages_by_role(state, role) -> List[Message]`

## Best Practices

### 1. State Design
- Keep state minimal and focused
- Use context for workflow-specific data
- Use shared_memory for cross-node communication
- Store intermediate results for debugging

### 2. Node Design
- Nodes should be stateless (state is in WorkflowState)
- Keep node logic focused and single-purpose
- Use descriptive node names
- Handle errors gracefully

### 3. Graph Design
- Start simple, add complexity as needed
- Use conditional routing for decision points
- Avoid deeply nested conditionals
- Document complex routing logic

### 4. Error Handling
- Use try-except in node execute methods
- Record errors in state for tracking
- Implement retry logic for transient failures
- Use error states for graceful degradation

### 5. Performance
- Use streaming for long-running workflows
- Implement checkpointing for resumability
- Monitor workflow execution times
- Optimize node execution order

### 6. Testing
- Test nodes independently
- Test workflows with mock data
- Verify state transitions
- Test error conditions

## Advanced Topics

### Custom Node Types

Create specialized nodes by subclassing BaseNode:

```python
from langgraph_orchestration.nodes import BaseNode

class DatabaseNode(BaseNode):
    def __init__(self, name: str, query: str):
        super().__init__(name, "Database query node")
        self.query = query

    def execute(self, state: WorkflowState) -> WorkflowState:
        # Execute database query
        result = execute_query(self.query, state["context"])

        # Update state
        new_state = StateManager.add_message(
            state,
            MessageRole.TOOL,
            f"Query result: {result}"
        )
        return new_state
```

### Custom State Types

Define custom state for specialized workflows:

```python
from typing import TypedDict
from typing_extensions import Annotated

class CustomState(WorkflowState):
    # Add custom fields
    user_profile: Dict[str, Any]
    session_data: Dict[str, Any]
    recommendations: List[str]
```

### Persistent Checkpointing

Use custom checkpointers for persistent storage:

```python
from langgraph.checkpoint import SqliteSaver

# Use SQLite for persistent checkpoints
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

builder = GraphBuilder("persistent_workflow")
# ... build graph
graph = builder.graph.compile(checkpointer=checkpointer)
```

### Human-in-the-Loop

Implement human approval steps:

```python
from langgraph_orchestration.nodes import HumanInputNode

builder = GraphBuilder("approval_workflow")
builder.add_node("process", process_node)
builder.add_node("human_review", HumanInputNode(
    "human_review",
    prompt="Please review and approve"
))
builder.add_node("finalize", finalize_node)

# Add edges
builder.add_edge("process", "human_review")
builder.add_edge("human_review", "finalize")
```

## Integration with Existing Framework

The LangGraph orchestration seamlessly integrates with:

- **BaseAgent**: Use existing agents in workflows
- **BaseSkill**: Chain skills into complex pipelines
- **SkillOrchestrator**: Compatible with existing orchestration
- **AgentRegistry**: Access registered agents
- **Skill Registry**: Access registered skills

### Migration Guide

Converting existing orchestration to LangGraph:

**Before (Skill Orchestrator):**
```python
from skills.orchestrator import SkillOrchestrator

orchestrator = SkillOrchestrator()
result = orchestrator.run_chain([skill1, skill2, skill3], input_data)
```

**After (LangGraph):**
```python
from langgraph_orchestration import LangGraphAgentOrchestrator

lg_orchestrator = LangGraphAgentOrchestrator()
lg_orchestrator.register_skill(skill1)
lg_orchestrator.register_skill(skill2)
lg_orchestrator.register_skill(skill3)

workflow = lg_orchestrator.create_skill_workflow(
    "my_workflow",
    ["skill1", "skill2", "skill3"]
)
result = workflow.run(initial_input=input_data)
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure langgraph is installed
2. **State Not Updating**: Check that nodes return updated state
3. **Routing Not Working**: Verify router function returns valid node names
4. **Checkpoints Not Saving**: Ensure checkpointer is configured correctly

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Visualization

Visualize workflows for debugging:

```python
workflow = builder.build()
workflow.visualize(output_path="workflow.txt")
```

## Examples

See `examples/example_langgraph_orchestration.py` for comprehensive examples including:
- Sequential workflows
- Agent workflows
- Mixed workflows
- Conditional routing
- State management
- Streaming execution

## Contributing

To extend the framework:
1. Create custom node types by subclassing BaseNode
2. Define custom state types by extending WorkflowState
3. Add helper functions to graph_builder.py
4. Submit tests for new functionality

## License

This framework is part of the ClaudeCodeFramework project.

## Support

For issues and questions:
- Check the examples directory
- Review existing agent/skill implementations
- Consult LangGraph documentation: https://langchain-ai.github.io/langgraph/
