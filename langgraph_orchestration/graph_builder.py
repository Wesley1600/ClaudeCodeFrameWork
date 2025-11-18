"""
Graph Builder for LangGraph Agent Orchestration

This module provides utilities for constructing LangGraph workflows with
conditional routing, parallel execution, and complex control flow.
"""

from typing import Dict, Any, Callable, List, Optional, Union
import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import WorkflowState, StateManager
from .nodes import BaseNode, RouterNode

logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    Builder for constructing LangGraph workflows.

    Provides a fluent API for adding nodes, edges, and conditional routing.
    """

    def __init__(self, name: str = "workflow"):
        """
        Initialize the graph builder.

        Args:
            name: Name of the workflow graph
        """
        self.name = name
        self.graph = StateGraph(WorkflowState)
        self.nodes: Dict[str, BaseNode] = {}
        self.entry_point: Optional[str] = None
        self.checkpointer = MemorySaver()

    def add_node(
        self,
        name: str,
        node: Union[BaseNode, Callable[[WorkflowState], WorkflowState]]
    ) -> "GraphBuilder":
        """
        Add a node to the graph.

        Args:
            name: Unique name for the node
            node: Node instance or callable function

        Returns:
            Self for chaining
        """
        if isinstance(node, BaseNode):
            self.nodes[name] = node
            self.graph.add_node(name, node)
        else:
            # Wrap callable in a lambda
            self.graph.add_node(name, node)

        logger.info(f"Added node: {name}")
        return self

    def add_edge(self, from_node: str, to_node: str) -> "GraphBuilder":
        """
        Add a direct edge between nodes.

        Args:
            from_node: Source node name
            to_node: Destination node name

        Returns:
            Self for chaining
        """
        self.graph.add_edge(from_node, to_node)
        logger.info(f"Added edge: {from_node} -> {to_node}")
        return self

    def add_conditional_edges(
        self,
        source: str,
        router: Callable[[WorkflowState], str],
        path_map: Optional[Dict[str, str]] = None
    ) -> "GraphBuilder":
        """
        Add conditional routing from a node.

        Args:
            source: Source node name
            router: Function that determines next node based on state
            path_map: Optional mapping of router outputs to node names

        Returns:
            Self for chaining
        """
        self.graph.add_conditional_edges(source, router, path_map)
        logger.info(f"Added conditional edges from: {source}")
        return self

    def set_entry_point(self, node_name: str) -> "GraphBuilder":
        """
        Set the entry point for the graph.

        Args:
            node_name: Name of the entry node

        Returns:
            Self for chaining
        """
        self.entry_point = node_name
        self.graph.set_entry_point(node_name)
        logger.info(f"Set entry point: {node_name}")
        return self

    def add_finish_edge(self, from_node: str) -> "GraphBuilder":
        """
        Add an edge from a node to the END.

        Args:
            from_node: Node that should end the workflow

        Returns:
            Self for chaining
        """
        self.graph.add_edge(from_node, END)
        logger.info(f"Added finish edge from: {from_node}")
        return self

    def build(self) -> "WorkflowGraph":
        """
        Compile and build the workflow graph.

        Returns:
            Compiled WorkflowGraph ready for execution
        """
        if not self.entry_point:
            raise ValueError("Entry point must be set before building graph")

        compiled = self.graph.compile(checkpointer=self.checkpointer)
        logger.info(f"Built workflow graph: {self.name}")

        return WorkflowGraph(
            name=self.name,
            compiled_graph=compiled,
            nodes=self.nodes,
            checkpointer=self.checkpointer
        )


class WorkflowGraph:
    """
    Represents a compiled and executable workflow graph.

    Provides methods for executing workflows with state management,
    checkpointing, and streaming.
    """

    def __init__(
        self,
        name: str,
        compiled_graph: Any,
        nodes: Dict[str, BaseNode],
        checkpointer: Any
    ):
        """
        Initialize a workflow graph.

        Args:
            name: Workflow name
            compiled_graph: Compiled LangGraph
            nodes: Dictionary of nodes in the graph
            checkpointer: Checkpointer for state persistence
        """
        self.name = name
        self.compiled_graph = compiled_graph
        self.nodes = nodes
        self.checkpointer = checkpointer
        self.execution_count = 0

    def run(
        self,
        initial_input: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None,
        max_loops: int = 10
    ) -> WorkflowState:
        """
        Execute the workflow with given input.

        Args:
            initial_input: Initial message/input for the workflow
            context: Initial context data
            workflow_id: Unique workflow identifier
            max_loops: Maximum number of workflow loops

        Returns:
            Final workflow state
        """
        # Generate workflow ID if not provided
        if not workflow_id:
            import uuid
            workflow_id = f"{self.name}_{uuid.uuid4().hex[:8]}"

        # Create initial state
        initial_state = StateManager.create_initial_state(
            workflow_id=workflow_id,
            initial_message=initial_input,
            context=context,
            max_loops=max_loops
        )

        logger.info(f"Starting workflow: {workflow_id}")

        # Execute graph
        try:
            result = self.compiled_graph.invoke(
                initial_state,
                config={"configurable": {"thread_id": workflow_id}}
            )
            self.execution_count += 1
            logger.info(f"Workflow completed: {workflow_id}")
            return result

        except Exception as e:
            logger.error(f"Workflow error: {e}")
            return StateManager.record_error(initial_state, e, {"workflow_id": workflow_id})

    def stream(
        self,
        initial_input: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None,
        max_loops: int = 10
    ):
        """
        Execute the workflow with streaming output.

        Args:
            initial_input: Initial message/input for the workflow
            context: Initial context data
            workflow_id: Unique workflow identifier
            max_loops: Maximum number of workflow loops

        Yields:
            State updates as workflow executes
        """
        # Generate workflow ID if not provided
        if not workflow_id:
            import uuid
            workflow_id = f"{self.name}_{uuid.uuid4().hex[:8]}"

        # Create initial state
        initial_state = StateManager.create_initial_state(
            workflow_id=workflow_id,
            initial_message=initial_input,
            context=context,
            max_loops=max_loops
        )

        logger.info(f"Starting streaming workflow: {workflow_id}")

        # Stream execution
        try:
            for chunk in self.compiled_graph.stream(
                initial_state,
                config={"configurable": {"thread_id": workflow_id}}
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Workflow streaming error: {e}")
            yield StateManager.record_error(initial_state, e, {"workflow_id": workflow_id})

    def get_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """
        Retrieve saved state for a workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Saved state or None if not found
        """
        try:
            config = {"configurable": {"thread_id": workflow_id}}
            state_snapshot = self.compiled_graph.get_state(config)
            return state_snapshot.values if state_snapshot else None
        except Exception as e:
            logger.error(f"Error retrieving state: {e}")
            return None

    def resume(
        self,
        workflow_id: str,
        new_input: Optional[str] = None
    ) -> WorkflowState:
        """
        Resume a workflow from a checkpoint.

        Args:
            workflow_id: Workflow identifier to resume
            new_input: Optional new input to add before resuming

        Returns:
            Final workflow state after resumption
        """
        logger.info(f"Resuming workflow: {workflow_id}")

        # Get current state
        current_state = self.get_state(workflow_id)
        if not current_state:
            raise ValueError(f"No saved state found for workflow: {workflow_id}")

        # Add new input if provided
        if new_input:
            current_state = StateManager.add_message(
                current_state,
                MessageRole.USER,
                new_input
            )

        # Resume execution
        try:
            result = self.compiled_graph.invoke(
                current_state,
                config={"configurable": {"thread_id": workflow_id}}
            )
            logger.info(f"Workflow resumed and completed: {workflow_id}")
            return result

        except Exception as e:
            logger.error(f"Workflow resume error: {e}")
            return StateManager.record_error(current_state, e, {"workflow_id": workflow_id})

    def visualize(self, output_path: Optional[str] = None) -> str:
        """
        Generate a visualization of the workflow graph.

        Args:
            output_path: Optional path to save visualization

        Returns:
            Graph description or path to saved visualization
        """
        try:
            # Try to get the graph structure
            if hasattr(self.compiled_graph, 'get_graph'):
                graph_data = self.compiled_graph.get_graph()

                # Create a simple text representation
                viz = f"Workflow: {self.name}\n"
                viz += "=" * 50 + "\n"
                viz += f"Nodes: {list(self.nodes.keys())}\n"
                viz += "=" * 50 + "\n"

                if output_path:
                    with open(output_path, 'w') as f:
                        f.write(viz)
                    logger.info(f"Visualization saved to: {output_path}")

                return viz
            else:
                return f"Workflow '{self.name}' with {len(self.nodes)} nodes"

        except Exception as e:
            logger.error(f"Error visualizing graph: {e}")
            return f"Error generating visualization: {e}"


def create_simple_chain(*nodes: BaseNode, name: str = "chain") -> WorkflowGraph:
    """
    Create a simple sequential chain of nodes.

    Args:
        *nodes: Nodes to chain in order
        name: Name for the workflow

    Returns:
        Compiled workflow graph
    """
    builder = GraphBuilder(name=name)

    # Add all nodes
    for i, node in enumerate(nodes):
        node_name = node.name if hasattr(node, 'name') else f"node_{i}"
        builder.add_node(node_name, node)

        # Add edge from previous node
        if i > 0:
            prev_name = nodes[i-1].name if hasattr(nodes[i-1], 'name') else f"node_{i-1}"
            builder.add_edge(prev_name, node_name)

    # Set entry point to first node
    first_name = nodes[0].name if hasattr(nodes[0], 'name') else "node_0"
    builder.set_entry_point(first_name)

    # Add finish edge from last node
    last_name = nodes[-1].name if hasattr(nodes[-1], 'name') else f"node_{len(nodes)-1}"
    builder.add_finish_edge(last_name)

    return builder.build()


def create_router_workflow(
    router_node: RouterNode,
    route_map: Dict[str, BaseNode],
    name: str = "router_workflow"
) -> WorkflowGraph:
    """
    Create a workflow with conditional routing.

    Args:
        router_node: Router node that determines the path
        route_map: Mapping of route names to nodes
        name: Name for the workflow

    Returns:
        Compiled workflow graph
    """
    builder = GraphBuilder(name=name)

    # Add router node
    builder.add_node(router_node.name, router_node)
    builder.set_entry_point(router_node.name)

    # Add route nodes
    for route_name, node in route_map.items():
        builder.add_node(route_name, node)
        builder.add_finish_edge(route_name)

    # Add conditional routing
    def route_function(state: WorkflowState) -> str:
        return state.get("routing_decision", "default")

    builder.add_conditional_edges(
        router_node.name,
        route_function,
        route_map={k: k for k in route_map.keys()}
    )

    return builder.build()
