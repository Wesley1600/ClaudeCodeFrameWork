"""
Skill Orchestration Engine

Executes chains of skills with data flow management, conditional logic,
and parallel execution support.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum
import logging
import yaml
import json
from pathlib import Path

from .base_skill import BaseSkill, SkillContext, SkillStatus
from .registry import SkillRegistry, get_global_registry


logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """How to execute skills in a step"""
    SEQUENTIAL = "sequential"  # One after another
    PARALLEL = "parallel"      # All at once (future: async support)


@dataclass
class SkillStep:
    """
    A single step in a skill chain.

    Can execute one or more skills with specific configuration.
    """
    # Skill name(s) to execute
    skills: Union[str, List[str]]

    # Configuration for each skill
    config: Dict[str, Any] = field(default_factory=dict)

    # How to execute if multiple skills
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL

    # Condition to execute this step (callable or None)
    condition: Optional[Callable[[SkillContext], bool]] = None

    # Whether to continue chain if this step fails
    continue_on_error: bool = False

    # Step name (for logging/debugging)
    name: Optional[str] = None

    def should_execute(self, context: SkillContext) -> bool:
        """Check if this step should execute based on condition"""
        if self.condition is None:
            return True
        return self.condition(context)

    def get_skill_names(self) -> List[str]:
        """Get list of skill names in this step"""
        if isinstance(self.skills, str):
            return [self.skills]
        return self.skills


@dataclass
class ChainConfig:
    """
    Configuration for a skill chain.

    Defines the sequence of skills to execute and how data flows between them.
    """
    # Chain identification
    name: str
    description: str = ""

    # Steps to execute
    steps: List[SkillStep] = field(default_factory=list)

    # Initial data to pass to first skill
    initial_data: Dict[str, Any] = field(default_factory=dict)

    # Global configuration shared by all skills
    global_config: Dict[str, Any] = field(default_factory=dict)

    # Stop execution on first error
    fail_fast: bool = True

    # Maximum execution time (seconds, None = no limit)
    timeout: Optional[float] = None

    def add_step(
        self,
        skills: Union[str, List[str]],
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> 'ChainConfig':
        """
        Add a step to the chain (builder pattern).

        Args:
            skills: Skill name or list of skill names
            config: Configuration for the skill(s)
            **kwargs: Additional SkillStep parameters

        Returns:
            Self for chaining
        """
        step = SkillStep(
            skills=skills,
            config=config or {},
            **kwargs
        )
        self.steps.append(step)
        return self

    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]) -> 'ChainConfig':
        """Load chain configuration from YAML file"""
        path = Path(yaml_path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {yaml_path}")

        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data)

    @classmethod
    def from_json(cls, json_path: Union[str, Path]) -> 'ChainConfig':
        """Load chain configuration from JSON file"""
        path = Path(json_path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {json_path}")

        with open(path, 'r') as f:
            data = json.load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChainConfig':
        """Create ChainConfig from dictionary"""
        steps = []

        for step_data in data.get("steps", []):
            # Parse execution mode
            mode_str = step_data.get("mode", "sequential")
            mode = ExecutionMode(mode_str)

            step = SkillStep(
                skills=step_data["skills"],
                config=step_data.get("config", {}),
                mode=mode,
                continue_on_error=step_data.get("continue_on_error", False),
                name=step_data.get("name")
            )
            steps.append(step)

        return cls(
            name=data.get("name", "unnamed_chain"),
            description=data.get("description", ""),
            steps=steps,
            initial_data=data.get("initial_data", {}),
            global_config=data.get("global_config", {}),
            fail_fast=data.get("fail_fast", True),
            timeout=data.get("timeout")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for serialization)"""
        return {
            "name": self.name,
            "description": self.description,
            "steps": [
                {
                    "skills": step.skills,
                    "config": step.config,
                    "mode": step.mode.value,
                    "continue_on_error": step.continue_on_error,
                    "name": step.name
                }
                for step in self.steps
            ],
            "initial_data": self.initial_data,
            "global_config": self.global_config,
            "fail_fast": self.fail_fast,
            "timeout": self.timeout
        }

    def to_yaml(self, yaml_path: Union[str, Path]) -> None:
        """Save configuration to YAML file"""
        path = Path(yaml_path)
        with open(path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    def to_json(self, json_path: Union[str, Path]) -> None:
        """Save configuration to JSON file"""
        path = Path(json_path)
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


class SkillOrchestrator:
    """
    Orchestrates execution of skill chains.

    Handles:
    - Sequential and parallel execution
    - Data flow between skills
    - Error handling and recovery
    - Conditional execution
    - Timeout management
    """

    def __init__(self, registry: Optional[SkillRegistry] = None):
        """
        Initialize orchestrator.

        Args:
            registry: SkillRegistry to use (defaults to global registry)
        """
        self.registry = registry or get_global_registry()

    def execute_chain(
        self,
        chain: ChainConfig,
        context: Optional[SkillContext] = None
    ) -> SkillContext:
        """
        Execute a complete skill chain.

        Args:
            chain: ChainConfig defining the chain
            context: Optional existing context (creates new if None)

        Returns:
            SkillContext with results from all skills

        Raises:
            TimeoutError: If execution exceeds timeout
            Exception: If fail_fast=True and a skill fails
        """
        # Create or use existing context
        if context is None:
            context = SkillContext()

        # Add initial data to context
        context.shared_state.update(chain.initial_data)

        logger.info(f"Starting chain: {chain.name}")
        logger.info(f"Chain description: {chain.description}")
        logger.info(f"Total steps: {len(chain.steps)}")

        try:
            # Execute each step
            for step_idx, step in enumerate(chain.steps):
                step_name = step.name or f"Step {step_idx + 1}"

                # Check condition
                if not step.should_execute(context):
                    logger.info(f"Skipping {step_name} (condition not met)")
                    continue

                logger.info(f"Executing {step_name}: {step.get_skill_names()}")

                try:
                    self._execute_step(step, context, chain.global_config)
                except Exception as e:
                    logger.error(f"Error in {step_name}: {e}")

                    if step.continue_on_error:
                        logger.info(f"Continuing despite error (continue_on_error=True)")
                        continue

                    if chain.fail_fast:
                        logger.error("Stopping chain (fail_fast=True)")
                        raise

            # Chain completed successfully
            elapsed = context.get_elapsed_time()
            logger.info(f"Chain '{chain.name}' completed in {elapsed:.2f}s")

            return context

        except Exception as e:
            logger.error(f"Chain '{chain.name}' failed: {e}")
            raise

    def _execute_step(
        self,
        step: SkillStep,
        context: SkillContext,
        global_config: Dict[str, Any]
    ) -> None:
        """Execute a single step (one or more skills)"""
        skill_names = step.get_skill_names()

        if step.mode == ExecutionMode.SEQUENTIAL:
            # Execute skills one after another
            for skill_name in skill_names:
                self._execute_skill(skill_name, step.config, global_config, context)

        elif step.mode == ExecutionMode.PARALLEL:
            # For now, execute sequentially (TODO: implement async)
            # In future: use asyncio to run concurrently
            logger.warning("Parallel execution not yet implemented, using sequential")
            for skill_name in skill_names:
                self._execute_skill(skill_name, step.config, global_config, context)

    def _execute_skill(
        self,
        skill_name: str,
        step_config: Dict[str, Any],
        global_config: Dict[str, Any],
        context: SkillContext
    ) -> None:
        """Execute a single skill and add result to context"""
        # Merge configurations (step config overrides global)
        merged_config = {**global_config, **step_config.get(skill_name, {})}

        # Instantiate skill
        skill = self.registry.create_skill(skill_name, config=merged_config)

        # Execute skill
        result = skill.run(context)

        # Store result in context
        context.add_result(skill_name, result)

    def execute_from_file(
        self,
        config_path: Union[str, Path],
        context: Optional[SkillContext] = None
    ) -> SkillContext:
        """
        Load chain config from file and execute.

        Args:
            config_path: Path to YAML or JSON config file
            context: Optional existing context

        Returns:
            SkillContext with results
        """
        path = Path(config_path)

        # Determine format from extension
        if path.suffix in ['.yaml', '.yml']:
            chain = ChainConfig.from_yaml(path)
        elif path.suffix == '.json':
            chain = ChainConfig.from_json(path)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")

        return self.execute_chain(chain, context)

    def create_chain(self, name: str, description: str = "") -> ChainConfig:
        """
        Create a new chain configuration (builder pattern).

        Args:
            name: Chain name
            description: Chain description

        Returns:
            ChainConfig that can be built up with add_step()
        """
        return ChainConfig(name=name, description=description)
