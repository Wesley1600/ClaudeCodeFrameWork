"""
Node Definitions for LangGraph Agent Orchestration

This module defines various node types that can be used in LangGraph workflows.
Nodes are the functional units that process state and perform actions.
"""

from typing import Dict, Any, Optional, Callable, List
import logging
from datetime import datetime

from .state import WorkflowState, MessageRole, Message, StateManager

logger = logging.getLogger(__name__)


class BaseNode:
    """
    Base class for all workflow nodes.

    Nodes are callable objects that take state and return updated state.
    """

    def __init__(self, name: str, description: str = ""):
        """
        Initialize a node.

        Args:
            name: Unique name for the node
            description: Optional description of node functionality
        """
        self.name = name
        self.description = description
        self.execution_count = 0
        self.last_execution_time: Optional[datetime] = None

    def __call__(self, state: WorkflowState) -> WorkflowState:
        """
        Execute the node.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        logger.info(f"Executing node: {self.name}")
        self.execution_count += 1
        self.last_execution_time = datetime.now()

        try:
            result = self.execute(state)
            return result
        except Exception as e:
            logger.error(f"Error in node {self.name}: {e}")
            return StateManager.record_error(state, e, {"node": self.name})

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute node logic. Override in subclasses.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        raise NotImplementedError("Subclasses must implement execute()")


class AgentNode(BaseNode):
    """
    Node that executes an agent from the framework.

    Integrates with the existing BaseAgent infrastructure.
    """

    def __init__(
        self,
        name: str,
        agent_factory: Callable[[], Any],
        description: str = "",
        process_output: Optional[Callable[[Any], str]] = None
    ):
        """
        Initialize an agent node.

        Args:
            name: Node name
            agent_factory: Factory function to create agent instance
            description: Node description
            process_output: Optional function to process agent output
        """
        super().__init__(name, description)
        self.agent_factory = agent_factory
        self.process_output = process_output or (lambda x: str(x))

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute the agent.

        Args:
            state: Current workflow state

        Returns:
            Updated state with agent results
        """
        # Get the latest message as input
        latest_message = StateManager.get_latest_message(state)
        input_text = latest_message.content if latest_message else ""

        # Create and execute agent
        agent = self.agent_factory()
        logger.info(f"Executing agent: {self.name}")

        # Execute agent (implementation depends on your BaseAgent interface)
        # This is a placeholder - adjust based on actual agent API
        result = self._execute_agent(agent, input_text, state)

        # Process output
        output = self.process_output(result)

        # Update state
        new_state = StateManager.add_message(
            state,
            MessageRole.ASSISTANT,
            output,
            metadata={"agent": self.name, "timestamp": datetime.now().isoformat()}
        )

        new_state = StateManager.record_agent_execution(new_state, self.name, result)
        new_state["current_agent"] = self.name
        new_state["agent_stack"] = list(state["agent_stack"]) + [self.name]

        return new_state

    def _execute_agent(self, agent: Any, input_text: str, state: WorkflowState) -> Any:
        """
        Execute the agent. Override for custom execution logic.

        Args:
            agent: Agent instance
            input_text: Input text
            state: Current state

        Returns:
            Agent execution result
        """
        # Default implementation - adjust based on your agent interface
        if hasattr(agent, 'process'):
            return agent.process(input_text, context=state["context"])
        elif hasattr(agent, 'run'):
            return agent.run(input_text)
        else:
            logger.warning(f"Agent {self.name} has no known execution method")
            return {"status": "not_implemented", "input": input_text}


class SkillNode(BaseNode):
    """
    Node that executes a skill from the framework.

    Integrates with the existing Skill infrastructure.
    """

    def __init__(
        self,
        name: str,
        skill_factory: Callable[[], Any],
        description: str = "",
        input_mapper: Optional[Callable[[WorkflowState], Dict[str, Any]]] = None,
        output_processor: Optional[Callable[[Any], str]] = None
    ):
        """
        Initialize a skill node.

        Args:
            name: Node name
            skill_factory: Factory function to create skill instance
            description: Node description
            input_mapper: Function to map state to skill inputs
            output_processor: Function to process skill outputs
        """
        super().__init__(name, description)
        self.skill_factory = skill_factory
        self.input_mapper = input_mapper or self._default_input_mapper
        self.output_processor = output_processor or (lambda x: str(x))

    def _default_input_mapper(self, state: WorkflowState) -> Dict[str, Any]:
        """Default input mapper extracts latest message."""
        latest = StateManager.get_latest_message(state)
        return {"input": latest.content if latest else ""}

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute the skill.

        Args:
            state: Current workflow state

        Returns:
            Updated state with skill results
        """
        # Create skill instance
        skill = self.skill_factory()
        logger.info(f"Executing skill: {self.name}")

        # Map inputs
        inputs = self.input_mapper(state)

        # Execute skill
        result = self._execute_skill(skill, inputs, state)

        # Process output
        output = self.output_processor(result)

        # Update state
        new_state = StateManager.add_message(
            state,
            MessageRole.TOOL,
            output,
            metadata={"skill": self.name, "timestamp": datetime.now().isoformat()}
        )

        # Record skill execution
        new_state["active_skills"] = list(state["active_skills"]) + [self.name]
        new_state["skill_results"] = {
            **state["skill_results"],
            self.name: result
        }

        return new_state

    def _execute_skill(self, skill: Any, inputs: Dict[str, Any], state: WorkflowState) -> Any:
        """
        Execute the skill. Override for custom execution logic.

        Args:
            skill: Skill instance
            inputs: Input parameters
            state: Current state

        Returns:
            Skill execution result
        """
        # Default implementation - adjust based on your skill interface
        # Import SkillContext here to avoid circular imports
        from skills.base_skill import SkillContext

        # Create a SkillContext for the skill
        skill_context = SkillContext(
            results=state.get("skill_results", {}),
            shared_state=state.get("shared_memory", {}),
            chain_id=state.get("workflow_id", "unknown")
        )

        # Execute using the skill's run method (which handles lifecycle)
        if hasattr(skill, 'run'):
            return skill.run(skill_context, **inputs)
        elif hasattr(skill, 'execute'):
            return skill.execute(skill_context, **inputs)
        else:
            logger.warning(f"Skill {self.name} has no known execution method")
            return {"status": "not_implemented", "inputs": inputs}


class RouterNode(BaseNode):
    """
    Node that performs conditional routing.

    Routes workflow to different paths based on state conditions.
    """

    def __init__(
        self,
        name: str,
        route_function: Callable[[WorkflowState], str],
        description: str = ""
    ):
        """
        Initialize a router node.

        Args:
            name: Node name
            route_function: Function that determines next route
            description: Node description
        """
        super().__init__(name, description)
        self.route_function = route_function

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Determine routing decision.

        Args:
            state: Current workflow state

        Returns:
            Updated state with routing decision
        """
        logger.info(f"Routing at node: {self.name}")

        # Determine next route
        next_route = self.route_function(state)

        # Update state
        new_state = state.copy()
        new_state["routing_decision"] = next_route
        new_state["next_step"] = next_route

        logger.info(f"Routing decision: {next_route}")

        return new_state


class ToolNode(BaseNode):
    """
    Node that executes a custom tool or function.

    Provides a flexible way to integrate arbitrary functions into workflows.
    """

    def __init__(
        self,
        name: str,
        tool_function: Callable[[WorkflowState], Any],
        description: str = "",
        update_state: bool = True
    ):
        """
        Initialize a tool node.

        Args:
            name: Node name
            tool_function: Function to execute
            description: Node description
            update_state: Whether to add tool output to messages
        """
        super().__init__(name, description)
        self.tool_function = tool_function
        self.update_state = update_state

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute the tool function.

        Args:
            state: Current workflow state

        Returns:
            Updated state with tool results
        """
        logger.info(f"Executing tool: {self.name}")

        # Execute tool
        result = self.tool_function(state)

        # Update state if configured
        if self.update_state:
            output = str(result)
            new_state = StateManager.add_message(
                state,
                MessageRole.TOOL,
                output,
                metadata={"tool": self.name, "timestamp": datetime.now().isoformat()}
            )
        else:
            new_state = state.copy()

        # Store result in intermediate results
        new_state["intermediate_results"] = {
            **state["intermediate_results"],
            self.name: result
        }

        return new_state


class HumanInputNode(BaseNode):
    """
    Node that requests human input.

    Pauses workflow execution to get input from a human operator.
    """

    def __init__(
        self,
        name: str,
        prompt: str = "Please provide input:",
        description: str = ""
    ):
        """
        Initialize a human input node.

        Args:
            name: Node name
            prompt: Prompt to display to user
            description: Node description
        """
        super().__init__(name, description)
        self.prompt = prompt

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Request human input.

        Args:
            state: Current workflow state

        Returns:
            Updated state with human input
        """
        logger.info(f"Requesting human input at node: {self.name}")

        # In a real implementation, this would pause and wait for input
        # For now, we'll mark it in the state
        new_state = StateManager.add_message(
            state,
            MessageRole.SYSTEM,
            f"[HUMAN_INPUT_REQUIRED] {self.prompt}",
            metadata={"node": self.name, "type": "human_input_request"}
        )

        new_state["context"] = {
            **state["context"],
            "awaiting_human_input": True,
            "human_input_prompt": self.prompt
        }

        return new_state


class AggregatorNode(BaseNode):
    """
    Node that aggregates results from multiple previous nodes.

    Useful for combining outputs from parallel execution paths.
    """

    def __init__(
        self,
        name: str,
        aggregation_function: Callable[[WorkflowState, List[str]], str],
        source_nodes: List[str],
        description: str = ""
    ):
        """
        Initialize an aggregator node.

        Args:
            name: Node name
            aggregation_function: Function to aggregate results
            source_nodes: List of node names to aggregate from
            description: Node description
        """
        super().__init__(name, description)
        self.aggregation_function = aggregation_function
        self.source_nodes = source_nodes

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Aggregate results from source nodes.

        Args:
            state: Current workflow state

        Returns:
            Updated state with aggregated results
        """
        logger.info(f"Aggregating results at node: {self.name}")

        # Get results from source nodes
        results = []
        for node_name in self.source_nodes:
            if node_name in state["intermediate_results"]:
                results.append(state["intermediate_results"][node_name])

        # Aggregate
        aggregated = self.aggregation_function(state, results)

        # Update state
        new_state = StateManager.add_message(
            state,
            MessageRole.ASSISTANT,
            str(aggregated),
            metadata={
                "node": self.name,
                "type": "aggregation",
                "source_nodes": self.source_nodes
            }
        )

        new_state["intermediate_results"] = {
            **state["intermediate_results"],
            self.name: aggregated
        }

        return new_state
