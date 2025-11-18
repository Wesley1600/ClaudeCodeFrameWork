"""
Workflow Orchestrator - Manages nested workflows with load balancing and agent coordination

This module provides a comprehensive orchestration system that:
- Spawns and manages child agents for subtask execution
- Tracks progress of all agents and tasks
- Executes tasks concurrently where possible
- Balances load across available workers
- Throttles or queues jobs during load spikes
- Supports nested workflows with dependency management

Author: Claude Code Framework
License: MIT
Version: 1.0.0
"""

import asyncio
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from collections import deque
from datetime import datetime
import threading
import psutil
import traceback


# ============================================================================
# Configuration and Constants
# ============================================================================

class TaskPriority(Enum):
    """Priority levels for task scheduling"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class TaskStatus(Enum):
    """Task lifecycle states"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class AgentStatus(Enum):
    """Agent worker states"""
    IDLE = "idle"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    FAILED = "failed"
    SHUTDOWN = "shutdown"


# Default configuration
DEFAULT_MAX_WORKERS = 4
DEFAULT_MAX_CONCURRENT_TASKS = 10
DEFAULT_CPU_THRESHOLD = 80.0  # Percentage
DEFAULT_MEMORY_THRESHOLD = 85.0  # Percentage
DEFAULT_TASK_TIMEOUT = 300  # Seconds
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_QUEUE_SIZE = 1000


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class TaskResult:
    """Result of a task execution"""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    error_traceback: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    retries: int = 0
    agent_id: Optional[str] = None

    @property
    def execution_time(self) -> float:
        """Calculate execution time in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return self.duration_seconds


@dataclass
class WorkflowTask:
    """
    Represents a task in the workflow

    Args:
        task_id: Unique identifier for the task
        func: Callable function to execute
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        priority: Task priority level
        dependencies: Set of task IDs this task depends on
        max_retries: Maximum number of retry attempts
        timeout: Task timeout in seconds
        metadata: Additional metadata for the task
        parent_task_id: ID of the parent task (for nested workflows)
    """
    task_id: str
    func: Callable
    args: Tuple = field(default_factory=tuple)
    kwargs: Dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: Set[str] = field(default_factory=set)
    max_retries: int = DEFAULT_RETRY_ATTEMPTS
    timeout: Optional[float] = DEFAULT_TASK_TIMEOUT
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_task_id: Optional[str] = None

    # Runtime state
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    assigned_agent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[TaskResult] = None
    child_tasks: List[str] = field(default_factory=list)

    def __lt__(self, other):
        """Enable priority queue comparison"""
        return self.priority.value < other.priority.value

    def can_execute(self, completed_tasks: Set[str]) -> bool:
        """Check if all dependencies are satisfied"""
        return self.dependencies.issubset(completed_tasks)

    def mark_running(self, agent_id: str):
        """Mark task as running"""
        self.status = TaskStatus.RUNNING
        self.assigned_agent_id = agent_id
        self.started_at = datetime.now()

    def mark_completed(self, result: TaskResult):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result

    def mark_failed(self, result: TaskResult):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.result = result


@dataclass
class Agent:
    """
    Worker agent that executes tasks

    Args:
        agent_id: Unique identifier for the agent
        max_concurrent_tasks: Maximum number of concurrent tasks
        executor_type: Type of executor ('thread' or 'process')
    """
    agent_id: str
    max_concurrent_tasks: int = 1
    executor_type: str = "thread"

    # Runtime state
    status: AgentStatus = AgentStatus.IDLE
    current_tasks: Set[str] = field(default_factory=set)
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_execution_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_task_completed_at: Optional[datetime] = None

    @property
    def is_available(self) -> bool:
        """Check if agent can accept more tasks"""
        return (
            self.status == AgentStatus.IDLE and
            len(self.current_tasks) < self.max_concurrent_tasks
        )

    @property
    def load_factor(self) -> float:
        """Calculate current load (0.0 to 1.0)"""
        if self.max_concurrent_tasks == 0:
            return 1.0
        return len(self.current_tasks) / self.max_concurrent_tasks

    def assign_task(self, task_id: str):
        """Assign a task to this agent"""
        self.current_tasks.add(task_id)
        if len(self.current_tasks) >= self.max_concurrent_tasks:
            self.status = AgentStatus.OVERLOADED
        else:
            self.status = AgentStatus.BUSY

    def complete_task(self, task_id: str, success: bool, execution_time: float):
        """Mark a task as completed"""
        if task_id in self.current_tasks:
            self.current_tasks.remove(task_id)

        if success:
            self.completed_tasks += 1
        else:
            self.failed_tasks += 1

        self.total_execution_time += execution_time
        self.last_task_completed_at = datetime.now()

        # Update status
        if len(self.current_tasks) == 0:
            self.status = AgentStatus.IDLE
        elif len(self.current_tasks) < self.max_concurrent_tasks:
            self.status = AgentStatus.BUSY

    @property
    def average_task_time(self) -> float:
        """Calculate average task execution time"""
        total_tasks = self.completed_tasks + self.failed_tasks
        if total_tasks == 0:
            return 0.0
        return self.total_execution_time / total_tasks


# ============================================================================
# Progress Tracking
# ============================================================================

class ProgressTracker:
    """
    Tracks progress of tasks and workflows

    Provides real-time monitoring and statistics for task execution
    """

    def __init__(self):
        self.tasks: Dict[str, WorkflowTask] = {}
        self.callbacks: List[Callable] = []
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    def register_task(self, task: WorkflowTask):
        """Register a new task for tracking"""
        with self._lock:
            self.tasks[task.task_id] = task
            self._notify_callbacks("task_registered", task)

    def update_task_status(self, task_id: str, status: TaskStatus):
        """Update task status"""
        with self._lock:
            if task_id in self.tasks:
                old_status = self.tasks[task_id].status
                self.tasks[task_id].status = status
                self._notify_callbacks("task_status_changed", self.tasks[task_id], old_status)

    def add_callback(self, callback: Callable):
        """Add a progress callback function"""
        self.callbacks.append(callback)

    def _notify_callbacks(self, event_type: str, *args):
        """Notify all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(event_type, *args)
            except Exception as e:
                self.logger.error(f"Error in progress callback: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        with self._lock:
            total = len(self.tasks)
            status_counts = {status: 0 for status in TaskStatus}

            for task in self.tasks.values():
                status_counts[task.status] += 1

            completed = status_counts[TaskStatus.COMPLETED]
            failed = status_counts[TaskStatus.FAILED]
            running = status_counts[TaskStatus.RUNNING]
            pending = status_counts[TaskStatus.PENDING] + status_counts[TaskStatus.QUEUED]

            # Calculate average execution time for completed tasks
            completed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED and t.result]
            avg_execution_time = 0.0
            if completed_tasks:
                avg_execution_time = sum(t.result.execution_time for t in completed_tasks) / len(completed_tasks)

            return {
                "total_tasks": total,
                "completed": completed,
                "failed": failed,
                "running": running,
                "pending": pending,
                "success_rate": completed / total if total > 0 else 0.0,
                "average_execution_time": avg_execution_time,
                "status_breakdown": {status.value: count for status, count in status_counts.items()}
            }

    def get_task_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get progress information for a specific task"""
        with self._lock:
            if task_id not in self.tasks:
                return None

            task = self.tasks[task_id]
            progress = {
                "task_id": task.task_id,
                "status": task.status.value,
                "priority": task.priority.value,
                "retry_count": task.retry_count,
                "created_at": task.created_at.isoformat(),
                "dependencies": list(task.dependencies),
                "child_tasks": task.child_tasks,
            }

            if task.started_at:
                progress["started_at"] = task.started_at.isoformat()
            if task.completed_at:
                progress["completed_at"] = task.completed_at.isoformat()
                progress["duration_seconds"] = (task.completed_at - task.started_at).total_seconds()

            if task.result:
                progress["success"] = task.result.success
                if task.result.error:
                    progress["error"] = str(task.result.error)

            return progress


# ============================================================================
# Load Balancer
# ============================================================================

class LoadBalancer:
    """
    Manages load distribution and throttling

    Monitors system resources and distributes tasks across agents
    """

    def __init__(
        self,
        cpu_threshold: float = DEFAULT_CPU_THRESHOLD,
        memory_threshold: float = DEFAULT_MEMORY_THRESHOLD,
        max_queue_size: int = DEFAULT_QUEUE_SIZE
    ):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.max_queue_size = max_queue_size
        self.logger = logging.getLogger(__name__)
        self._monitoring = False
        self._monitor_interval = 1.0  # seconds

    def check_system_resources(self) -> Dict[str, Any]:
        """Check current system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "available_memory_mb": memory.available / (1024 * 1024),
                "can_accept_tasks": (
                    cpu_percent < self.cpu_threshold and
                    memory.percent < self.memory_threshold
                )
            }
        except Exception as e:
            self.logger.error(f"Error checking system resources: {e}")
            return {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "available_memory_mb": 0.0,
                "can_accept_tasks": False
            }

    def should_throttle(self, current_queue_size: int) -> bool:
        """Determine if task execution should be throttled"""
        resources = self.check_system_resources()

        # Throttle if resources are high
        if not resources["can_accept_tasks"]:
            self.logger.warning(
                f"Throttling due to resource usage: "
                f"CPU={resources['cpu_percent']:.1f}%, "
                f"Memory={resources['memory_percent']:.1f}%"
            )
            return True

        # Throttle if queue is full
        if current_queue_size >= self.max_queue_size:
            self.logger.warning(f"Throttling due to queue size: {current_queue_size}/{self.max_queue_size}")
            return True

        return False

    def select_agent(self, agents: List[Agent], task: WorkflowTask) -> Optional[Agent]:
        """
        Select the best agent for a task using load balancing

        Strategy: Round-robin with load awareness
        """
        available_agents = [a for a in agents if a.is_available]

        if not available_agents:
            return None

        # Sort by load factor (least loaded first)
        available_agents.sort(key=lambda a: (a.load_factor, a.completed_tasks))

        return available_agents[0]

    def calculate_optimal_workers(self, task_count: int) -> int:
        """Calculate optimal number of workers based on task count and resources"""
        cpu_count = psutil.cpu_count() or 1

        # Use up to 75% of available CPUs
        max_workers = max(1, int(cpu_count * 0.75))

        # Don't create more workers than tasks
        optimal_workers = min(max_workers, task_count)

        return max(1, optimal_workers)


# ============================================================================
# Workflow Orchestrator
# ============================================================================

class WorkflowOrchestrator:
    """
    Main orchestrator for managing nested workflows with load balancing

    Features:
    - Spawns and manages child agents for subtask execution
    - Tracks progress of all tasks and agents
    - Executes tasks concurrently where possible
    - Balances load across available workers
    - Throttles or queues jobs during load spikes
    - Supports nested workflows with dependency management

    Example:
        >>> orchestrator = WorkflowOrchestrator(max_workers=4)
        >>>
        >>> # Define workflow tasks
        >>> task1 = WorkflowTask(
        ...     task_id="fetch_data",
        ...     func=fetch_from_api,
        ...     args=(url,),
        ...     priority=TaskPriority.HIGH
        ... )
        >>>
        >>> task2 = WorkflowTask(
        ...     task_id="process_data",
        ...     func=process_data,
        ...     dependencies={"fetch_data"},
        ...     priority=TaskPriority.NORMAL
        ... )
        >>>
        >>> # Execute workflow
        >>> results = await orchestrator.execute_workflow([task1, task2])
        >>>
        >>> # Monitor progress
        >>> stats = orchestrator.get_statistics()
        >>> print(f"Completed: {stats['completed']}/{stats['total_tasks']}")
    """

    def __init__(
        self,
        max_workers: int = DEFAULT_MAX_WORKERS,
        max_concurrent_tasks: int = DEFAULT_MAX_CONCURRENT_TASKS,
        cpu_threshold: float = DEFAULT_CPU_THRESHOLD,
        memory_threshold: float = DEFAULT_MEMORY_THRESHOLD,
        enable_nested_workflows: bool = True,
        log_level: int = logging.INFO
    ):
        """
        Initialize the workflow orchestrator

        Args:
            max_workers: Maximum number of worker agents
            max_concurrent_tasks: Maximum concurrent tasks per agent
            cpu_threshold: CPU threshold for throttling (percentage)
            memory_threshold: Memory threshold for throttling (percentage)
            enable_nested_workflows: Enable nested workflow support
            log_level: Logging level
        """
        # Configuration
        self.max_workers = max_workers
        self.max_concurrent_tasks = max_concurrent_tasks
        self.enable_nested_workflows = enable_nested_workflows

        # Core components
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, WorkflowTask] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()

        # Executors
        self.thread_executor: Optional[ThreadPoolExecutor] = None
        self.process_executor: Optional[ProcessPoolExecutor] = None

        # Supporting systems
        self.progress_tracker = ProgressTracker()
        self.load_balancer = LoadBalancer(cpu_threshold, memory_threshold)

        # State management
        self._running = False
        self._shutdown = False
        self._lock = asyncio.Lock()
        self._worker_tasks: List[asyncio.Task] = []

        # Logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        # Statistics
        self.workflow_start_time: Optional[datetime] = None
        self.workflow_end_time: Optional[datetime] = None

    async def initialize(self):
        """Initialize the orchestrator and spawn agents"""
        self.logger.info(f"Initializing workflow orchestrator with {self.max_workers} workers")

        # Create thread executor
        self.thread_executor = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="orchestrator-worker"
        )

        # Create process executor for CPU-intensive tasks
        self.process_executor = ProcessPoolExecutor(max_workers=max(1, self.max_workers // 2))

        # Spawn worker agents
        for i in range(self.max_workers):
            agent = Agent(
                agent_id=f"agent-{i:03d}",
                max_concurrent_tasks=self.max_concurrent_tasks,
                executor_type="thread"
            )
            self.agents[agent.agent_id] = agent
            self.logger.debug(f"Spawned agent: {agent.agent_id}")

        self._running = True
        self.logger.info("Orchestrator initialized successfully")

    async def shutdown(self):
        """Shutdown the orchestrator and cleanup resources"""
        self.logger.info("Shutting down orchestrator...")
        self._shutdown = True
        self._running = False

        # Wait for worker tasks to complete
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)

        # Shutdown executors
        if self.thread_executor:
            self.thread_executor.shutdown(wait=True)
        if self.process_executor:
            self.process_executor.shutdown(wait=True)

        # Update agent statuses
        for agent in self.agents.values():
            agent.status = AgentStatus.SHUTDOWN

        self.logger.info("Orchestrator shutdown complete")

    def add_task(
        self,
        func: Callable,
        *args,
        task_id: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: Optional[Set[str]] = None,
        max_retries: int = DEFAULT_RETRY_ATTEMPTS,
        timeout: Optional[float] = DEFAULT_TASK_TIMEOUT,
        metadata: Optional[Dict] = None,
        parent_task_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Add a task to the workflow

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            task_id: Optional task ID (generated if not provided)
            priority: Task priority
            dependencies: Set of task IDs this task depends on
            max_retries: Maximum retry attempts
            timeout: Task timeout in seconds
            metadata: Additional metadata
            parent_task_id: Parent task ID for nested workflows
            **kwargs: Keyword arguments for the function

        Returns:
            Task ID
        """
        if not task_id:
            task_id = f"task-{uuid.uuid4().hex[:12]}"

        task = WorkflowTask(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            dependencies=dependencies or set(),
            max_retries=max_retries,
            timeout=timeout,
            metadata=metadata or {},
            parent_task_id=parent_task_id
        )

        self.tasks[task_id] = task
        self.progress_tracker.register_task(task)

        self.logger.debug(f"Added task: {task_id} (priority={priority.name})")

        return task_id

    async def execute_workflow(
        self,
        tasks: Optional[List[WorkflowTask]] = None,
        wait_for_completion: bool = True
    ) -> Dict[str, TaskResult]:
        """
        Execute a workflow of tasks

        Args:
            tasks: List of tasks to execute (uses already added tasks if None)
            wait_for_completion: Wait for all tasks to complete

        Returns:
            Dictionary mapping task IDs to results
        """
        if not self._running:
            await self.initialize()

        # Register tasks if provided
        if tasks:
            for task in tasks:
                if task.task_id not in self.tasks:
                    self.tasks[task.task_id] = task
                    self.progress_tracker.register_task(task)

        self.workflow_start_time = datetime.now()
        self.logger.info(f"Starting workflow execution with {len(self.tasks)} tasks")

        # Queue all tasks that have no dependencies
        async with self._lock:
            for task in self.tasks.values():
                if task.can_execute(self.completed_tasks):
                    await self._queue_task(task)

        # Start worker coroutines
        num_workers = min(self.max_workers, len(self.tasks))
        self._worker_tasks = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(num_workers)
        ]

        if wait_for_completion:
            # Wait for all tasks to complete
            await self._wait_for_completion()

            self.workflow_end_time = datetime.now()

            # Gather results
            results = {}
            for task_id, task in self.tasks.items():
                if task.result:
                    results[task_id] = task.result

            self.logger.info(
                f"Workflow completed: {len(self.completed_tasks)} succeeded, "
                f"{len(self.failed_tasks)} failed"
            )

            return results

        return {}

    async def _queue_task(self, task: WorkflowTask):
        """Queue a task for execution"""
        task.status = TaskStatus.QUEUED
        self.progress_tracker.update_task_status(task.task_id, TaskStatus.QUEUED)

        # Priority queue uses (priority, task)
        await self.task_queue.put((task.priority.value, task.task_id))

        self.logger.debug(f"Queued task: {task.task_id}")

    async def _worker(self, worker_id: str):
        """Worker coroutine that processes tasks from the queue"""
        self.logger.debug(f"Worker {worker_id} started")

        while self._running and not self._shutdown:
            try:
                # Check if we should throttle
                if self.load_balancer.should_throttle(self.task_queue.qsize()):
                    await asyncio.sleep(1.0)
                    continue

                # Get task from queue with timeout
                try:
                    priority, task_id = await asyncio.wait_for(
                        self.task_queue.get(),
                        timeout=0.5
                    )
                except asyncio.TimeoutError:
                    # Check if all tasks are completed
                    if await self._all_tasks_processed():
                        break
                    continue

                # Get task object
                task = self.tasks.get(task_id)
                if not task:
                    self.logger.error(f"Task not found: {task_id}")
                    continue

                # Check dependencies again
                if not task.can_execute(self.completed_tasks):
                    # Re-queue the task
                    await self.task_queue.put((priority, task_id))
                    await asyncio.sleep(0.1)
                    continue

                # Select an agent
                agent = self.load_balancer.select_agent(list(self.agents.values()), task)
                if not agent:
                    # No available agents, re-queue
                    await self.task_queue.put((priority, task_id))
                    await asyncio.sleep(0.5)
                    continue

                # Execute the task
                await self._execute_task(task, agent)

                # Check for dependent tasks that can now be executed
                await self._check_and_queue_dependent_tasks(task_id)

            except Exception as e:
                self.logger.error(f"Error in worker {worker_id}: {e}\n{traceback.format_exc()}")

        self.logger.debug(f"Worker {worker_id} stopped")

    async def _execute_task(self, task: WorkflowTask, agent: Agent):
        """Execute a task using the assigned agent"""
        task.mark_running(agent.agent_id)
        agent.assign_task(task.task_id)
        self.progress_tracker.update_task_status(task.task_id, TaskStatus.RUNNING)

        self.logger.info(f"Executing task {task.task_id} on agent {agent.agent_id}")

        start_time = datetime.now()
        result = None

        try:
            # Execute the function
            loop = asyncio.get_event_loop()

            # Choose executor based on agent type
            executor = self.thread_executor if agent.executor_type == "thread" else self.process_executor

            # Run with timeout
            if task.timeout:
                result = await asyncio.wait_for(
                    loop.run_in_executor(executor, task.func, *task.args, **task.kwargs),
                    timeout=task.timeout
                )
            else:
                result = await loop.run_in_executor(
                    executor,
                    task.func,
                    *task.args,
                    **task.kwargs
                )

            # Task succeeded
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            task_result = TaskResult(
                task_id=task.task_id,
                success=True,
                result=result,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=execution_time,
                retries=task.retry_count,
                agent_id=agent.agent_id
            )

            task.mark_completed(task_result)
            self.completed_tasks.add(task.task_id)
            agent.complete_task(task.task_id, True, execution_time)
            self.progress_tracker.update_task_status(task.task_id, TaskStatus.COMPLETED)

            self.logger.info(
                f"Task {task.task_id} completed successfully in {execution_time:.2f}s"
            )

        except asyncio.TimeoutError:
            # Task timeout
            error = TimeoutError(f"Task {task.task_id} timed out after {task.timeout}s")
            await self._handle_task_failure(task, agent, error, start_time)

        except Exception as e:
            # Task failed
            await self._handle_task_failure(task, agent, e, start_time)

    async def _handle_task_failure(
        self,
        task: WorkflowTask,
        agent: Agent,
        error: Exception,
        start_time: datetime
    ):
        """Handle task failure with retry logic"""
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        self.logger.error(f"Task {task.task_id} failed: {error}")

        # Check if we should retry
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRYING
            agent.complete_task(task.task_id, False, execution_time)
            self.progress_tracker.update_task_status(task.task_id, TaskStatus.RETRYING)

            self.logger.info(
                f"Retrying task {task.task_id} (attempt {task.retry_count}/{task.max_retries})"
            )

            # Re-queue the task with exponential backoff
            await asyncio.sleep(min(2 ** task.retry_count, 30))
            await self._queue_task(task)

        else:
            # Max retries exceeded, mark as failed
            task_result = TaskResult(
                task_id=task.task_id,
                success=False,
                error=error,
                error_traceback=traceback.format_exc(),
                start_time=start_time,
                end_time=end_time,
                duration_seconds=execution_time,
                retries=task.retry_count,
                agent_id=agent.agent_id
            )

            task.mark_failed(task_result)
            self.failed_tasks.add(task.task_id)
            agent.complete_task(task.task_id, False, execution_time)
            self.progress_tracker.update_task_status(task.task_id, TaskStatus.FAILED)

            self.logger.error(
                f"Task {task.task_id} failed permanently after {task.retry_count} retries"
            )

    async def _check_and_queue_dependent_tasks(self, completed_task_id: str):
        """Check and queue tasks that depend on the completed task"""
        async with self._lock:
            for task in self.tasks.values():
                if (
                    task.status == TaskStatus.PENDING and
                    completed_task_id in task.dependencies and
                    task.can_execute(self.completed_tasks)
                ):
                    await self._queue_task(task)

    async def _wait_for_completion(self):
        """Wait for all tasks to complete"""
        while True:
            if await self._all_tasks_processed():
                break
            await asyncio.sleep(0.5)

        # Cancel worker tasks
        for worker_task in self._worker_tasks:
            if not worker_task.done():
                worker_task.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self._worker_tasks, return_exceptions=True)

    async def _all_tasks_processed(self) -> bool:
        """Check if all tasks have been processed"""
        total_processed = len(self.completed_tasks) + len(self.failed_tasks)
        return total_processed >= len(self.tasks) and self.task_queue.empty()

    def spawn_child_workflow(
        self,
        parent_task_id: str,
        child_tasks: List[WorkflowTask]
    ) -> List[str]:
        """
        Spawn a nested child workflow

        Args:
            parent_task_id: ID of the parent task
            child_tasks: List of child tasks to execute

        Returns:
            List of child task IDs
        """
        if not self.enable_nested_workflows:
            raise ValueError("Nested workflows are not enabled")

        child_task_ids = []

        for child_task in child_tasks:
            child_task.parent_task_id = parent_task_id
            self.tasks[child_task.task_id] = child_task
            self.progress_tracker.register_task(child_task)
            child_task_ids.append(child_task.task_id)

        # Update parent task with child references
        if parent_task_id in self.tasks:
            self.tasks[parent_task_id].child_tasks.extend(child_task_ids)

        self.logger.info(
            f"Spawned {len(child_task_ids)} child tasks for parent {parent_task_id}"
        )

        return child_task_ids

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the workflow execution"""
        stats = self.progress_tracker.get_statistics()

        # Add agent statistics
        agent_stats = []
        for agent in self.agents.values():
            agent_stats.append({
                "agent_id": agent.agent_id,
                "status": agent.status.value,
                "completed_tasks": agent.completed_tasks,
                "failed_tasks": agent.failed_tasks,
                "current_load": agent.load_factor,
                "average_task_time": agent.average_task_time
            })

        stats["agents"] = agent_stats

        # Add system resource stats
        stats["system_resources"] = self.load_balancer.check_system_resources()

        # Add workflow timing
        if self.workflow_start_time:
            stats["workflow_start_time"] = self.workflow_start_time.isoformat()
        if self.workflow_end_time:
            stats["workflow_end_time"] = self.workflow_end_time.isoformat()
            duration = (self.workflow_end_time - self.workflow_start_time).total_seconds()
            stats["total_workflow_duration"] = duration

        return stats

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        return self.progress_tracker.get_task_progress(task_id)

    def add_progress_callback(self, callback: Callable):
        """
        Add a callback for progress events

        Callback signature: callback(event_type: str, *args)
        """
        self.progress_tracker.add_callback(callback)


# ============================================================================
# Utility Functions
# ============================================================================

def create_task_from_function(
    func: Callable,
    *args,
    task_id: Optional[str] = None,
    priority: TaskPriority = TaskPriority.NORMAL,
    dependencies: Optional[Set[str]] = None,
    **kwargs
) -> WorkflowTask:
    """
    Convenience function to create a WorkflowTask from a function

    Example:
        >>> task = create_task_from_function(
        ...     my_function,
        ...     arg1, arg2,
        ...     task_id="my_task",
        ...     priority=TaskPriority.HIGH,
        ...     kwarg1=value1
        ... )
    """
    if not task_id:
        task_id = f"task-{uuid.uuid4().hex[:12]}"

    return WorkflowTask(
        task_id=task_id,
        func=func,
        args=args,
        kwargs=kwargs,
        priority=priority,
        dependencies=dependencies or set()
    )


# ============================================================================
# Example Usage (if run as main module)
# ============================================================================

if __name__ == "__main__":
    # This section is for demonstration only
    import random

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Example task functions
    def example_task(task_name: str, duration: float = 1.0) -> str:
        """Example task that simulates work"""
        time.sleep(duration)
        return f"{task_name} completed"

    def failing_task(task_name: str) -> str:
        """Example task that fails"""
        raise ValueError(f"{task_name} failed intentionally")

    async def main():
        # Create orchestrator
        orchestrator = WorkflowOrchestrator(
            max_workers=4,
            max_concurrent_tasks=2
        )

        # Add progress callback
        def progress_callback(event_type: str, *args):
            if event_type == "task_status_changed":
                task = args[0]
                old_status = args[1]
                print(f"Task {task.task_id}: {old_status.value} -> {task.status.value}")

        orchestrator.add_progress_callback(progress_callback)

        # Create workflow tasks
        tasks = []

        # Task 1: High priority task
        task1_id = orchestrator.add_task(
            example_task,
            "Task 1",
            2.0,
            task_id="task-1",
            priority=TaskPriority.HIGH
        )

        # Task 2: Depends on task 1
        task2_id = orchestrator.add_task(
            example_task,
            "Task 2",
            1.5,
            task_id="task-2",
            dependencies={task1_id},
            priority=TaskPriority.NORMAL
        )

        # Task 3: Independent task
        task3_id = orchestrator.add_task(
            example_task,
            "Task 3",
            1.0,
            task_id="task-3",
            priority=TaskPriority.NORMAL
        )

        # Execute workflow
        print("Starting workflow execution...")
        results = await orchestrator.execute_workflow()

        # Print results
        print("\n=== Workflow Results ===")
        for task_id, result in results.items():
            print(f"{task_id}: success={result.success}, result={result.result}")

        # Print statistics
        print("\n=== Workflow Statistics ===")
        stats = orchestrator.get_statistics()
        print(f"Total tasks: {stats['total_tasks']}")
        print(f"Completed: {stats['completed']}")
        print(f"Failed: {stats['failed']}")
        print(f"Success rate: {stats['success_rate']:.1%}")
        print(f"Average execution time: {stats['average_execution_time']:.2f}s")
        print(f"Total workflow duration: {stats.get('total_workflow_duration', 0):.2f}s")

        # Shutdown orchestrator
        await orchestrator.shutdown()

    # Run the example
    asyncio.run(main())
