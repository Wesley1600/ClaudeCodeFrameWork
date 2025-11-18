"""
Configuration management for Agent Pulse system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import time


@dataclass
class PulseConfig:
    """Configuration for the Agent Pulse system."""

    # Storage paths
    memory_store_path: Path = field(default_factory=lambda: Path.home() / ".agent_pulse" / "memory")
    preferences_path: Path = field(default_factory=lambda: Path.home() / ".agent_pulse" / "preferences.json")
    conversation_history_path: Path = field(default_factory=lambda: Path.home() / ".agent_pulse" / "conversations")

    # Scheduling
    schedule_enabled: bool = True
    schedule_time: time = field(default_factory=lambda: time(6, 0))  # 6:00 AM by default
    schedule_frequency: str = "daily"  # daily, weekly, manual

    # Analysis settings
    max_conversations_to_analyze: int = 50
    lookback_days: int = 7
    min_conversation_length: int = 3  # Minimum messages to analyze

    # Agent settings
    enable_conversation_analysis: bool = True
    enable_research: bool = True
    enable_opportunity_finding: bool = True
    enable_problem_solving: bool = True

    # Research settings
    max_web_searches: int = 5
    max_topics_per_update: int = 8

    # Update card settings
    card_style: str = "detailed"  # minimal, detailed, comprehensive
    include_sources: bool = True
    include_action_items: bool = True

    # Personalization
    user_interests: List[str] = field(default_factory=list)
    tracked_metrics: List[str] = field(default_factory=list)
    focus_areas: List[str] = field(default_factory=list)

    # Integration settings
    integrations: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Feedback settings
    learning_rate: float = 0.1  # For preference learning
    feedback_history_size: int = 100

    def __post_init__(self):
        """Ensure paths are Path objects."""
        self.memory_store_path = Path(self.memory_store_path)
        self.preferences_path = Path(self.preferences_path)
        self.conversation_history_path = Path(self.conversation_history_path)

        # Create directories if they don't exist
        self.memory_store_path.mkdir(parents=True, exist_ok=True)
        self.conversation_history_path.mkdir(parents=True, exist_ok=True)
        self.preferences_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, path: Optional[Path] = None) -> None:
        """Save configuration to JSON file."""
        save_path = path or (Path.home() / ".agent_pulse" / "config.json")
        save_path.parent.mkdir(parents=True, exist_ok=True)

        config_dict = {
            "memory_store_path": str(self.memory_store_path),
            "preferences_path": str(self.preferences_path),
            "conversation_history_path": str(self.conversation_history_path),
            "schedule_enabled": self.schedule_enabled,
            "schedule_time": self.schedule_time.isoformat(),
            "schedule_frequency": self.schedule_frequency,
            "max_conversations_to_analyze": self.max_conversations_to_analyze,
            "lookback_days": self.lookback_days,
            "min_conversation_length": self.min_conversation_length,
            "enable_conversation_analysis": self.enable_conversation_analysis,
            "enable_research": self.enable_research,
            "enable_opportunity_finding": self.enable_opportunity_finding,
            "enable_problem_solving": self.enable_problem_solving,
            "max_web_searches": self.max_web_searches,
            "max_topics_per_update": self.max_topics_per_update,
            "card_style": self.card_style,
            "include_sources": self.include_sources,
            "include_action_items": self.include_action_items,
            "user_interests": self.user_interests,
            "tracked_metrics": self.tracked_metrics,
            "focus_areas": self.focus_areas,
            "integrations": self.integrations,
            "learning_rate": self.learning_rate,
            "feedback_history_size": self.feedback_history_size,
        }

        with open(save_path, 'w') as f:
            json.dump(config_dict, f, indent=2)

    @classmethod
    def load(cls, path: Optional[Path] = None) -> 'PulseConfig':
        """Load configuration from JSON file."""
        load_path = path or (Path.home() / ".agent_pulse" / "config.json")

        if not load_path.exists():
            return cls()

        with open(load_path, 'r') as f:
            config_dict = json.load(f)

        # Convert time string back to time object
        if "schedule_time" in config_dict:
            time_str = config_dict["schedule_time"]
            hour, minute = map(int, time_str.split(":"))
            config_dict["schedule_time"] = time(hour, minute)

        # Convert path strings to Path objects
        for key in ["memory_store_path", "preferences_path", "conversation_history_path"]:
            if key in config_dict:
                config_dict[key] = Path(config_dict[key])

        return cls(**config_dict)

    def add_interest(self, interest: str) -> None:
        """Add a user interest."""
        if interest not in self.user_interests:
            self.user_interests.append(interest)

    def remove_interest(self, interest: str) -> None:
        """Remove a user interest."""
        if interest in self.user_interests:
            self.user_interests.remove(interest)

    def add_tracked_metric(self, metric: str) -> None:
        """Add a metric to track."""
        if metric not in self.tracked_metrics:
            self.tracked_metrics.append(metric)

    def add_focus_area(self, area: str) -> None:
        """Add a focus area."""
        if area not in self.focus_areas:
            self.focus_areas.append(area)
