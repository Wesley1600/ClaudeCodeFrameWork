"""
RAG Reranking Skill for Retrieval-Augmented Generation Pipelines

A flexible reranking framework that supports multiple scoring algorithms including
semantic similarity, recency-based scoring, BM25-like lexical matching, and hybrid
approaches. Designed to plug into vector/hybrid search pipelines and enhance
retrieval quality through intelligent reranking, filtering, and aggregation.

Key Features:
- Multiple pluggable reranking algorithms (semantic, recency, lexical, hybrid)
- Filtering by score threshold, top-k, or custom predicates
- Result aggregation with multiple fusion strategies (RRF, weighted, voting)
- Batch processing support for efficient large-scale reranking
- Extensible base class for custom rerankers
- Comprehensive metadata handling (timestamps, sources, relevance scores)

Example Usage:
    ```python
    from rag_reranker import (
        SemanticReranker,
        RecencyReranker,
        HybridReranker,
        ResultAggregator,
    )

    # Semantic reranking
    reranker = SemanticReranker(query_embedding, metric="cosine")
    results = reranker.rerank(passages, k=10, threshold=0.5)

    # Hybrid approach
    hybrid = HybridReranker(
        query_embedding=query_emb,
        query_text="what is machine learning",
        weights={"semantic": 0.6, "recency": 0.3, "lexical": 0.1}
    )
    results = hybrid.rerank(passages, k=20)
    ```
"""

import math
import re
from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import torch
import torch.nn.functional as F


# =========================
# Data Structures
# =========================
@dataclass
class Passage:
    """
    Represents a single passage/document in the retrieval results.

    Attributes:
        text: The passage content
        embedding: Optional dense vector representation
        metadata: Additional metadata (source, timestamp, etc.)
        score: Initial retrieval score (e.g., from vector search)
        id: Unique identifier for the passage
    """
    text: str
    embedding: Optional[torch.Tensor] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    id: Optional[str] = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(hash(self.text))


@dataclass
class RankedResult:
    """
    Represents a reranked passage with scoring details.

    Attributes:
        passage: The original passage
        rerank_score: Score assigned by the reranker
        original_score: Original retrieval score
        rank: Position in the reranked list (1-indexed)
        explanation: Optional explanation of the score
    """
    passage: Passage
    rerank_score: float
    original_score: float
    rank: int = 0
    explanation: Optional[str] = None


# =========================
# Abstract Base Reranker
# =========================
class BaseReranker(ABC):
    """
    Abstract base class for all rerankers.

    Provides common functionality for scoring, filtering, and ranking passages.
    Subclasses must implement the `score_passage` method.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        normalize_scores: bool = True,
    ):
        """
        Initialize the base reranker.

        Args:
            name: Optional name for this reranker instance
            normalize_scores: Whether to normalize scores to [0, 1] range
        """
        self.name = name or self.__class__.__name__
        self.normalize_scores = normalize_scores

    @abstractmethod
    def score_passage(self, passage: Passage) -> float:
        """
        Score a single passage. Must be implemented by subclasses.

        Args:
            passage: The passage to score

        Returns:
            Relevance score (higher = more relevant)
        """
        pass

    def score_batch(self, passages: List[Passage]) -> List[float]:
        """
        Score a batch of passages. Override for efficient batch processing.

        Args:
            passages: List of passages to score

        Returns:
            List of scores corresponding to input passages
        """
        return [self.score_passage(p) for p in passages]

    def rerank(
        self,
        passages: List[Passage],
        k: Optional[int] = None,
        threshold: Optional[float] = None,
        filter_fn: Optional[Callable[[Passage], bool]] = None,
    ) -> List[RankedResult]:
        """
        Rerank passages based on the scoring function.

        Args:
            passages: List of passages to rerank
            k: Optional maximum number of results to return
            threshold: Optional minimum score threshold
            filter_fn: Optional custom filter function

        Returns:
            List of RankedResult objects, sorted by rerank_score (descending)
        """
        if not passages:
            return []

        # Apply custom filter if provided
        if filter_fn:
            passages = [p for p in passages if filter_fn(p)]

        if not passages:
            return []

        # Score all passages
        scores = self.score_batch(passages)

        # Normalize scores if requested
        if self.normalize_scores and scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                scores = [(s - min_score) / (max_score - min_score) for s in scores]

        # Create ranked results
        results = [
            RankedResult(
                passage=p,
                rerank_score=score,
                original_score=p.score,
            )
            for p, score in zip(passages, scores)
        ]

        # Apply threshold filter
        if threshold is not None:
            results = [r for r in results if r.rerank_score >= threshold]

        # Sort by rerank_score (descending)
        results.sort(key=lambda x: x.rerank_score, reverse=True)

        # Apply top-k cutoff
        if k is not None:
            results = results[:k]

        # Assign ranks
        for i, result in enumerate(results, 1):
            result.rank = i

        return results


# =========================
# Semantic Similarity Reranker
# =========================
class SemanticReranker(BaseReranker):
    """
    Rerank passages based on semantic similarity to a query embedding.

    Supports multiple similarity metrics:
    - cosine: Cosine similarity (default)
    - dot: Dot product similarity
    - euclidean: Negative L2 distance (inverted to make higher = better)
    """

    def __init__(
        self,
        query_embedding: torch.Tensor,
        metric: str = "cosine",
        name: Optional[str] = None,
        normalize_scores: bool = True,
    ):
        """
        Initialize semantic reranker.

        Args:
            query_embedding: Query embedding vector (1D tensor)
            metric: Similarity metric ("cosine", "dot", or "euclidean")
            name: Optional name for this reranker
            normalize_scores: Whether to normalize scores
        """
        super().__init__(name=name, normalize_scores=normalize_scores)
        self.query_embedding = query_embedding.squeeze()
        self.metric = metric.lower()

        if self.metric not in {"cosine", "dot", "euclidean"}:
            raise ValueError(f"Unknown metric: {metric}. Use 'cosine', 'dot', or 'euclidean'.")

    def score_passage(self, passage: Passage) -> float:
        """Score a passage based on embedding similarity."""
        if passage.embedding is None:
            return 0.0

        emb = passage.embedding.squeeze()

        if self.metric == "cosine":
            # Cosine similarity
            sim = F.cosine_similarity(
                self.query_embedding.unsqueeze(0),
                emb.unsqueeze(0),
                dim=-1
            ).item()
            return float(sim)

        elif self.metric == "dot":
            # Dot product
            sim = torch.dot(self.query_embedding, emb).item()
            return float(sim)

        elif self.metric == "euclidean":
            # Negative L2 distance (inverted so higher = better)
            dist = torch.norm(self.query_embedding - emb).item()
            return float(-dist)

        return 0.0

    def score_batch(self, passages: List[Passage]) -> List[float]:
        """Efficient batch scoring using vectorized operations."""
        # Filter passages with embeddings
        valid_indices = [i for i, p in enumerate(passages) if p.embedding is not None]

        if not valid_indices:
            return [0.0] * len(passages)

        # Stack embeddings
        embeddings = torch.stack([passages[i].embedding.squeeze() for i in valid_indices])
        query = self.query_embedding.unsqueeze(0)

        # Compute similarities
        if self.metric == "cosine":
            sims = F.cosine_similarity(query, embeddings, dim=-1)
        elif self.metric == "dot":
            sims = torch.matmul(embeddings, query.T).squeeze()
        elif self.metric == "euclidean":
            sims = -torch.norm(embeddings - query, dim=-1)
        else:
            sims = torch.zeros(len(valid_indices))

        # Map back to original indices
        scores = [0.0] * len(passages)
        for i, idx in enumerate(valid_indices):
            scores[idx] = float(sims[i].item())

        return scores


# =========================
# Recency-Based Reranker
# =========================
class RecencyReranker(BaseReranker):
    """
    Rerank passages based on recency (timestamp).

    Supports multiple scoring strategies:
    - exponential: Exponential decay from reference time
    - linear: Linear decay with cutoff
    - step: Step function with hard cutoffs
    """

    def __init__(
        self,
        timestamp_key: str = "timestamp",
        reference_time: Optional[datetime] = None,
        decay_rate: float = 0.1,
        strategy: str = "exponential",
        name: Optional[str] = None,
        normalize_scores: bool = True,
    ):
        """
        Initialize recency reranker.

        Args:
            timestamp_key: Key in passage.metadata for timestamp
            reference_time: Reference time for recency calculation (default: now)
            decay_rate: Decay rate parameter (interpretation depends on strategy)
            strategy: Scoring strategy ("exponential", "linear", or "step")
            name: Optional name for this reranker
            normalize_scores: Whether to normalize scores
        """
        super().__init__(name=name, normalize_scores=normalize_scores)
        self.timestamp_key = timestamp_key
        self.reference_time = reference_time or datetime.now()
        self.decay_rate = decay_rate
        self.strategy = strategy.lower()

        if self.strategy not in {"exponential", "linear", "step"}:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _get_timestamp(self, passage: Passage) -> Optional[datetime]:
        """Extract timestamp from passage metadata."""
        ts = passage.metadata.get(self.timestamp_key)

        if ts is None:
            return None

        if isinstance(ts, datetime):
            return ts

        if isinstance(ts, (int, float)):
            # Assume Unix timestamp
            return datetime.fromtimestamp(ts)

        if isinstance(ts, str):
            # Try to parse ISO format
            try:
                return datetime.fromisoformat(ts)
            except ValueError:
                return None

        return None

    def score_passage(self, passage: Passage) -> float:
        """Score a passage based on recency."""
        timestamp = self._get_timestamp(passage)

        if timestamp is None:
            return 0.0

        # Time difference in days
        delta = (self.reference_time - timestamp).total_seconds() / 86400.0

        if delta < 0:
            # Future timestamp - treat as very recent
            delta = 0

        if self.strategy == "exponential":
            # Exponential decay: score = exp(-decay_rate * days)
            score = math.exp(-self.decay_rate * delta)

        elif self.strategy == "linear":
            # Linear decay: score = max(0, 1 - decay_rate * days)
            score = max(0.0, 1.0 - self.decay_rate * delta)

        elif self.strategy == "step":
            # Step function: 1 if within threshold, 0 otherwise
            threshold_days = 1.0 / max(self.decay_rate, 1e-6)
            score = 1.0 if delta <= threshold_days else 0.0

        else:
            score = 0.0

        return float(score)


# =========================
# Lexical (BM25-like) Reranker
# =========================
class LexicalReranker(BaseReranker):
    """
    Rerank passages based on lexical overlap with query.

    Implements a simplified BM25-like scoring:
    - Term frequency with saturation
    - Inverse document frequency (optional)
    - Document length normalization
    """

    def __init__(
        self,
        query_text: str,
        k1: float = 1.5,
        b: float = 0.75,
        use_idf: bool = True,
        name: Optional[str] = None,
        normalize_scores: bool = True,
    ):
        """
        Initialize lexical reranker.

        Args:
            query_text: Query text string
            k1: BM25 term frequency saturation parameter
            b: BM25 length normalization parameter
            use_idf: Whether to use IDF weighting
            name: Optional name for this reranker
            normalize_scores: Whether to normalize scores
        """
        super().__init__(name=name, normalize_scores=normalize_scores)
        self.query_text = query_text.lower()
        self.query_terms = self._tokenize(self.query_text)
        self.k1 = k1
        self.b = b
        self.use_idf = use_idf

        # Will be computed during first batch scoring
        self.idf_scores: Dict[str, float] = {}
        self.avg_doc_length: float = 0.0
        self._initialized = False

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization: lowercase and split on non-alphanumeric."""
        return [t for t in re.findall(r'\w+', text.lower()) if len(t) > 1]

    def _compute_idf(self, passages: List[Passage]):
        """Compute IDF scores from passages."""
        if self._initialized:
            return

        N = len(passages)
        if N == 0:
            return

        # Count documents containing each term
        df: Counter = Counter()
        doc_lengths = []

        for passage in passages:
            terms = set(self._tokenize(passage.text))
            for term in terms:
                df[term] += 1
            doc_lengths.append(len(self._tokenize(passage.text)))

        # Compute IDF: log((N - df(t) + 0.5) / (df(t) + 0.5) + 1)
        for term in self.query_terms:
            df_t = df.get(term, 0)
            idf = math.log((N - df_t + 0.5) / (df_t + 0.5) + 1.0)
            self.idf_scores[term] = idf

        # Average document length
        self.avg_doc_length = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 1.0
        self._initialized = True

    def score_passage(self, passage: Passage) -> float:
        """Score a passage based on lexical overlap."""
        # Tokenize document
        doc_terms = self._tokenize(passage.text)
        doc_length = len(doc_terms)

        if doc_length == 0:
            return 0.0

        # Term frequency
        tf: Counter = Counter(doc_terms)

        # BM25 score
        score = 0.0
        for term in self.query_terms:
            if term not in tf:
                continue

            # Term frequency component with saturation
            freq = tf[term]
            tf_component = (freq * (self.k1 + 1)) / (
                freq + self.k1 * (1 - self.b + self.b * doc_length / max(self.avg_doc_length, 1.0))
            )

            # IDF component
            idf = self.idf_scores.get(term, 0.0) if self.use_idf else 1.0

            score += tf_component * idf

        return float(score)

    def score_batch(self, passages: List[Passage]) -> List[float]:
        """Batch scoring with IDF initialization."""
        if self.use_idf and not self._initialized:
            self._compute_idf(passages)

        return [self.score_passage(p) for p in passages]


# =========================
# Hybrid Reranker
# =========================
class HybridReranker(BaseReranker):
    """
    Combine multiple rerankers with weighted fusion.

    Supports plugging in any combination of rerankers and combining
    their scores using weighted averaging.
    """

    def __init__(
        self,
        rerankers: Optional[List[BaseReranker]] = None,
        weights: Optional[Dict[str, float]] = None,
        query_embedding: Optional[torch.Tensor] = None,
        query_text: Optional[str] = None,
        timestamp_key: str = "timestamp",
        name: Optional[str] = None,
        normalize_scores: bool = True,
    ):
        """
        Initialize hybrid reranker.

        Args:
            rerankers: List of reranker instances (or None to auto-create)
            weights: Dict mapping reranker names to weights
            query_embedding: Query embedding for semantic reranker
            query_text: Query text for lexical reranker
            timestamp_key: Timestamp key for recency reranker
            name: Optional name for this reranker
            normalize_scores: Whether to normalize final scores
        """
        super().__init__(name=name, normalize_scores=normalize_scores)

        # Auto-create rerankers if not provided
        if rerankers is None:
            rerankers = []

            if query_embedding is not None:
                rerankers.append(SemanticReranker(
                    query_embedding,
                    name="semantic",
                    normalize_scores=True,
                ))

            if query_text is not None:
                rerankers.append(LexicalReranker(
                    query_text,
                    name="lexical",
                    normalize_scores=True,
                ))
                rerankers.append(RecencyReranker(
                    timestamp_key=timestamp_key,
                    name="recency",
                    normalize_scores=True,
                ))

        self.rerankers = rerankers

        # Default equal weights if not provided
        if weights is None:
            weights = {r.name: 1.0 / len(rerankers) for r in rerankers}

        # Normalize weights to sum to 1
        total = sum(weights.values())
        self.weights = {k: v / total for k, v in weights.items()} if total > 0 else weights

    def score_passage(self, passage: Passage) -> float:
        """Score a passage by combining scores from all rerankers."""
        combined_score = 0.0

        for reranker in self.rerankers:
            score = reranker.score_passage(passage)
            weight = self.weights.get(reranker.name, 0.0)
            combined_score += score * weight

        return float(combined_score)

    def score_batch(self, passages: List[Passage]) -> List[float]:
        """Efficient batch scoring by calling batch methods of sub-rerankers."""
        if not passages:
            return []

        # Collect scores from all rerankers
        all_scores = {}
        for reranker in self.rerankers:
            scores = reranker.score_batch(passages)
            all_scores[reranker.name] = scores

        # Combine weighted scores
        combined_scores = []
        for i in range(len(passages)):
            score = 0.0
            for reranker in self.rerankers:
                weight = self.weights.get(reranker.name, 0.0)
                score += all_scores[reranker.name][i] * weight
            combined_scores.append(score)

        return combined_scores


# =========================
# Custom Scoring Reranker
# =========================
class CustomReranker(BaseReranker):
    """
    Reranker that uses a custom scoring function.

    Useful for quick prototyping or domain-specific scoring logic.
    """

    def __init__(
        self,
        scoring_fn: Callable[[Passage], float],
        name: Optional[str] = None,
        normalize_scores: bool = True,
    ):
        """
        Initialize custom reranker.

        Args:
            scoring_fn: Function that takes a Passage and returns a score
            name: Optional name for this reranker
            normalize_scores: Whether to normalize scores
        """
        super().__init__(name=name, normalize_scores=normalize_scores)
        self.scoring_fn = scoring_fn

    def score_passage(self, passage: Passage) -> float:
        """Score using the custom function."""
        return float(self.scoring_fn(passage))


# =========================
# Result Aggregation
# =========================
class ResultAggregator:
    """
    Aggregate and fuse results from multiple rerankers.

    Supports several fusion strategies:
    - rrf: Reciprocal Rank Fusion
    - borda: Borda count voting
    - weighted: Weighted score combination
    - max: Maximum score across rerankers
    """

    @staticmethod
    def reciprocal_rank_fusion(
        results_list: List[List[RankedResult]],
        k: int = 60,
    ) -> List[RankedResult]:
        """
        Reciprocal Rank Fusion (RRF) aggregation.

        RRF score = sum(1 / (k + rank_i)) across all result lists.

        Args:
            results_list: List of ranked result lists from different rerankers
            k: RRF constant (default: 60)

        Returns:
            Fused ranked results
        """
        # Collect scores for each passage ID
        passage_scores: Dict[str, float] = defaultdict(float)
        passage_map: Dict[str, Passage] = {}

        for results in results_list:
            for result in results:
                pid = result.passage.id
                passage_map[pid] = result.passage
                # RRF score: 1 / (k + rank)
                passage_scores[pid] += 1.0 / (k + result.rank)

        # Create fused results
        fused = [
            RankedResult(
                passage=passage_map[pid],
                rerank_score=score,
                original_score=passage_map[pid].score,
            )
            for pid, score in passage_scores.items()
        ]

        # Sort by fused score
        fused.sort(key=lambda x: x.rerank_score, reverse=True)

        # Assign ranks
        for i, result in enumerate(fused, 1):
            result.rank = i

        return fused

    @staticmethod
    def borda_count(
        results_list: List[List[RankedResult]],
    ) -> List[RankedResult]:
        """
        Borda count voting aggregation.

        Each passage receives points based on its rank in each list:
        points = (N - rank + 1) where N is the list length.

        Args:
            results_list: List of ranked result lists

        Returns:
            Fused ranked results
        """
        passage_scores: Dict[str, float] = defaultdict(float)
        passage_map: Dict[str, Passage] = {}

        for results in results_list:
            N = len(results)
            for result in results:
                pid = result.passage.id
                passage_map[pid] = result.passage
                # Borda points: (N - rank + 1)
                passage_scores[pid] += (N - result.rank + 1)

        # Create fused results
        fused = [
            RankedResult(
                passage=passage_map[pid],
                rerank_score=score,
                original_score=passage_map[pid].score,
            )
            for pid, score in passage_scores.items()
        ]

        fused.sort(key=lambda x: x.rerank_score, reverse=True)

        for i, result in enumerate(fused, 1):
            result.rank = i

        return fused

    @staticmethod
    def weighted_fusion(
        results_list: List[List[RankedResult]],
        weights: Optional[List[float]] = None,
    ) -> List[RankedResult]:
        """
        Weighted score fusion.

        Combines scores from multiple rerankers using weighted averaging.

        Args:
            results_list: List of ranked result lists
            weights: Optional weights for each result list (default: equal)

        Returns:
            Fused ranked results
        """
        if weights is None:
            weights = [1.0 / len(results_list)] * len(results_list)

        # Normalize weights
        total = sum(weights)
        weights = [w / total for w in weights]

        passage_scores: Dict[str, float] = defaultdict(float)
        passage_map: Dict[str, Passage] = {}

        for results, weight in zip(results_list, weights):
            for result in results:
                pid = result.passage.id
                passage_map[pid] = result.passage
                passage_scores[pid] += result.rerank_score * weight

        fused = [
            RankedResult(
                passage=passage_map[pid],
                rerank_score=score,
                original_score=passage_map[pid].score,
            )
            for pid, score in passage_scores.items()
        ]

        fused.sort(key=lambda x: x.rerank_score, reverse=True)

        for i, result in enumerate(fused, 1):
            result.rank = i

        return fused

    @staticmethod
    def max_fusion(
        results_list: List[List[RankedResult]],
    ) -> List[RankedResult]:
        """
        Maximum score fusion (optimistic aggregation).

        Each passage receives the maximum score it achieved across all rerankers.

        Args:
            results_list: List of ranked result lists

        Returns:
            Fused ranked results
        """
        passage_scores: Dict[str, float] = defaultdict(lambda: float('-inf'))
        passage_map: Dict[str, Passage] = {}

        for results in results_list:
            for result in results:
                pid = result.passage.id
                passage_map[pid] = result.passage
                passage_scores[pid] = max(passage_scores[pid], result.rerank_score)

        fused = [
            RankedResult(
                passage=passage_map[pid],
                rerank_score=score,
                original_score=passage_map[pid].score,
            )
            for pid, score in passage_scores.items()
        ]

        fused.sort(key=lambda x: x.rerank_score, reverse=True)

        for i, result in enumerate(fused, 1):
            result.rank = i

        return fused


# =========================
# Utility Functions
# =========================
def filter_by_metadata(
    passages: List[Passage],
    filters: Dict[str, Any],
) -> List[Passage]:
    """
    Filter passages by metadata criteria.

    Args:
        passages: List of passages
        filters: Dict of metadata key-value pairs to match

    Returns:
        Filtered list of passages
    """
    def matches(passage: Passage) -> bool:
        for key, value in filters.items():
            if passage.metadata.get(key) != value:
                return False
        return True

    return [p for p in passages if matches(p)]


def deduplicate_passages(
    passages: List[Passage],
    key: str = "text",
    similarity_threshold: float = 0.95,
) -> List[Passage]:
    """
    Remove duplicate or near-duplicate passages.

    Args:
        passages: List of passages
        key: Metadata key to use for deduplication ("text" for exact matching)
        similarity_threshold: Similarity threshold for near-duplicate detection

    Returns:
        Deduplicated list of passages
    """
    if key == "text":
        # Exact text matching
        seen: Set[str] = set()
        unique = []
        for p in passages:
            if p.text not in seen:
                seen.add(p.text)
                unique.append(p)
        return unique
    else:
        # Metadata-based deduplication
        seen_values: Set[Any] = set()
        unique = []
        for p in passages:
            value = p.metadata.get(key)
            if value is not None and value not in seen_values:
                seen_values.add(value)
                unique.append(p)
        return unique


# =========================
# Example and Demo
# =========================
if __name__ == "__main__":
    print("=" * 80)
    print("RAG Reranking Skill - Demo")
    print("=" * 80)

    # Create sample passages
    passages = [
        Passage(
            text="Machine learning is a subset of artificial intelligence that focuses on learning from data.",
            embedding=torch.randn(384),
            metadata={"source": "wiki", "timestamp": datetime(2024, 1, 15)},
            score=0.85,
        ),
        Passage(
            text="Deep learning uses neural networks with multiple layers to learn hierarchical representations.",
            embedding=torch.randn(384),
            metadata={"source": "wiki", "timestamp": datetime(2024, 6, 1)},
            score=0.78,
        ),
        Passage(
            text="Artificial intelligence encompasses machine learning, robotics, and expert systems.",
            embedding=torch.randn(384),
            metadata={"source": "textbook", "timestamp": datetime(2023, 3, 20)},
            score=0.82,
        ),
        Passage(
            text="Neural networks are inspired by biological neurons in the human brain.",
            embedding=torch.randn(384),
            metadata={"source": "wiki", "timestamp": datetime(2024, 8, 10)},
            score=0.75,
        ),
        Passage(
            text="Supervised learning requires labeled training data to learn patterns.",
            embedding=torch.randn(384),
            metadata={"source": "blog", "timestamp": datetime(2024, 9, 5)},
            score=0.70,
        ),
    ]

    query_text = "what is machine learning"
    query_embedding = torch.randn(384)

    print(f"\nQuery: '{query_text}'")
    print(f"Number of passages: {len(passages)}\n")

    # Demo 1: Semantic Reranking
    print("-" * 80)
    print("Demo 1: Semantic Reranking (Cosine Similarity)")
    print("-" * 80)

    semantic_reranker = SemanticReranker(query_embedding, metric="cosine")
    semantic_results = semantic_reranker.rerank(passages, k=3)

    print(f"\nTop 3 results:")
    for result in semantic_results:
        print(f"  [{result.rank}] Score: {result.rerank_score:.4f}")
        print(f"      Text: {result.passage.text[:80]}...")
        print()

    # Demo 2: Recency Reranking
    print("-" * 80)
    print("Demo 2: Recency Reranking (Exponential Decay)")
    print("-" * 80)

    recency_reranker = RecencyReranker(
        timestamp_key="timestamp",
        reference_time=datetime(2024, 10, 1),
        decay_rate=0.01,
        strategy="exponential",
    )
    recency_results = recency_reranker.rerank(passages, k=3)

    print(f"\nTop 3 most recent results:")
    for result in recency_results:
        ts = result.passage.metadata.get("timestamp")
        print(f"  [{result.rank}] Score: {result.rerank_score:.4f}, Date: {ts.date()}")
        print(f"      Text: {result.passage.text[:80]}...")
        print()

    # Demo 3: Lexical Reranking
    print("-" * 80)
    print("Demo 3: Lexical Reranking (BM25-like)")
    print("-" * 80)

    lexical_reranker = LexicalReranker(query_text)
    lexical_results = lexical_reranker.rerank(passages, k=3)

    print(f"\nTop 3 lexically similar results:")
    for result in lexical_results:
        print(f"  [{result.rank}] Score: {result.rerank_score:.4f}")
        print(f"      Text: {result.passage.text[:80]}...")
        print()

    # Demo 4: Hybrid Reranking
    print("-" * 80)
    print("Demo 4: Hybrid Reranking (Semantic + Recency + Lexical)")
    print("-" * 80)

    hybrid_reranker = HybridReranker(
        query_embedding=query_embedding,
        query_text=query_text,
        weights={"semantic": 0.5, "lexical": 0.3, "recency": 0.2},
    )
    hybrid_results = hybrid_reranker.rerank(passages, k=5)

    print(f"\nTop 5 hybrid-ranked results:")
    for result in hybrid_results:
        print(f"  [{result.rank}] Score: {result.rerank_score:.4f}")
        print(f"      Text: {result.passage.text[:80]}...")
        print()

    # Demo 5: Result Aggregation (RRF)
    print("-" * 80)
    print("Demo 5: Reciprocal Rank Fusion (RRF)")
    print("-" * 80)

    aggregator = ResultAggregator()
    rrf_results = aggregator.reciprocal_rank_fusion(
        [semantic_results, recency_results, lexical_results],
        k=60,
    )

    print(f"\nTop 5 RRF-fused results:")
    for i, result in enumerate(rrf_results[:5], 1):
        result.rank = i
        print(f"  [{result.rank}] RRF Score: {result.rerank_score:.4f}")
        print(f"      Text: {result.passage.text[:80]}...")
        print()

    # Demo 6: Filtering and Custom Reranking
    print("-" * 80)
    print("Demo 6: Custom Reranking with Filtering")
    print("-" * 80)

    # Custom scorer: prefer shorter passages
    def length_scorer(passage: Passage) -> float:
        length = len(passage.text)
        return 1.0 / (1.0 + length / 100.0)

    custom_reranker = CustomReranker(length_scorer, name="length_scorer")

    # Filter by source and rerank
    wiki_passages = filter_by_metadata(passages, {"source": "wiki"})
    custom_results = custom_reranker.rerank(wiki_passages, k=3)

    print(f"\nTop 3 shortest wiki passages:")
    for result in custom_results:
        print(f"  [{result.rank}] Score: {result.rerank_score:.4f}, Length: {len(result.passage.text)}")
        print(f"      Text: {result.passage.text[:80]}...")
        print()

    print("=" * 80)
    print("Demo complete!")
    print("=" * 80)
