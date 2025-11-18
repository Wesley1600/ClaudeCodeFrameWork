"""
Integration Layer for LangGraph with Existing Framework

This module provides integration between the LangGraph orchestration system
and the existing BaseAgent and BaseSkill infrastructure.
"""

from typing import Dict, Any, Optional, Callable, List
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent, AgentConfig
from skills.base_skill import BaseSkill, SkillContext, SkillStatus
from .state import WorkflowState, MessageRole, StateManager
from .nodes import AgentNode, SkillNode, BaseNode
from .graph_builder import GraphBuilder, WorkflowGraph

logger = logging.getLogger(__name__)


class FrameworkAgentNode(AgentNode):
    """
    Agent node that integrates with the BaseAgent framework.

    Wraps BaseAgent instances for use in LangGraph workflows.
    """

    def __init__(
        self,
        name: str,
        agent: BaseAgent,
        description: str = ""
    ):
        """
        Initialize framework agent node.

        Args:
            name: Node name
            agent: BaseAgent instance
            description: Node description
        """
        # Create factory that returns the agent
        factory = lambda: agent

        super().__init__(
            name=name,
            agent_factory=factory,
            description=description or agent.config.description
        )
        self.agent = agent

    def _execute_agent(self, agent: BaseAgent, input_text: str, state: WorkflowState) -> Any:
        """
        Execute the BaseAgent.

        Args:
            agent: BaseAgent instance
            input_text: Input text
            state: Current workflow state

        Returns:
            Agent execution result
        """
        # Ensure agent is initialized
        if not agent._initialized:
            agent.initialize()

        # Execute agent skills if available
        results = {}

        # If agent has skills, execute them
        for skill_id in agent.config.skills:
            try:
                logger.info(f"Agent {agent.config.name} executing skill: {skill_id}")
                result = agent.execute_skill(
                    skill_id,
                    input=input_text,
                    context=state["context"]
                )
                results[skill_id] = result
            except Exception as e:
                logger.error(f"Error executing skill {skill_id}: {e}")
                results[skill_id] = {"error": str(e)}

        return {
            "agent_id": agent.config.id,
            "agent_name": agent.config.name,
            "input": input_text,
            "skill_results": results,
            "metadata": agent.config.metadata
        }


class FrameworkSkillNode(SkillNode):
    """
    Skill node that integrates with the BaseSkill framework.

    Wraps BaseSkill instances for use in LangGraph workflows.
    """

    def __init__(
        self,
        name: str,
        skill: BaseSkill,
        description: str = "",
        skill_kwargs: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize framework skill node.

        Args:
            name: Node name
            skill: BaseSkill instance
            description: Node description
            skill_kwargs: Additional kwargs to pass to skill execution
        """
        # Create factory that returns the skill
        factory = lambda: skill

        super().__init__(
            name=name,
            skill_factory=factory,
            description=description or skill.metadata.description,
            input_mapper=lambda state: self._map_state_to_skill_context(state),
            output_processor=lambda result: self._process_skill_result(result)
        )
        self.skill = skill
        self.skill_kwargs = skill_kwargs or {}

    def _map_state_to_skill_context(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Map WorkflowState to SkillContext for skill execution.

        Args:
            state: Current workflow state

        Returns:
            Dictionary with SkillContext and kwargs
        """
        # Create SkillContext from workflow state
        skill_context = SkillContext(
            results=state.get("skill_results", {}),
            shared_state=state.get("shared_memory", {}),
            chain_id=state.get("workflow_id", "unknown")
        )

        # Get latest message as input
        latest_message = StateManager.get_latest_message(state)
        input_text = latest_message.content if latest_message else ""

        return {
            "context": skill_context,
            "input": input_text,
            **self.skill_kwargs
        }

    def _process_skill_result(self, result: Any) -> str:
        """
        Process skill result into string format.

        Args:
            result: Skill execution result

        Returns:
            String representation of result
        """
        if isinstance(result, dict):
            return str(result)
        elif isinstance(result, str):
            return result
        else:
            return str(result)

    def _execute_skill(self, skill: BaseSkill, inputs: Dict[str, Any], state: WorkflowState) -> Any:
        """
        Execute the BaseSkill using its run() method.

        Args:
            skill: BaseSkill instance
            inputs: Input parameters including SkillContext
            state: Current workflow state

        Returns:
            Skill execution result
        """
        context = inputs.get("context")
        kwargs = {k: v for k, v in inputs.items() if k != "context"}

        # Execute skill using its run() method
        try:
            result = skill.run(context, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error executing skill {skill.name}: {e}")
            return {"error": str(e), "status": "failed"}


class LangGraphAgentOrchestrator:
    """
    High-level orchestrator that integrates BaseAgent and BaseSkill
    with LangGraph workflows.

    Provides a simplified interface for creating and executing
    agent-based workflows using the existing framework components.
    """

    def __init__(self, name: str = "orchestrator"):
        """
        Initialize the orchestrator.

        Args:
            name: Orchestrator name
        """
        self.name = name
        self.agents: Dict[str, BaseAgent] = {}
        self.skills: Dict[str, BaseSkill] = {}
        self.workflows: Dict[str, WorkflowGraph] = {}
        logger.info(f"Initialized LangGraphAgentOrchestrator: {name}")

    def register_agent(self, agent: BaseAgent) -> "LangGraphAgentOrchestrator":
        """
        Register an agent with the orchestrator.

        Args:
            agent: BaseAgent instance

        Returns:
            Self for chaining
        """
        self.agents[agent.config.id] = agent
        logger.info(f"Registered agent: {agent.config.name} (ID: {agent.config.id})")
        return self

    def register_skill(self, skill: BaseSkill, skill_id: Optional[str] = None) -> "LangGraphAgentOrchestrator":
        """
        Register a skill with the orchestrator.

        Args:
            skill: BaseSkill instance
            skill_id: Optional skill ID (uses skill.name if not provided)

        Returns:
            Self for chaining
        """
        sid = skill_id or skill.name
        self.skills[sid] = skill
        logger.info(f"Registered skill: {skill.name} (ID: {sid})")
        return self

    def create_agent_workflow(
        self,
        workflow_name: str,
        agent_sequence: List[str]
    ) -> WorkflowGraph:
        """
        Create a sequential workflow of agents.

        Args:
            workflow_name: Name for the workflow
            agent_sequence: List of agent IDs in execution order

        Returns:
            Compiled WorkflowGraph

        Example:
            >>> workflow = orchestrator.create_agent_workflow(
            ...     "research_and_summarize",
            ...     ["research_agent", "summarizer_agent"]
            ... )
        """
        builder = GraphBuilder(name=workflow_name)

        # Add agent nodes
        for i, agent_id in enumerate(agent_sequence):
            if agent_id not in self.agents:
                raise ValueError(f"Agent not registered: {agent_id}")

            agent = self.agents[agent_id]
            node = FrameworkAgentNode(
                name=f"agent_{i}_{agent_id}",
                agent=agent
            )

            builder.add_node(node.name, node)

            # Add edge from previous node
            if i > 0:
                prev_name = f"agent_{i-1}_{agent_sequence[i-1]}"
                builder.add_edge(prev_name, node.name)

        # Set entry point
        first_name = f"agent_0_{agent_sequence[0]}"
        builder.set_entry_point(first_name)

        # Add finish edge
        last_name = f"agent_{len(agent_sequence)-1}_{agent_sequence[-1]}"
        builder.add_finish_edge(last_name)

        # Build and store workflow
        workflow = builder.build()
        self.workflows[workflow_name] = workflow
        logger.info(f"Created agent workflow: {workflow_name}")

        return workflow

    def create_skill_workflow(
        self,
        workflow_name: str,
        skill_sequence: List[str],
        skill_kwargs: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> WorkflowGraph:
        """
        Create a sequential workflow of skills.

        Args:
            workflow_name: Name for the workflow
            skill_sequence: List of skill IDs in execution order
            skill_kwargs: Optional dict mapping skill IDs to their kwargs

        Returns:
            Compiled WorkflowGraph

        Example:
            >>> workflow = orchestrator.create_skill_workflow(
            ...     "data_pipeline",
            ...     ["extract_skill", "transform_skill", "load_skill"]
            ... )
        """
        builder = GraphBuilder(name=workflow_name)
        skill_kwargs = skill_kwargs or {}

        # Add skill nodes
        for i, skill_id in enumerate(skill_sequence):
            if skill_id not in self.skills:
                raise ValueError(f"Skill not registered: {skill_id}")

            skill = self.skills[skill_id]
            kwargs = skill_kwargs.get(skill_id, {})

            node = FrameworkSkillNode(
                name=f"skill_{i}_{skill_id}",
                skill=skill,
                skill_kwargs=kwargs
            )

            builder.add_node(node.name, node)

            # Add edge from previous node
            if i > 0:
                prev_name = f"skill_{i-1}_{skill_sequence[i-1]}"
                builder.add_edge(prev_name, node.name)

        # Set entry point
        first_name = f"skill_0_{skill_sequence[0]}"
        builder.set_entry_point(first_name)

        # Add finish edge
        last_name = f"skill_{len(skill_sequence)-1}_{skill_sequence[-1]}"
        builder.add_finish_edge(last_name)

        # Build and store workflow
        workflow = builder.build()
        self.workflows[workflow_name] = workflow
        logger.info(f"Created skill workflow: {workflow_name}")

        return workflow

    def create_mixed_workflow(
        self,
        workflow_name: str,
        steps: List[Dict[str, Any]]
    ) -> WorkflowGraph:
        """
        Create a workflow with mixed agents and skills.

        Args:
            workflow_name: Name for the workflow
            steps: List of step definitions with 'type' (agent/skill) and 'id'

        Returns:
            Compiled WorkflowGraph

        Example:
            >>> workflow = orchestrator.create_mixed_workflow(
            ...     "complex_workflow",
            ...     [
            ...         {"type": "agent", "id": "research_agent"},
            ...         {"type": "skill", "id": "summarize_skill"},
            ...         {"type": "agent", "id": "writer_agent"}
            ...     ]
            ... )
        """
        builder = GraphBuilder(name=workflow_name)

        # Add nodes for each step
        for i, step in enumerate(steps):
            step_type = step.get("type")
            step_id = step.get("id")
            node_name = f"{step_type}_{i}_{step_id}"

            if step_type == "agent":
                if step_id not in self.agents:
                    raise ValueError(f"Agent not registered: {step_id}")

                node = FrameworkAgentNode(
                    name=node_name,
                    agent=self.agents[step_id]
                )

            elif step_type == "skill":
                if step_id not in self.skills:
                    raise ValueError(f"Skill not registered: {step_id}")

                node = FrameworkSkillNode(
                    name=node_name,
                    skill=self.skills[step_id],
                    skill_kwargs=step.get("kwargs", {})
                )

            else:
                raise ValueError(f"Unknown step type: {step_type}")

            builder.add_node(node_name, node)

            # Add edge from previous node
            if i > 0:
                prev_step = steps[i-1]
                prev_name = f"{prev_step['type']}_{i-1}_{prev_step['id']}"
                builder.add_edge(prev_name, node_name)

        # Set entry point
        first_step = steps[0]
        first_name = f"{first_step['type']}_0_{first_step['id']}"
        builder.set_entry_point(first_name)

        # Add finish edge
        last_step = steps[-1]
        last_name = f"{last_step['type']}_{len(steps)-1}_{last_step['id']}"
        builder.add_finish_edge(last_name)

        # Build and store workflow
        workflow = builder.build()
        self.workflows[workflow_name] = workflow
        logger.info(f"Created mixed workflow: {workflow_name}")

        return workflow

    def run_workflow(
        self,
        workflow_name: str,
        input_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowState:
        """
        Execute a workflow by name.

        Args:
            workflow_name: Name of the workflow to execute
            input_message: Initial input message
            context: Optional context data

        Returns:
            Final workflow state

        Example:
            >>> result = orchestrator.run_workflow(
            ...     "research_and_summarize",
            ...     "What is quantum computing?"
            ... )
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_name}")

        workflow = self.workflows[workflow_name]
        logger.info(f"Running workflow: {workflow_name}")

        return workflow.run(
            initial_input=input_message,
            context=context
        )

    def get_workflow(self, workflow_name: str) -> Optional[WorkflowGraph]:
        """
        Get a workflow by name.

        Args:
            workflow_name: Name of the workflow

        Returns:
            WorkflowGraph or None if not found
        """
        return self.workflows.get(workflow_name)

    def list_workflows(self) -> List[str]:
        """
        List all registered workflows.

        Returns:
            List of workflow names
        """
        return list(self.workflows.keys())

    def list_agents(self) -> List[str]:
        """
        List all registered agents.

        Returns:
            List of agent IDs
        """
        return list(self.agents.keys())

    def list_skills(self) -> List[str]:
        """
        List all registered skills.

        Returns:
            List of skill IDs
        """
        return list(self.skills.keys())
