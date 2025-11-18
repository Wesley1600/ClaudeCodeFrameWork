"""
Update Card Generator

Creates visual update cards for different types of information:
- Research updates
- Problem solutions
- Opportunities
- Action items
- Metrics and progress
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json


@dataclass
class UpdateCard:
    """
    Represents a visual update card.
    """

    id: str
    title: str
    category: str  # research, problem_solution, opportunity, action_items, metrics, news
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
    sources: List[Dict[str, str]] = field(default_factory=list)
    priority: str = "medium"  # low, medium, high
    tags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    read: bool = False
    saved: bool = False

    def to_markdown(self, detail_level: str = "detailed") -> str:
        """
        Render card as markdown.

        Args:
            detail_level: minimal, detailed, or comprehensive
        """
        lines = []

        # Header
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(self.priority, "⚪")
        category_emoji = {
            "research": "🔍",
            "problem_solution": "🔧",
            "opportunity": "💡",
            "action_items": "✅",
            "metrics": "📊",
            "news": "📰",
        }.get(self.category, "📋")

        lines.append(f"## {category_emoji} {self.title} {priority_emoji}")
        lines.append("")

        # Summary
        lines.append(f"**Summary:** {self.summary}")
        lines.append("")

        # Details (if detailed or comprehensive)
        if detail_level in ["detailed", "comprehensive"] and self.details:
            lines.append("### Details")
            for key, value in self.details.items():
                if isinstance(value, list):
                    lines.append(f"**{key.replace('_', ' ').title()}:**")
                    for item in value:
                        if isinstance(item, dict):
                            # Format dict items
                            for k, v in item.items():
                                lines.append(f"  - **{k}:** {v}")
                        else:
                            lines.append(f"  - {item}")
                else:
                    lines.append(f"**{key.replace('_', ' ').title()}:** {value}")
            lines.append("")

        # Actions
        if self.actions:
            lines.append("### Suggested Actions")
            for action in self.actions:
                lines.append(f"- [ ] {action}")
            lines.append("")

        # Sources (if comprehensive or detailed with include_sources)
        if detail_level == "comprehensive" and self.sources:
            lines.append("### Sources")
            for source in self.sources:
                title = source.get("title", "Source")
                url = source.get("url", "#")
                lines.append(f"- [{title}]({url})")
            lines.append("")

        # Tags
        if self.tags:
            tag_str = " ".join(f"`{tag}`" for tag in self.tags)
            lines.append(f"**Tags:** {tag_str}")
            lines.append("")

        # Footer
        lines.append(f"*Generated: {self.timestamp}* | *Card ID: {self.id[:8]}*")
        lines.append("")
        lines.append("---")
        lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "summary": self.summary,
            "details": self.details,
            "actions": self.actions,
            "sources": self.sources,
            "priority": self.priority,
            "tags": self.tags,
            "timestamp": self.timestamp,
            "read": self.read,
            "saved": self.saved,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UpdateCard':
        """Create from dictionary."""
        return cls(**data)


class UpdateCardGenerator:
    """
    Generates update cards from various data sources.
    """

    def __init__(self, detail_level: str = "detailed", include_sources: bool = True):
        self.detail_level = detail_level
        self.include_sources = include_sources

    def generate_research_card(
        self,
        topic: str,
        research_data: Dict[str, Any]
    ) -> UpdateCard:
        """
        Generate a research update card.
        """
        card_id = self._generate_card_id(f"research_{topic}")

        summary = research_data.get("summary", f"Research update on {topic}")

        details = {}
        if "key_findings" in research_data:
            details["key_findings"] = research_data["key_findings"]
        if "recent_developments" in research_data:
            details["recent_developments"] = research_data["recent_developments"]

        actions = research_data.get("action_suggestions", [])

        sources = []
        if self.include_sources and "resources" in research_data:
            sources = research_data["resources"]

        return UpdateCard(
            id=card_id,
            title=f"Research: {topic}",
            category="research",
            summary=summary,
            details=details,
            actions=actions,
            sources=sources,
            priority="medium",
            tags=[topic, "research"],
        )

    def generate_problem_solution_card(
        self,
        problem: Dict[str, Any]
    ) -> UpdateCard:
        """
        Generate a problem solution card.
        """
        problem_text = problem.get("problem", "Unknown problem")
        card_id = self._generate_card_id(f"problem_{problem_text}")

        summary = f"Solution suggestions for: {problem_text[:100]}"

        details = {
            "category": problem.get("category", "general"),
            "suggested_solutions": problem.get("suggested_solutions", []),
        }

        actions = problem.get("suggested_solutions", [])[:3]  # Top 3 solutions as actions

        sources = problem.get("resources", [])

        priority = problem.get("priority", "medium")

        return UpdateCard(
            id=card_id,
            title=f"Solution: {problem.get('category', 'General').title()} Issue",
            category="problem_solution",
            summary=summary,
            details=details,
            actions=actions,
            sources=sources if self.include_sources else [],
            priority=priority,
            tags=[problem.get("category", "general"), "solution"],
        )

    def generate_opportunity_card(
        self,
        opportunity: Dict[str, Any]
    ) -> UpdateCard:
        """
        Generate an opportunity card.
        """
        card_id = self._generate_card_id(f"opportunity_{opportunity.get('title', '')}")

        title = opportunity.get("title", "New Opportunity")
        summary = opportunity.get("description", "")

        details = {
            "type": opportunity.get("type", "unknown"),
            "priority": opportunity.get("priority", "medium"),
            "effort": opportunity.get("effort", "medium"),
            "impact": opportunity.get("impact", "medium"),
        }

        actions = opportunity.get("actions", [])

        return UpdateCard(
            id=card_id,
            title=f"Opportunity: {title}",
            category="opportunity",
            summary=summary,
            details=details,
            actions=actions,
            sources=[],
            priority=opportunity.get("priority", "medium"),
            tags=[opportunity.get("type", "general"), "opportunity"],
        )

    def generate_action_items_card(
        self,
        action_items: List[Dict[str, Any]]
    ) -> UpdateCard:
        """
        Generate an action items summary card.
        """
        card_id = self._generate_card_id(f"actions_{datetime.now().isoformat()}")

        summary = f"You have {len(action_items)} pending action items"

        details = {
            "total_items": len(action_items),
            "items": [item.get("item", "") for item in action_items[:10]],
        }

        actions = [item.get("item", "") for item in action_items[:5]]

        return UpdateCard(
            id=card_id,
            title="Action Items Summary",
            category="action_items",
            summary=summary,
            details=details,
            actions=actions,
            sources=[],
            priority="high",
            tags=["action_items", "todo"],
        )

    def generate_metrics_card(
        self,
        metric_name: str,
        metric_data: Dict[str, Any]
    ) -> UpdateCard:
        """
        Generate a metrics card.
        """
        card_id = self._generate_card_id(f"metrics_{metric_name}")

        summary = metric_data.get("summary", f"Update on {metric_name}")

        details = {
            "current_value": metric_data.get("current_value"),
            "previous_value": metric_data.get("previous_value"),
            "change": metric_data.get("change"),
            "trend": metric_data.get("trend", "stable"),
        }

        actions = metric_data.get("recommendations", [])

        return UpdateCard(
            id=card_id,
            title=f"Metrics: {metric_name}",
            category="metrics",
            summary=summary,
            details=details,
            actions=actions,
            sources=[],
            priority="medium",
            tags=[metric_name, "metrics"],
        )

    def generate_news_card(
        self,
        topic: str,
        news_items: List[Dict[str, Any]]
    ) -> UpdateCard:
        """
        Generate a news update card.
        """
        card_id = self._generate_card_id(f"news_{topic}")

        summary = f"{len(news_items)} recent updates on {topic}"

        details = {
            "updates": [
                {
                    "title": item.get("title", ""),
                    "summary": item.get("summary", "")[:200],
                    "date": item.get("date", ""),
                }
                for item in news_items[:5]
            ]
        }

        sources = [
            {
                "title": item.get("title", ""),
                "url": item.get("url", "#"),
            }
            for item in news_items
        ]

        return UpdateCard(
            id=card_id,
            title=f"News: {topic}",
            category="news",
            summary=summary,
            details=details,
            actions=[f"Review latest updates on {topic}"],
            sources=sources if self.include_sources else [],
            priority="low",
            tags=[topic, "news"],
        )

    def generate_daily_digest(
        self,
        cards: List[UpdateCard],
        date: Optional[str] = None
    ) -> str:
        """
        Generate a daily digest from multiple cards.
        """
        if date is None:
            date = datetime.now().strftime("%B %d, %Y")

        lines = [
            f"# 🌅 Daily Pulse - {date}",
            "",
            f"*Good morning! Here are {len(cards)} updates for you today.*",
            "",
            "---",
            "",
        ]

        # Group cards by category
        by_category = {}
        for card in cards:
            category = card.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(card)

        # Render each category
        category_order = ["action_items", "problem_solution", "opportunity", "research", "metrics", "news"]

        for category in category_order:
            if category in by_category:
                category_cards = by_category[category]
                category_name = category.replace("_", " ").title()

                lines.append(f"## {category_name} ({len(category_cards)})")
                lines.append("")

                for card in category_cards:
                    lines.append(card.to_markdown(self.detail_level))

        lines.append("---")
        lines.append("")
        lines.append("*End of Daily Pulse*")
        lines.append("")

        return "\n".join(lines)

    def _generate_card_id(self, content: str) -> str:
        """Generate a unique card ID."""
        hash_input = f"{content}_{datetime.now().isoformat()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
