"""
Text Summarization Skill

Provides various summarization strategies:
- Extractive: Select important sentences
- Abstractive: Generate new summary text (mock)
- Multi-document: Summarize across multiple documents
"""

from typing import Any, Dict, List, Optional
from enum import Enum
import logging
import re

from ..base_skill import BaseSkill, SkillContext, SkillMetadata


logger = logging.getLogger(__name__)


class SummarizationStrategy(Enum):
    """Summarization approach"""
    EXTRACTIVE = "extractive"      # Extract key sentences
    ABSTRACTIVE = "abstractive"    # Generate new text
    BULLET_POINTS = "bullet_points"  # Key points list
    PROGRESSIVE = "progressive"    # Layered detail levels


class SummarizationSkill(BaseSkill):
    """
    Text summarization with multiple strategies.

    Can summarize:
    - Single documents
    - Retrieved context from RAG pipeline
    - Multi-document collections

    Configuration:
        strategy: Summarization strategy (extractive/abstractive/bullet_points)
        max_length: Maximum summary length in words (default: 200)
        min_length: Minimum summary length in words (default: 50)
        num_sentences: For extractive, number of sentences to extract (default: 3)
        compression_ratio: Target compression (0-1, default: 0.3)
    """

    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="summarization",
            description="Text summarization with multiple strategies",
            version="1.0.0",
            author="Skill Framework",
            input_schema={
                "text": "str - Text to summarize",
                "context": "Optional[str] - Context from RAG pipeline"
            },
            output_schema={
                "summary": "str - Generated summary",
                "key_points": "List[str] - Key points extracted",
                "metadata": "Dict - Summarization metadata"
            },
            dependencies=["rag_pipeline"],  # Can use RAG output
            tags=["summarization", "nlp", "text-processing"]
        )

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        # Configuration
        strategy_str = self.config.get("strategy", "extractive")
        self.strategy = SummarizationStrategy(strategy_str)

        self.max_length = self.config.get("max_length", 200)
        self.min_length = self.config.get("min_length", 50)
        self.num_sentences = self.config.get("num_sentences", 3)
        self.compression_ratio = self.config.get("compression_ratio", 0.3)

    def execute(self, context: SkillContext, **kwargs) -> Dict[str, Any]:
        """
        Execute summarization.

        Args:
            context: Skill context
            **kwargs:
                text: Text to summarize (optional if using RAG context)

        Returns:
            Dict with summary, key_points, and metadata
        """
        # Get text to summarize
        text = kwargs.get("text")

        # If no text, try to get from RAG pipeline context
        if not text:
            rag_result = context.get_result("rag_pipeline")
            if rag_result and "context" in rag_result and rag_result["context"].strip():
                text = rag_result["context"]
                logger.info("Using context from RAG pipeline")

        # Still no text? Try shared state
        if not text:
            text = context.shared_state.get("text")

        if not text or not text.strip():
            raise ValueError("No text provided for summarization. RAG retrieved no documents.")

        # Perform summarization based on strategy
        if self.strategy == SummarizationStrategy.EXTRACTIVE:
            summary, key_points = self._extractive_summarization(text)

        elif self.strategy == SummarizationStrategy.ABSTRACTIVE:
            summary, key_points = self._abstractive_summarization(text)

        elif self.strategy == SummarizationStrategy.BULLET_POINTS:
            summary, key_points = self._bullet_point_summarization(text)

        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

        # Calculate statistics
        original_words = len(text.split())
        summary_words = len(summary.split())
        actual_compression = summary_words / original_words if original_words > 0 else 0

        result = {
            "summary": summary,
            "key_points": key_points,
            "metadata": {
                "strategy": self.strategy.value,
                "original_length": original_words,
                "summary_length": summary_words,
                "compression_ratio": actual_compression,
                "num_key_points": len(key_points)
            }
        }

        logger.info(
            f"Summarization complete: {original_words} -> {summary_words} words "
            f"({actual_compression:.1%} compression)"
        )

        return result

    def _extractive_summarization(self, text: str) -> tuple[str, List[str]]:
        """
        Extract most important sentences.

        Simple implementation using:
        - Sentence position (first sentences often important)
        - Word frequency (TF-IDF-like scoring)
        - Length (prefer medium-length sentences)
        """
        sentences = self._split_sentences(text)

        if len(sentences) <= self.num_sentences:
            summary = text
            key_points = sentences
            return summary, key_points

        # Score sentences
        scored_sentences = []
        word_freq = self._compute_word_frequencies(text)

        for idx, sentence in enumerate(sentences):
            score = 0.0

            # Position score (earlier sentences weighted higher)
            position_score = 1.0 / (idx + 1)
            score += position_score * 2.0

            # Content score (sum of word frequencies)
            words = re.findall(r'\w+', sentence.lower())
            content_score = sum(word_freq.get(word, 0) for word in words)
            score += content_score

            # Length score (prefer medium length)
            length = len(words)
            if 10 <= length <= 30:
                score += 1.0

            scored_sentences.append((score, idx, sentence))

        # Sort by score and take top N
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        top_sentences = scored_sentences[:self.num_sentences]

        # Re-sort by original position
        top_sentences.sort(key=lambda x: x[1])

        summary = ' '.join([sent for _, _, sent in top_sentences])
        key_points = [sent.strip() for _, _, sent in top_sentences]

        return summary, key_points

    def _abstractive_summarization(self, text: str) -> tuple[str, List[str]]:
        """
        Generate new summary text (MOCK implementation).

        In production, use:
        - Transformer models (BART, T5, Pegasus)
        - GPT-based summarization
        - Fine-tuned models
        """
        # For now, fall back to extractive and add prefix
        summary, key_points = self._extractive_summarization(text)

        # Add abstractive-style prefix
        summary = f"The text discusses: {summary}"

        logger.warning("Using mock abstractive summarization (extractive + prefix)")

        return summary, key_points

    def _bullet_point_summarization(self, text: str) -> tuple[str, List[str]]:
        """Create bullet-point summary"""
        # Extract key sentences
        _, key_points = self._extractive_summarization(text)

        # Format as bullet points
        bullet_summary = "Key Points:\n" + "\n".join([
            f"• {point}" for point in key_points
        ])

        return bullet_summary, key_points

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences (simple implementation)"""
        # Simple sentence splitting (naive)
        # In production, use NLTK, spaCy, or regex with better rules
        sentences = re.split(r'[.!?]+', text)

        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _compute_word_frequencies(self, text: str) -> Dict[str, float]:
        """Compute word frequency scores (simple TF)"""
        words = re.findall(r'\w+', text.lower())

        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }

        words = [w for w in words if w not in stop_words and len(w) > 2]

        # Count frequencies
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1

        # Normalize
        max_freq = max(freq.values()) if freq else 1
        for word in freq:
            freq[word] /= max_freq

        return freq

    def validate_inputs(self, context: SkillContext, **kwargs) -> bool:
        """Validate that we have text to summarize"""
        text = kwargs.get("text")

        if not text:
            # Check RAG context
            rag_result = context.get_result("rag_pipeline")
            if rag_result and "context" in rag_result:
                return True

            # Check shared state
            text = context.shared_state.get("text")

        return text is not None
