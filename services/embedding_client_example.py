"""
Example client for the Qwen3 Embedding Service

Demonstrates how to interact with the embedding service from your agents.
"""

import asyncio
import httpx
from typing import List, Optional, Union
import numpy as np


class EmbeddingClient:
    """
    Async client for the embedding service.

    Usage in your agent orchestration platform:
        client = EmbeddingClient("http://localhost:8000")
        embeddings = await client.embed(["query text", "document text"])
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 120.0,
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    async def health(self) -> dict:
        """Check service health"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def embed(
        self,
        texts: Union[str, List[str]],
        dimensions: Optional[int] = None,
        model: str = "Qwen/Qwen3-Embedding-4B",
        encoding_format: str = "float",
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Generate embeddings for text(s).

        Args:
            texts: Single text or list of texts to embed
            dimensions: Target dimension (default: 2560)
            model: Model identifier
            encoding_format: "float" or "base64"
            normalize: Whether embeddings are normalized (always True from service)

        Returns:
            numpy array of shape (n_texts, dimensions)
        """
        request_data = {
            "model": model,
            "input": texts,
            "encoding_format": encoding_format,
        }

        if dimensions:
            request_data["dimensions"] = dimensions

        async with httpx.AsyncClient(
            timeout=self.timeout,
            headers=self.headers
        ) as client:
            response = await client.post(
                f"{self.base_url}/v1/embeddings",
                json=request_data,
            )
            response.raise_for_status()
            result = response.json()

        # Extract embeddings
        embeddings = []
        for item in result["data"]:
            if encoding_format == "base64":
                import base64
                emb_bytes = base64.b64decode(item["embedding"])
                emb = np.frombuffer(emb_bytes, dtype=np.float32)
            else:
                emb = np.array(item["embedding"], dtype=np.float32)
            embeddings.append(emb)

        return np.array(embeddings)

    async def similarity(
        self,
        text1: str,
        text2: str,
        dimensions: Optional[int] = None,
    ) -> float:
        """
        Compute cosine similarity between two texts.

        Args:
            text1: First text
            text2: Second text
            dimensions: Embedding dimension

        Returns:
            Cosine similarity score (0-1)
        """
        embeddings = await self.embed([text1, text2], dimensions=dimensions)

        # Cosine similarity (embeddings are already normalized)
        similarity = float(np.dot(embeddings[0], embeddings[1]))
        return similarity

    async def batch_embed(
        self,
        texts: List[str],
        batch_size: int = 32,
        dimensions: Optional[int] = None,
        show_progress: bool = True,
    ) -> np.ndarray:
        """
        Embed large batches of texts with automatic chunking.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch
            dimensions: Target dimension
            show_progress: Whether to show progress

        Returns:
            numpy array of all embeddings
        """
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            if show_progress:
                print(f"Processing batch {i // batch_size + 1}/{(len(texts) - 1) // batch_size + 1}")

            embeddings = await self.embed(batch, dimensions=dimensions)
            all_embeddings.append(embeddings)

        return np.vstack(all_embeddings)


# ----- Usage Examples -----
async def example_basic_usage():
    """Basic embedding generation"""
    client = EmbeddingClient()

    # Check health
    health = await client.health()
    print(f"Service status: {health['status']}")
    print(f"Device: {health['device']}")

    # Embed single text
    text = "This is a test document for the knowledge base"
    embedding = await client.embed(text)
    print(f"Embedding shape: {embedding.shape}")  # (1, 2560)

    # Embed multiple texts
    texts = [
        "Agent orchestration platform",
        "Vector database for knowledge storage",
        "Graph database for relationship mapping",
    ]
    embeddings = await client.embed(texts, dimensions=1024)
    print(f"Batch embeddings shape: {embeddings.shape}")  # (3, 1024)


async def example_similarity_search():
    """Semantic similarity example"""
    client = EmbeddingClient()

    query = "machine learning model"
    documents = [
        "neural network architecture for deep learning",
        "database indexing strategy",
        "artificial intelligence algorithms",
        "web server configuration",
    ]

    # Embed query and documents
    query_emb = await client.embed(query)
    doc_embs = await client.embed(documents)

    # Compute similarities (embeddings are normalized, so dot product = cosine sim)
    similarities = np.dot(doc_embs, query_emb.T).flatten()

    # Rank documents
    ranked_indices = np.argsort(similarities)[::-1]

    print("\nSemantic Search Results:")
    for idx in ranked_indices:
        print(f"  {similarities[idx]:.3f} - {documents[idx]}")


async def example_knowledge_base_integration():
    """Example: Integrating with a vector database for agent knowledge base"""
    client = EmbeddingClient()

    # Simulate knowledge base documents
    kb_documents = [
        "Python is a high-level programming language",
        "FastAPI is a modern web framework for APIs",
        "Vector databases store high-dimensional embeddings",
        "Agents use tools to accomplish complex tasks",
        "Graph databases represent relationships between entities",
    ]

    print("Building knowledge base embeddings...")
    kb_embeddings = await client.batch_embed(
        kb_documents,
        batch_size=3,
        dimensions=512,  # Use lower dim for faster retrieval
    )

    print(f"Knowledge base shape: {kb_embeddings.shape}")

    # Agent query
    agent_query = "How do I build an API?"
    query_emb = await client.embed(agent_query, dimensions=512)

    # Retrieve top-k relevant documents
    similarities = np.dot(kb_embeddings, query_emb.T).flatten()
    top_k = 2
    top_indices = np.argsort(similarities)[::-1][:top_k]

    print(f"\nAgent Query: '{agent_query}'")
    print("Top relevant documents:")
    for idx in top_indices:
        print(f"  [{similarities[idx]:.3f}] {kb_documents[idx]}")


async def example_multi_modal_kb():
    """
    Example: Multi-modal knowledge base structure

    Demonstrates how embeddings can support different database types:
    - Vector DB: Semantic search
    - Graph DB: Entity relationships
    - Relational DB: Structured metadata
    """
    client = EmbeddingClient()

    # Entities with metadata
    entities = [
        {
            "id": "agent_001",
            "type": "agent",
            "name": "ResearchAgent",
            "description": "Specialized agent for web research and information gathering",
            "capabilities": ["web_search", "summarization", "fact_checking"],
        },
        {
            "id": "agent_002",
            "type": "agent",
            "name": "CodeAgent",
            "description": "Agent for code analysis and generation tasks",
            "capabilities": ["code_review", "bug_fixing", "refactoring"],
        },
        {
            "id": "tool_001",
            "type": "tool",
            "name": "VectorSearch",
            "description": "Semantic search over vector embeddings",
            "use_cases": ["similarity_search", "recommendation", "clustering"],
        },
    ]

    # Generate embeddings for semantic search (Vector DB)
    descriptions = [e["description"] for e in entities]
    embeddings = await client.embed(descriptions, dimensions=1024)

    # Store in your databases:
    # 1. Vector DB: Store embeddings for semantic retrieval
    # 2. Graph DB: Store relationships (agent uses tool, tool depends on resource)
    # 3. Relational DB: Store metadata (id, type, name, capabilities)

    print("\nMulti-modal Knowledge Base Setup:")
    print(f"Generated {len(embeddings)} embeddings for vector database")
    print(f"Entities can be linked in graph database by capabilities/use_cases")
    print(f"Metadata stored in relational database for structured queries")

    # Example query: Find tools for an agent's task
    task_query = "I need to search for similar documents"
    task_emb = await client.embed(task_query, dimensions=1024)

    similarities = np.dot(embeddings, task_emb.T).flatten()
    best_match_idx = np.argmax(similarities)

    print(f"\nTask: '{task_query}'")
    print(f"Best match: {entities[best_match_idx]['name']}")
    print(f"  Type: {entities[best_match_idx]['type']}")
    print(f"  Similarity: {similarities[best_match_idx]:.3f}")


async def main():
    """Run all examples"""
    print("=" * 60)
    print("Qwen3 Embedding Service - Client Examples")
    print("=" * 60)

    try:
        print("\n[1] Basic Usage")
        print("-" * 60)
        await example_basic_usage()

        print("\n[2] Similarity Search")
        print("-" * 60)
        await example_similarity_search()

        print("\n[3] Knowledge Base Integration")
        print("-" * 60)
        await example_knowledge_base_integration()

        print("\n[4] Multi-Modal Knowledge Base")
        print("-" * 60)
        await example_multi_modal_kb()

    except httpx.ConnectError:
        print("\nError: Could not connect to embedding service.")
        print("Make sure the service is running: python embedding_service.py")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
