# Dispatcher Skill - Semantic Router for Multi-Agent Coordination

A production-ready dispatcher skill that interprets plans and assigns subtasks to appropriate specialized agents using semantic routing. This implements the planning design pattern with a semantic router that coordinates multiple specialized agents.

## Overview

The Dispatcher Skill provides:

1. **Plan Interpretation** - Parses plans from multiple formats (dict, markdown, objects)
2. **Semantic Routing** - Intelligently routes tasks to appropriate specialized agents
3. **Dependency Management** - Handles task dependencies and execution ordering
4. **Execution Coordination** - Manages parallel/sequential task execution
5. **Result Aggregation** - Collects and organizes results from multiple agents

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       TaskDispatcher                            │
│  (Main orchestration engine)                                    │
└──────────────┬─────────────┬──────────────┬─────────────────────┘
               │             │              │
       ┌───────▼──────┐  ┌──▼────────┐  ┌──▼──────────────┐
       │  PlanParser  │  │RoutingMap │  │ AgentRegistry   │
       │              │  │            │  │                 │
       │ - Dict       │  │- Patterns  │  │- Code Generator │
       │ - Markdown   │  │- Keywords  │  │- Testing        │
       │ - Objects    │  │- Priority  │  │- Documentation  │
       └──────────────┘  └────────────┘  │- Debugging      │
                                         │- Refactoring    │
                                         │- Analysis       │
                                         │- Generic        │
                                         └─────────────────┘
                              │
                    ┌─────────▼────────────┐
                    │ExecutionCoordinator  │
                    │                      │
                    │- Dependency Graph    │
                    │- Topological Sort    │
                    │- Execution Control   │
                    │- Result Collection   │
                    └──────────────────────┘
```

## Key Components

### 1. TaskDispatcher

Main interface for the dispatcher skill. Integrates all components.

```python
dispatcher = TaskDispatcher()

# Register agents
dispatcher.register_agent(CodeGeneratorAgent())
dispatcher.register_agent(TestingAgent())

# Dispatch a plan
result = dispatcher.dispatch_plan(plan_dict)

# Analyze without executing
analysis = dispatcher.analyze_plan(plan_dict)
```

### 2. RoutingMap

Semantic routing using patterns, keywords, and priorities.

```python
routing_map = RoutingMap()

# Add pattern-based rules
routing_map.add_rule(
    r'\b(implement|code|write)\b.*\b(function|class)\b',
    AgentType.CODE_GENERATOR,
    priority=2.0
)

# Add keyword mappings
routing_map.add_keyword_mapping("test", AgentType.TESTING)

# Route a task
agent_type = routing_map.route(task)
```

### 3. AgentRegistry

Manages specialized agents and their capabilities.

```python
registry = AgentRegistry()

# Register agents
registry.register_agent(GenericAgent())
registry.register_agent(CodeGeneratorAgent())

# Get appropriate agent
agent = registry.get_agent(AgentType.CODE_GENERATOR, task)
```

### 4. PlanParser

Parses plans from multiple formats.

```python
# From dictionary
plan = PlanParser.parse_dict(plan_dict)

# From markdown
plan = PlanParser.parse_markdown(markdown_text)
```

### 5. ExecutionCoordinator

Manages task execution with dependency resolution.

```python
coordinator = ExecutionCoordinator(registry)

# Execute plan
result = coordinator.execute_plan(plan, context)
```

## Plan Formats

### Dictionary Format

```python
plan = {
    "id": "feature_001",
    "goal": "Implement user authentication",
    "tasks": [
        {
            "id": "task_1",
            "description": "Write unit tests for auth module",
            "task_type": "testing",  # Optional explicit type
            "dependencies": [],
            "priority": 2,
            "metadata": {"framework": "pytest"}
        },
        {
            "id": "task_2",
            "description": "Implement JWT token generation",
            "dependencies": ["task_1"],
            "priority": 1
        }
    ],
    "context": {
        "framework": "Flask",
        "database": "PostgreSQL"
    }
}
```

### Markdown Format

```markdown
# Goal: Implement user authentication feature

## Tasks
1. [type:testing, priority:2] Write unit tests for auth module
2. [type:code_generator, depends:1] Implement JWT token generation
3. [depends:2] Create user registration endpoint
4. [type:documentation, depends:2&3] Update API documentation
```

Metadata tags in markdown:
- `type:AGENT_TYPE` - Explicit agent type
- `depends:N` - Single dependency on task N
- `depends:N&M` - Multiple dependencies
- `priority:N` - Priority level (higher = more urgent)

## Agent Types

Built-in agent types:

- **CODE_GENERATOR** - Implements code, functions, classes, modules
- **TESTING** - Writes and runs tests (unit, integration, e2e)
- **DOCUMENTATION** - Creates docs, READMEs, docstrings
- **DEBUGGING** - Fixes bugs, troubleshoots issues
- **REFACTORING** - Improves code structure, optimizes
- **DATA_PROCESSOR** - Processes, transforms, parses data
- **ANALYSIS** - Analyzes, reviews, evaluates code
- **OPTIMIZATION** - Performance optimization
- **INTEGRATION** - Integrates components, systems
- **GENERIC** - Fallback for general tasks

## Creating Custom Agents

```python
from dispatcher_skill import Agent, AgentType, Task
from typing import Dict, Any

class MyCustomAgent(Agent):
    """Custom agent for specific domain."""

    def __init__(self):
        super().__init__(AgentType.CUSTOM, "MyCustomAgent")
        self.capabilities = ["capability1", "capability2"]

    def can_handle(self, task: Task) -> bool:
        """Determine if this agent can handle the task."""
        keywords = ["keyword1", "keyword2"]
        return any(kw in task.description.lower() for kw in keywords)

    def execute(self, task: Task, context: Dict[str, Any]) -> Any:
        """Execute the task and return results."""
        # Your implementation here
        result = perform_work(task, context)
        return {
            "status": "completed",
            "output": result,
            "agent": self.name
        }

    def estimate_cost(self, task: Task) -> float:
        """Estimate computational cost (optional)."""
        return len(task.description) * 0.1  # Example metric

# Register with dispatcher
dispatcher.register_agent(MyCustomAgent())
```

## Usage Examples

### Basic Usage

```python
from dispatcher_skill import create_default_dispatcher

# Create dispatcher with default agents
dispatcher = create_default_dispatcher()

# Define a plan
plan = {
    "id": "refactor_001",
    "goal": "Refactor authentication module",
    "tasks": [
        {
            "id": "task_1",
            "description": "Analyze current authentication implementation",
            "priority": 2
        },
        {
            "id": "task_2",
            "description": "Write comprehensive tests for auth module",
            "dependencies": ["task_1"]
        },
        {
            "id": "task_3",
            "description": "Refactor auth code for better modularity",
            "dependencies": ["task_2"]
        },
        {
            "id": "task_4",
            "description": "Update authentication documentation",
            "dependencies": ["task_3"]
        }
    ]
}

# Execute the plan
result = dispatcher.dispatch_plan(plan)

# Check results
print(f"Status: {result['status']}")
print(f"Completed: {len(result['completed_tasks'])} tasks")
print(f"Failed: {len(result['failed_tasks'])} tasks")

for task_id, task_result in result['results'].items():
    print(f"\n{task_id}:")
    print(f"  {task_result}")
```

### Analyze Before Executing

```python
# Analyze plan to see routing decisions
analysis = dispatcher.analyze_plan(plan)

print(f"Goal: {analysis['goal']}")
print(f"\nRouting Assignments:")
for task_id, agent_type in analysis['routing_assignments'].items():
    desc = analysis['dependency_graph'][task_id]['description']
    print(f"  {task_id} → {agent_type}")
    print(f"    {desc}")

print(f"\nExecution Order: {' → '.join(analysis['execution_order'])}")

if analysis['warnings']:
    print("\nWarnings:")
    for warning in analysis['warnings']:
        print(f"  ⚠ {warning}")
```

### Using Markdown Plans

```python
markdown_plan = """
# Goal: Build REST API for user management

## Tasks
1. [type:analysis, priority:3] Review API design requirements
2. [type:testing, depends:1] Write API endpoint tests
3. [type:code_generator, depends:2] Implement CRUD endpoints
4. [type:testing, depends:3] Add integration tests
5. [type:documentation, depends:3&4] Generate API documentation
"""

result = dispatcher.dispatch_plan(markdown_plan)
```

### Custom Context and Agent Registration

```python
from dispatcher_skill import TaskDispatcher, Agent, AgentType

class DatabaseAgent(Agent):
    def __init__(self):
        super().__init__(AgentType.DATA_PROCESSOR, "DatabaseAgent")

    def can_handle(self, task: Task) -> bool:
        return "database" in task.description.lower()

    def execute(self, task: Task, context: Dict[str, Any]) -> Any:
        db_connection = context.get("db_connection")
        # Use db_connection to execute task
        return {"status": "completed", "rows_affected": 42}

# Create dispatcher and register custom agent
dispatcher = TaskDispatcher()
dispatcher.register_agent(DatabaseAgent())

# Provide execution context
context = {
    "db_connection": "postgresql://localhost/mydb",
    "api_key": "secret_key",
    "environment": "staging"
}

result = dispatcher.dispatch_plan(plan, context)
```

### Handling Errors

```python
result = dispatcher.dispatch_plan(plan)

if result['status'] == 'failed':
    print("Plan execution failed!")
    for task_id in result['failed_tasks']:
        error_info = result['results'][task_id]
        print(f"Task {task_id} failed: {error_info.get('error')}")

elif result['status'] == 'partial':
    print("Plan partially completed")
    print(f"Completed: {result['completed_tasks']}")
    print(f"Failed: {result['failed_tasks']}")

else:
    print("Plan completed successfully!")
```

## Routing Rules

Default routing rules are pattern-based:

| Pattern | Agent Type | Priority |
|---------|------------|----------|
| `implement\|code\|write.*function\|class` | CODE_GENERATOR | 2.0 |
| `test\|unit test\|pytest\|jest` | TESTING | 2.0 |
| `document\|readme\|docstring` | DOCUMENTATION | 2.0 |
| `debug\|fix\|bug\|error` | DEBUGGING | 2.0 |
| `refactor\|clean\|optimize` | REFACTORING | 1.5 |
| `process\|transform\|parse` | DATA_PROCESSOR | 1.5 |
| `analyze\|review\|inspect` | ANALYSIS | 1.5 |

### Custom Routing Rules

```python
dispatcher = TaskDispatcher()

# Add high-priority rule for security tasks
dispatcher.routing_map.add_rule(
    r'\b(security|vulnerability|exploit|CVE)\b',
    AgentType.DEBUGGING,
    priority=10.0  # Highest priority
)

# Add keyword mapping
dispatcher.routing_map.add_keyword_mapping(
    "machine learning",
    AgentType.DATA_PROCESSOR
)

# Set fallback agent
dispatcher.routing_map.set_fallback_agent(AgentType.ANALYSIS)
```

## Dependency Management

The dispatcher automatically:

1. **Topologically sorts** tasks based on dependencies
2. **Validates** for circular dependencies
3. **Prioritizes** tasks with higher priority values
4. **Skips** tasks whose dependencies failed
5. **Propagates** results through context

Example dependency graph:

```
task_1 (priority: 3)
  ├─→ task_2 (depends: task_1)
  └─→ task_3 (depends: task_1)
        └─→ task_4 (depends: task_3)
```

Execution order: `task_1 → (task_2, task_3) → task_4`

Tasks at the same level are sorted by priority.

## Execution Results

The `dispatch_plan` method returns:

```python
{
    "plan_id": str,              # Plan identifier
    "status": str,               # "completed", "partial", or "failed"
    "completed_tasks": List[str], # Task IDs that completed
    "failed_tasks": List[str],    # Task IDs that failed
    "results": {                  # Results per task
        "task_1": {...},
        "task_2": {...}
    },
    "context": Dict[str, Any]    # Final execution context
}
```

Task results are also stored in the execution context as `task_result_{task_id}` for downstream tasks to access.

## Testing

Run the test suite:

```bash
# Install pytest
pip install pytest

# Run tests
pytest test_dispatcher_skill.py -v

# Run with coverage
pytest test_dispatcher_skill.py --cov=dispatcher_skill --cov-report=html
```

Test coverage includes:
- ✅ Data structures (Task, Plan)
- ✅ Agent implementations
- ✅ Routing logic
- ✅ Agent registry
- ✅ Plan parsing (dict and markdown)
- ✅ Execution coordination
- ✅ Dependency resolution
- ✅ Error handling
- ✅ Integration workflows

## Performance Considerations

### Parallel Execution

Currently tasks are executed sequentially based on dependencies. For production use, consider:

```python
import asyncio

class AsyncExecutionCoordinator(ExecutionCoordinator):
    """Execute independent tasks in parallel."""

    async def execute_plan_async(self, plan: Plan) -> Dict[str, Any]:
        # Group tasks by dependency level
        levels = self._build_dependency_levels(plan.tasks)

        # Execute each level in parallel
        for level in levels:
            tasks = [self._execute_task_async(t) for t in level]
            await asyncio.gather(*tasks)
```

### Caching

For repeated plan execution:

```python
from functools import lru_cache

class CachingDispatcher(TaskDispatcher):
    @lru_cache(maxsize=100)
    def analyze_plan_cached(self, plan_hash: str) -> Dict[str, Any]:
        return self.analyze_plan(plan_hash)
```

### Large Plans

For plans with 100+ tasks:

1. Use streaming results
2. Implement checkpoint/resume
3. Add progress callbacks
4. Consider distributed execution

## Integration with Planner

The dispatcher is designed to work with planner output (item 4). Expected integration:

```python
from planner import create_plan  # Your planner module
from dispatcher_skill import create_default_dispatcher

# Generate plan from high-level goal
plan = create_plan(
    goal="Build microservice for payment processing",
    constraints={"max_tasks": 20, "priority": "security"}
)

# Dispatch the plan
dispatcher = create_default_dispatcher()
result = dispatcher.dispatch_plan(plan)

# Handle results
if result['status'] == 'completed':
    notify_completion(result)
else:
    handle_failures(result['failed_tasks'])
```

## API Reference

See inline documentation in `dispatcher_skill.py` for complete API reference:

- `Task` - Task data structure
- `Plan` - Plan data structure
- `Agent` - Abstract agent base class
- `AgentType` - Enum of agent types
- `TaskStatus` - Enum of task statuses
- `RoutingMap` - Semantic routing engine
- `AgentRegistry` - Agent management
- `PlanParser` - Plan parsing utilities
- `ExecutionCoordinator` - Execution orchestration
- `TaskDispatcher` - Main dispatcher interface
- `create_default_dispatcher()` - Factory for default setup

## Roadmap

### Current (v1.0)
- ✅ Core dispatcher implementation
- ✅ Semantic routing with patterns/keywords
- ✅ Dependency resolution and topological sort
- ✅ Multiple plan format support
- ✅ Default agent implementations
- ✅ Comprehensive test suite

### Planned (v1.1)
- [ ] Async/parallel execution
- [ ] Progress callbacks and streaming
- [ ] Checkpoint/resume for long plans
- [ ] Plugin architecture for agents
- [ ] Enhanced routing with embeddings

### Future (v2.0)
- [ ] Distributed execution across nodes
- [ ] Learning-based routing optimization
- [ ] Visual plan editor
- [ ] Real-time plan adaptation
- [ ] Integration with popular frameworks

## License

MIT License - See main project LICENSE file

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues, questions, or feature requests, please open a GitHub issue.

---

**Status**: Production-ready v1.0

**Last updated**: 2025-11-18
