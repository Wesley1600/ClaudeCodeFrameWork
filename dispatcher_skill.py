"""
Dispatcher Skill - Semantic Router for Multi-Agent Task Coordination

This module implements a dispatcher that interprets plans and assigns subtasks
to appropriate specialized agents using a routing map. It coordinates execution
across multiple agents in a planning design pattern.

Key Components:
1. TaskDispatcher - Main orchestration engine
2. RoutingMap - Semantic routing to specialized agents
3. AgentRegistry - Registry of available specialized agents
4. PlanParser - Interprets plan structures from planner output
5. ExecutionCoordinator - Manages task execution and dependencies

Analogous to a semantic router that coordinates multiple specialized agents.
"""

from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import re
from abc import ABC, abstractmethod


class TaskStatus(Enum):
    """Status of a task in the execution pipeline."""
    PENDING = "pending"
    ROUTING = "routing"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentType(Enum):
    """Types of specialized agents available in the system."""
    CODE_GENERATOR = "code_generator"
    DATA_PROCESSOR = "data_processor"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    ANALYSIS = "analysis"
    INTEGRATION = "integration"
    GENERIC = "generic"


@dataclass
class Task:
    """
    Represents a subtask to be executed by an agent.

    Attributes:
        id: Unique identifier for the task
        description: Natural language description of the task
        task_type: Type of task (for routing)
        dependencies: List of task IDs this task depends on
        priority: Priority level (higher = more urgent)
        metadata: Additional task-specific metadata
        status: Current status of the task
        assigned_agent: Agent type assigned to handle this task
        result: Result of task execution (if completed)
        error: Error message (if failed)
    """
    id: str
    description: str
    task_type: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[AgentType] = None
    result: Optional[Any] = None
    error: Optional[str] = None

    def is_ready(self, completed_tasks: set) -> bool:
        """Check if all dependencies are satisfied."""
        return all(dep_id in completed_tasks for dep_id in self.dependencies)


@dataclass
class Plan:
    """
    Represents a plan consisting of multiple subtasks.

    Attributes:
        id: Unique identifier for the plan
        goal: High-level goal of the plan
        tasks: List of tasks in the plan
        context: Additional context for plan execution
    """
    id: str
    goal: str
    tasks: List[Task]
    context: Dict[str, Any] = field(default_factory=dict)

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None


class Agent(ABC):
    """
    Abstract base class for specialized agents.

    Each agent implements specific capabilities and can execute
    tasks within its domain of expertise.
    """

    def __init__(self, agent_type: AgentType, name: str):
        self.agent_type = agent_type
        self.name = name
        self.capabilities: List[str] = []

    @abstractmethod
    def can_handle(self, task: Task) -> bool:
        """
        Determine if this agent can handle the given task.

        Args:
            task: Task to evaluate

        Returns:
            True if agent can handle the task, False otherwise
        """
        pass

    @abstractmethod
    def execute(self, task: Task, context: Dict[str, Any]) -> Any:
        """
        Execute the given task.

        Args:
            task: Task to execute
            context: Execution context (shared state, resources, etc.)

        Returns:
            Task execution result

        Raises:
            Exception if task execution fails
        """
        pass

    def estimate_cost(self, task: Task) -> float:
        """
        Estimate the computational cost of executing this task.

        Args:
            task: Task to estimate

        Returns:
            Estimated cost (arbitrary units, for prioritization)
        """
        return 1.0


class RoutingMap:
    """
    Semantic routing map that assigns tasks to appropriate agents.

    Uses pattern matching, keyword extraction, and semantic similarity
    to route tasks to the most suitable specialized agent.
    """

    def __init__(self):
        self.routing_rules: List[Tuple[str, AgentType, float]] = []
        self.keyword_map: Dict[str, AgentType] = {}
        self.fallback_agent: AgentType = AgentType.GENERIC

    def add_rule(self, pattern: str, agent_type: AgentType, priority: float = 1.0):
        """
        Add a routing rule based on regex pattern.

        Args:
            pattern: Regex pattern to match task descriptions
            agent_type: Agent type to route to if pattern matches
            priority: Priority of this rule (higher = checked first)
        """
        self.routing_rules.append((pattern, agent_type, priority))
        # Sort by priority (descending)
        self.routing_rules.sort(key=lambda x: x[2], reverse=True)

    def add_keyword_mapping(self, keyword: str, agent_type: AgentType):
        """
        Add a keyword-based routing.

        Args:
            keyword: Keyword to look for (case-insensitive)
            agent_type: Agent type to route to if keyword is found
        """
        self.keyword_map[keyword.lower()] = agent_type

    def route(self, task: Task) -> AgentType:
        """
        Determine which agent should handle the task.

        Args:
            task: Task to route

        Returns:
            Agent type that should handle the task
        """
        description = task.description.lower()

        # First, check explicit task type
        if task.task_type:
            try:
                return AgentType(task.task_type.lower())
            except ValueError:
                pass

        # Check pattern-based rules (ordered by priority)
        for pattern, agent_type, _ in self.routing_rules:
            if re.search(pattern, description, re.IGNORECASE):
                return agent_type

        # Check keyword mapping
        for keyword, agent_type in self.keyword_map.items():
            if keyword in description:
                return agent_type

        # Fallback to generic agent
        return self.fallback_agent

    def set_fallback_agent(self, agent_type: AgentType):
        """Set the fallback agent for unmatched tasks."""
        self.fallback_agent = agent_type


class AgentRegistry:
    """
    Registry of available specialized agents.

    Manages agent lifecycle, registration, and retrieval.
    """

    def __init__(self):
        self.agents: Dict[AgentType, List[Agent]] = {}
        self.agent_pool: Dict[str, Agent] = {}

    def register_agent(self, agent: Agent):
        """
        Register a new agent in the registry.

        Args:
            agent: Agent instance to register
        """
        if agent.agent_type not in self.agents:
            self.agents[agent.agent_type] = []
        self.agents[agent.agent_type].append(agent)
        self.agent_pool[agent.name] = agent

    def get_agent(self, agent_type: AgentType, task: Optional[Task] = None) -> Optional[Agent]:
        """
        Get an agent of the specified type.

        Args:
            agent_type: Type of agent needed
            task: Optional task to match against agent capabilities

        Returns:
            Agent instance, or None if no suitable agent found
        """
        if agent_type not in self.agents or not self.agents[agent_type]:
            return None

        # If task is provided, find agent that can handle it
        if task:
            for agent in self.agents[agent_type]:
                if agent.can_handle(task):
                    return agent

        # Otherwise, return first available agent of this type
        return self.agents[agent_type][0]

    def get_all_agents(self, agent_type: AgentType) -> List[Agent]:
        """Get all agents of the specified type."""
        return self.agents.get(agent_type, [])

    def list_agent_types(self) -> List[AgentType]:
        """List all registered agent types."""
        return list(self.agents.keys())


class PlanParser:
    """
    Parser for plan structures from planner output.

    Supports multiple plan formats:
    - Structured dictionary format
    - Markdown-style task lists
    - JSON format
    """

    @staticmethod
    def parse_dict(plan_dict: Dict[str, Any]) -> Plan:
        """
        Parse a plan from dictionary format.

        Expected format:
        {
            "id": "plan_001",
            "goal": "Implement feature X",
            "tasks": [
                {
                    "id": "task_1",
                    "description": "Write unit tests",
                    "task_type": "testing",
                    "dependencies": [],
                    "priority": 1
                },
                ...
            ],
            "context": {...}
        }

        Args:
            plan_dict: Dictionary containing plan data

        Returns:
            Parsed Plan object
        """
        plan_id = plan_dict.get("id", "plan_default")
        goal = plan_dict.get("goal", "No goal specified")
        context = plan_dict.get("context", {})

        tasks = []
        for task_data in plan_dict.get("tasks", []):
            task = Task(
                id=task_data.get("id", f"task_{len(tasks)}"),
                description=task_data.get("description", ""),
                task_type=task_data.get("task_type"),
                dependencies=task_data.get("dependencies", []),
                priority=task_data.get("priority", 0),
                metadata=task_data.get("metadata", {})
            )
            tasks.append(task)

        return Plan(id=plan_id, goal=goal, tasks=tasks, context=context)

    @staticmethod
    def parse_markdown(markdown_text: str, plan_id: str = "plan_md") -> Plan:
        """
        Parse a plan from Markdown format.

        Expected format:
        # Goal: Implement feature X

        ## Tasks
        1. [type:testing] Write unit tests
        2. [type:code_generator, depends:1] Implement core logic
        3. [type:documentation] Update README

        Args:
            markdown_text: Markdown-formatted plan
            plan_id: ID for the plan

        Returns:
            Parsed Plan object
        """
        lines = markdown_text.strip().split('\n')
        goal = "No goal specified"
        tasks = []

        # Extract goal
        for line in lines:
            if line.startswith('# Goal:'):
                goal = line.replace('# Goal:', '').strip()
                break

        # Extract tasks
        task_pattern = re.compile(r'^(\d+)\.\s*(?:\[(.*?)\])?\s*(.+)$')
        for line in lines:
            match = task_pattern.match(line.strip())
            if match:
                task_num, metadata_str, description = match.groups()

                task_type = None
                dependencies = []
                priority = 0

                # Parse metadata
                if metadata_str:
                    for item in metadata_str.split(','):
                        item = item.strip()
                        if item.startswith('type:'):
                            task_type = item.replace('type:', '').strip()
                        elif item.startswith('depends:'):
                            dep_nums = item.replace('depends:', '').strip()
                            dependencies = [f"task_{n.strip()}" for n in dep_nums.split('&')]
                        elif item.startswith('priority:'):
                            priority = int(item.replace('priority:', '').strip())

                task = Task(
                    id=f"task_{task_num}",
                    description=description.strip(),
                    task_type=task_type,
                    dependencies=dependencies,
                    priority=priority
                )
                tasks.append(task)

        return Plan(id=plan_id, goal=goal, tasks=tasks)


class ExecutionCoordinator:
    """
    Coordinates task execution across multiple agents.

    Manages:
    - Dependency resolution
    - Parallel execution where possible
    - Result aggregation
    - Error handling and recovery
    """

    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.execution_context: Dict[str, Any] = {}

    def execute_plan(
        self,
        plan: Plan,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete plan.

        Args:
            plan: Plan to execute
            context: Additional execution context

        Returns:
            Dictionary containing execution results:
            {
                "plan_id": str,
                "status": "completed" | "partial" | "failed",
                "completed_tasks": List[str],
                "failed_tasks": List[str],
                "results": Dict[str, Any]
            }
        """
        if context:
            self.execution_context.update(context)
        if plan.context:
            self.execution_context.update(plan.context)

        completed_tasks = set()
        failed_tasks = set()
        results = {}

        # Topological sort for dependency resolution
        sorted_tasks = self._topological_sort(plan.tasks)

        for task in sorted_tasks:
            if not task.is_ready(completed_tasks):
                # Skip tasks whose dependencies failed
                task.status = TaskStatus.SKIPPED
                continue

            try:
                # Get appropriate agent
                if not task.assigned_agent:
                    raise ValueError(f"Task {task.id} has no assigned agent")

                agent = self.registry.get_agent(task.assigned_agent, task)
                if not agent:
                    raise ValueError(f"No agent available for type {task.assigned_agent}")

                # Execute task
                task.status = TaskStatus.IN_PROGRESS
                result = agent.execute(task, self.execution_context)

                # Update status and store result
                task.status = TaskStatus.COMPLETED
                task.result = result
                completed_tasks.add(task.id)
                results[task.id] = result

                # Update context with result for downstream tasks
                self.execution_context[f"task_result_{task.id}"] = result

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                failed_tasks.add(task.id)
                results[task.id] = {"error": str(e)}

        # Determine overall status
        if len(failed_tasks) == 0:
            status = "completed"
        elif len(completed_tasks) > 0:
            status = "partial"
        else:
            status = "failed"

        return {
            "plan_id": plan.id,
            "status": status,
            "completed_tasks": list(completed_tasks),
            "failed_tasks": list(failed_tasks),
            "results": results,
            "context": self.execution_context
        }

    def _topological_sort(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks based on dependencies using topological sort.

        Args:
            tasks: List of tasks to sort

        Returns:
            Sorted list of tasks
        """
        # Build dependency graph
        task_map = {task.id: task for task in tasks}
        in_degree = {task.id: len(task.dependencies) for task in tasks}

        # Find tasks with no dependencies
        queue = [task for task in tasks if in_degree[task.id] == 0]
        sorted_tasks = []

        while queue:
            # Sort by priority before processing
            queue.sort(key=lambda t: t.priority, reverse=True)
            current = queue.pop(0)
            sorted_tasks.append(current)

            # Update in-degrees of dependent tasks
            for task in tasks:
                if current.id in task.dependencies:
                    in_degree[task.id] -= 1
                    if in_degree[task.id] == 0:
                        queue.append(task)

        # Check for cycles
        if len(sorted_tasks) != len(tasks):
            raise ValueError("Circular dependency detected in task dependencies")

        return sorted_tasks


class TaskDispatcher:
    """
    Main dispatcher that coordinates plan interpretation and task assignment.

    This is the primary interface for the dispatcher skill. It integrates:
    - Plan parsing
    - Semantic routing
    - Agent assignment
    - Execution coordination
    """

    def __init__(self):
        self.routing_map = RoutingMap()
        self.agent_registry = AgentRegistry()
        self.plan_parser = PlanParser()
        self.execution_coordinator = ExecutionCoordinator(self.agent_registry)

        # Initialize default routing rules
        self._setup_default_routing()

    def _setup_default_routing(self):
        """Setup default routing rules for common task types."""
        # Code-related tasks
        self.routing_map.add_rule(
            r'\b(implement|code|write|create|develop|build)\b.*\b(function|class|module|component)\b',
            AgentType.CODE_GENERATOR,
            priority=2.0
        )

        # Testing tasks
        self.routing_map.add_rule(
            r'\b(test|unit test|integration test|e2e|pytest|jest)\b',
            AgentType.TESTING,
            priority=2.0
        )

        # Documentation tasks
        self.routing_map.add_rule(
            r'\b(document|readme|docstring|comment|doc)\b',
            AgentType.DOCUMENTATION,
            priority=2.0
        )

        # Debugging tasks
        self.routing_map.add_rule(
            r'\b(debug|fix|bug|error|issue|troubleshoot)\b',
            AgentType.DEBUGGING,
            priority=2.0
        )

        # Refactoring tasks
        self.routing_map.add_rule(
            r'\b(refactor|clean|optimize|improve|reorganize)\b',
            AgentType.REFACTORING,
            priority=1.5
        )

        # Data processing tasks
        self.routing_map.add_rule(
            r'\b(process|transform|parse|extract|load|etl)\b',
            AgentType.DATA_PROCESSOR,
            priority=1.5
        )

        # Analysis tasks
        self.routing_map.add_rule(
            r'\b(analyze|review|inspect|evaluate|assess)\b',
            AgentType.ANALYSIS,
            priority=1.5
        )

        # Optimization tasks
        self.routing_map.add_rule(
            r'\b(optimize|performance|speed up|improve efficiency)\b',
            AgentType.OPTIMIZATION,
            priority=1.5
        )

        # Keyword mappings
        self.routing_map.add_keyword_mapping("test", AgentType.TESTING)
        self.routing_map.add_keyword_mapping("documentation", AgentType.DOCUMENTATION)
        self.routing_map.add_keyword_mapping("refactor", AgentType.REFACTORING)
        self.routing_map.add_keyword_mapping("bug", AgentType.DEBUGGING)

    def register_agent(self, agent: Agent):
        """
        Register a specialized agent with the dispatcher.

        Args:
            agent: Agent instance to register
        """
        self.agent_registry.register_agent(agent)

    def dispatch_plan(
        self,
        plan_input: Union[Dict[str, Any], str, Plan],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main dispatch method: parse plan, route tasks, and execute.

        Args:
            plan_input: Plan in dict, markdown string, or Plan object format
            context: Additional execution context

        Returns:
            Execution results dictionary
        """
        # Parse plan if needed
        if isinstance(plan_input, dict):
            plan = self.plan_parser.parse_dict(plan_input)
        elif isinstance(plan_input, str):
            plan = self.plan_parser.parse_markdown(plan_input)
        elif isinstance(plan_input, Plan):
            plan = plan_input
        else:
            raise ValueError(f"Unsupported plan input type: {type(plan_input)}")

        # Route each task to appropriate agent
        for task in plan.tasks:
            if task.assigned_agent is None:
                task.assigned_agent = self.routing_map.route(task)
                task.status = TaskStatus.ASSIGNED

        # Execute plan
        results = self.execution_coordinator.execute_plan(plan, context)

        return results

    def analyze_plan(self, plan_input: Union[Dict[str, Any], str, Plan]) -> Dict[str, Any]:
        """
        Analyze a plan without executing it.

        Returns routing decisions, dependency graph, and execution order.

        Args:
            plan_input: Plan in dict, markdown string, or Plan object format

        Returns:
            Analysis results including:
            - routing_assignments: Dict[task_id, agent_type]
            - dependency_graph: Visual representation
            - execution_order: Topologically sorted task IDs
            - warnings: List of potential issues
        """
        # Parse plan
        if isinstance(plan_input, dict):
            plan = self.plan_parser.parse_dict(plan_input)
        elif isinstance(plan_input, str):
            plan = self.plan_parser.parse_markdown(plan_input)
        elif isinstance(plan_input, Plan):
            plan = plan_input
        else:
            raise ValueError(f"Unsupported plan input type: {type(plan_input)}")

        # Assign agents
        routing_assignments = {}
        for task in plan.tasks:
            agent_type = self.routing_map.route(task)
            routing_assignments[task.id] = agent_type.value

        # Get execution order
        try:
            sorted_tasks = self.execution_coordinator._topological_sort(plan.tasks)
            execution_order = [task.id for task in sorted_tasks]
        except ValueError as e:
            execution_order = []
            warnings = [str(e)]
        else:
            warnings = []

        # Build dependency graph representation
        dependency_graph = {}
        for task in plan.tasks:
            dependency_graph[task.id] = {
                "description": task.description,
                "dependencies": task.dependencies,
                "assigned_agent": routing_assignments[task.id]
            }

        # Check for warnings
        for task in plan.tasks:
            agent_type = AgentType(routing_assignments[task.id])
            agent = self.agent_registry.get_agent(agent_type, task)
            if not agent:
                warnings.append(f"No agent registered for type {agent_type.value} (task: {task.id})")

        return {
            "plan_id": plan.id,
            "goal": plan.goal,
            "routing_assignments": routing_assignments,
            "dependency_graph": dependency_graph,
            "execution_order": execution_order,
            "warnings": warnings
        }


# Example agent implementations for demonstration
class GenericAgent(Agent):
    """Generic agent that can handle basic tasks."""

    def __init__(self):
        super().__init__(AgentType.GENERIC, "GenericAgent")
        self.capabilities = ["basic_execution"]

    def can_handle(self, task: Task) -> bool:
        return True

    def execute(self, task: Task, context: Dict[str, Any]) -> Any:
        return {
            "status": "completed",
            "message": f"Executed task: {task.description}",
            "agent": self.name
        }


class CodeGeneratorAgent(Agent):
    """Agent specialized in code generation tasks."""

    def __init__(self):
        super().__init__(AgentType.CODE_GENERATOR, "CodeGeneratorAgent")
        self.capabilities = ["code_generation", "implementation"]

    def can_handle(self, task: Task) -> bool:
        keywords = ["implement", "code", "write", "create", "develop"]
        return any(kw in task.description.lower() for kw in keywords)

    def execute(self, task: Task, context: Dict[str, Any]) -> Any:
        return {
            "status": "completed",
            "message": f"Generated code for: {task.description}",
            "agent": self.name,
            "code": "# Generated code placeholder"
        }


class QAAgent(Agent):
    """Agent specialized in testing and quality assurance tasks."""

    def __init__(self):
        super().__init__(AgentType.TESTING, "QAAgent")
        self.capabilities = ["unit_testing", "integration_testing"]

    def can_handle(self, task: Task) -> bool:
        keywords = ["test", "pytest", "unittest", "jest"]
        return any(kw in task.description.lower() for kw in keywords)

    def execute(self, task: Task, context: Dict[str, Any]) -> Any:
        return {
            "status": "completed",
            "message": f"Created tests for: {task.description}",
            "agent": self.name,
            "tests_passed": True,
            "coverage": 0.95
        }


def create_default_dispatcher() -> TaskDispatcher:
    """
    Create a dispatcher with default agents registered.

    Returns:
        TaskDispatcher instance with basic agents
    """
    dispatcher = TaskDispatcher()

    # Register default agents
    dispatcher.register_agent(GenericAgent())
    dispatcher.register_agent(CodeGeneratorAgent())
    dispatcher.register_agent(QAAgent())

    return dispatcher


if __name__ == "__main__":
    # Example usage
    print("=" * 80)
    print("Dispatcher Skill - Example Usage")
    print("=" * 80)

    # Create dispatcher with default agents
    dispatcher = create_default_dispatcher()

    # Example plan in dictionary format
    example_plan = {
        "id": "feature_001",
        "goal": "Implement user authentication feature",
        "tasks": [
            {
                "id": "task_1",
                "description": "Write unit tests for authentication module",
                "task_type": "testing",
                "dependencies": [],
                "priority": 2
            },
            {
                "id": "task_2",
                "description": "Implement login function with JWT tokens",
                "dependencies": ["task_1"],
                "priority": 1
            },
            {
                "id": "task_3",
                "description": "Create user registration endpoint",
                "dependencies": ["task_2"],
                "priority": 1
            }
        ],
        "context": {
            "framework": "FastAPI",
            "database": "PostgreSQL"
        }
    }

    # Analyze the plan first
    print("\n" + "=" * 80)
    print("PLAN ANALYSIS")
    print("=" * 80)
    analysis = dispatcher.analyze_plan(example_plan)
    print(f"\nPlan ID: {analysis['plan_id']}")
    print(f"Goal: {analysis['goal']}")
    print(f"\nRouting Assignments:")
    for task_id, agent_type in analysis['routing_assignments'].items():
        task_desc = analysis['dependency_graph'][task_id]['description']
        print(f"  {task_id} -> {agent_type}")
        print(f"    Description: {task_desc}")

    print(f"\nExecution Order: {' -> '.join(analysis['execution_order'])}")

    if analysis['warnings']:
        print(f"\nWarnings:")
        for warning in analysis['warnings']:
            print(f"  - {warning}")

    # Execute the plan
    print("\n" + "=" * 80)
    print("PLAN EXECUTION")
    print("=" * 80)
    results = dispatcher.dispatch_plan(example_plan)

    print(f"\nPlan Status: {results['status']}")
    print(f"Completed Tasks: {len(results['completed_tasks'])}")
    print(f"Failed Tasks: {len(results['failed_tasks'])}")

    print(f"\nTask Results:")
    for task_id, result in results['results'].items():
        print(f"\n  {task_id}:")
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"    {key}: {value}")
        else:
            print(f"    {result}")

    # Example with Markdown format
    print("\n" + "=" * 80)
    print("MARKDOWN PLAN EXAMPLE")
    print("=" * 80)

    markdown_plan = """
# Goal: Refactor data processing pipeline

## Tasks
1. [type:analysis, priority:2] Analyze current pipeline performance
2. [type:refactoring, depends:1] Refactor ETL module for better efficiency
3. [type:testing, depends:2] Add comprehensive unit tests
4. [type:documentation, depends:2&3] Update technical documentation
"""

    print("\nMarkdown Plan:")
    print(markdown_plan)

    md_analysis = dispatcher.analyze_plan(markdown_plan)
    print(f"\nParsed {len(md_analysis['execution_order'])} tasks from markdown")
    print(f"Execution order: {' -> '.join(md_analysis['execution_order'])}")

    print("\n" + "=" * 80)
    print("Example Complete!")
    print("=" * 80)
