"""
Memory storage system for conversation history and context.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
import json
import hashlib


@dataclass
class ConversationEntry:
    """Represents a single conversation entry."""

    id: str
    timestamp: datetime
    messages: List[Dict[str, str]]  # [{"role": "user/assistant", "content": "..."}]
    topics: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)  # People, projects, tools mentioned
    action_items: List[str] = field(default_factory=list)
    problems: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationEntry':
        """Create from dictionary."""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    @property
    def message_count(self) -> int:
        """Number of messages in conversation."""
        return len(self.messages)

    @property
    def summary(self) -> str:
        """Generate a brief summary of the conversation."""
        if not self.messages:
            return "Empty conversation"

        first_msg = next((m["content"] for m in self.messages if m["role"] == "user"), "")
        return first_msg[:100] + "..." if len(first_msg) > 100 else first_msg


class MemoryStore:
    """
    Manages conversation history and extracted insights.
    """

    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_path / "index.json"
        self._load_index()

    def _load_index(self) -> None:
        """Load the conversation index."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {"conversations": [], "last_updated": datetime.now().isoformat()}

    def _save_index(self) -> None:
        """Save the conversation index."""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def add_conversation(self, conversation: ConversationEntry) -> None:
        """Add a conversation to the store."""
        # Save conversation to its own file
        conv_file = self.storage_path / f"{conversation.id}.json"
        with open(conv_file, 'w') as f:
            json.dump(conversation.to_dict(), f, indent=2)

        # Update index
        if conversation.id not in [c["id"] for c in self.index["conversations"]]:
            self.index["conversations"].append({
                "id": conversation.id,
                "timestamp": conversation.timestamp.isoformat(),
                "message_count": conversation.message_count,
                "topics": conversation.topics,
            })
            self._save_index()

    def get_conversation(self, conversation_id: str) -> Optional[ConversationEntry]:
        """Retrieve a specific conversation."""
        conv_file = self.storage_path / f"{conversation_id}.json"
        if not conv_file.exists():
            return None

        with open(conv_file, 'r') as f:
            data = json.load(f)
        return ConversationEntry.from_dict(data)

    def get_recent_conversations(
        self,
        days: int = 7,
        max_count: int = 50,
        min_messages: int = 3
    ) -> List[ConversationEntry]:
        """Get recent conversations within the specified timeframe."""
        cutoff = datetime.now() - timedelta(days=days)
        conversations = []

        for conv_info in reversed(self.index["conversations"]):
            if len(conversations) >= max_count:
                break

            timestamp = datetime.fromisoformat(conv_info["timestamp"])
            if timestamp < cutoff:
                continue

            if conv_info["message_count"] < min_messages:
                continue

            conv = self.get_conversation(conv_info["id"])
            if conv:
                conversations.append(conv)

        return conversations

    def search_by_topic(self, topic: str, max_results: int = 10) -> List[ConversationEntry]:
        """Search conversations by topic."""
        results = []
        topic_lower = topic.lower()

        for conv_info in reversed(self.index["conversations"]):
            if len(results) >= max_results:
                break

            if any(topic_lower in t.lower() for t in conv_info.get("topics", [])):
                conv = self.get_conversation(conv_info["id"])
                if conv:
                    results.append(conv)

        return results

    def search_by_entity(self, entity: str, max_results: int = 10) -> List[ConversationEntry]:
        """Search conversations mentioning a specific entity."""
        results = []
        entity_lower = entity.lower()

        for conv_info in self.index["conversations"]:
            if len(results) >= max_results:
                break

            conv = self.get_conversation(conv_info["id"])
            if conv and any(entity_lower in e.lower() for e in conv.entities):
                results.append(conv)

        return results

    def get_all_topics(self, days: Optional[int] = None) -> List[str]:
        """Get all unique topics, optionally filtered by recency."""
        topics = set()
        cutoff = datetime.now() - timedelta(days=days) if days else None

        for conv_info in self.index["conversations"]:
            if cutoff:
                timestamp = datetime.fromisoformat(conv_info["timestamp"])
                if timestamp < cutoff:
                    continue

            topics.update(conv_info.get("topics", []))

        return sorted(list(topics))

    def get_all_action_items(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get all action items from recent conversations."""
        conversations = self.get_recent_conversations(days=days)
        action_items = []

        for conv in conversations:
            for item in conv.action_items:
                action_items.append({
                    "item": item,
                    "conversation_id": conv.id,
                    "timestamp": conv.timestamp,
                })

        return sorted(action_items, key=lambda x: x["timestamp"], reverse=True)

    def get_all_problems(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get all problems from recent conversations."""
        conversations = self.get_recent_conversations(days=days)
        problems = []

        for conv in conversations:
            for problem in conv.problems:
                problems.append({
                    "problem": problem,
                    "conversation_id": conv.id,
                    "timestamp": conv.timestamp,
                })

        return sorted(problems, key=lambda x: x["timestamp"], reverse=True)

    def get_all_opportunities(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get all opportunities from recent conversations."""
        conversations = self.get_recent_conversations(days=days)
        opportunities = []

        for conv in conversations:
            for opp in conv.opportunities:
                opportunities.append({
                    "opportunity": opp,
                    "conversation_id": conv.id,
                    "timestamp": conv.timestamp,
                })

        return sorted(opportunities, key=lambda x: x["timestamp"], reverse=True)

    def update_conversation_metadata(
        self,
        conversation_id: str,
        topics: Optional[List[str]] = None,
        entities: Optional[List[str]] = None,
        action_items: Optional[List[str]] = None,
        problems: Optional[List[str]] = None,
        opportunities: Optional[List[str]] = None,
    ) -> None:
        """Update extracted metadata for a conversation."""
        conv = self.get_conversation(conversation_id)
        if not conv:
            return

        if topics is not None:
            conv.topics = topics
        if entities is not None:
            conv.entities = entities
        if action_items is not None:
            conv.action_items = action_items
        if problems is not None:
            conv.problems = problems
        if opportunities is not None:
            conv.opportunities = opportunities

        self.add_conversation(conv)

    @staticmethod
    def generate_conversation_id(messages: List[Dict[str, str]]) -> str:
        """Generate a unique conversation ID from messages."""
        content = json.dumps(messages, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the memory store."""
        total_conversations = len(self.index["conversations"])
        recent_conversations = len(self.get_recent_conversations(days=7))
        all_topics = self.get_all_topics()

        return {
            "total_conversations": total_conversations,
            "recent_conversations_7d": recent_conversations,
            "unique_topics": len(all_topics),
            "last_updated": self.index.get("last_updated"),
        }
