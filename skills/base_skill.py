"""
Base Skill Interface and Core Abstractions

This module defines the foundational architecture for the skill orchestration system.
All skills must inherit from BaseSkill and implement the execute() method.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
import uuid


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillStatus(Enum):
    """Execution status of a skill"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SkillContext:
    """
    Context object passed between skills in a chain.

    Accumulates results from previous skills and provides shared state.
    """
    # Results from all previous skills {skill_name: result}
    results: Dict[str, Any] = field(default_factory=dict)

    # Shared state that skills can read/write
    shared_state: Dict[str, Any] = field(default_factory=dict)

    # Chain execution metadata
    chain_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: float = field(default_factory=time.time)

    # Error tracking
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def add_result(self, skill_name: str, result: Any) -> None:
        """Store result from a skill"""
        self.results[skill_name] = result

    def get_result(self, skill_name: str, default: Any = None) -> Any:
        """Retrieve result from a previous skill"""
        return self.results.get(skill_name, default)

    def add_error(self, skill_name: str, error: Exception, fatal: bool = False) -> None:
        """Record an error during execution"""
        self.errors.append({
            "skill": skill_name,
            "error": str(error),
            "error_type": type(error).__name__,
            "fatal": fatal,
            "timestamp": time.time()
        })

    def get_elapsed_time(self) -> float:
        """Get total elapsed time in seconds"""
        return time.time() - self.start_time


@dataclass
class SkillMetadata:
    """Metadata describing a skill's capabilities"""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Unknown"

    # Input/output schema (optional type hints)
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None

    # Resource requirements
    requires_gpu: bool = False
    estimated_time_seconds: Optional[float] = None

    # Dependencies on other skills
    dependencies: List[str] = field(default_factory=list)

    # Tags for categorization
    tags: List[str] = field(default_factory=list)


class BaseSkill(ABC):
    """
    Abstract base class for all skills.

    Skills are modular, reusable components that can be chained together
    to create complex workflows. Each skill:
    - Receives a SkillContext with previous results
    - Performs its specific task
    - Returns a result that gets added to context
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize skill with optional configuration.

        Args:
            config: Skill-specific configuration parameters
        """
        self.config = config or {}
        self.status = SkillStatus.PENDING
        self._metadata = self._create_metadata()

    @abstractmethod
    def _create_metadata(self) -> SkillMetadata:
        """Create metadata describing this skill"""
        pass

    @abstractmethod
    def execute(self, context: SkillContext, **kwargs) -> Any:
        """
        Execute the skill's main logic.

        Args:
            context: SkillContext with results from previous skills
            **kwargs: Additional parameters passed at execution time

        Returns:
            Result that will be added to context for downstream skills
        """
        pass

    def validate_inputs(self, context: SkillContext, **kwargs) -> bool:
        """
        Validate that required inputs are available.

        Override this to implement custom validation logic.

        Args:
            context: Current execution context
            **kwargs: Additional parameters

        Returns:
            True if inputs are valid, False otherwise
        """
        return True

    def on_before_execute(self, context: SkillContext) -> None:
        """Hook called before execute(). Override for setup logic."""
        pass

    def on_after_execute(self, context: SkillContext, result: Any) -> None:
        """Hook called after execute(). Override for cleanup logic."""
        pass

    def on_error(self, context: SkillContext, error: Exception) -> None:
        """Hook called when execute() raises an error. Override for error handling."""
        logger.error(f"Error in skill {self.name}: {error}")

    def run(self, context: SkillContext, **kwargs) -> Any:
        """
        Main execution wrapper that handles lifecycle and error handling.

        This method should not be overridden. Override execute() instead.
        """
        try:
            logger.info(f"Starting skill: {self.name}")
            self.status = SkillStatus.RUNNING

            # Validate inputs
            if not self.validate_inputs(context, **kwargs):
                raise ValueError(f"Input validation failed for skill: {self.name}")

            # Pre-execution hook
            self.on_before_execute(context)

            # Execute main logic
            start_time = time.time()
            result = self.execute(context, **kwargs)
            execution_time = time.time() - start_time

            logger.info(f"Skill {self.name} completed in {execution_time:.2f}s")

            # Post-execution hook
            self.on_after_execute(context, result)

            self.status = SkillStatus.COMPLETED
            return result

        except Exception as e:
            self.status = SkillStatus.FAILED
            self.on_error(context, e)
            context.add_error(self.name, e, fatal=True)
            raise

    @property
    def name(self) -> str:
        """Get skill name from metadata"""
        return self._metadata.name

    @property
    def metadata(self) -> SkillMetadata:
        """Get skill metadata"""
        return self._metadata

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', status={self.status.value})>"


class PassthroughSkill(BaseSkill):
    """
    Simple skill that passes through its input unchanged.
    Useful for testing and debugging chains.
    """

    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="passthrough",
            description="Passes input through unchanged",
            tags=["utility", "testing"]
        )

    def execute(self, context: SkillContext, **kwargs) -> Any:
        """Return the input data unchanged"""
        input_data = kwargs.get("data")
        logger.info(f"Passthrough: {input_data}")
        return input_data


class TransformSkill(BaseSkill):
    """
    Base class for skills that transform data.

    Subclass this for common data transformation patterns.
    """

    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="transform",
            description="Base transformation skill",
            tags=["transform"]
        )

    @abstractmethod
    def transform(self, data: Any) -> Any:
        """Transform the input data. Override this method."""
        pass

    def execute(self, context: SkillContext, **kwargs) -> Any:
        """Execute the transformation"""
        # Get data from previous skill or kwargs
        data = kwargs.get("data") or context.results.get(kwargs.get("source_skill"))

        if data is None:
            raise ValueError("No input data provided for transformation")

        return self.transform(data)
