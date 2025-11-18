"""
Comprehensive tests for the Workflow Orchestrator

Tests cover:
- Basic task execution
- Dependency management
- Nested workflows
- Load balancing
- Throttling
- Progress tracking
- Error handling and retries
- Concurrent execution
"""

import asyncio
import logging
import pytest
import time
from datetime import datetime
from typing import List

from workflow_orchestrator import (
    WorkflowOrchestrator,
    WorkflowTask,
    TaskPriority,
    TaskStatus,
    AgentStatus,
    create_task_from_function,
    ProgressTracker,
    LoadBalancer,
    Agent,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def orchestrator():
    """Create a test orchestrator instance"""
    orch = WorkflowOrchestrator(
        max_workers=2,
        max_concurrent_tasks=2,
        log_level=logging.DEBUG
    )
    yield orch
    # Cleanup
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(orch.shutdown())
    except:
        pass


@pytest.fixture
def progress_tracker():
    """Create a progress tracker instance"""
    return ProgressTracker()


@pytest.fixture
def load_balancer():
    """Create a load balancer instance"""
    return LoadBalancer()


# ============================================================================
# Helper Functions for Testing
# ============================================================================

def simple_task(value: int) -> int:
    """Simple task that returns double the input"""
    return value * 2


def slow_task(duration: float = 1.0, value: str = "done") -> str:
    """Task that takes time to complete"""
    time.sleep(duration)
    return value


def failing_task(error_message: str = "Task failed") -> None:
    """Task that always fails"""
    raise ValueError(error_message)


def cpu_intensive_task(n: int = 1000000) -> int:
    """CPU-intensive task for testing load balancing"""
    result = 0
    for i in range(n):
        result += i
    return result


def nested_workflow_task(orchestrator: WorkflowOrchestrator, parent_id: str) -> List[str]:
    """Task that spawns child tasks"""
    child_tasks = [
        WorkflowTask(
            task_id=f"child-{parent_id}-{i}",
            func=simple_task,
            args=(i,),
            priority=TaskPriority.NORMAL
        )
        for i in range(3)
    ]

    return orchestrator.spawn_child_workflow(parent_id, child_tasks)


# ============================================================================
# Basic Functionality Tests
# ============================================================================

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    orch = WorkflowOrchestrator(max_workers=4)
    await orch.initialize()

    assert orch._running is True
    assert len(orch.agents) == 4
    assert orch.thread_executor is not None
    assert orch.process_executor is not None

    # Check all agents are idle
    for agent in orch.agents.values():
        assert agent.status == AgentStatus.IDLE

    await orch.shutdown()


@pytest.mark.asyncio
async def test_simple_task_execution():
    """Test execution of a simple task"""
    orch = WorkflowOrchestrator(max_workers=2)

    task_id = orch.add_task(simple_task, 5, task_id="simple-1")

    results = await orch.execute_workflow()

    assert task_id in results
    assert results[task_id].success is True
    assert results[task_id].result == 10

    await orch.shutdown()


@pytest.mark.asyncio
async def test_multiple_tasks_execution():
    """Test execution of multiple independent tasks"""
    orch = WorkflowOrchestrator(max_workers=4)

    task_ids = []
    for i in range(5):
        task_id = orch.add_task(
            simple_task,
            i,
            task_id=f"task-{i}",
            priority=TaskPriority.NORMAL
        )
        task_ids.append(task_id)

    results = await orch.execute_workflow()

    assert len(results) == 5
    for i, task_id in enumerate(task_ids):
        assert results[task_id].success is True
        assert results[task_id].result == i * 2

    await orch.shutdown()


# ============================================================================
# Dependency Management Tests
# ============================================================================

@pytest.mark.asyncio
async def test_task_dependencies():
    """Test tasks with dependencies execute in correct order"""
    orch = WorkflowOrchestrator(max_workers=2)

    # Create tasks with dependencies
    task1_id = orch.add_task(simple_task, 1, task_id="task-1")
    task2_id = orch.add_task(
        simple_task,
        2,
        task_id="task-2",
        dependencies={task1_id}
    )
    task3_id = orch.add_task(
        simple_task,
        3,
        task_id="task-3",
        dependencies={task1_id, task2_id}
    )

    results = await orch.execute_workflow()

    # All tasks should complete
    assert len(results) == 3
    assert all(r.success for r in results.values())

    # Check execution order through timestamps
    task1_end = results[task1_id].end_time
    task2_start = results[task2_id].start_time
    task3_start = results[task3_id].start_time

    assert task2_start >= task1_end
    assert task3_start >= results[task2_id].end_time

    await orch.shutdown()


@pytest.mark.asyncio
async def test_complex_dependency_graph():
    """Test complex dependency graph"""
    orch = WorkflowOrchestrator(max_workers=4)

    # Create diamond dependency pattern
    #     A
    #    / \
    #   B   C
    #    \ /
    #     D

    task_a = orch.add_task(simple_task, 1, task_id="A")
    task_b = orch.add_task(simple_task, 2, task_id="B", dependencies={task_a})
    task_c = orch.add_task(simple_task, 3, task_id="C", dependencies={task_a})
    task_d = orch.add_task(simple_task, 4, task_id="D", dependencies={task_b, task_c})

    results = await orch.execute_workflow()

    assert len(results) == 4
    assert all(r.success for r in results.values())

    # D should start after both B and C complete
    assert results[task_d].start_time >= results[task_b].end_time
    assert results[task_d].start_time >= results[task_c].end_time

    await orch.shutdown()


# ============================================================================
# Priority and Scheduling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_task_priority():
    """Test that high priority tasks execute first"""
    orch = WorkflowOrchestrator(max_workers=1)  # Single worker to ensure serial execution

    # Add tasks in reverse priority order
    low_task = orch.add_task(
        slow_task,
        0.1,
        "low",
        task_id="low",
        priority=TaskPriority.LOW
    )
    high_task = orch.add_task(
        slow_task,
        0.1,
        "high",
        task_id="high",
        priority=TaskPriority.HIGH
    )
    normal_task = orch.add_task(
        slow_task,
        0.1,
        "normal",
        task_id="normal",
        priority=TaskPriority.NORMAL
    )

    results = await orch.execute_workflow()

    # High priority should start before normal and low
    assert results[high_task].start_time < results[normal_task].start_time
    assert results[normal_task].start_time < results[low_task].start_time

    await orch.shutdown()


# ============================================================================
# Error Handling and Retry Tests
# ============================================================================

@pytest.mark.asyncio
async def test_task_failure():
    """Test task failure handling"""
    orch = WorkflowOrchestrator(max_workers=2)

    failing_task_id = orch.add_task(
        failing_task,
        "Expected failure",
        task_id="failing",
        max_retries=0  # No retries
    )

    results = await orch.execute_workflow()

    assert failing_task_id in results
    assert results[failing_task_id].success is False
    assert results[failing_task_id].error is not None
    assert "Expected failure" in str(results[failing_task_id].error)

    await orch.shutdown()


@pytest.mark.asyncio
async def test_task_retry():
    """Test task retry mechanism"""
    orch = WorkflowOrchestrator(max_workers=2)

    retry_count = 0

    def sometimes_failing_task():
        nonlocal retry_count
        retry_count += 1
        if retry_count < 3:
            raise ValueError("Not yet!")
        return "Success after retries"

    task_id = orch.add_task(
        sometimes_failing_task,
        task_id="retry-task",
        max_retries=3
    )

    results = await orch.execute_workflow()

    assert task_id in results
    assert results[task_id].success is True
    assert results[task_id].result == "Success after retries"
    assert results[task_id].retries == 2  # Succeeded on 3rd attempt (2 retries)

    await orch.shutdown()


@pytest.mark.asyncio
async def test_task_timeout():
    """Test task timeout"""
    orch = WorkflowOrchestrator(max_workers=2)

    task_id = orch.add_task(
        slow_task,
        5.0,  # Task takes 5 seconds
        "should timeout",
        task_id="timeout-task",
        timeout=1.0,  # But timeout is 1 second
        max_retries=0
    )

    results = await orch.execute_workflow()

    assert task_id in results
    assert results[task_id].success is False
    assert isinstance(results[task_id].error, TimeoutError)

    await orch.shutdown()


# ============================================================================
# Concurrent Execution Tests
# ============================================================================

@pytest.mark.asyncio
async def test_concurrent_execution():
    """Test that tasks execute concurrently"""
    orch = WorkflowOrchestrator(max_workers=4)

    start_time = time.time()

    # Create 4 tasks that each take 1 second
    task_ids = []
    for i in range(4):
        task_id = orch.add_task(
            slow_task,
            1.0,
            f"task-{i}",
            task_id=f"concurrent-{i}"
        )
        task_ids.append(task_id)

    results = await orch.execute_workflow()

    end_time = time.time()
    total_time = end_time - start_time

    # With 4 workers, 4 tasks should complete in ~1 second (concurrent)
    # Not 4 seconds (sequential)
    assert total_time < 2.5  # Allow some overhead

    assert all(results[tid].success for tid in task_ids)

    await orch.shutdown()


# ============================================================================
# Progress Tracking Tests
# ============================================================================

def test_progress_tracker_registration():
    """Test progress tracker task registration"""
    tracker = ProgressTracker()

    task = WorkflowTask(
        task_id="test-task",
        func=simple_task,
        args=(5,)
    )

    tracker.register_task(task)

    assert "test-task" in tracker.tasks
    assert tracker.tasks["test-task"] == task


def test_progress_tracker_statistics():
    """Test progress tracker statistics"""
    tracker = ProgressTracker()

    # Register tasks with different statuses
    for i in range(10):
        task = WorkflowTask(
            task_id=f"task-{i}",
            func=simple_task,
            args=(i,)
        )
        tracker.register_task(task)

    # Update statuses
    for i in range(5):
        tracker.update_task_status(f"task-{i}", TaskStatus.COMPLETED)

    for i in range(5, 7):
        tracker.update_task_status(f"task-{i}", TaskStatus.RUNNING)

    for i in range(7, 9):
        tracker.update_task_status(f"task-{i}", TaskStatus.FAILED)

    stats = tracker.get_statistics()

    assert stats["total_tasks"] == 10
    assert stats["completed"] == 5
    assert stats["running"] == 2
    assert stats["failed"] == 2
    assert stats["success_rate"] == 0.5


def test_progress_callbacks():
    """Test progress callback notifications"""
    tracker = ProgressTracker()

    events_received = []

    def callback(event_type: str, *args):
        events_received.append((event_type, args))

    tracker.add_callback(callback)

    task = WorkflowTask(
        task_id="callback-task",
        func=simple_task,
        args=(1,)
    )

    tracker.register_task(task)
    tracker.update_task_status("callback-task", TaskStatus.RUNNING)
    tracker.update_task_status("callback-task", TaskStatus.COMPLETED)

    assert len(events_received) == 3
    assert events_received[0][0] == "task_registered"
    assert events_received[1][0] == "task_status_changed"
    assert events_received[2][0] == "task_status_changed"


# ============================================================================
# Load Balancer Tests
# ============================================================================

def test_load_balancer_resource_check():
    """Test load balancer resource checking"""
    balancer = LoadBalancer()

    resources = balancer.check_system_resources()

    assert "cpu_percent" in resources
    assert "memory_percent" in resources
    assert "available_memory_mb" in resources
    assert "can_accept_tasks" in resources


def test_load_balancer_agent_selection():
    """Test load balancer agent selection"""
    balancer = LoadBalancer()

    # Create agents with different loads
    agent1 = Agent(agent_id="agent-1", max_concurrent_tasks=2)
    agent2 = Agent(agent_id="agent-2", max_concurrent_tasks=2)
    agent3 = Agent(agent_id="agent-3", max_concurrent_tasks=2)

    # Load agents differently
    agent1.assign_task("task-1")
    agent2.assign_task("task-2")
    agent2.assign_task("task-3")

    task = WorkflowTask(task_id="new-task", func=simple_task)

    # Should select least loaded agent (agent1 and agent3 tied, agent3 returned)
    selected = balancer.select_agent([agent1, agent2, agent3], task)

    assert selected in [agent1, agent3]  # Either is valid as both have load=0.5
    assert selected != agent2  # agent2 is fully loaded


def test_load_balancer_throttling():
    """Test load balancer throttling logic"""
    balancer = LoadBalancer(max_queue_size=10)

    # Should not throttle with empty queue
    assert balancer.should_throttle(0) is False

    # Should throttle when queue is full
    assert balancer.should_throttle(10) is True
    assert balancer.should_throttle(15) is True


def test_load_balancer_optimal_workers():
    """Test optimal worker calculation"""
    balancer = LoadBalancer()

    # Should return reasonable number based on task count
    assert balancer.calculate_optimal_workers(1) >= 1
    assert balancer.calculate_optimal_workers(100) >= 1

    # Should not exceed task count
    optimal = balancer.calculate_optimal_workers(2)
    assert optimal <= 2


# ============================================================================
# Agent Tests
# ============================================================================

def test_agent_availability():
    """Test agent availability logic"""
    agent = Agent(agent_id="test-agent", max_concurrent_tasks=2)

    assert agent.is_available is True

    agent.assign_task("task-1")
    assert agent.is_available is True
    assert agent.status == AgentStatus.BUSY

    agent.assign_task("task-2")
    assert agent.is_available is False
    assert agent.status == AgentStatus.OVERLOADED


def test_agent_load_factor():
    """Test agent load factor calculation"""
    agent = Agent(agent_id="test-agent", max_concurrent_tasks=4)

    assert agent.load_factor == 0.0

    agent.assign_task("task-1")
    assert agent.load_factor == 0.25

    agent.assign_task("task-2")
    assert agent.load_factor == 0.5

    agent.complete_task("task-1", True, 1.0)
    assert agent.load_factor == 0.25


def test_agent_statistics():
    """Test agent statistics tracking"""
    agent = Agent(agent_id="test-agent", max_concurrent_tasks=2)

    agent.assign_task("task-1")
    agent.complete_task("task-1", True, 2.5)

    agent.assign_task("task-2")
    agent.complete_task("task-2", True, 1.5)

    agent.assign_task("task-3")
    agent.complete_task("task-3", False, 3.0)

    assert agent.completed_tasks == 2
    assert agent.failed_tasks == 1
    assert agent.total_execution_time == 7.0
    assert agent.average_task_time == 7.0 / 3


# ============================================================================
# Nested Workflow Tests
# ============================================================================

@pytest.mark.asyncio
async def test_nested_workflow():
    """Test nested workflow execution"""
    orch = WorkflowOrchestrator(max_workers=4, enable_nested_workflows=True)

    # Create parent task that spawns child tasks
    parent_id = "parent-task"

    def spawn_children():
        child_tasks = [
            WorkflowTask(
                task_id=f"child-{i}",
                func=simple_task,
                args=(i,)
            )
            for i in range(3)
        ]
        return orch.spawn_child_workflow(parent_id, child_tasks)

    orch.add_task(spawn_children, task_id=parent_id)

    results = await orch.execute_workflow()

    # Parent should complete successfully
    assert parent_id in results
    assert results[parent_id].success is True

    # Should have returned child task IDs
    child_ids = results[parent_id].result
    assert len(child_ids) == 3

    await orch.shutdown()


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_workflow_integration():
    """Test complete workflow with all features"""
    orch = WorkflowOrchestrator(max_workers=4)

    # Track events
    events = []

    def event_callback(event_type: str, *args):
        events.append(event_type)

    orch.add_progress_callback(event_callback)

    # Create complex workflow
    # Stage 1: Data fetching (parallel)
    fetch1 = orch.add_task(
        slow_task,
        0.5,
        "data1",
        task_id="fetch-1",
        priority=TaskPriority.HIGH
    )
    fetch2 = orch.add_task(
        slow_task,
        0.5,
        "data2",
        task_id="fetch-2",
        priority=TaskPriority.HIGH
    )

    # Stage 2: Processing (depends on fetching)
    process = orch.add_task(
        simple_task,
        10,
        task_id="process",
        dependencies={fetch1, fetch2},
        priority=TaskPriority.NORMAL
    )

    # Stage 3: Aggregation (depends on processing)
    aggregate = orch.add_task(
        simple_task,
        5,
        task_id="aggregate",
        dependencies={process},
        priority=TaskPriority.NORMAL
    )

    results = await orch.execute_workflow()

    # All tasks should complete
    assert len(results) == 4
    assert all(r.success for r in results.values())

    # Check execution order
    assert results[process].start_time >= results[fetch1].end_time
    assert results[process].start_time >= results[fetch2].end_time
    assert results[aggregate].start_time >= results[process].end_time

    # Check statistics
    stats = orch.get_statistics()
    assert stats["completed"] == 4
    assert stats["failed"] == 0
    assert stats["success_rate"] == 1.0

    # Should have received events
    assert len(events) > 0

    await orch.shutdown()


@pytest.mark.asyncio
async def test_workflow_with_failures_and_retries():
    """Test workflow handling failures and retries"""
    orch = WorkflowOrchestrator(max_workers=2)

    retry_attempts = {"task-1": 0, "task-2": 0}

    def flaky_task(task_id: str, fail_times: int):
        retry_attempts[task_id] += 1
        if retry_attempts[task_id] <= fail_times:
            raise ValueError(f"Attempt {retry_attempts[task_id]} failed")
        return f"Success on attempt {retry_attempts[task_id]}"

    # Task that succeeds after 2 retries
    task1 = orch.add_task(
        flaky_task,
        "task-1",
        2,
        task_id="task-1",
        max_retries=3
    )

    # Task that always fails
    task2 = orch.add_task(
        flaky_task,
        "task-2",
        10,
        task_id="task-2",
        max_retries=2
    )

    results = await orch.execute_workflow()

    # Task 1 should succeed after retries
    assert results[task1].success is True
    assert "Success" in results[task1].result

    # Task 2 should fail
    assert results[task2].success is False

    # Check statistics
    stats = orch.get_statistics()
    assert stats["completed"] == 1
    assert stats["failed"] == 1

    await orch.shutdown()


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "-s"])
