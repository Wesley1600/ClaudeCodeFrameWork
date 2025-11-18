"""
User preference management and feedback learning.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class FeedbackType(Enum):
    """Types of user feedback."""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    DISMISS = "dismiss"
    SAVE = "save"
    SHARE = "share"


@dataclass
class UserFeedback:
    """Represents user feedback on an update card."""

    card_id: str
    feedback_type: FeedbackType
    timestamp: datetime
    card_category: str  # e.g., "research", "problem_solution", "opportunity"
    card_topic: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "card_id": self.card_id,
            "feedback_type": self.feedback_type.value,
            "timestamp": self.timestamp.isoformat(),
            "card_category": self.card_category,
            "card_topic": self.card_topic,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserFeedback':
        """Create from dictionary."""
        data = data.copy()
        data["feedback_type"] = FeedbackType(data["feedback_type"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class PreferenceManager:
    """
    Manages user preferences and learns from feedback.
    """

    def __init__(self, preferences_path: Path):
        self.preferences_path = Path(preferences_path)
        self.preferences_path.parent.mkdir(parents=True, exist_ok=True)
        self.feedback_history_path = self.preferences_path.parent / "feedback_history.json"
        self._load_preferences()
        self._load_feedback_history()

    def _load_preferences(self) -> None:
        """Load user preferences."""
        if self.preferences_path.exists():
            with open(self.preferences_path, 'r') as f:
                self.preferences = json.load(f)
        else:
            self.preferences = {
                "topic_weights": {},  # topic -> weight (0.0 to 1.0)
                "category_weights": {  # category -> weight
                    "research": 1.0,
                    "problem_solution": 1.0,
                    "opportunity": 1.0,
                    "action_items": 1.0,
                    "metrics": 1.0,
                    "news": 1.0,
                },
                "dismissed_topics": [],
                "favorite_topics": [],
                "preferred_time": "06:00",
                "preferred_card_count": 8,
                "preferred_detail_level": "detailed",  # minimal, detailed, comprehensive
                "last_updated": datetime.now().isoformat(),
            }

    def _save_preferences(self) -> None:
        """Save user preferences."""
        self.preferences["last_updated"] = datetime.now().isoformat()
        with open(self.preferences_path, 'w') as f:
            json.dump(self.preferences, f, indent=2)

    def _load_feedback_history(self) -> None:
        """Load feedback history."""
        if self.feedback_history_path.exists():
            with open(self.feedback_history_path, 'r') as f:
                data = json.load(f)
                self.feedback_history = [
                    UserFeedback.from_dict(item) for item in data
                ]
        else:
            self.feedback_history = []

    def _save_feedback_history(self) -> None:
        """Save feedback history."""
        data = [fb.to_dict() for fb in self.feedback_history]
        with open(self.feedback_history_path, 'w') as f:
            json.dump(data, f, indent=2)

    def record_feedback(
        self,
        card_id: str,
        feedback_type: FeedbackType,
        card_category: str,
        card_topic: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Record user feedback and update preferences."""
        feedback = UserFeedback(
            card_id=card_id,
            feedback_type=feedback_type,
            timestamp=datetime.now(),
            card_category=card_category,
            card_topic=card_topic,
            notes=notes,
        )

        self.feedback_history.append(feedback)
        self._save_feedback_history()

        # Update preferences based on feedback
        self._update_preferences_from_feedback(feedback)

    def _update_preferences_from_feedback(self, feedback: UserFeedback) -> None:
        """Update preferences based on feedback."""
        learning_rate = 0.1

        # Update category weights
        current_weight = self.preferences["category_weights"].get(feedback.card_category, 1.0)

        if feedback.feedback_type in [FeedbackType.THUMBS_UP, FeedbackType.SAVE, FeedbackType.SHARE]:
            # Increase weight for positive feedback
            new_weight = min(1.0, current_weight + learning_rate * (1.0 - current_weight))
        elif feedback.feedback_type == FeedbackType.THUMBS_DOWN:
            # Decrease weight for negative feedback
            new_weight = max(0.1, current_weight - learning_rate * current_weight)
        elif feedback.feedback_type == FeedbackType.DISMISS:
            # Slight decrease for dismissals
            new_weight = max(0.3, current_weight - 0.05 * current_weight)
        else:
            new_weight = current_weight

        self.preferences["category_weights"][feedback.card_category] = new_weight

        # Update topic weights if topic is specified
        if feedback.card_topic:
            current_topic_weight = self.preferences["topic_weights"].get(feedback.card_topic, 1.0)

            if feedback.feedback_type in [FeedbackType.THUMBS_UP, FeedbackType.SAVE]:
                new_topic_weight = min(1.0, current_topic_weight + learning_rate * (1.0 - current_topic_weight))
                if feedback.card_topic not in self.preferences["favorite_topics"]:
                    self.preferences["favorite_topics"].append(feedback.card_topic)
            elif feedback.feedback_type == FeedbackType.THUMBS_DOWN:
                new_topic_weight = max(0.1, current_topic_weight - learning_rate * current_topic_weight)
            elif feedback.feedback_type == FeedbackType.DISMISS:
                new_topic_weight = max(0.3, current_topic_weight - 0.05 * current_topic_weight)
                if feedback.card_topic not in self.preferences["dismissed_topics"]:
                    self.preferences["dismissed_topics"].append(feedback.card_topic)
            else:
                new_topic_weight = current_topic_weight

            self.preferences["topic_weights"][feedback.card_topic] = new_topic_weight

        self._save_preferences()

    def get_topic_weight(self, topic: str) -> float:
        """Get the preference weight for a topic."""
        return self.preferences["topic_weights"].get(topic, 1.0)

    def get_category_weight(self, category: str) -> float:
        """Get the preference weight for a category."""
        return self.preferences["category_weights"].get(category, 1.0)

    def is_topic_dismissed(self, topic: str) -> bool:
        """Check if a topic has been dismissed."""
        return topic in self.preferences.get("dismissed_topics", [])

    def is_topic_favorite(self, topic: str) -> bool:
        """Check if a topic is a favorite."""
        return topic in self.preferences.get("favorite_topics", [])

    def get_favorite_topics(self) -> List[str]:
        """Get list of favorite topics."""
        return self.preferences.get("favorite_topics", [])

    def add_favorite_topic(self, topic: str) -> None:
        """Add a topic to favorites."""
        if topic not in self.preferences["favorite_topics"]:
            self.preferences["favorite_topics"].append(topic)
            self._save_preferences()

    def remove_favorite_topic(self, topic: str) -> None:
        """Remove a topic from favorites."""
        if topic in self.preferences["favorite_topics"]:
            self.preferences["favorite_topics"].remove(topic)
            self._save_preferences()

    def set_preferred_card_count(self, count: int) -> None:
        """Set preferred number of cards per update."""
        self.preferences["preferred_card_count"] = max(1, min(20, count))
        self._save_preferences()

    def set_detail_level(self, level: str) -> None:
        """Set preferred detail level."""
        if level in ["minimal", "detailed", "comprehensive"]:
            self.preferences["preferred_detail_level"] = level
            self._save_preferences()

    def get_feedback_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary of recent feedback."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)

        recent_feedback = [fb for fb in self.feedback_history if fb.timestamp > cutoff]

        summary = {
            "total_feedback": len(recent_feedback),
            "by_type": {},
            "by_category": {},
            "top_topics": {},
        }

        for fb in recent_feedback:
            # Count by feedback type
            type_name = fb.feedback_type.value
            summary["by_type"][type_name] = summary["by_type"].get(type_name, 0) + 1

            # Count by category
            summary["by_category"][fb.card_category] = summary["by_category"].get(fb.card_category, 0) + 1

            # Count by topic
            if fb.card_topic:
                summary["top_topics"][fb.card_topic] = summary["top_topics"].get(fb.card_topic, 0) + 1

        # Sort top topics
        summary["top_topics"] = dict(
            sorted(summary["top_topics"].items(), key=lambda x: x[1], reverse=True)[:10]
        )

        return summary

    def get_preferences_dict(self) -> Dict[str, Any]:
        """Get all preferences as a dictionary."""
        return self.preferences.copy()
