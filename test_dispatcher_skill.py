"""
Unit tests for the Dispatcher Skill module.

Tests cover:
- Task and Plan data structures
- Agent implementations
- Routing map logic
- Agent registry
- Plan parsing (dict and markdown)
- Execution coordination
- Task dispatcher integration
"""

import pytest
from typing import Dict, Any
from dispatcher_skill import (
    Task, Plan, Agent, TaskStatus, AgentType,
    RoutingMap, AgentRegistry, PlanParser, ExecutionCoordinator, TaskDispatcher,
    GenericAgent, CodeGeneratorAgent, QAAgent,
    create_default_dispatcher
)


# ============================================================================
# Test Data Structures
# ============================================================================

class TestTask:
    """Test Task data structure."""

    def test_task_creation(self):
        task = Task(
            id="task_1",
            description="Test task",
            priority=1
        )
        assert task.id == "task_1"
        assert task.description == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == 1
        assert len(task.dependencies) == 0

    def test_task_dependencies(self):
        task = Task(
            id="task_2",
            description="Dependent task",
            dependencies=["task_1"]
        )
        assert not task.is_ready(set())
        assert task.is_ready({"task_1"})

    def test_task_multiple_dependencies(self):
        task = Task(
            id="task_3",
            description="Multi-dependent task",
            dependencies=["task_1", "task_2"]
        )
        assert not task.is_ready({"task_1"})
        assert task.is_ready({"task_1", "task_2"})


class TestPlan:
    """Test Plan data structure."""

    def test_plan_creation(self):
        tasks = [
            Task(id="task_1", description="First task"),
            Task(id="task_2", description="Second task")
        ]
        plan = Plan(
            id="plan_1",
            goal="Test goal",
            tasks=tasks
        )
        assert plan.id == "plan_1"
        assert plan.goal == "Test goal"
        assert len(plan.tasks) == 2

    def test_get_task_by_id(self):
        tasks = [
            Task(id="task_1", description="First task"),
            Task(id="task_2", description="Second task")
        ]
        plan = Plan(id="plan_1", goal="Test", tasks=tasks)

        task = plan.get_task_by_id("task_1")
        assert task is not None
        assert task.id == "task_1"

        task = plan.get_task_by_id("nonexistent")
        assert task is None


# ============================================================================
# Test Agent Implementations
# ============================================================================

class MockAgent(Agent):
    """Mock agent for testing."""

    def __init__(self, agent_type: AgentType, name: str, should_handle: bool = True):
        super().__init__(agent_type, name)
        self.should_handle = should_handle
        self.executed_tasks = []

    def can_handle(self, task: Task) -> bool:
        return self.should_handle

    def execute(self, task: Task, context: Dict[str, Any]) -> Any:
        self.executed_tasks.append(task.id)
        return {"status": "completed", "task_id": task.id}


class TestAgentImplementations:
    """Test agent implementations."""

    def test_generic_agent(self):
        agent = GenericAgent()
        assert agent.agent_type == AgentType.GENERIC
        assert agent.can_handle(Task(id="any", description="any task"))

        result = agent.execute(
            Task(id="test", description="test task"),
            {}
        )
        assert result["status"] == "completed"

    def test_code_generator_agent(self):
        agent = CodeGeneratorAgent()
        assert agent.agent_type == AgentType.CODE_GENERATOR

        # Should handle code-related tasks
        task1 = Task(id="t1", description="Implement a function")
        assert agent.can_handle(task1)

        task2 = Task(id="t2", description="Create a new class for users")
        assert agent.can_handle(task2)

        # Should not handle pure test tasks (no code generation keywords)
        task3 = Task(id="t3", description="Run the test suite")
        assert not agent.can_handle(task3)

    def test_qa_agent(self):
        agent = QAAgent()
        assert agent.agent_type == AgentType.TESTING

        # Should handle test-related tasks
        task1 = Task(id="t1", description="Write pytest tests")
        assert agent.can_handle(task1)

        task2 = Task(id="t2", description="Implement a function")
        assert not agent.can_handle(task2)


# ============================================================================
# Test Routing Map
# ============================================================================

class TestRoutingMap:
    """Test RoutingMap functionality."""

    def test_pattern_based_routing(self):
        routing_map = RoutingMap()
        routing_map.add_rule(r'\btest\b', AgentType.TESTING)

        task = Task(id="t1", description="Write test cases")
        assert routing_map.route(task) == AgentType.TESTING

    def test_keyword_routing(self):
        routing_map = RoutingMap()
        routing_map.add_keyword_mapping("refactor", AgentType.REFACTORING)

        task = Task(id="t1", description="Refactor the module")
        assert routing_map.route(task) == AgentType.REFACTORING

    def test_priority_routing(self):
        routing_map = RoutingMap()
        routing_map.add_rule(r'\bcode\b', AgentType.CODE_GENERATOR, priority=1.0)
        routing_map.add_rule(r'\bcode\b', AgentType.DEBUGGING, priority=2.0)

        task = Task(id="t1", description="Fix code bug")
        # Should match higher priority rule
        assert routing_map.route(task) == AgentType.DEBUGGING

    def test_explicit_task_type(self):
        routing_map = RoutingMap()
        task = Task(
            id="t1",
            description="Some task",
            task_type="testing"
        )
        assert routing_map.route(task) == AgentType.TESTING

    def test_fallback_routing(self):
        routing_map = RoutingMap()
        routing_map.set_fallback_agent(AgentType.ANALYSIS)

        task = Task(id="t1", description="Unknown task type")
        assert routing_map.route(task) == AgentType.ANALYSIS


# ============================================================================
# Test Agent Registry
# ============================================================================

class TestAgentRegistry:
    """Test AgentRegistry functionality."""

    def test_register_and_get_agent(self):
        registry = AgentRegistry()
        agent = MockAgent(AgentType.TESTING, "TestAgent")

        registry.register_agent(agent)
        retrieved = registry.get_agent(AgentType.TESTING)

        assert retrieved is not None
        assert retrieved.name == "TestAgent"

    def test_get_nonexistent_agent(self):
        registry = AgentRegistry()
        agent = registry.get_agent(AgentType.TESTING)
        assert agent is None

    def test_multiple_agents_same_type(self):
        registry = AgentRegistry()
        agent1 = MockAgent(AgentType.TESTING, "Agent1")
        agent2 = MockAgent(AgentType.TESTING, "Agent2")

        registry.register_agent(agent1)
        registry.register_agent(agent2)

        all_agents = registry.get_all_agents(AgentType.TESTING)
        assert len(all_agents) == 2

    def test_get_agent_with_task_matching(self):
        registry = AgentRegistry()
        agent1 = MockAgent(AgentType.TESTING, "Agent1", should_handle=False)
        agent2 = MockAgent(AgentType.TESTING, "Agent2", should_handle=True)

        registry.register_agent(agent1)
        registry.register_agent(agent2)

        task = Task(id="t1", description="Test task")
        agent = registry.get_agent(AgentType.TESTING, task)

        # Should get the agent that can handle the task
        assert agent.name == "Agent2"

    def test_list_agent_types(self):
        registry = AgentRegistry()
        registry.register_agent(MockAgent(AgentType.TESTING, "A1"))
        registry.register_agent(MockAgent(AgentType.CODE_GENERATOR, "A2"))

        types = registry.list_agent_types()
        assert AgentType.TESTING in types
        assert AgentType.CODE_GENERATOR in types


# ============================================================================
# Test Plan Parser
# ============================================================================

class TestPlanParser:
    """Test PlanParser functionality."""

    def test_parse_dict_basic(self):
        plan_dict = {
            "id": "plan_1",
            "goal": "Test goal",
            "tasks": [
                {
                    "id": "task_1",
                    "description": "First task",
                    "priority": 1
                }
            ]
        }

        plan = PlanParser.parse_dict(plan_dict)
        assert plan.id == "plan_1"
        assert plan.goal == "Test goal"
        assert len(plan.tasks) == 1
        assert plan.tasks[0].id == "task_1"

    def test_parse_dict_with_dependencies(self):
        plan_dict = {
            "id": "plan_1",
            "goal": "Test",
            "tasks": [
                {"id": "task_1", "description": "First"},
                {"id": "task_2", "description": "Second", "dependencies": ["task_1"]}
            ]
        }

        plan = PlanParser.parse_dict(plan_dict)
        assert plan.tasks[1].dependencies == ["task_1"]

    def test_parse_dict_with_context(self):
        plan_dict = {
            "id": "plan_1",
            "goal": "Test",
            "tasks": [],
            "context": {"key": "value"}
        }

        plan = PlanParser.parse_dict(plan_dict)
        assert plan.context["key"] == "value"

    def test_parse_markdown_basic(self):
        markdown = """
# Goal: Build feature X

## Tasks
1. Write tests
2. Implement code
3. Update docs
"""
        plan = PlanParser.parse_markdown(markdown)
        assert plan.goal == "Build feature X"
        assert len(plan.tasks) == 3
        assert plan.tasks[0].id == "task_1"
        assert plan.tasks[0].description == "Write tests"

    def test_parse_markdown_with_metadata(self):
        markdown = """
# Goal: Test project

## Tasks
1. [type:testing, priority:2] Write unit tests
2. [type:code_generator, depends:1] Implement feature
"""
        plan = PlanParser.parse_markdown(markdown)
        assert len(plan.tasks) == 2

        task1 = plan.tasks[0]
        assert task1.task_type == "testing"
        assert task1.priority == 2

        task2 = plan.tasks[1]
        assert task2.task_type == "code_generator"
        assert task2.dependencies == ["task_1"]

    def test_parse_markdown_multiple_dependencies(self):
        markdown = """
# Goal: Complex dependencies

## Tasks
1. First task
2. Second task
3. [depends:1&2] Third task depends on both
"""
        plan = PlanParser.parse_markdown(markdown)
        task3 = plan.tasks[2]
        assert "task_1" in task3.dependencies
        assert "task_2" in task3.dependencies


# ============================================================================
# Test Execution Coordinator
# ============================================================================

class TestExecutionCoordinator:
    """Test ExecutionCoordinator functionality."""

    def test_topological_sort_simple(self):
        registry = AgentRegistry()
        coordinator = ExecutionCoordinator(registry)

        tasks = [
            Task(id="task_1", description="First"),
            Task(id="task_2", description="Second", dependencies=["task_1"]),
            Task(id="task_3", description="Third", dependencies=["task_2"])
        ]

        sorted_tasks = coordinator._topological_sort(tasks)
        ids = [t.id for t in sorted_tasks]

        assert ids.index("task_1") < ids.index("task_2")
        assert ids.index("task_2") < ids.index("task_3")

    def test_topological_sort_with_priorities(self):
        registry = AgentRegistry()
        coordinator = ExecutionCoordinator(registry)

        tasks = [
            Task(id="task_1", description="Low priority", priority=1),
            Task(id="task_2", description="High priority", priority=10),
            Task(id="task_3", description="Medium priority", priority=5)
        ]

        sorted_tasks = coordinator._topological_sort(tasks)
        # Higher priority tasks should come first when no dependencies
        assert sorted_tasks[0].id == "task_2"

    def test_topological_sort_circular_dependency(self):
        registry = AgentRegistry()
        coordinator = ExecutionCoordinator(registry)

        tasks = [
            Task(id="task_1", description="First", dependencies=["task_2"]),
            Task(id="task_2", description="Second", dependencies=["task_1"])
        ]

        with pytest.raises(ValueError, match="Circular dependency"):
            coordinator._topological_sort(tasks)

    def test_execute_plan_simple(self):
        registry = AgentRegistry()
        agent = MockAgent(AgentType.GENERIC, "TestAgent")
        registry.register_agent(agent)

        coordinator = ExecutionCoordinator(registry)

        tasks = [
            Task(id="task_1", description="First", assigned_agent=AgentType.GENERIC)
        ]
        plan = Plan(id="plan_1", goal="Test", tasks=tasks)

        result = coordinator.execute_plan(plan)

        assert result["status"] == "completed"
        assert "task_1" in result["completed_tasks"]
        assert len(result["failed_tasks"]) == 0

    def test_execute_plan_with_dependencies(self):
        registry = AgentRegistry()
        agent = MockAgent(AgentType.GENERIC, "TestAgent")
        registry.register_agent(agent)

        coordinator = ExecutionCoordinator(registry)

        tasks = [
            Task(id="task_1", description="First", assigned_agent=AgentType.GENERIC),
            Task(id="task_2", description="Second", dependencies=["task_1"],
                 assigned_agent=AgentType.GENERIC)
        ]
        plan = Plan(id="plan_1", goal="Test", tasks=tasks)

        result = coordinator.execute_plan(plan)

        # Both tasks should complete
        assert result["status"] == "completed"
        assert len(result["completed_tasks"]) == 2

        # Verify execution order
        assert agent.executed_tasks.index("task_1") < agent.executed_tasks.index("task_2")

    def test_execute_plan_with_context(self):
        registry = AgentRegistry()

        class ContextAwareAgent(MockAgent):
            def execute(self, task: Task, context: Dict[str, Any]) -> Any:
                return {"value": context.get("test_key", "not found")}

        agent = ContextAwareAgent(AgentType.GENERIC, "ContextAgent")
        registry.register_agent(agent)

        coordinator = ExecutionCoordinator(registry)

        tasks = [Task(id="task_1", description="Test", assigned_agent=AgentType.GENERIC)]
        plan = Plan(id="plan_1", goal="Test", tasks=tasks)

        result = coordinator.execute_plan(plan, context={"test_key": "test_value"})

        assert result["results"]["task_1"]["value"] == "test_value"

    def test_execute_plan_missing_agent(self):
        registry = AgentRegistry()
        coordinator = ExecutionCoordinator(registry)

        tasks = [
            Task(id="task_1", description="Test", assigned_agent=AgentType.TESTING)
        ]
        plan = Plan(id="plan_1", goal="Test", tasks=tasks)

        result = coordinator.execute_plan(plan)

        assert result["status"] == "failed"
        assert "task_1" in result["failed_tasks"]


# ============================================================================
# Test Task Dispatcher
# ============================================================================

class TestTaskDispatcher:
    """Test TaskDispatcher integration."""

    def test_dispatcher_initialization(self):
        dispatcher = TaskDispatcher()
        assert dispatcher.routing_map is not None
        assert dispatcher.agent_registry is not None
        assert dispatcher.plan_parser is not None
        assert dispatcher.execution_coordinator is not None

    def test_register_agent(self):
        dispatcher = TaskDispatcher()
        agent = MockAgent(AgentType.TESTING, "TestAgent")

        dispatcher.register_agent(agent)
        retrieved = dispatcher.agent_registry.get_agent(AgentType.TESTING)

        assert retrieved is not None
        assert retrieved.name == "TestAgent"

    def test_default_routing_rules(self):
        dispatcher = TaskDispatcher()

        # Test code generation routing
        task1 = Task(id="t1", description="Implement a new function")
        assert dispatcher.routing_map.route(task1) == AgentType.CODE_GENERATOR

        # Test testing routing
        task2 = Task(id="t2", description="Write unit tests")
        assert dispatcher.routing_map.route(task2) == AgentType.TESTING

        # Test documentation routing
        task3 = Task(id="t3", description="Update the README documentation")
        assert dispatcher.routing_map.route(task3) == AgentType.DOCUMENTATION

        # Test debugging routing
        task4 = Task(id="t4", description="Fix the bug in authentication")
        assert dispatcher.routing_map.route(task4) == AgentType.DEBUGGING

    def test_dispatch_plan_dict(self):
        dispatcher = create_default_dispatcher()

        plan_dict = {
            "id": "test_plan",
            "goal": "Test dispatch",
            "tasks": [
                {"id": "task_1", "description": "Write tests for module"},
                {"id": "task_2", "description": "Implement the feature", "dependencies": ["task_1"]}
            ]
        }

        result = dispatcher.dispatch_plan(plan_dict)

        assert result["plan_id"] == "test_plan"
        assert result["status"] == "completed"
        assert len(result["completed_tasks"]) == 2

    def test_dispatch_plan_markdown(self):
        dispatcher = create_default_dispatcher()

        markdown = """
# Goal: Build authentication

## Tasks
1. Write unit tests
2. [depends:1] Implement login function
"""

        result = dispatcher.dispatch_plan(markdown)
        assert result["status"] == "completed"
        assert len(result["completed_tasks"]) == 2

    def test_analyze_plan(self):
        dispatcher = create_default_dispatcher()

        plan_dict = {
            "id": "test_plan",
            "goal": "Test analysis",
            "tasks": [
                {"id": "task_1", "description": "Write tests"},
                {"id": "task_2", "description": "Implement code", "dependencies": ["task_1"]}
            ]
        }

        analysis = dispatcher.analyze_plan(plan_dict)

        assert analysis["plan_id"] == "test_plan"
        assert analysis["goal"] == "Test analysis"
        assert "task_1" in analysis["routing_assignments"]
        assert "task_2" in analysis["routing_assignments"]
        assert len(analysis["execution_order"]) == 2

    def test_analyze_plan_with_warnings(self):
        dispatcher = TaskDispatcher()  # No agents registered

        plan_dict = {
            "id": "test_plan",
            "goal": "Test",
            "tasks": [
                {"id": "task_1", "description": "Write tests"}
            ]
        }

        analysis = dispatcher.analyze_plan(plan_dict)

        # Should have warnings about missing agents
        assert len(analysis["warnings"]) > 0

    def test_dispatch_plan_object(self):
        dispatcher = create_default_dispatcher()

        tasks = [
            Task(id="task_1", description="Write tests"),
            Task(id="task_2", description="Implement feature", dependencies=["task_1"])
        ]
        plan = Plan(id="plan_1", goal="Test", tasks=tasks)

        result = dispatcher.dispatch_plan(plan)
        assert result["status"] == "completed"


# ============================================================================
# Test Default Dispatcher Creation
# ============================================================================

class TestDefaultDispatcher:
    """Test default dispatcher creation."""

    def test_create_default_dispatcher(self):
        dispatcher = create_default_dispatcher()

        # Should have agents registered
        assert len(dispatcher.agent_registry.list_agent_types()) > 0

        # Should have default routing rules
        task = Task(id="t1", description="Write unit tests")
        agent_type = dispatcher.routing_map.route(task)
        assert agent_type == AgentType.TESTING


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_workflow(self):
        """Test a complete workflow from plan to execution."""
        dispatcher = create_default_dispatcher()

        plan = {
            "id": "feature_auth",
            "goal": "Implement authentication",
            "tasks": [
                {
                    "id": "task_1",
                    "description": "Write unit tests for auth module",
                    "priority": 2
                },
                {
                    "id": "task_2",
                    "description": "Implement JWT token generation",
                    "dependencies": ["task_1"],
                    "priority": 1
                },
                {
                    "id": "task_3",
                    "description": "Write integration tests",
                    "dependencies": ["task_2"],
                    "priority": 1
                }
            ],
            "context": {
                "framework": "Flask",
                "auth_method": "JWT"
            }
        }

        # Analyze first
        analysis = dispatcher.analyze_plan(plan)
        assert len(analysis["warnings"]) == 0
        assert len(analysis["execution_order"]) == 3

        # Execute
        result = dispatcher.dispatch_plan(plan)
        assert result["status"] == "completed"
        assert len(result["completed_tasks"]) == 3
        assert len(result["failed_tasks"]) == 0

    def test_mixed_success_failure(self):
        """Test handling of mixed success and failure."""
        dispatcher = TaskDispatcher()

        class FailingAgent(Agent):
            def __init__(self):
                super().__init__(AgentType.GENERIC, "FailingAgent")

            def can_handle(self, task: Task) -> bool:
                return True

            def execute(self, task: Task, context: Dict[str, Any]) -> Any:
                if "fail" in task.description.lower():
                    raise Exception("Simulated failure")
                return {"status": "ok"}

        dispatcher.register_agent(FailingAgent())

        plan = {
            "id": "test",
            "goal": "Test failures",
            "tasks": [
                {"id": "task_1", "description": "This will succeed"},
                {"id": "task_2", "description": "This will FAIL"},
                {"id": "task_3", "description": "This depends on failure",
                 "dependencies": ["task_2"]}
            ]
        }

        result = dispatcher.dispatch_plan(plan)
        assert result["status"] == "partial"
        assert "task_1" in result["completed_tasks"]
        assert "task_2" in result["failed_tasks"]
        # task_3 might be skipped since task_2 failed


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
