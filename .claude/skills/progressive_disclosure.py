#!/usr/bin/env python3
"""
Progressive Disclosure Implementation

This module provides a reference implementation of the progressive disclosure
system for managing skill content in Claude Code.

Usage:
    from progressive_disclosure import SkillManager

    manager = SkillManager()
    loaded_skills = manager.process_query("How do I optimize UMAP for large datasets?")
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum


class SkillLevel(Enum):
    """Skill disclosure levels."""
    METADATA = "metadata"
    INSTRUCTIONS = "instructions"
    RESOURCES = "resources"


@dataclass
class SkillMetadata:
    """Parsed skill metadata."""
    name: str
    skill_type: str
    version: str
    purpose: str
    triggers: List[str]
    dependencies: List[str]
    context_cost: str
    complexity: float
    summary: str
    path: str


@dataclass
class RelevanceScore:
    """Skill relevance scoring."""
    skill_name: str
    keyword_score: float
    topic_score: float
    task_type_score: float
    complexity_score: float
    total_score: float
    recommended_level: SkillLevel


class SkillLoader:
    """Loads specific levels of skills from markdown files."""

    @staticmethod
    def load_skill_level(skill_path: str, level: SkillLevel) -> str:
        """
        Load only the specified level of a skill.

        Args:
            skill_path: Path to skill markdown file
            level: One of SkillLevel enum values

        Returns:
            Extracted content for the specified level
        """
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Define level boundaries
        level_markers = {
            SkillLevel.METADATA: ("<!-- LEVEL: METADATA -->", "<!-- LEVEL: INSTRUCTIONS -->"),
            SkillLevel.INSTRUCTIONS: ("<!-- LEVEL: INSTRUCTIONS -->", "<!-- LEVEL: RESOURCES -->"),
            SkillLevel.RESOURCES: ("<!-- LEVEL: RESOURCES -->", None)
        }

        start_marker, end_marker = level_markers[level]

        # Extract section
        start_idx = content.find(start_marker)
        if start_idx == -1:
            return ""

        if end_marker:
            end_idx = content.find(end_marker, start_idx)
            if end_idx == -1:
                return content[start_idx:]
            return content[start_idx:end_idx].strip()
        else:
            return content[start_idx:].strip()

    @staticmethod
    def parse_metadata(skill_path: str) -> SkillMetadata:
        """
        Parse metadata from a skill file.

        Args:
            skill_path: Path to skill markdown file

        Returns:
            Parsed skill metadata
        """
        metadata_content = SkillLoader.load_skill_level(skill_path, SkillLevel.METADATA)

        # Extract fields using regex
        def extract_field(field_name: str, default: str = "") -> str:
            pattern = rf'\*\*{field_name}:\*\*\s*(.+?)(?:\n|$)'
            match = re.search(pattern, metadata_content)
            return match.group(1).strip() if match else default

        def extract_triggers(content: str) -> List[str]:
            triggers_str = extract_field("Triggers")
            if triggers_str:
                return [t.strip() for t in triggers_str.split(',')]
            return []

        def extract_dependencies(content: str) -> List[str]:
            deps_str = extract_field("Dependencies")
            if deps_str and deps_str.lower() != "none":
                return [d.strip() for d in deps_str.split(',')]
            return []

        def extract_summary(content: str) -> str:
            pattern = r'\*\*Quick Summary:\*\*\s*(.+?)(?:\n---|\Z)'
            match = re.search(pattern, content, re.DOTALL)
            return match.group(1).strip() if match else ""

        def extract_complexity(content: str) -> float:
            complexity_str = extract_field("Complexity")
            try:
                return float(complexity_str)
            except (ValueError, TypeError):
                return 0.5  # Default to medium complexity

        return SkillMetadata(
            name=extract_field("Skill Name"),
            skill_type=extract_field("Type"),
            version=extract_field("Version"),
            purpose=extract_field("Purpose"),
            triggers=extract_triggers(metadata_content),
            dependencies=extract_dependencies(metadata_content),
            context_cost=extract_field("Context Cost"),
            complexity=extract_complexity(metadata_content),
            summary=extract_summary(metadata_content),
            path=skill_path
        )


class RelevanceScorer:
    """Calculates relevance scores for skills."""

    def __init__(self, config: Dict):
        """
        Initialize relevance scorer with configuration.

        Args:
            config: Configuration dictionary with weights
        """
        self.keyword_weight = config.get('keyword_weight', 0.3)
        self.topic_weight = config.get('topic_similarity_weight', 0.3)
        self.task_type_weight = config.get('task_type_weight', 0.2)
        self.complexity_weight = config.get('complexity_weight', 0.2)

    def calculate_relevance(
        self,
        query: str,
        skill_metadata: SkillMetadata,
        context: Optional[Dict] = None
    ) -> RelevanceScore:
        """
        Calculate how relevant a skill is to the current task.

        Args:
            query: User's query/request
            skill_metadata: Skill metadata
            context: Optional task context

        Returns:
            Relevance score with breakdown
        """
        # 1. Keyword matching
        keyword_score = self._calculate_keyword_score(query, skill_metadata)

        # 2. Topic similarity (simplified - using keyword overlap as proxy)
        topic_score = self._calculate_topic_score(query, skill_metadata)

        # 3. Task type matching
        task_type_score = self._calculate_task_type_score(query, skill_metadata)

        # 4. Complexity alignment
        complexity_score = self._calculate_complexity_score(query, skill_metadata)

        # Weighted combination
        total_score = (
            keyword_score * self.keyword_weight +
            topic_score * self.topic_weight +
            task_type_score * self.task_type_weight +
            complexity_score * self.complexity_weight
        )

        # Determine recommended level
        recommended_level = self._determine_level(total_score)

        return RelevanceScore(
            skill_name=skill_metadata.name,
            keyword_score=keyword_score,
            topic_score=topic_score,
            task_type_score=task_type_score,
            complexity_score=complexity_score,
            total_score=total_score,
            recommended_level=recommended_level
        )

    def _calculate_keyword_score(self, query: str, metadata: SkillMetadata) -> float:
        """Calculate keyword match score."""
        query_tokens = set(self._tokenize(query.lower()))
        skill_keywords = set(kw.lower() for kw in metadata.triggers)

        if not skill_keywords:
            return 0.0

        overlap = len(query_tokens & skill_keywords)
        return min(1.0, overlap / max(1, len(skill_keywords) * 0.3))

    def _calculate_topic_score(self, query: str, metadata: SkillMetadata) -> float:
        """Calculate topic similarity score (simplified version)."""
        query_tokens = set(self._tokenize(query.lower()))
        purpose_tokens = set(self._tokenize(metadata.purpose.lower()))
        summary_tokens = set(self._tokenize(metadata.summary.lower()))

        all_skill_tokens = purpose_tokens | summary_tokens

        if not all_skill_tokens:
            return 0.0

        overlap = len(query_tokens & all_skill_tokens)
        return min(1.0, overlap / max(1, len(all_skill_tokens) * 0.2))

    def _calculate_task_type_score(self, query: str, metadata: SkillMetadata) -> float:
        """Calculate task type match score."""
        task_type = self._identify_task_type(query)
        skill_type = metadata.skill_type.lower()

        # Direct match
        if task_type == skill_type:
            return 1.0

        # Partial matches
        related_types = {
            'optimize': ['optimization', 'performance'],
            'debug': ['debugging', 'fix', 'error'],
            'implement': ['implementation', 'create', 'build'],
            'analyze': ['analysis', 'understanding'],
        }

        if task_type in related_types:
            if skill_type in related_types[task_type]:
                return 0.8

        return 0.0

    def _calculate_complexity_score(self, query: str, metadata: SkillMetadata) -> float:
        """Calculate complexity alignment score."""
        query_complexity = self._estimate_complexity(query)
        skill_complexity = metadata.complexity

        # Prefer skills that match complexity level
        complexity_diff = abs(query_complexity - skill_complexity)
        return max(0.0, 1.0 - complexity_diff)

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        return [word.strip(".,!?;:()[]{}") for word in text.split() if len(word) > 2]

    def _identify_task_type(self, query: str) -> str:
        """Identify task type from query."""
        query_lower = query.lower()

        task_patterns = {
            "optimize": ["optimize", "improve", "faster", "performance", "speed"],
            "debug": ["debug", "fix", "error", "bug", "issue", "problem"],
            "implement": ["implement", "create", "add", "build", "write"],
            "analyze": ["analyze", "understand", "explain", "how does", "what is"],
            "refactor": ["refactor", "clean", "reorganize"],
            "test": ["test", "verify", "validate"],
        }

        for task_type, keywords in task_patterns.items():
            if any(kw in query_lower for kw in keywords):
                return task_type

        return "general"

    def _estimate_complexity(self, query: str) -> float:
        """Estimate task complexity from query."""
        complexity_signals = {
            "simple": ["simple", "basic", "quick", "just", "only"],
            "complex": ["complex", "advanced", "comprehensive", "full", "production"]
        }

        query_lower = query.lower()

        if any(kw in query_lower for kw in complexity_signals["simple"]):
            return 0.2
        elif any(kw in query_lower for kw in complexity_signals["complex"]):
            return 0.9

        # Estimate by query length
        word_count = len(query.split())
        if word_count < 10:
            return 0.3
        elif word_count < 30:
            return 0.5
        else:
            return 0.7

    def _determine_level(self, relevance_score: float) -> SkillLevel:
        """Determine which level to load based on relevance score."""
        if relevance_score >= 0.8:
            return SkillLevel.RESOURCES
        elif relevance_score >= 0.5:
            return SkillLevel.INSTRUCTIONS
        else:
            return SkillLevel.METADATA


class ContextWindowManager:
    """Manages context window budget for skill loading."""

    def __init__(self, config: Dict):
        """
        Initialize context window manager.

        Args:
            config: Configuration with budget settings
        """
        self.max_tokens = config.get('total_tokens', 200000)
        self.reserved_tokens = config.get('reserved_tokens', 60000)
        self.available_tokens = self.max_tokens - self.reserved_tokens
        self.current_usage = {}

        # Token cost estimates per level
        self.level_costs = {
            SkillLevel.METADATA: 500,
            SkillLevel.INSTRUCTIONS: 3000,
            SkillLevel.RESOURCES: 15000
        }

    def can_load(self, skill_name: str, level: SkillLevel) -> bool:
        """Check if we have budget to load this skill at this level."""
        estimated_cost = self.level_costs[level]
        current_total = sum(self.current_usage.values())

        return (current_total + estimated_cost) <= self.available_tokens

    def record_load(self, skill_name: str, level: SkillLevel):
        """Record that a skill was loaded."""
        self.current_usage[skill_name] = self.level_costs[level]

    def get_usage_stats(self) -> Dict:
        """Get current usage statistics."""
        total_used = sum(self.current_usage.values())
        return {
            'total_used': total_used,
            'available': self.available_tokens - total_used,
            'percentage_used': (total_used / self.available_tokens) * 100,
            'skills_loaded': len(self.current_usage)
        }


class SkillManager:
    """Main skill management system with progressive disclosure."""

    def __init__(self, skills_dir: str = ".claude/skills", config_path: Optional[str] = None):
        """
        Initialize skill manager.

        Args:
            skills_dir: Path to skills directory
            config_path: Optional path to config file
        """
        self.skills_dir = Path(skills_dir)
        self.config = self._load_config(config_path)
        self.loader = SkillLoader()
        self.scorer = RelevanceScorer(self.config.get('relevance_scoring', {}))
        self.context_manager = ContextWindowManager(
            self.config.get('progressive_disclosure', {}).get('context_budget', {})
        )
        self.skills_metadata = self._discover_skills()

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file."""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)

        # Try default location
        default_config = self.skills_dir / "config.json"
        if default_config.exists():
            with open(default_config, 'r') as f:
                return json.load(f)

        # Return empty config with defaults
        return {}

    def _discover_skills(self) -> Dict[str, SkillMetadata]:
        """Discover all available skills."""
        skills = {}

        if not self.skills_dir.exists():
            return skills

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_file = skill_dir / "skill.md"
            if not skill_file.exists():
                continue

            try:
                metadata = self.loader.parse_metadata(str(skill_file))
                skills[metadata.name] = metadata
            except Exception as e:
                print(f"Warning: Failed to parse skill {skill_dir.name}: {e}")

        return skills

    def process_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, str]:
        """
        Process a user query and load relevant skills.

        Args:
            query: User's query
            context: Optional task context

        Returns:
            Dictionary mapping skill names to loaded content
        """
        # Score all skills
        scored_skills = []
        for metadata in self.skills_metadata.values():
            score = self.scorer.calculate_relevance(query, metadata, context)
            if score.total_score >= 0.2:  # Skip irrelevant skills
                scored_skills.append(score)

        # Sort by relevance
        scored_skills.sort(key=lambda s: s.total_score, reverse=True)

        # Load skills within budget
        loaded_skills = {}
        for score in scored_skills:
            metadata = self.skills_metadata[score.skill_name]
            level = score.recommended_level

            # Check budget
            if self.context_manager.can_load(score.skill_name, level):
                try:
                    content = self.loader.load_skill_level(metadata.path, level)
                    loaded_skills[score.skill_name] = content
                    self.context_manager.record_load(score.skill_name, level)
                except Exception as e:
                    print(f"Warning: Failed to load {score.skill_name}: {e}")

        return loaded_skills

    def get_stats(self) -> Dict:
        """Get usage statistics."""
        return {
            'total_skills': len(self.skills_metadata),
            'context_usage': self.context_manager.get_usage_stats()
        }


def main():
    """Example usage of the progressive disclosure system."""
    # Initialize manager
    manager = SkillManager()

    # Example queries
    queries = [
        "How do I optimize UMAP for large datasets?",
        "What's the difference between metadata and instructions?",
        "Help me implement a new feature",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        print("=" * 80)

        loaded_skills = manager.process_query(query)

        print(f"Loaded {len(loaded_skills)} skills:")
        for skill_name in loaded_skills.keys():
            print(f"  - {skill_name}")

        stats = manager.get_stats()
        print(f"\nContext usage: {stats['context_usage']['percentage_used']:.1f}%")
        print(f"Tokens used: {stats['context_usage']['total_used']:,}")


if __name__ == "__main__":
    main()
