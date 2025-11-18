# RAG Reranking Skill - Comprehensive Guide

A powerful, flexible reranking framework for Retrieval-Augmented Generation (RAG) pipelines. This skill enhances retrieval quality by intelligently reordering search results using semantic similarity, recency, lexical matching, and custom scoring algorithms.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Reranking Algorithms](#reranking-algorithms)
- [Result Aggregation](#result-aggregation)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

RAG pipelines typically consist of two stages:
1. **Retrieval**: Fast approximate search (vector/BM25/hybrid) to get candidate passages
2. **Reranking**: Slower but more accurate scoring to refine the top results

This skill provides the reranking layer with:

- **Multiple scoring algorithms**: Semantic, recency, lexical (BM25-like), custom
- **Hybrid fusion**: Combine multiple signals with weighted averaging
- **Flexible filtering**: By score threshold, top-k, metadata, or custom predicates
- **Result aggregation**: RRF, Borda count, weighted fusion, max fusion
- **Batch processing**: Efficient vectorized operations for large result sets
- **Extensible design**: Easy to add custom rerankers

## Installation

```bash
# Dependencies
pip install torch

# The skill is self-contained in rag_reranker.py
# Simply import it in your project:
from rag_reranker import *
```

### Requirements
- Python 3.8+
- PyTorch 1.10+ (for semantic similarity)

## Quick Start

### Basic Semantic Reranking

```python
from rag_reranker import Passage, SemanticReranker
import torch

# Your retrieval results
passages = [
    Passage(
        text="Machine learning is a subset of AI...",
        embedding=torch.randn(384),  # From your encoder
        score=0.85,  # Original retrieval score
    ),
    # ... more passages
]

# Query embedding
query_embedding = torch.randn(384)  # From your encoder

# Rerank using semantic similarity
reranker = SemanticReranker(query_embedding, metric="cosine")
results = reranker.rerank(passages, k=10, threshold=0.5)

# Access top results
for result in results:
    print(f"Rank {result.rank}: {result.passage.text}")
    print(f"  Score: {result.rerank_score:.4f}")
```

### Hybrid Reranking (Recommended)

```python
from rag_reranker import HybridReranker

# Combine semantic + lexical + recency
hybrid = HybridReranker(
    query_embedding=query_embedding,
    query_text="what is machine learning",
    weights={
        "semantic": 0.6,  # Emphasize semantic similarity
        "lexical": 0.3,   # Some lexical overlap
        "recency": 0.1,   # Slight preference for recent
    }
)

results = hybrid.rerank(passages, k=20)
```

### Multi-Reranker Fusion

```python
from rag_reranker import SemanticReranker, RecencyReranker, ResultAggregator

# Get results from multiple rerankers
semantic_results = SemanticReranker(query_emb).rerank(passages, k=20)
recency_results = RecencyReranker().rerank(passages, k=20)

# Fuse using Reciprocal Rank Fusion (RRF)
aggregator = ResultAggregator()
final_results = aggregator.reciprocal_rank_fusion([
    semantic_results,
    recency_results,
])
```

## Core Concepts

### Passage

The `Passage` dataclass represents a single document/passage:

```python
@dataclass
class Passage:
    text: str                          # Content
    embedding: Optional[torch.Tensor]  # Dense vector (for semantic)
    metadata: Dict[str, Any]           # Source, timestamp, etc.
    score: float                       # Original retrieval score
    id: Optional[str]                  # Unique ID (auto-generated)
```

**Example:**
```python
passage = Passage(
    text="Deep learning uses neural networks...",
    embedding=encoder.encode("Deep learning..."),
    metadata={
        "source": "wikipedia",
        "timestamp": datetime(2024, 10, 15),
        "author": "Alice",
        "doc_id": "wiki_12345",
    },
    score=0.82,
)
```

### RankedResult

The `RankedResult` dataclass contains reranking output:

```python
@dataclass
class RankedResult:
    passage: Passage         # Original passage
    rerank_score: float      # Score from reranker
    original_score: float    # Original retrieval score
    rank: int                # Position (1-indexed)
    explanation: Optional[str]  # Optional scoring explanation
```

## Reranking Algorithms

### 1. Semantic Reranker

Rerank by embedding similarity to the query.

**Metrics:**
- `cosine`: Cosine similarity (recommended for normalized embeddings)
- `dot`: Dot product (for unnormalized or magnitude-aware scoring)
- `euclidean`: Negative L2 distance

**Usage:**
```python
reranker = SemanticReranker(
    query_embedding=query_emb,
    metric="cosine",
    normalize_scores=True,
)
results = reranker.rerank(passages, k=10)
```

**When to use:**
- Primary reranking signal for semantic search
- When you have high-quality embeddings (BERT, sentence-transformers, etc.)
- Cross-lingual retrieval (with multilingual embeddings)

### 2. Recency Reranker

Rerank by document freshness/timestamp.

**Strategies:**
- `exponential`: Smooth exponential decay (recommended)
  - Score = exp(-decay_rate × days_old)
- `linear`: Linear decay with hard cutoff
  - Score = max(0, 1 - decay_rate × days_old)
- `step`: Binary cutoff (recent vs. old)
  - Score = 1 if days_old ≤ threshold else 0

**Usage:**
```python
from datetime import datetime

reranker = RecencyReranker(
    timestamp_key="timestamp",           # Metadata key
    reference_time=datetime.now(),       # "Now" (default)
    decay_rate=0.01,                     # Decay parameter
    strategy="exponential",
)
results = reranker.rerank(passages, k=10)
```

**When to use:**
- News, social media, time-sensitive content
- Combine with semantic (0.8 semantic + 0.2 recency)
- When freshness matters but isn't captured in embeddings

### 3. Lexical Reranker (BM25-like)

Rerank by term overlap with the query.

**Algorithm:**
- Simplified BM25 scoring
- Term frequency with saturation (k1 parameter)
- Document length normalization (b parameter)
- Optional IDF weighting

**Usage:**
```python
reranker = LexicalReranker(
    query_text="machine learning algorithms",
    k1=1.5,          # TF saturation (BM25 default)
    b=0.75,          # Length normalization (BM25 default)
    use_idf=True,    # Enable IDF weighting
)
results = reranker.rerank(passages, k=10)
```

**When to use:**
- Exact keyword matching is important
- Handling entity names, technical terms, rare words
- Complementing semantic search (lexical gap problem)
- Transparent, interpretable scoring

### 4. Hybrid Reranker

Combine multiple rerankers with weighted fusion.

**Usage:**
```python
# Option 1: Auto-create sub-rerankers
hybrid = HybridReranker(
    query_embedding=query_emb,
    query_text=query_text,
    weights={
        "semantic": 0.6,
        "lexical": 0.3,
        "recency": 0.1,
    }
)

# Option 2: Provide custom rerankers
hybrid = HybridReranker(
    rerankers=[
        SemanticReranker(query_emb, metric="cosine", name="sem_cos"),
        SemanticReranker(query_emb, metric="dot", name="sem_dot"),
        LexicalReranker(query_text, name="lex"),
    ],
    weights={
        "sem_cos": 0.5,
        "sem_dot": 0.3,
        "lex": 0.2,
    }
)

results = hybrid.rerank(passages, k=20)
```

**When to use:**
- Production systems (best overall performance)
- When multiple signals are available
- Tuning weights on held-out validation data

### 5. Custom Reranker

Create your own scoring function.

**Usage:**
```python
def custom_scorer(passage: Passage) -> float:
    # Example: Prefer passages with specific metadata
    score = 0.0

    # Boost by source quality
    if passage.metadata.get("source") == "wikipedia":
        score += 0.5

    # Penalize long passages
    score -= len(passage.text) / 10000.0

    # Boost if contains keyword
    if "neural" in passage.text.lower():
        score += 0.3

    return score

reranker = CustomReranker(custom_scorer, name="custom")
results = reranker.rerank(passages, k=10)
```

## Result Aggregation

Combine outputs from multiple rerankers using different fusion strategies.

### Reciprocal Rank Fusion (RRF)

**Formula:** `RRF_score = Σ 1/(k + rank_i)` across all rankers

**Best for:** Robust fusion without tuning, different scoring scales

```python
aggregator = ResultAggregator()
fused = aggregator.reciprocal_rank_fusion(
    [results1, results2, results3],
    k=60,  # RRF constant (default: 60)
)
```

### Borda Count

**Formula:** Each result gets `(N - rank + 1)` points per ranker

**Best for:** Voting-based fusion, interpretable results

```python
fused = aggregator.borda_count([results1, results2, results3])
```

### Weighted Fusion

**Formula:** Weighted average of normalized scores

**Best for:** When you have confidence in each reranker's quality

```python
fused = aggregator.weighted_fusion(
    [results1, results2, results3],
    weights=[0.5, 0.3, 0.2],  # Must sum to 1
)
```

### Max Fusion

**Formula:** Each passage gets its maximum score across rankers

**Best for:** Optimistic/permissive fusion, recall-oriented

```python
fused = aggregator.max_fusion([results1, results2, results3])
```

## Advanced Usage

### Filtering

#### By Score Threshold
```python
# Only return results above threshold
results = reranker.rerank(passages, threshold=0.7)
```

#### By Metadata
```python
from rag_reranker import filter_by_metadata

# Pre-filter by metadata
wiki_passages = filter_by_metadata(passages, {"source": "wikipedia"})
results = reranker.rerank(wiki_passages, k=10)
```

#### By Custom Predicate
```python
# Custom filter function
def is_long_passage(p: Passage) -> bool:
    return len(p.text) > 500

results = reranker.rerank(
    passages,
    k=10,
    filter_fn=is_long_passage,
)
```

### Deduplication

```python
from rag_reranker import deduplicate_passages

# Exact text deduplication
unique = deduplicate_passages(passages, key="text")

# Metadata-based deduplication
unique = deduplicate_passages(passages, key="doc_id")
```

### Batch Processing

All rerankers support efficient batch processing:

```python
# score_batch() is called automatically by rerank()
# Override for custom batch optimization
class MyReranker(BaseReranker):
    def score_batch(self, passages: List[Passage]) -> List[float]:
        # Vectorized batch scoring
        embeddings = torch.stack([p.embedding for p in passages])
        scores = torch.matmul(embeddings, self.query_emb).tolist()
        return scores
```

### Custom Reranker Implementation

```python
class DomainReranker(BaseReranker):
    def __init__(self, preferred_domains: List[str]):
        super().__init__(name="domain")
        self.preferred_domains = set(preferred_domains)

    def score_passage(self, passage: Passage) -> float:
        domain = passage.metadata.get("domain", "")
        return 1.0 if domain in self.preferred_domains else 0.0

reranker = DomainReranker(["wikipedia.org", "arxiv.org"])
```

## API Reference

### BaseReranker

**Abstract base class for all rerankers.**

```python
class BaseReranker(ABC):
    def __init__(self, name: str, normalize_scores: bool = True)

    @abstractmethod
    def score_passage(self, passage: Passage) -> float:
        """Score a single passage."""
        pass

    def score_batch(self, passages: List[Passage]) -> List[float]:
        """Score a batch (override for efficiency)."""
        pass

    def rerank(
        self,
        passages: List[Passage],
        k: Optional[int] = None,
        threshold: Optional[float] = None,
        filter_fn: Optional[Callable] = None,
    ) -> List[RankedResult]:
        """Rerank passages."""
        pass
```

### SemanticReranker

```python
SemanticReranker(
    query_embedding: torch.Tensor,     # Query embedding
    metric: str = "cosine",            # "cosine", "dot", "euclidean"
    name: str = "semantic",
    normalize_scores: bool = True,
)
```

### RecencyReranker

```python
RecencyReranker(
    timestamp_key: str = "timestamp",        # Metadata key
    reference_time: datetime = datetime.now(),
    decay_rate: float = 0.1,                 # Decay parameter
    strategy: str = "exponential",           # "exponential", "linear", "step"
    name: str = "recency",
    normalize_scores: bool = True,
)
```

### LexicalReranker

```python
LexicalReranker(
    query_text: str,                   # Query string
    k1: float = 1.5,                   # BM25 TF saturation
    b: float = 0.75,                   # BM25 length normalization
    use_idf: bool = True,              # Enable IDF
    name: str = "lexical",
    normalize_scores: bool = True,
)
```

### HybridReranker

```python
HybridReranker(
    rerankers: Optional[List[BaseReranker]] = None,
    weights: Optional[Dict[str, float]] = None,
    query_embedding: Optional[torch.Tensor] = None,
    query_text: Optional[str] = None,
    timestamp_key: str = "timestamp",
    name: str = "hybrid",
    normalize_scores: bool = True,
)
```

### CustomReranker

```python
CustomReranker(
    scoring_fn: Callable[[Passage], float],
    name: str = "custom",
    normalize_scores: bool = True,
)
```

### ResultAggregator

```python
ResultAggregator.reciprocal_rank_fusion(
    results_list: List[List[RankedResult]],
    k: int = 60,
) -> List[RankedResult]

ResultAggregator.borda_count(
    results_list: List[List[RankedResult]],
) -> List[RankedResult]

ResultAggregator.weighted_fusion(
    results_list: List[List[RankedResult]],
    weights: Optional[List[float]] = None,
) -> List[RankedResult]

ResultAggregator.max_fusion(
    results_list: List[List[RankedResult]],
) -> List[RankedResult]
```

## Best Practices

### 1. Choose the Right Algorithm

| Use Case | Recommended Approach |
|----------|---------------------|
| General semantic search | `SemanticReranker` (cosine) |
| News/time-sensitive | `HybridReranker` (semantic + recency) |
| Technical/keyword search | `HybridReranker` (semantic + lexical) |
| Multi-signal production | `HybridReranker` (all three) |
| Exact keyword matching | `LexicalReranker` |
| Custom domain logic | `CustomReranker` |

### 2. Weight Tuning

Start with these defaults for hybrid reranking:
- **Semantic-only**: `{semantic: 1.0}`
- **Semantic + Lexical**: `{semantic: 0.7, lexical: 0.3}`
- **Semantic + Recency**: `{semantic: 0.8, recency: 0.2}`
- **All three**: `{semantic: 0.6, lexical: 0.3, recency: 0.1}`

Tune on validation data by grid search or Bayesian optimization.

### 3. Performance Optimization

- **Use batch scoring**: Implement `score_batch()` for vectorized ops
- **Filter early**: Apply metadata filters before reranking
- **Limit candidates**: Only rerank top-K from retrieval (e.g., top 100)
- **Cache embeddings**: Precompute and store passage embeddings
- **Use GPU**: Move embeddings to GPU for large batches

### 4. Quality Monitoring

Track these metrics:
- **nDCG@K**: Normalized Discounted Cumulative Gain
- **MRR**: Mean Reciprocal Rank
- **Recall@K**: Coverage of relevant results
- **Latency**: Reranking time (should be <100ms for production)

### 5. A/B Testing

When deploying:
1. Start with semantic reranker only
2. A/B test hybrid vs. semantic
3. Tune weights based on user engagement (CTR, dwell time)
4. Monitor for degradation over time (model drift)

## Examples

### Example 1: RAG Pipeline Integration

```python
from rag_reranker import Passage, HybridReranker

def rag_pipeline(query_text: str, query_embedding: torch.Tensor):
    # Step 1: Fast retrieval (vector search)
    initial_results = vector_search(query_embedding, k=100)

    # Step 2: Convert to Passage objects
    passages = [
        Passage(
            text=doc["text"],
            embedding=doc["embedding"],
            metadata={"source": doc["source"], "timestamp": doc["timestamp"]},
            score=doc["score"],
        )
        for doc in initial_results
    ]

    # Step 3: Hybrid reranking
    reranker = HybridReranker(
        query_embedding=query_embedding,
        query_text=query_text,
        weights={"semantic": 0.6, "lexical": 0.3, "recency": 0.1},
    )
    reranked = reranker.rerank(passages, k=10, threshold=0.5)

    # Step 4: Return top results
    return [r.passage.text for r in reranked]

# Usage
answer = rag_pipeline(
    query_text="What is transformers architecture?",
    query_embedding=encode("What is transformers architecture?"),
)
```

### Example 2: Multi-Stage Reranking

```python
# Stage 1: Fast semantic filtering
stage1_reranker = SemanticReranker(query_emb, metric="dot")
stage1_results = stage1_reranker.rerank(passages, k=50)

# Stage 2: Hybrid refinement
stage2_passages = [r.passage for r in stage1_results]
stage2_reranker = HybridReranker(
    query_embedding=query_emb,
    query_text=query_text,
    weights={"semantic": 0.7, "lexical": 0.3},
)
final_results = stage2_reranker.rerank(stage2_passages, k=10)
```

### Example 3: Ensemble Reranking

```python
# Create multiple rerankers
rerankers = [
    SemanticReranker(query_emb, metric="cosine", name="cos"),
    SemanticReranker(query_emb, metric="dot", name="dot"),
    LexicalReranker(query_text, name="lex"),
    RecencyReranker(name="rec"),
]

# Get results from each
results_list = [r.rerank(passages, k=20) for r in rerankers]

# Fuse with RRF
aggregator = ResultAggregator()
final = aggregator.reciprocal_rank_fusion(results_list, k=60)
```

### Example 4: Domain-Specific Reranking

```python
# Custom reranker for medical domain
def medical_scorer(passage: Passage) -> float:
    score = 0.0

    # Boost peer-reviewed sources
    if passage.metadata.get("peer_reviewed"):
        score += 0.5

    # Boost by citation count
    citations = passage.metadata.get("citations", 0)
    score += min(1.0, citations / 100.0)

    # Recent papers preferred
    year = passage.metadata.get("year", 2000)
    recency = (year - 2000) / 24.0  # Normalize 2000-2024
    score += recency * 0.3

    return score

# Combine with semantic
hybrid = HybridReranker(
    rerankers=[
        SemanticReranker(query_emb, name="sem"),
        CustomReranker(medical_scorer, name="med"),
    ],
    weights={"sem": 0.7, "med": 0.3},
)
```

### Example 5: Cross-Encoder Reranking

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class CrossEncoderReranker(BaseReranker):
    """Reranker using a cross-encoder model (e.g., ms-marco-MiniLM)."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        super().__init__(name="cross_encoder")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        self.query_text = None

    def set_query(self, query_text: str):
        self.query_text = query_text

    def score_passage(self, passage: Passage) -> float:
        if self.query_text is None:
            return 0.0

        inputs = self.tokenizer(
            self.query_text,
            passage.text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            logits = self.model(**inputs).logits

        return float(logits[0][0].item())

# Usage
reranker = CrossEncoderReranker()
reranker.set_query("What is machine learning?")
results = reranker.rerank(passages, k=10)
```

## Performance Benchmarks

Typical latency on a single CPU core (10 passages):

| Reranker | Latency |
|----------|---------|
| SemanticReranker | ~1ms |
| RecencyReranker | ~0.1ms |
| LexicalReranker | ~5ms |
| HybridReranker (all) | ~6ms |
| CrossEncoderReranker | ~50ms |

**Notes:**
- Semantic reranking is very fast (simple dot product)
- Lexical has one-time IDF computation (cached after first batch)
- Cross-encoders are slowest but most accurate (use for top-K only)
- GPU can speed up cross-encoders by 10-50x

## Conclusion

This RAG reranking skill provides a production-ready, extensible framework for enhancing retrieval quality. Start simple with semantic reranking, then layer in hybrid approaches as needed. Monitor metrics and tune weights for your specific domain.

**Next Steps:**
1. Run the demo: `python rag_reranker.py`
2. Integrate with your RAG pipeline
3. Tune weights on validation data
4. A/B test in production
5. Monitor quality metrics

For questions or issues, please open a GitHub issue.
