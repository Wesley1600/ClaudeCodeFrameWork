"""
Conversation Analyzer Agent

Analyzes past conversations to extract:
- Key topics and themes
- Mentioned entities (people, projects, tools)
- Action items and commitments
- Problems and challenges
- Opportunities and ideas
"""

from typing import List, Dict, Set, Any, Optional
from datetime import datetime
import re
from ..storage.memory_store import ConversationEntry, MemoryStore


class ConversationAnalyzer:
    """
    Analyzes conversations to extract meaningful insights.
    """

    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store

        # Keywords for different categories
        self.action_keywords = [
            "todo", "task", "need to", "should", "must", "will",
            "going to", "plan to", "remind", "follow up", "action item"
        ]

        self.problem_keywords = [
            "error", "bug", "issue", "problem", "failing", "broken",
            "not working", "crash", "exception", "warning", "stuck",
            "difficulty", "challenge", "blocker"
        ]

        self.opportunity_keywords = [
            "opportunity", "could improve", "potential", "idea",
            "enhancement", "feature request", "optimization",
            "interesting", "worth exploring", "consider"
        ]

        self.question_keywords = [
            "how to", "what is", "where", "when", "why",
            "can you", "could you", "would you", "help with"
        ]

    def analyze_conversation(self, conversation: ConversationEntry) -> Dict[str, Any]:
        """
        Analyze a single conversation and return extracted insights.
        """
        insights = {
            "topics": self._extract_topics(conversation),
            "entities": self._extract_entities(conversation),
            "action_items": self._extract_action_items(conversation),
            "problems": self._extract_problems(conversation),
            "opportunities": self._extract_opportunities(conversation),
            "questions": self._extract_questions(conversation),
            "sentiment": self._analyze_sentiment(conversation),
        }

        return insights

    def analyze_recent_conversations(
        self,
        days: int = 7,
        max_count: int = 50
    ) -> Dict[str, Any]:
        """
        Analyze recent conversations and aggregate insights.
        """
        conversations = self.memory_store.get_recent_conversations(
            days=days,
            max_count=max_count
        )

        all_topics = []
        all_entities = []
        all_action_items = []
        all_problems = []
        all_opportunities = []
        all_questions = []

        for conv in conversations:
            insights = self.analyze_conversation(conv)

            all_topics.extend(insights["topics"])
            all_entities.extend(insights["entities"])
            all_action_items.extend(insights["action_items"])
            all_problems.extend(insights["problems"])
            all_opportunities.extend(insights["opportunities"])
            all_questions.extend(insights["questions"])

            # Update conversation metadata
            self.memory_store.update_conversation_metadata(
                conv.id,
                topics=insights["topics"],
                entities=insights["entities"],
                action_items=insights["action_items"],
                problems=insights["problems"],
                opportunities=insights["opportunities"],
            )

        # Aggregate and rank
        aggregated = {
            "top_topics": self._rank_items(all_topics, top_n=10),
            "top_entities": self._rank_items(all_entities, top_n=10),
            "recent_action_items": all_action_items[:20],
            "recent_problems": all_problems[:15],
            "recent_opportunities": all_opportunities[:15],
            "unanswered_questions": all_questions[:10],
            "total_conversations": len(conversations),
            "analysis_timestamp": datetime.now().isoformat(),
        }

        return aggregated

    def _extract_topics(self, conversation: ConversationEntry) -> List[str]:
        """Extract main topics from conversation."""
        topics = set()

        # Common technical topics and domains
        topic_patterns = {
            "machine learning": r"\b(machine learning|ml|neural network|deep learning|model training)\b",
            "web development": r"\b(web dev|frontend|backend|react|vue|angular|django|flask)\b",
            "database": r"\b(database|sql|nosql|mongodb|postgresql|mysql|redis)\b",
            "api": r"\b(api|rest|graphql|endpoint|microservice)\b",
            "deployment": r"\b(deploy|deployment|docker|kubernetes|ci/cd|pipeline)\b",
            "testing": r"\b(test|testing|unit test|integration test|pytest|jest)\b",
            "performance": r"\b(performance|optimization|speed|latency|throughput)\b",
            "security": r"\b(security|authentication|authorization|encryption|vulnerability)\b",
            "data science": r"\b(data science|analytics|visualization|pandas|numpy)\b",
            "cloud": r"\b(cloud|aws|azure|gcp|serverless)\b",
            "git": r"\b(git|github|gitlab|version control|branch|merge|commit)\b",
            "python": r"\b(python|pip|virtualenv|conda)\b",
            "javascript": r"\b(javascript|js|typescript|node|npm)\b",
        }

        full_text = " ".join(m["content"].lower() for m in conversation.messages)

        for topic, pattern in topic_patterns.items():
            if re.search(pattern, full_text, re.IGNORECASE):
                topics.add(topic)

        # Extract capitalized phrases (likely proper nouns/projects)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
                                 " ".join(m["content"] for m in conversation.messages))
        topics.update(c for c in capitalized if len(c) > 3 and len(c.split()) <= 3)

        return list(topics)[:10]

    def _extract_entities(self, conversation: ConversationEntry) -> List[str]:
        """Extract entities (people, projects, tools) from conversation."""
        entities = set()

        full_text = " ".join(m["content"] for m in conversation.messages)

        # Extract capitalized words/phrases (likely proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-zA-Z0-9_]+(?:\s+[A-Z][a-zA-Z0-9_]+)*\b', full_text)
        entities.update(c for c in capitalized if len(c) > 2)

        # Extract common tools and technologies
        tools_pattern = r'\b(GitHub|GitLab|Docker|Kubernetes|AWS|Azure|GCP|MongoDB|PostgreSQL|Redis|React|Vue|Angular|Django|Flask|FastAPI|TensorFlow|PyTorch|Pandas|NumPy)\b'
        tools = re.findall(tools_pattern, full_text, re.IGNORECASE)
        entities.update(tools)

        return list(entities)[:15]

    def _extract_action_items(self, conversation: ConversationEntry) -> List[str]:
        """Extract action items and tasks from conversation."""
        action_items = []

        for message in conversation.messages:
            if message["role"] == "user":
                content = message["content"]

                # Check for action keywords
                for keyword in self.action_keywords:
                    if keyword in content.lower():
                        # Extract sentence containing the keyword
                        sentences = re.split(r'[.!?]\s+', content)
                        for sentence in sentences:
                            if keyword in sentence.lower() and len(sentence) > 10:
                                action_items.append(sentence.strip())

        return action_items[:10]

    def _extract_problems(self, conversation: ConversationEntry) -> List[str]:
        """Extract problems and issues from conversation."""
        problems = []

        for message in conversation.messages:
            content = message["content"]

            # Check for problem keywords
            for keyword in self.problem_keywords:
                if keyword in content.lower():
                    sentences = re.split(r'[.!?]\s+', content)
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence) > 15:
                            problems.append(sentence.strip())

        return problems[:10]

    def _extract_opportunities(self, conversation: ConversationEntry) -> List[str]:
        """Extract opportunities and ideas from conversation."""
        opportunities = []

        for message in conversation.messages:
            content = message["content"]

            # Check for opportunity keywords
            for keyword in self.opportunity_keywords:
                if keyword in content.lower():
                    sentences = re.split(r'[.!?]\s+', content)
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence) > 15:
                            opportunities.append(sentence.strip())

        return opportunities[:10]

    def _extract_questions(self, conversation: ConversationEntry) -> List[str]:
        """Extract questions from conversation."""
        questions = []

        for message in conversation.messages:
            if message["role"] == "user":
                content = message["content"]

                # Extract sentences ending with '?'
                question_sentences = re.findall(r'([^.!?]*\?)', content)
                questions.extend(q.strip() for q in question_sentences if len(q.strip()) > 10)

                # Extract sentences starting with question words
                for keyword in self.question_keywords:
                    if keyword in content.lower():
                        sentences = re.split(r'[.!?]\s+', content)
                        for sentence in sentences:
                            if sentence.lower().startswith(keyword) and len(sentence) > 10:
                                questions.append(sentence.strip() + "?")

        return questions[:10]

    def _analyze_sentiment(self, conversation: ConversationEntry) -> str:
        """Analyze overall sentiment of conversation (simplified)."""
        positive_words = ["good", "great", "excellent", "perfect", "works", "solved", "success", "thanks"]
        negative_words = ["bad", "error", "fail", "problem", "issue", "broken", "stuck", "difficult"]

        full_text = " ".join(m["content"].lower() for m in conversation.messages)

        positive_count = sum(1 for word in positive_words if word in full_text)
        negative_count = sum(1 for word in negative_words if word in full_text)

        if positive_count > negative_count * 1.5:
            return "positive"
        elif negative_count > positive_count * 1.5:
            return "negative"
        else:
            return "neutral"

    def _rank_items(self, items: List[str], top_n: int = 10) -> List[Dict[str, Any]]:
        """Rank items by frequency."""
        from collections import Counter

        counter = Counter(items)
        ranked = [
            {"item": item, "count": count}
            for item, count in counter.most_common(top_n)
        ]

        return ranked

    def get_trending_topics(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get trending topics based on recent conversations."""
        insights = self.analyze_recent_conversations(days=days)
        return insights["top_topics"]

    def get_active_projects(self, days: int = 14) -> List[str]:
        """Identify active projects based on conversation frequency."""
        insights = self.analyze_recent_conversations(days=days)
        entities = insights["top_entities"]

        # Filter for project-like entities (capitalized, multiple mentions)
        projects = [
            e["item"] for e in entities
            if e["count"] >= 2 and len(e["item"].split()) <= 3
        ]

        return projects[:10]
