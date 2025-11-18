# Workflow Orchestrator

A comprehensive, production-ready orchestration system for managing nested workflows with load balancing, agent coordination, and intelligent task scheduling.

## Features

### Core Capabilities

- ✅ **Agent-Based Architecture**: Spawn and manage multiple worker agents for parallel task execution
- ✅ **Nested Workflows**: Support for parent-child task relationships and hierarchical workflows
- ✅ **Dependency Management**: Automatic task ordering based on dependencies with DAG (Directed Acyclic Graph) support
- ✅ **Load Balancing**: Intelligent distribution of tasks across agents based on current load
- ✅ **Throttling & Queueing**: Automatic throttling based on system resources (CPU, memory) with configurable thresholds
- ✅ **Progress Tracking**: Real-time monitoring of task execution with callback support
- ✅ **Error Handling**: Automatic retries with exponential backoff and comprehensive error tracking
- ✅ **Concurrent Execution**: Execute independent tasks in parallel for maximum throughput
- ✅ **Priority Scheduling**: Task prioritization (CRITICAL, HIGH, NORMAL, LOW, BACKGROUND)
- ✅ **Resource Monitoring**: System resource tracking and adaptive load management

### Advanced Features

- **Timeout Support**: Per-task timeout configuration
- **Retry Mechanisms**: Configurable retry attempts with automatic failure recovery
- **Event System**: Extensible callback system for progress monitoring and custom integrations
- **Statistics**: Comprehensive workflow and agent statistics
- **Flexible Execution**: Support for both thread-based and process-based execution
- **Task Metadata**: Attach custom metadata to tasks for tracking and filtering

## Installation

### Requirements

```bash
pip install psutil pytest pytest-asyncio
```

### Quick Start

```python
import asyncio
from workflow_orchestrator import (
    WorkflowOrchestrator,
    TaskPriority,
)

# Define your task function
def process_data(data_id: int) -> dict:
    # Your processing logic here
    return {"id": data_id, "processed": True}

async def main():
    # Create orchestrator
    orchestrator = WorkflowOrchestrator(
        max_workers=4,
        max_concurrent_tasks=2
    )

    # Add tasks
    task1 = orchestrator.add_task(
        process_data,
        1,
        task_id="task-1",
        priority=TaskPriority.HIGH
    )

    task2 = orchestrator.add_task(
        process_data,
        2,
        task_id="task-2",
        dependencies={task1},  # Runs after task1
        priority=TaskPriority.NORMAL
    )

    # Execute workflow
    results = await orchestrator.execute_workflow()

    # Check results
    for task_id, result in results.items():
        print(f"{task_id}: success={result.success}, result={result.result}")

    # Cleanup
    await orchestrator.shutdown()

# Run
asyncio.run(main())
```

## Architecture

### Components

#### 1. WorkflowOrchestrator
Main orchestrator class that manages the entire workflow execution.

**Key Parameters:**
- `max_workers`: Maximum number of worker agents (default: 4)
- `max_concurrent_tasks`: Tasks per agent (default: 10)
- `cpu_threshold`: CPU threshold for throttling (default: 80%)
- `memory_threshold`: Memory threshold for throttling (default: 85%)
- `enable_nested_workflows`: Enable parent-child workflows (default: True)

**Key Methods:**
- `add_task()`: Add a task to the workflow
- `execute_workflow()`: Execute all tasks
- `spawn_child_workflow()`: Create nested workflows
- `get_statistics()`: Get execution statistics
- `add_progress_callback()`: Register progress callbacks

#### 2. Agent
Worker agents that execute tasks.

**Properties:**
- `agent_id`: Unique identifier
- `status`: Current status (IDLE, BUSY, OVERLOADED, FAILED, SHUTDOWN)
- `load_factor`: Current load (0.0 to 1.0)
- `completed_tasks`: Number of completed tasks
- `average_task_time`: Average execution time

#### 3. WorkflowTask
Represents a task in the workflow.

**Properties:**
- `task_id`: Unique identifier
- `func`: Function to execute
- `priority`: Task priority level
- `dependencies`: Set of dependent task IDs
- `max_retries`: Maximum retry attempts
- `timeout`: Execution timeout
- `metadata`: Custom metadata dictionary

#### 4. LoadBalancer
Manages load distribution and throttling.

**Features:**
- System resource monitoring (CPU, memory)
- Agent selection based on load
- Queue size management
- Adaptive throttling

#### 5. ProgressTracker
Tracks task progress and statistics.

**Features:**
- Real-time task status tracking
- Callback notifications
- Statistics aggregation
- Task history

## Usage Examples

### Example 1: Simple Task Execution

```python
async def example_simple():
    orchestrator = WorkflowOrchestrator(max_workers=2)

    # Add simple task
    task_id = orchestrator.add_task(
        lambda x: x * 2,
        5,
        task_id="double-task"
    )

    results = await orchestrator.execute_workflow()
    print(f"Result: {results[task_id].result}")  # Output: 10

    await orchestrator.shutdown()
```

### Example 2: Tasks with Dependencies

```python
async def example_dependencies():
    orchestrator = WorkflowOrchestrator(max_workers=4)

    # Create dependency chain
    t1 = orchestrator.add_task(fetch_data, task_id="fetch")
    t2 = orchestrator.add_task(validate_data, task_id="validate", dependencies={t1})
    t3 = orchestrator.add_task(transform_data, task_id="transform", dependencies={t2})
    t4 = orchestrator.add_task(save_data, task_id="save", dependencies={t3})

    results = await orchestrator.execute_workflow()
    await orchestrator.shutdown()
```

### Example 3: Parallel Processing

```python
async def example_parallel():
    orchestrator = WorkflowOrchestrator(max_workers=8)

    # Add multiple independent tasks (execute in parallel)
    for i in range(10):
        orchestrator.add_task(
            process_item,
            i,
            task_id=f"process-{i}",
            priority=TaskPriority.NORMAL
        )

    results = await orchestrator.execute_workflow()
    await orchestrator.shutdown()
```

### Example 4: Error Handling with Retries

```python
async def example_retries():
    orchestrator = WorkflowOrchestrator(max_workers=2)

    # Task with retry logic
    task_id = orchestrator.add_task(
        flaky_api_call,
        task_id="api-call",
        max_retries=3,  # Retry up to 3 times
        timeout=10.0,   # 10 second timeout
        priority=TaskPriority.HIGH
    )

    results = await orchestrator.execute_workflow()

    if results[task_id].success:
        print(f"Succeeded after {results[task_id].retries} retries")
    else:
        print(f"Failed: {results[task_id].error}")

    await orchestrator.shutdown()
```

### Example 5: Nested Workflows

```python
async def example_nested():
    orchestrator = WorkflowOrchestrator(
        max_workers=4,
        enable_nested_workflows=True
    )

    def spawn_children(orchestrator, parent_id):
        # Create child tasks
        child_tasks = [
            WorkflowTask(
                task_id=f"child-{i}",
                func=process_item,
                args=(i,)
            )
            for i in range(5)
        ]
        return orchestrator.spawn_child_workflow(parent_id, child_tasks)

    # Add parent task that spawns children
    parent_id = orchestrator.add_task(
        spawn_children,
        orchestrator,
        "parent-task",
        task_id="parent-task"
    )

    results = await orchestrator.execute_workflow()
    await orchestrator.shutdown()
```

### Example 6: Progress Monitoring

```python
async def example_progress():
    orchestrator = WorkflowOrchestrator(max_workers=4)

    # Add progress callback
    def progress_callback(event_type, *args):
        if event_type == "task_status_changed":
            task = args[0]
            old_status = args[1]
            print(f"Task {task.task_id}: {old_status.value} → {task.status.value}")

    orchestrator.add_progress_callback(progress_callback)

    # Add tasks
    for i in range(5):
        orchestrator.add_task(process_item, i, task_id=f"task-{i}")

    results = await orchestrator.execute_workflow()

    # Get statistics
    stats = orchestrator.get_statistics()
    print(f"Completed: {stats['completed']}/{stats['total_tasks']}")
    print(f"Success rate: {stats['success_rate']:.1%}")

    await orchestrator.shutdown()
```

### Example 7: Priority Scheduling

```python
async def example_priority():
    orchestrator = WorkflowOrchestrator(max_workers=1)  # Single worker

    # Add tasks with different priorities
    orchestrator.add_task(low_priority_task, task_id="low", priority=TaskPriority.LOW)
    orchestrator.add_task(high_priority_task, task_id="high", priority=TaskPriority.HIGH)
    orchestrator.add_task(critical_task, task_id="critical", priority=TaskPriority.CRITICAL)

    # Execution order: critical → high → low
    results = await orchestrator.execute_workflow()
    await orchestrator.shutdown()
```

## Task Priority Levels

| Priority | Value | Use Case |
|----------|-------|----------|
| CRITICAL | 0 | Time-sensitive, system-critical tasks |
| HIGH | 1 | Important tasks that should execute soon |
| NORMAL | 2 | Standard tasks (default) |
| LOW | 3 | Background processing, non-urgent tasks |
| BACKGROUND | 4 | Maintenance, cleanup tasks |

## Task Status Lifecycle

```
PENDING → QUEUED → RUNNING → COMPLETED
                          ↓
                       FAILED → RETRYING → RUNNING
                          ↓
                     CANCELLED
```

## Performance Tuning

### Optimizing Worker Count

```python
# For I/O-bound tasks (API calls, file I/O)
orchestrator = WorkflowOrchestrator(max_workers=16)

# For CPU-bound tasks (computation)
orchestrator = WorkflowOrchestrator(max_workers=4)  # ~= CPU cores

# Mixed workload
orchestrator = WorkflowOrchestrator(max_workers=8)
```

### Adjusting Thresholds

```python
# More aggressive throttling
orchestrator = WorkflowOrchestrator(
    cpu_threshold=60.0,      # Throttle at 60% CPU
    memory_threshold=70.0    # Throttle at 70% memory
)

# More lenient (high-performance systems)
orchestrator = WorkflowOrchestrator(
    cpu_threshold=90.0,
    memory_threshold=95.0
)
```

### Concurrency Control

```python
# High concurrency per agent
orchestrator = WorkflowOrchestrator(
    max_workers=4,
    max_concurrent_tasks=10  # Each agent handles 10 tasks
)

# Low concurrency (resource-intensive tasks)
orchestrator = WorkflowOrchestrator(
    max_workers=8,
    max_concurrent_tasks=1  # One task per agent
)
```

## Statistics and Monitoring

### Available Statistics

```python
stats = orchestrator.get_statistics()

# Task statistics
print(stats['total_tasks'])         # Total number of tasks
print(stats['completed'])           # Completed tasks
print(stats['failed'])              # Failed tasks
print(stats['running'])             # Currently running
print(stats['pending'])             # Pending/queued
print(stats['success_rate'])        # Success rate (0.0 to 1.0)
print(stats['average_execution_time'])  # Average task time

# Agent statistics
for agent in stats['agents']:
    print(agent['agent_id'])
    print(agent['status'])
    print(agent['completed_tasks'])
    print(agent['average_task_time'])
    print(agent['current_load'])    # Load factor (0.0 to 1.0)

# System resources
resources = stats['system_resources']
print(resources['cpu_percent'])
print(resources['memory_percent'])
print(resources['available_memory_mb'])
print(resources['can_accept_tasks'])

# Workflow timing
print(stats['workflow_start_time'])
print(stats['workflow_end_time'])
print(stats['total_workflow_duration'])
```

### Task-Level Statistics

```python
task_progress = orchestrator.get_task_status("task-1")

print(task_progress['status'])
print(task_progress['priority'])
print(task_progress['retry_count'])
print(task_progress['dependencies'])
print(task_progress['child_tasks'])
print(task_progress['duration_seconds'])
```

## Error Handling

### Common Error Scenarios

#### 1. Task Timeout
```python
# Task exceeds timeout limit
task_id = orchestrator.add_task(
    long_running_task,
    timeout=30.0  # 30 second limit
)

results = await orchestrator.execute_workflow()
if not results[task_id].success:
    print(f"Error: {results[task_id].error}")  # TimeoutError
```

#### 2. Task Failure with Retries
```python
# Task fails but retries automatically
task_id = orchestrator.add_task(
    flaky_function,
    max_retries=3
)

results = await orchestrator.execute_workflow()
print(f"Retries: {results[task_id].retries}")
```

#### 3. Dependency Failure
```python
# If a dependency fails, dependent tasks are skipped
t1 = orchestrator.add_task(failing_task, task_id="t1")
t2 = orchestrator.add_task(dependent_task, task_id="t2", dependencies={t1})

results = await orchestrator.execute_workflow()
# t2 will not execute if t1 fails
```

## Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest test_workflow_orchestrator.py -v

# Run specific test
pytest test_workflow_orchestrator.py::test_simple_task_execution -v

# Run with coverage
pytest test_workflow_orchestrator.py --cov=workflow_orchestrator --cov-report=html
```

## Examples

See `example_orchestrator_usage.py` for comprehensive real-world examples:

1. **Data Processing Pipeline**: Parallel data fetching, validation, transformation, and aggregation
2. **Machine Learning Training**: Train multiple models in parallel and select the best
3. **ETL Workflow**: Extract-Transform-Load with error handling and retries
4. **Nested Workflows**: Parent tasks spawning child workflows
5. **Load Balancing**: CPU-intensive tasks with automatic load balancing

Run examples:

```bash
python example_orchestrator_usage.py
```

## Best Practices

### 1. Task Design
- Keep tasks focused and single-purpose
- Use pure functions when possible (easier to test and retry)
- Avoid shared state between tasks
- Handle exceptions within tasks when appropriate

### 2. Dependency Management
- Keep dependency graphs simple and acyclic
- Use task priorities to optimize execution order
- Avoid deep dependency chains (can impact parallelism)

### 3. Resource Management
- Set appropriate timeouts for all tasks
- Configure retry attempts based on task criticality
- Monitor system resources during execution
- Adjust worker count based on workload type

### 4. Error Handling
- Use retries for transient failures (network, API rate limits)
- Set max_retries=0 for deterministic failures
- Log errors with task metadata for debugging
- Use callbacks to monitor failures in real-time

### 5. Performance Optimization
- Group independent tasks for parallel execution
- Use process executors for CPU-bound tasks
- Use thread executors for I/O-bound tasks
- Tune worker count and concurrency for your workload

## Limitations

- **No distributed execution**: Single-machine only (future: support for distributed workers)
- **In-memory state**: Task state is not persisted (future: database backend)
- **No cycle detection**: Circular dependencies will cause deadlock
- **Limited observability**: Basic logging only (future: integration with observability tools)

## Future Enhancements

- [ ] Distributed execution across multiple machines
- [ ] Persistent task queue with database backend
- [ ] Web UI for workflow visualization
- [ ] Integration with popular workflow engines (Airflow, Prefect)
- [ ] Advanced scheduling algorithms (fair scheduling, work stealing)
- [ ] Task result caching and memoization
- [ ] GraphQL/REST API for remote task submission
- [ ] Kubernetes integration for containerized execution

## Contributing

Contributions are welcome! Please ensure:
- All tests pass (`pytest test_workflow_orchestrator.py`)
- Code follows existing style conventions
- New features include tests and documentation
- Performance-critical code is benchmarked

## License

MIT License - see LICENSE file for details

## Support

For questions, issues, or feature requests:
- File an issue on GitHub
- Check the examples in `example_orchestrator_usage.py`
- Review the test suite for usage patterns

---

**Version**: 1.0.0
**Author**: Claude Code Framework
**Last Updated**: 2025-11-18
