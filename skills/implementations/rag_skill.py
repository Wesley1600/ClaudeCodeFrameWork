"""
RAG (Retrieval-Augmented Generation) Pipeline Skill

This skill implements a complete RAG pipeline:
1. Document loading and chunking
2. Vector embedding
3. Semantic search/retrieval
4. Context assembly
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import math
import random

from ..base_skill import BaseSkill, SkillContext, SkillMetadata


logger = logging.getLogger(__name__)


@dataclass
class Document:
    """A document with metadata"""
    content: str
    metadata: Dict[str, Any]
    doc_id: Optional[str] = None
    embedding: Optional[List[float]] = None


@dataclass
class RetrievalResult:
    """Result from retrieval operation"""
    documents: List[Document]
    query: str
    scores: List[float]
    total_retrieved: int


class RAGPipelineSkill(BaseSkill):
    """
    Retrieval-Augmented Generation Pipeline.

    Performs semantic retrieval over a document collection to gather
    relevant context for downstream tasks (e.g., summarization, Q&A).

    Configuration:
        documents: List of documents to index (or path to document store)
        embedding_dim: Dimension of embeddings (default: 384)
        chunk_size: Max tokens per chunk (default: 512)
        chunk_overlap: Overlap between chunks (default: 50)
        top_k: Number of documents to retrieve (default: 5)
        similarity_threshold: Minimum similarity score (default: 0.5)
    """

    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="rag_pipeline",
            description="Retrieval-Augmented Generation pipeline for context gathering",
            version="1.0.0",
            author="Skill Framework",
            input_schema={
                "query": "str - Search query",
                "documents": "Optional[List[str]] - Documents to search"
            },
            output_schema={
                "documents": "List[Document] - Retrieved documents",
                "context": "str - Assembled context text",
                "scores": "List[float] - Relevance scores"
            },
            tags=["rag", "retrieval", "embedding", "search"]
        )

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        # Configuration
        self.embedding_dim = self.config.get("embedding_dim", 384)
        self.chunk_size = self.config.get("chunk_size", 512)
        self.chunk_overlap = self.config.get("chunk_overlap", 50)
        self.top_k = self.config.get("top_k", 5)
        self.similarity_threshold = self.config.get("similarity_threshold", 0.5)

        # Document store
        self.documents: List[Document] = []
        self.index_built = False

        # Load initial documents if provided
        initial_docs = self.config.get("documents", [])
        if initial_docs:
            self._load_documents(initial_docs)

    def _load_documents(self, documents: List[str]) -> None:
        """Load and chunk documents"""
        logger.info(f"Loading {len(documents)} documents")

        for idx, doc_text in enumerate(documents):
            # Simple chunking (split by sentences/paragraphs)
            chunks = self._chunk_text(doc_text)

            for chunk_idx, chunk in enumerate(chunks):
                doc = Document(
                    content=chunk,
                    metadata={
                        "source_doc": idx,
                        "chunk_id": chunk_idx,
                        "total_chunks": len(chunks)
                    },
                    doc_id=f"doc_{idx}_chunk_{chunk_idx}"
                )
                self.documents.append(doc)

        logger.info(f"Created {len(self.documents)} chunks")

    def _chunk_text(self, text: str) -> List[str]:
        """
        Simple text chunking strategy.

        In production, use more sophisticated methods:
        - Sentence boundary detection
        - Paragraph-aware chunking
        - Sliding window with overlap
        """
        # Simple split by periods (naive approach)
        sentences = text.split('. ')

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence.split())

            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
                # Keep overlap
                overlap_sentences = current_chunk[-2:] if len(current_chunk) > 2 else current_chunk
                current_chunk = overlap_sentences
                current_length = sum(len(s.split()) for s in current_chunk)

            current_chunk.append(sentence)
            current_length += sentence_length

        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')

        return chunks

    def _build_index(self) -> None:
        """Build embeddings for all documents"""
        if self.index_built:
            return

        logger.info("Building document index...")

        for doc in self.documents:
            # Simple embedding: TF-IDF-like bag of words (mock)
            # In production, use: sentence-transformers, OpenAI embeddings, etc.
            doc.embedding = self._embed_text(doc.content)

        self.index_built = True
        logger.info("Index built successfully")

    def _embed_text(self, text: str) -> List[float]:
        """
        Create embedding for text.

        This is a MOCK implementation using random embeddings.
        In production, replace with real embeddings:
        - sentence-transformers (e.g., all-MiniLM-L6-v2)
        - OpenAI embeddings
        - Custom fine-tuned models
        """
        # Simple hash-based mock embedding (deterministic)
        random.seed(hash(text) % (2**32))
        embedding = [random.gauss(0, 1) for _ in range(self.embedding_dim)]

        # Normalize
        norm = math.sqrt(sum(x*x for x in embedding)) + 1e-8
        embedding = [x / norm for x in embedding]

        return embedding

    def _retrieve(self, query: str) -> RetrievalResult:
        """Retrieve relevant documents for query"""
        # Ensure index is built
        self._build_index()

        # Embed query
        query_embedding = self._embed_text(query)

        # Compute similarities (dot product)
        similarities = []
        for doc in self.documents:
            sim = sum(q * d for q, d in zip(query_embedding, doc.embedding))
            similarities.append(sim)

        # Get top-k indices
        indexed_sims = list(enumerate(similarities))
        indexed_sims.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in indexed_sims[:self.top_k]]

        # Filter by threshold
        retrieved_docs = []
        scores = []

        for idx in top_indices:
            score = similarities[idx]
            if score >= self.similarity_threshold:
                retrieved_docs.append(self.documents[idx])
                scores.append(float(score))

        logger.info(f"Retrieved {len(retrieved_docs)} documents (threshold={self.similarity_threshold})")

        return RetrievalResult(
            documents=retrieved_docs,
            query=query,
            scores=scores,
            total_retrieved=len(retrieved_docs)
        )

    def execute(self, context: SkillContext, **kwargs) -> Dict[str, Any]:
        """
        Execute RAG pipeline.

        Args:
            context: Skill context
            **kwargs:
                query: Search query (required)
                documents: Optional list of documents to add

        Returns:
            Dict with:
                - documents: List of retrieved documents
                - context: Assembled context text
                - scores: Relevance scores
                - metadata: Retrieval metadata
        """
        # Get query
        query = kwargs.get("query")
        if not query:
            # Try to get from context
            query = context.shared_state.get("query")

        if not query:
            raise ValueError("No query provided. Pass 'query' parameter or set in context.")

        # Add any new documents
        new_documents = kwargs.get("documents")

        # If not in kwargs, check shared_state (for YAML chains using initial_data)
        if not new_documents:
            new_documents = context.shared_state.get("documents")

        if new_documents:
            self._load_documents(new_documents)
            self.index_built = False  # Rebuild index

        # Perform retrieval
        result = self._retrieve(query)

        # Assemble context text
        context_text = "\n\n---\n\n".join([
            f"[Document {i+1}] (score: {result.scores[i]:.3f})\n{doc.content}"
            for i, doc in enumerate(result.documents)
        ])

        # Return structured result
        return {
            "documents": [
                {
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "doc_id": doc.doc_id
                }
                for doc in result.documents
            ],
            "context": context_text,
            "scores": result.scores,
            "metadata": {
                "query": query,
                "total_retrieved": result.total_retrieved,
                "total_indexed": len(self.documents),
                "top_k": self.top_k,
                "threshold": self.similarity_threshold
            }
        }

    def validate_inputs(self, context: SkillContext, **kwargs) -> bool:
        """Validate that we have a query"""
        query = kwargs.get("query") or context.shared_state.get("query")
        return query is not None
