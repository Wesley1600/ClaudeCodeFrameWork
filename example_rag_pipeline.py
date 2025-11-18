"""
Complete RAG Pipeline Example with Reranking

Demonstrates a full retrieval-augmented generation pipeline:
1. Document indexing with embeddings
2. Vector search for initial retrieval
3. Multi-stage reranking with different strategies
4. Result fusion and filtering
5. Final context assembly for LLM

This example uses synthetic data but can be adapted to real document collections.
"""

import torch
import torch.nn.functional as F
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

from rag_reranker import (
    Passage,
    SemanticReranker,
    RecencyReranker,
    LexicalReranker,
    HybridReranker,
    CustomReranker,
    ResultAggregator,
    filter_by_metadata,
    deduplicate_passages,
)


# =========================
# Synthetic Document Collection
# =========================
def create_sample_documents() -> List[Dict[str, Any]]:
    """Create a synthetic document collection about AI/ML topics."""

    documents = [
        {
            "text": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.",
            "source": "wikipedia",
            "author": "AI Research Team",
            "timestamp": datetime.now() - timedelta(days=30),
            "citations": 150,
            "doc_id": "doc_001",
        },
        {
            "text": "Deep learning is a machine learning technique that teaches computers to do what comes naturally to humans: learn by example. It is a key technology behind driverless cars, voice control in devices, and many other applications.",
            "source": "blog",
            "author": "John Smith",
            "timestamp": datetime.now() - timedelta(days=5),
            "citations": 45,
            "doc_id": "doc_002",
        },
        {
            "text": "Neural networks are computing systems inspired by biological neural networks in animal brains. They consist of interconnected nodes (neurons) that process information using a connectionist approach to computation.",
            "source": "textbook",
            "author": "Dr. Alice Johnson",
            "timestamp": datetime.now() - timedelta(days=365),
            "citations": 320,
            "doc_id": "doc_003",
        },
        {
            "text": "Supervised learning is a machine learning paradigm where the algorithm learns from labeled training data. The algorithm makes predictions on the data and is corrected by the teacher when it makes mistakes.",
            "source": "wikipedia",
            "author": "ML Contributors",
            "timestamp": datetime.now() - timedelta(days=60),
            "citations": 200,
            "doc_id": "doc_004",
        },
        {
            "text": "Unsupervised learning algorithms discover hidden patterns or data groupings without human intervention. Common techniques include clustering, dimensionality reduction, and association rule learning.",
            "source": "arxiv",
            "author": "Research Lab",
            "timestamp": datetime.now() - timedelta(days=15),
            "citations": 89,
            "doc_id": "doc_005",
        },
        {
            "text": "Reinforcement learning is an area of machine learning where an agent learns to make decisions by taking actions in an environment to maximize cumulative reward. It's inspired by behaviorist psychology.",
            "source": "blog",
            "author": "RL Expert",
            "timestamp": datetime.now() - timedelta(days=3),
            "citations": 67,
            "doc_id": "doc_006",
        },
        {
            "text": "Transformers are a type of neural network architecture that has revolutionized natural language processing. They use self-attention mechanisms to process sequential data more effectively than recurrent networks.",
            "source": "arxiv",
            "author": "Vaswani et al.",
            "timestamp": datetime.now() - timedelta(days=7),
            "citations": 50000,
            "doc_id": "doc_007",
        },
        {
            "text": "Convolutional neural networks (CNNs) are specialized neural networks for processing grid-like data such as images. They use convolutional layers that apply filters to detect features like edges, textures, and patterns.",
            "source": "textbook",
            "author": "Prof. Bob Lee",
            "timestamp": datetime.now() - timedelta(days=200),
            "citations": 890,
            "doc_id": "doc_008",
        },
        {
            "text": "Transfer learning involves taking a pre-trained model and adapting it to a new but related problem. This approach significantly reduces training time and improves performance, especially when labeled data is limited.",
            "source": "blog",
            "author": "Sarah Chen",
            "timestamp": datetime.now() - timedelta(days=10),
            "citations": 123,
            "doc_id": "doc_009",
        },
        {
            "text": "Generative adversarial networks (GANs) consist of two neural networks competing against each other: a generator creates fake data and a discriminator tries to distinguish real from fake. This adversarial process produces highly realistic synthetic data.",
            "source": "arxiv",
            "author": "Ian Goodfellow",
            "timestamp": datetime.now() - timedelta(days=20),
            "citations": 15000,
            "doc_id": "doc_010",
        },
        {
            "text": "Natural language processing (NLP) enables computers to understand, interpret, and generate human language. Modern NLP uses deep learning models like BERT and GPT for tasks such as translation, summarization, and question answering.",
            "source": "wikipedia",
            "author": "NLP Research Group",
            "timestamp": datetime.now() - timedelta(days=12),
            "citations": 450,
            "doc_id": "doc_011",
        },
        {
            "text": "Computer vision is a field of AI that trains computers to interpret and understand visual information from the world. Applications include facial recognition, object detection, and autonomous navigation.",
            "source": "textbook",
            "author": "Vision Lab",
            "timestamp": datetime.now() - timedelta(days=90),
            "citations": 560,
            "doc_id": "doc_012",
        },
    ]

    return documents


# =========================
# Simple Embedding Generator
# =========================
def generate_embedding(text: str, dim: int = 384) -> torch.Tensor:
    """
    Generate a synthetic embedding for text.

    In production, use a real encoder like:
    - sentence-transformers
    - OpenAI embeddings
    - Cohere embeddings
    """
    # Simple hash-based embedding (for demo only!)
    # In production, use actual embedding models
    random.seed(hash(text.lower()) % (2**32))
    embedding = torch.randn(dim)

    # Add some semantic structure
    keywords = ["learning", "neural", "network", "deep", "data", "model", "training"]
    for i, keyword in enumerate(keywords):
        if keyword in text.lower():
            embedding[i * 10:(i + 1) * 10] += 2.0

    return F.normalize(embedding, dim=-1)


# =========================
# Vector Search (Initial Retrieval)
# =========================
class SimpleVectorStore:
    """Simple in-memory vector store for demonstration."""

    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: List[torch.Tensor] = []

    def add_documents(self, documents: List[Dict[str, Any]]):
        """Index documents with embeddings."""
        print(f"Indexing {len(documents)} documents...")

        for doc in documents:
            self.documents.append(doc)
            embedding = generate_embedding(doc["text"])
            self.embeddings.append(embedding)

        print(f"✓ Indexed {len(self.documents)} documents")

    def search(self, query_embedding: torch.Tensor, k: int = 100) -> List[Passage]:
        """Retrieve top-k documents by cosine similarity."""
        if not self.embeddings:
            return []

        # Stack all embeddings
        all_embeddings = torch.stack(self.embeddings)

        # Compute cosine similarities
        similarities = F.cosine_similarity(
            query_embedding.unsqueeze(0),
            all_embeddings,
            dim=-1
        )

        # Get top-k
        top_k = min(k, len(similarities))
        scores, indices = torch.topk(similarities, k=top_k)

        # Convert to Passage objects
        passages = []
        for idx, score in zip(indices.tolist(), scores.tolist()):
            doc = self.documents[idx]
            passage = Passage(
                text=doc["text"],
                embedding=self.embeddings[idx],
                metadata={
                    "source": doc["source"],
                    "author": doc["author"],
                    "timestamp": doc["timestamp"],
                    "citations": doc["citations"],
                    "doc_id": doc["doc_id"],
                },
                score=score,
                id=doc["doc_id"],
            )
            passages.append(passage)

        return passages


# =========================
# RAG Pipeline
# =========================
class RAGPipeline:
    """Complete RAG pipeline with configurable reranking."""

    def __init__(self, vector_store: SimpleVectorStore):
        self.vector_store = vector_store

    def retrieve(
        self,
        query_text: str,
        k: int = 5,
        reranking_strategy: str = "hybrid",
        initial_k: int = 50,
    ) -> List[Passage]:
        """
        Retrieve and rerank documents for a query.

        Args:
            query_text: The search query
            k: Number of final results to return
            reranking_strategy: "semantic", "lexical", "recency", "hybrid", "ensemble"
            initial_k: Number of candidates to retrieve before reranking

        Returns:
            List of top-k reranked passages
        """
        print(f"\n{'='*80}")
        print(f"Query: '{query_text}'")
        print(f"Strategy: {reranking_strategy}")
        print(f"{'='*80}\n")

        # Step 1: Initial retrieval (vector search)
        print(f"[1/3] Initial retrieval (top-{initial_k})...")
        query_embedding = generate_embedding(query_text)
        candidates = self.vector_store.search(query_embedding, k=initial_k)
        print(f"  ✓ Retrieved {len(candidates)} candidates")

        # Step 2: Reranking
        print(f"\n[2/3] Reranking with '{reranking_strategy}' strategy...")

        if reranking_strategy == "semantic":
            reranker = SemanticReranker(query_embedding, metric="cosine")
            results = reranker.rerank(candidates, k=k)

        elif reranking_strategy == "lexical":
            reranker = LexicalReranker(query_text)
            results = reranker.rerank(candidates, k=k)

        elif reranking_strategy == "recency":
            reranker = RecencyReranker(
                timestamp_key="timestamp",
                decay_rate=0.01,
                strategy="exponential",
            )
            results = reranker.rerank(candidates, k=k)

        elif reranking_strategy == "hybrid":
            reranker = HybridReranker(
                query_embedding=query_embedding,
                query_text=query_text,
                weights={
                    "semantic": 0.6,
                    "lexical": 0.3,
                    "recency": 0.1,
                },
            )
            results = reranker.rerank(candidates, k=k)

        elif reranking_strategy == "ensemble":
            # Multi-reranker ensemble with RRF fusion
            semantic_results = SemanticReranker(query_embedding).rerank(candidates, k=k*2)
            lexical_results = LexicalReranker(query_text).rerank(candidates, k=k*2)
            recency_results = RecencyReranker().rerank(candidates, k=k*2)

            aggregator = ResultAggregator()
            results = aggregator.reciprocal_rank_fusion(
                [semantic_results, lexical_results, recency_results],
                k=60,
            )
            results = results[:k]

        elif reranking_strategy == "custom":
            # Custom domain-specific scorer
            def quality_scorer(passage: Passage) -> float:
                score = 0.0

                # Boost highly-cited papers
                citations = passage.metadata.get("citations", 0)
                score += min(1.0, citations / 1000.0)

                # Boost arxiv and textbooks
                source = passage.metadata.get("source", "")
                if source in {"arxiv", "textbook"}:
                    score += 0.5

                # Recency bonus
                timestamp = passage.metadata.get("timestamp")
                if timestamp:
                    days_old = (datetime.now() - timestamp).days
                    score += max(0, 1.0 - days_old / 365.0) * 0.3

                return score

            # Combine custom scorer with semantic
            hybrid = HybridReranker(
                rerankers=[
                    SemanticReranker(query_embedding, name="sem"),
                    CustomReranker(quality_scorer, name="quality"),
                ],
                weights={"sem": 0.7, "quality": 0.3},
            )
            results = hybrid.rerank(candidates, k=k)

        else:
            raise ValueError(f"Unknown strategy: {reranking_strategy}")

        print(f"  ✓ Reranked to top-{len(results)} results")

        # Step 3: Post-processing
        print(f"\n[3/3] Post-processing...")

        # Deduplication
        unique_passages = deduplicate_passages([r.passage for r in results], key="text")
        print(f"  ✓ Deduplicated: {len(results)} → {len(unique_passages)} passages")

        return unique_passages[:k]

    def print_results(self, passages: List[Passage]):
        """Pretty-print retrieval results."""
        print(f"\n{'='*80}")
        print("FINAL RESULTS")
        print(f"{'='*80}\n")

        for i, passage in enumerate(passages, 1):
            print(f"[{i}] Score: {passage.score:.4f}")
            print(f"    Source: {passage.metadata.get('source', 'N/A')}")
            print(f"    Author: {passage.metadata.get('author', 'N/A')}")
            print(f"    Citations: {passage.metadata.get('citations', 0)}")

            timestamp = passage.metadata.get('timestamp')
            if timestamp:
                days_ago = (datetime.now() - timestamp).days
                print(f"    Date: {timestamp.date()} ({days_ago} days ago)")

            print(f"    Text: {passage.text[:150]}...")
            print()


# =========================
# Main Demo
# =========================
def main():
    print("=" * 80)
    print("RAG PIPELINE WITH RERANKING - DEMONSTRATION")
    print("=" * 80)

    # Initialize document collection
    documents = create_sample_documents()

    # Create vector store and index documents
    vector_store = SimpleVectorStore()
    vector_store.add_documents(documents)

    # Create RAG pipeline
    pipeline = RAGPipeline(vector_store)

    # Test queries
    test_queries = [
        "What is machine learning?",
        "Tell me about transformers in NLP",
        "How do neural networks work?",
    ]

    # Test different reranking strategies
    strategies = ["semantic", "hybrid", "ensemble", "custom"]

    for query in test_queries[:1]:  # Test first query with all strategies
        for strategy in strategies:
            results = pipeline.retrieve(
                query_text=query,
                k=5,
                reranking_strategy=strategy,
                initial_k=12,  # Small for demo
            )
            pipeline.print_results(results)
            print("\n" + "=" * 80 + "\n")

    # Comparison: Different strategies on same query
    print("\n" + "=" * 80)
    print("STRATEGY COMPARISON")
    print("=" * 80)

    query = "recent advances in deep learning"
    print(f"\nQuery: '{query}'\n")

    for strategy in ["semantic", "recency", "hybrid"]:
        print(f"\n--- {strategy.upper()} ---")
        results = pipeline.retrieve(query, k=3, reranking_strategy=strategy, initial_k=12)

        for i, passage in enumerate(results, 1):
            source = passage.metadata.get('source', 'N/A')
            timestamp = passage.metadata.get('timestamp')
            days_ago = (datetime.now() - timestamp).days if timestamp else 'N/A'

            print(f"  [{i}] {source} | {days_ago} days old")
            print(f"      {passage.text[:80]}...")

    print("\n" + "=" * 80)
    print("DEMO COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
