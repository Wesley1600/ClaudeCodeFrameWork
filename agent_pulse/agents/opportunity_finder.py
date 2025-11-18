"""
Opportunity Finder Agent

Identifies opportunities based on:
- Mentioned ideas and interests in conversations
- Trends in the user's field
- Connections between different topics
- Potential optimizations and improvements
"""

from typing import List, Dict, Any, Set, Optional
from datetime import datetime
from ..storage.memory_store import MemoryStore


class OpportunityFinder:
    """
    Identifies opportunities for the user.
    """

    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store

    def find_opportunities(
        self,
        topics: List[str],
        entities: List[str],
        user_interests: List[str],
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Find opportunities based on conversation context.

        Args:
            topics: Active topics from conversations
            entities: Mentioned entities (projects, tools, etc.)
            user_interests: User's stated interests
            days: Days to look back

        Returns:
            List of identified opportunities
        """
        opportunities = []

        # Find learning opportunities
        learning_opps = self._find_learning_opportunities(topics, user_interests)
        opportunities.extend(learning_opps)

        # Find collaboration opportunities
        collab_opps = self._find_collaboration_opportunities(entities)
        opportunities.extend(collab_opps)

        # Find optimization opportunities
        optimization_opps = self._find_optimization_opportunities(days)
        opportunities.extend(optimization_opps)

        # Find trend-based opportunities
        trend_opps = self._find_trend_opportunities(topics)
        opportunities.extend(trend_opps)

        # Rank and return top opportunities
        ranked = self._rank_opportunities(opportunities)
        return ranked[:10]

    def _find_learning_opportunities(
        self,
        topics: List[str],
        user_interests: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Identify learning opportunities based on topics and interests.
        """
        opportunities = []

        # Find topics that overlap with interests
        for topic in topics:
            for interest in user_interests:
                if interest.lower() in topic.lower() or topic.lower() in interest.lower():
                    opportunities.append({
                        "type": "learning",
                        "category": "skill_development",
                        "title": f"Deepen knowledge in {topic}",
                        "description": f"You've been discussing {topic} recently. Consider exploring advanced concepts or related areas.",
                        "priority": "medium",
                        "effort": "medium",
                        "impact": "high",
                        "actions": [
                            f"Find advanced tutorials on {topic}",
                            f"Build a project using {topic}",
                            f"Join communities focused on {topic}",
                        ],
                        "timestamp": datetime.now().isoformat(),
                    })

        # Identify emerging topics
        for topic in topics:
            if topic not in user_interests:
                opportunities.append({
                    "type": "learning",
                    "category": "exploration",
                    "title": f"Explore {topic}",
                    "description": f"{topic} has appeared in your recent conversations. It might be worth exploring further.",
                    "priority": "low",
                    "effort": "low",
                    "impact": "medium",
                    "actions": [
                        f"Read introductory articles about {topic}",
                        f"Watch overview videos on {topic}",
                    ],
                    "timestamp": datetime.now().isoformat(),
                })

        return opportunities

    def _find_collaboration_opportunities(
        self,
        entities: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Identify potential collaboration opportunities.
        """
        opportunities = []

        # Find projects that could be integrated
        if len(entities) > 1:
            for i, entity1 in enumerate(entities):
                for entity2 in entities[i+1:]:
                    opportunities.append({
                        "type": "collaboration",
                        "category": "integration",
                        "title": f"Integrate {entity1} with {entity2}",
                        "description": f"Both {entity1} and {entity2} are active in your workflow. Consider integration opportunities.",
                        "priority": "low",
                        "effort": "high",
                        "impact": "medium",
                        "actions": [
                            f"Research {entity1} and {entity2} integration",
                            "Identify common use cases",
                            "Prototype a simple integration",
                        ],
                        "timestamp": datetime.now().isoformat(),
                    })

        return opportunities[:3]  # Limit integration suggestions

    def _find_optimization_opportunities(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Identify optimization opportunities from past problems.
        """
        opportunities = []

        # Get recent problems
        problems = self.memory_store.get_all_problems(days=days)

        # Group similar problems
        problem_groups = self._group_similar_items([p["problem"] for p in problems])

        for group in problem_groups:
            if len(group) >= 2:  # Recurring problem
                opportunities.append({
                    "type": "optimization",
                    "category": "automation",
                    "title": "Automate recurring issue resolution",
                    "description": f"You've encountered similar issues multiple times. Consider automating the solution.",
                    "priority": "high",
                    "effort": "medium",
                    "impact": "high",
                    "actions": [
                        "Document the recurring issue",
                        "Create a script or tool to automate the fix",
                        "Add it to your toolkit",
                    ],
                    "related_problems": group,
                    "timestamp": datetime.now().isoformat(),
                })

        return opportunities

    def _find_trend_opportunities(self, topics: List[str]) -> List[Dict[str, Any]]:
        """
        Identify opportunities based on trending topics.
        """
        opportunities = []

        # Topics that are gaining popularity
        trending_topics = ["AI agents", "LLMs", "automation", "data visualization"]

        for trend in trending_topics:
            for topic in topics:
                if trend.lower() in topic.lower():
                    opportunities.append({
                        "type": "trend",
                        "category": "market_opportunity",
                        "title": f"Leverage {trend} in your work",
                        "description": f"{trend} is trending and aligns with your recent work in {topic}.",
                        "priority": "medium",
                        "effort": "medium",
                        "impact": "high",
                        "actions": [
                            f"Research latest developments in {trend}",
                            f"Identify use cases in your projects",
                            f"Build a proof of concept",
                        ],
                        "timestamp": datetime.now().isoformat(),
                    })

        return opportunities

    def _group_similar_items(self, items: List[str]) -> List[List[str]]:
        """
        Group similar items (simple keyword-based approach).
        """
        groups = []
        used = set()

        for i, item1 in enumerate(items):
            if i in used:
                continue

            group = [item1]
            used.add(i)

            for j, item2 in enumerate(items[i+1:], start=i+1):
                if j in used:
                    continue

                # Simple similarity: shared keywords
                words1 = set(item1.lower().split())
                words2 = set(item2.lower().split())

                if len(words1 & words2) >= 2:  # At least 2 shared words
                    group.append(item2)
                    used.add(j)

            if len(group) > 1:
                groups.append(group)

        return groups

    def _rank_opportunities(
        self,
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rank opportunities by priority, impact, and effort.
        """
        priority_scores = {"high": 3, "medium": 2, "low": 1}
        impact_scores = {"high": 3, "medium": 2, "low": 1}
        effort_scores = {"low": 3, "medium": 2, "high": 1}  # Lower effort is better

        for opp in opportunities:
            priority = priority_scores.get(opp.get("priority", "low"), 1)
            impact = impact_scores.get(opp.get("impact", "low"), 1)
            effort = effort_scores.get(opp.get("effort", "medium"), 2)

            # Composite score: prioritize high impact, low effort, high priority
            opp["score"] = (priority * 2) + (impact * 3) + (effort * 1.5)

        # Sort by score (descending)
        sorted_opps = sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)

        return sorted_opps

    def suggest_next_actions(
        self,
        opportunities: List[Dict[str, Any]],
        max_suggestions: int = 5
    ) -> List[str]:
        """
        Suggest immediate next actions based on opportunities.
        """
        actions = []

        for opp in opportunities[:max_suggestions]:
            if "actions" in opp and opp["actions"]:
                actions.append({
                    "opportunity": opp["title"],
                    "next_action": opp["actions"][0],  # First action
                    "category": opp.get("category", "general"),
                })

        return actions

    def identify_knowledge_gaps(
        self,
        topics: List[str],
        user_interests: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Identify knowledge gaps based on topics and interests.
        """
        gaps = []

        # Topics mentioned but not in user interests
        for topic in topics:
            if not any(interest.lower() in topic.lower() for interest in user_interests):
                gaps.append({
                    "topic": topic,
                    "type": "emerging_interest",
                    "suggestion": f"Consider adding {topic} to your learning roadmap",
                })

        return gaps
