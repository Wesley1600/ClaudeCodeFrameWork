"""
Pulse Orchestrator

Main orchestrator that coordinates all agents and generates pulse updates.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json

from .config import PulseConfig
from .scheduler import PulseScheduler
from ..storage.memory_store import MemoryStore, ConversationEntry
from ..storage.preferences import PreferenceManager, FeedbackType
from ..agents.conversation_analyzer import ConversationAnalyzer
from ..agents.research_agent import ResearchAgent
from ..agents.opportunity_finder import OpportunityFinder
from ..agents.problem_solver import ProblemSolver
from ..generators.card_generator import UpdateCardGenerator, UpdateCard


class PulseOrchestrator:
    """
    Main orchestrator for the Agent Pulse system.

    Coordinates all agents to generate proactive updates.
    """

    def __init__(self, config: Optional[PulseConfig] = None):
        """
        Initialize the pulse orchestrator.

        Args:
            config: Configuration object. If None, loads default config.
        """
        self.config = config or PulseConfig.load()

        # Initialize storage
        self.memory_store = MemoryStore(self.config.memory_store_path)
        self.preference_manager = PreferenceManager(self.config.preferences_path)

        # Initialize agents
        self.conversation_analyzer = ConversationAnalyzer(self.memory_store)
        self.research_agent = ResearchAgent(max_searches=self.config.max_web_searches)
        self.opportunity_finder = OpportunityFinder(self.memory_store)
        self.problem_solver = ProblemSolver(self.memory_store)

        # Initialize card generator
        self.card_generator = UpdateCardGenerator(
            detail_level=self.config.card_style,
            include_sources=self.config.include_sources,
        )

        # Initialize scheduler
        self.scheduler = PulseScheduler(
            schedule_time=self.config.schedule_time,
            frequency=self.config.schedule_frequency,
            enabled=self.config.schedule_enabled,
        )
        self.scheduler.set_callback(self.generate_pulse_update)

        # Pulse history
        self.pulse_history_path = self.config.memory_store_path.parent / "pulse_history"
        self.pulse_history_path.mkdir(parents=True, exist_ok=True)

    def add_conversation(
        self,
        messages: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationEntry:
        """
        Add a conversation to the memory store.

        Args:
            messages: List of messages [{"role": "user/assistant", "content": "..."}]
            metadata: Optional metadata

        Returns:
            ConversationEntry object
        """
        conversation_id = MemoryStore.generate_conversation_id(messages)

        conversation = ConversationEntry(
            id=conversation_id,
            timestamp=datetime.now(),
            messages=messages,
            metadata=metadata or {},
        )

        self.memory_store.add_conversation(conversation)
        return conversation

    def generate_pulse_update(self) -> Dict[str, Any]:
        """
        Generate a complete pulse update.

        This is the main method that coordinates all agents.

        Returns:
            Dictionary containing all update cards and metadata
        """
        print(f"\n{'='*60}")
        print(f"🌅 Generating Pulse Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}\n")

        cards = []

        # Step 1: Analyze recent conversations
        if self.config.enable_conversation_analysis:
            print("📊 Analyzing recent conversations...")
            conversation_insights = self.conversation_analyzer.analyze_recent_conversations(
                days=self.config.lookback_days,
                max_count=self.config.max_conversations_to_analyze,
            )
            print(f"   Found {conversation_insights['total_conversations']} recent conversations")
            print(f"   Top topics: {', '.join([t['item'] for t in conversation_insights['top_topics'][:3]])}")
        else:
            conversation_insights = None

        # Step 2: Generate action items card
        if conversation_insights and conversation_insights.get("recent_action_items"):
            print("\n✅ Generating action items card...")
            action_items = self.memory_store.get_all_action_items(days=self.config.lookback_days)
            if action_items:
                card = self.card_generator.generate_action_items_card(action_items)
                cards.append(card)
                print(f"   Created card with {len(action_items)} action items")

        # Step 3: Generate problem solution cards
        if self.config.enable_problem_solving:
            print("\n🔧 Analyzing problems and generating solutions...")
            problem_analysis = self.problem_solver.analyze_problems(days=self.config.lookback_days)

            if problem_analysis["all_problems"]:
                # Create cards for high-priority problems
                high_priority = [p for p in problem_analysis["all_problems"] if p.get("priority") == "high"]
                for problem in high_priority[:3]:  # Top 3 high-priority problems
                    card = self.card_generator.generate_problem_solution_card(problem)
                    cards.append(card)
                print(f"   Created {len(high_priority[:3])} problem solution cards")

        # Step 4: Find and generate opportunity cards
        if self.config.enable_opportunity_finding and conversation_insights:
            print("\n💡 Finding opportunities...")
            topics = [t["item"] for t in conversation_insights.get("top_topics", [])]
            entities = [e["item"] for e in conversation_insights.get("top_entities", [])]

            opportunities = self.opportunity_finder.find_opportunities(
                topics=topics,
                entities=entities,
                user_interests=self.config.user_interests,
                days=self.config.lookback_days,
            )

            for opp in opportunities[:3]:  # Top 3 opportunities
                card = self.card_generator.generate_opportunity_card(opp)
                cards.append(card)
            print(f"   Created {min(3, len(opportunities))} opportunity cards")

        # Step 5: Conduct research on trending topics
        if self.config.enable_research and conversation_insights:
            print("\n🔍 Conducting research on trending topics...")
            top_topics = [t["item"] for t in conversation_insights.get("top_topics", [])[:3]]

            # Filter by user preferences
            weighted_topics = []
            for topic in top_topics:
                weight = self.preference_manager.get_topic_weight(topic)
                if weight > 0.3:  # Only research topics with reasonable weight
                    weighted_topics.append(topic)

            for topic in weighted_topics[:2]:  # Research top 2 topics
                research_result = self.research_agent.research_topic(
                    topic=topic,
                    focus_areas=self.config.focus_areas,
                    include_news=True,
                )
                card = self.card_generator.generate_research_card(topic, research_result)
                cards.append(card)
            print(f"   Created {len(weighted_topics[:2])} research cards")

        # Step 6: Filter and rank cards by preferences
        print("\n🎯 Applying user preferences...")
        filtered_cards = self._filter_cards_by_preferences(cards)
        ranked_cards = self._rank_cards_by_preferences(filtered_cards)

        # Limit to preferred card count
        final_cards = ranked_cards[:self.config.max_topics_per_update]

        # Step 7: Generate the pulse update
        pulse_update = {
            "timestamp": datetime.now().isoformat(),
            "cards": [card.to_dict() for card in final_cards],
            "summary": {
                "total_cards": len(final_cards),
                "by_category": self._count_by_category(final_cards),
                "conversations_analyzed": conversation_insights["total_conversations"] if conversation_insights else 0,
            },
        }

        # Save pulse update
        self._save_pulse_update(pulse_update)

        print(f"\n✨ Pulse update generated with {len(final_cards)} cards")
        print(f"{'='*60}\n")

        return pulse_update

    def render_pulse_update(
        self,
        pulse_update: Optional[Dict[str, Any]] = None,
        output_format: str = "markdown"
    ) -> str:
        """
        Render a pulse update in the specified format.

        Args:
            pulse_update: Pulse update dict. If None, generates a new one.
            output_format: Output format (markdown, json)

        Returns:
            Rendered string
        """
        if pulse_update is None:
            pulse_update = self.generate_pulse_update()

        if output_format == "json":
            return json.dumps(pulse_update, indent=2)

        # Markdown format (default)
        cards = [UpdateCard.from_dict(c) for c in pulse_update["cards"]]
        return self.card_generator.generate_daily_digest(cards)

    def record_feedback(
        self,
        card_id: str,
        feedback_type: str,
        notes: Optional[str] = None
    ) -> None:
        """
        Record user feedback on a card.

        Args:
            card_id: ID of the card
            feedback_type: Type of feedback (thumbs_up, thumbs_down, dismiss, save, share)
            notes: Optional notes
        """
        # Find the card to get its category and topic
        latest_pulse = self._load_latest_pulse()
        if not latest_pulse:
            print("No pulse update found")
            return

        card_dict = next((c for c in latest_pulse["cards"] if c["id"] == card_id), None)
        if not card_dict:
            print(f"Card {card_id} not found")
            return

        feedback_enum = FeedbackType(feedback_type)

        self.preference_manager.record_feedback(
            card_id=card_id,
            feedback_type=feedback_enum,
            card_category=card_dict["category"],
            card_topic=card_dict.get("tags", [None])[0],
            notes=notes,
        )

        print(f"Feedback recorded for card {card_id[:8]}")

    def _filter_cards_by_preferences(self, cards: List[UpdateCard]) -> List[UpdateCard]:
        """Filter cards based on user preferences."""
        filtered = []

        for card in cards:
            # Check if category is enabled
            category_weight = self.preference_manager.get_category_weight(card.category)
            if category_weight < 0.2:  # Skip very low-weighted categories
                continue

            # Check if topic is dismissed
            if card.tags:
                topic = card.tags[0]
                if self.preference_manager.is_topic_dismissed(topic):
                    continue

            filtered.append(card)

        return filtered

    def _rank_cards_by_preferences(self, cards: List[UpdateCard]) -> List[UpdateCard]:
        """Rank cards based on user preferences and priority."""
        priority_scores = {"high": 3, "medium": 2, "low": 1}

        card_scores = []
        for card in cards:
            # Base score from priority
            score = priority_scores.get(card.priority, 1)

            # Adjust by category weight
            category_weight = self.preference_manager.get_category_weight(card.category)
            score *= category_weight

            # Adjust by topic weight if available
            if card.tags:
                topic = card.tags[0]
                topic_weight = self.preference_manager.get_topic_weight(topic)
                score *= topic_weight

            # Boost favorite topics
            if card.tags and self.preference_manager.is_topic_favorite(card.tags[0]):
                score *= 1.5

            card_scores.append((card, score))

        # Sort by score (descending)
        sorted_cards = sorted(card_scores, key=lambda x: x[1], reverse=True)
        return [card for card, score in sorted_cards]

    def _count_by_category(self, cards: List[UpdateCard]) -> Dict[str, int]:
        """Count cards by category."""
        counts = {}
        for card in cards:
            counts[card.category] = counts.get(card.category, 0) + 1
        return counts

    def _save_pulse_update(self, pulse_update: Dict[str, Any]) -> None:
        """Save pulse update to history."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.pulse_history_path / f"pulse_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(pulse_update, f, indent=2)

    def _load_latest_pulse(self) -> Optional[Dict[str, Any]]:
        """Load the most recent pulse update."""
        pulse_files = sorted(self.pulse_history_path.glob("pulse_*.json"), reverse=True)

        if not pulse_files:
            return None

        with open(pulse_files[0], 'r') as f:
            return json.load(f)

    def get_pulse_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent pulse update history."""
        pulse_files = sorted(self.pulse_history_path.glob("pulse_*.json"), reverse=True)

        history = []
        for file in pulse_files[:count]:
            with open(file, 'r') as f:
                data = json.load(f)
                history.append({
                    "timestamp": data["timestamp"],
                    "card_count": data["summary"]["total_cards"],
                    "file": str(file),
                })

        return history

    def start_scheduler(self) -> None:
        """Start the pulse scheduler."""
        self.scheduler.start()

    def stop_scheduler(self) -> None:
        """Stop the pulse scheduler."""
        self.scheduler.stop()

    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            "memory_store": self.memory_store.get_statistics(),
            "scheduler": self.scheduler.get_status(),
            "config": {
                "schedule_enabled": self.config.schedule_enabled,
                "lookback_days": self.config.lookback_days,
                "max_topics": self.config.max_topics_per_update,
            },
            "preferences": {
                "user_interests": self.config.user_interests,
                "tracked_metrics": self.config.tracked_metrics,
                "favorite_topics": self.preference_manager.get_favorite_topics(),
            },
        }
