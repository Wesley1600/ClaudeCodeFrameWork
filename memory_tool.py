"""
Persistent Memory Tool for Claude

This module provides a persistent memory system that can store and retrieve
information across sessions. It supports:
- CRUD operations (Create, Read, Update, Delete)
- Vector-based semantic search
- Multiple memory types (facts, summaries, models, embeddings)
- Automatic indexing and retrieval

Example usage:
    >>> from memory_tool import MemoryTool
    >>>
    >>> memory = MemoryTool()
    >>>
    >>> # Store a fact
    >>> memory.create("user_preference", "The user prefers concise explanations",
    ...               memory_type="fact")
    >>>
    >>> # Store a model checkpoint
    >>> memory.create("analogy_model_v1", model_state_dict,
    ...               memory_type="model", metadata={"epoch": 200})
    >>>
    >>> # Search for relevant memories
    >>> results = memory.search("What does the user like?", k=3)
    >>>
    >>> # Retrieve specific memory
    >>> fact = memory.read("user_preference")
"""

import os
import json
import pickle
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, asdict
import torch
import torch.nn.functional as F


# Memory storage directory
MEMORY_DIR = Path(".memory")
FACTS_DIR = MEMORY_DIR / "facts"
SUMMARIES_DIR = MEMORY_DIR / "summaries"
MODELS_DIR = MEMORY_DIR / "models"
EMBEDDINGS_DIR = MEMORY_DIR / "embeddings"
INDEX_FILE = MEMORY_DIR / "index.json"


@dataclass
class MemoryEntry:
    """A single memory entry with metadata."""
    key: str
    content: Any
    memory_type: str  # "fact", "summary", "model", "embedding", "vector"
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]
    embedding: Optional[torch.Tensor] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (without embedding tensor for JSON serialization)."""
        d = asdict(self)
        d.pop('embedding', None)  # Remove embedding from dict
        return d


class MemoryTool:
    """
    Persistent memory system with vector-based semantic retrieval.

    Features:
    - File-based persistence in .memory/ directory
    - Automatic indexing with timestamps
    - Vector embeddings for semantic search
    - Support for multiple data types (text, tensors, models)
    - CRUD operations with metadata support

    Memory Types:
    - fact: Simple key-value facts (text)
    - summary: Task summaries and session notes
    - model: Trained model weights and state dicts
    - embedding: Vector representations and relation axes
    - vector: Generic tensor data
    """

    def __init__(self, memory_dir: Optional[Path] = None, verbose: bool = True):
        """
        Initialize the memory tool.

        Args:
            memory_dir: Custom memory directory (default: .memory/)
            verbose: Print status messages
        """
        self.memory_dir = memory_dir or MEMORY_DIR
        self.verbose = verbose
        self.index: Dict[str, Dict[str, Any]] = {}

        # Initialize directory structure
        self._init_directories()

        # Load existing index
        self._load_index()

        if self.verbose:
            print(f"✓ MemoryTool initialized with {len(self.index)} memories")

    def _init_directories(self):
        """Create memory directory structure."""
        for directory in [FACTS_DIR, SUMMARIES_DIR, MODELS_DIR, EMBEDDINGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_index(self):
        """Load memory index from disk."""
        if INDEX_FILE.exists():
            try:
                with open(INDEX_FILE, 'r') as f:
                    self.index = json.load(f)
                if self.verbose:
                    print(f"✓ Loaded memory index with {len(self.index)} entries")
            except json.JSONDecodeError as e:
                if self.verbose:
                    print(f"⚠ Warning: Could not load index file: {e}")
                self.index = {}
        else:
            self.index = {}

    def _save_index(self):
        """Save memory index to disk."""
        with open(INDEX_FILE, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _get_directory(self, memory_type: str) -> Path:
        """Get the appropriate directory for a memory type."""
        type_map = {
            "fact": FACTS_DIR,
            "summary": SUMMARIES_DIR,
            "model": MODELS_DIR,
            "embedding": EMBEDDINGS_DIR,
            "vector": EMBEDDINGS_DIR,
        }
        return type_map.get(memory_type, FACTS_DIR)

    def _get_file_path(self, key: str, memory_type: str) -> Path:
        """Get the file path for a memory entry."""
        directory = self._get_directory(memory_type)

        # Use appropriate extension based on type
        if memory_type in ["model", "embedding", "vector"]:
            ext = ".pt"  # PyTorch tensor format
        elif memory_type == "summary":
            ext = ".txt"
        else:
            ext = ".json"

        # Sanitize key for filename
        safe_key = "".join(c if c.isalnum() or c in "._-" else "_" for c in key)
        return directory / f"{safe_key}{ext}"

    def _compute_embedding(self, text: str) -> torch.Tensor:
        """
        Compute a simple embedding for text-based semantic search.

        For production use, replace this with a proper embedding model
        (e.g., sentence-transformers, OpenAI embeddings, etc.)

        Current implementation: Simple character-based hashing to vectors
        (placeholder for demonstration)
        """
        # Simple hash-based embedding (replace with real embeddings in production)
        # This is just a placeholder that creates a 128-dim vector from the text
        hash_obj = hashlib.sha512(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()

        # Convert to float vector
        embedding = torch.tensor([b / 255.0 for b in hash_bytes[:128]], dtype=torch.float32)

        # Normalize
        embedding = F.normalize(embedding.unsqueeze(0), dim=-1).squeeze(0)

        return embedding

    def create(
        self,
        key: str,
        content: Any,
        memory_type: str = "fact",
        metadata: Optional[Dict[str, Any]] = None,
        compute_embedding: bool = True
    ) -> bool:
        """
        Create a new memory entry.

        Args:
            key: Unique identifier for the memory
            content: The content to store (text, dict, tensor, model state, etc.)
            memory_type: Type of memory ("fact", "summary", "model", "embedding", "vector")
            metadata: Optional metadata dictionary
            compute_embedding: Whether to compute semantic embedding for search

        Returns:
            True if successful, False otherwise
        """
        if key in self.index:
            if self.verbose:
                print(f"⚠ Warning: Memory '{key}' already exists. Use update() to modify.")
            return False

        timestamp = datetime.now().isoformat()
        metadata = metadata or {}

        # Compute embedding for text content if needed
        embedding = None
        if compute_embedding and isinstance(content, str):
            embedding = self._compute_embedding(content)

        # Save content to file
        file_path = self._get_file_path(key, memory_type)

        try:
            if memory_type in ["model", "embedding", "vector"]:
                # Save PyTorch tensors/models
                torch.save(content, file_path)
            elif memory_type == "summary":
                # Save as text file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(content))
            else:
                # Save as JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2)

            # Save embedding if exists
            if embedding is not None:
                emb_path = EMBEDDINGS_DIR / f"{key}_embedding.pt"
                torch.save(embedding, emb_path)

            # Update index
            self.index[key] = {
                "key": key,
                "memory_type": memory_type,
                "file_path": str(file_path),
                "created_at": timestamp,
                "updated_at": timestamp,
                "metadata": metadata,
                "has_embedding": embedding is not None,
            }

            self._save_index()

            if self.verbose:
                print(f"✓ Created memory '{key}' ({memory_type})")

            return True

        except Exception as e:
            if self.verbose:
                print(f"✗ Error creating memory '{key}': {e}")
            return False

    def read(self, key: str) -> Optional[Any]:
        """
        Read a memory entry by key.

        Args:
            key: The memory key to retrieve

        Returns:
            The memory content, or None if not found
        """
        if key not in self.index:
            if self.verbose:
                print(f"⚠ Memory '{key}' not found")
            return None

        entry = self.index[key]
        file_path = Path(entry["file_path"])
        memory_type = entry["memory_type"]

        try:
            if memory_type in ["model", "embedding", "vector"]:
                content = torch.load(file_path)
            elif memory_type == "summary":
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)

            if self.verbose:
                print(f"✓ Retrieved memory '{key}'")

            return content

        except Exception as e:
            if self.verbose:
                print(f"✗ Error reading memory '{key}': {e}")
            return None

    def update(
        self,
        key: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        compute_embedding: bool = True
    ) -> bool:
        """
        Update an existing memory entry.

        Args:
            key: The memory key to update
            content: New content
            metadata: Optional metadata to merge/update
            compute_embedding: Whether to recompute semantic embedding

        Returns:
            True if successful, False otherwise
        """
        if key not in self.index:
            if self.verbose:
                print(f"⚠ Memory '{key}' not found. Use create() to add new memories.")
            return False

        entry = self.index[key]
        memory_type = entry["memory_type"]
        file_path = Path(entry["file_path"])

        try:
            # Save updated content
            if memory_type in ["model", "embedding", "vector"]:
                torch.save(content, file_path)
            elif memory_type == "summary":
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(content))
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2)

            # Update embedding if needed
            if compute_embedding and isinstance(content, str):
                embedding = self._compute_embedding(content)
                emb_path = EMBEDDINGS_DIR / f"{key}_embedding.pt"
                torch.save(embedding, emb_path)
                entry["has_embedding"] = True

            # Update metadata
            entry["updated_at"] = datetime.now().isoformat()
            if metadata:
                entry["metadata"].update(metadata)

            self._save_index()

            if self.verbose:
                print(f"✓ Updated memory '{key}'")

            return True

        except Exception as e:
            if self.verbose:
                print(f"✗ Error updating memory '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete a memory entry.

        Args:
            key: The memory key to delete

        Returns:
            True if successful, False otherwise
        """
        if key not in self.index:
            if self.verbose:
                print(f"⚠ Memory '{key}' not found")
            return False

        entry = self.index[key]
        file_path = Path(entry["file_path"])

        try:
            # Delete main file
            if file_path.exists():
                file_path.unlink()

            # Delete embedding file if exists
            emb_path = EMBEDDINGS_DIR / f"{key}_embedding.pt"
            if emb_path.exists():
                emb_path.unlink()

            # Remove from index
            del self.index[key]
            self._save_index()

            if self.verbose:
                print(f"✓ Deleted memory '{key}'")

            return True

        except Exception as e:
            if self.verbose:
                print(f"✗ Error deleting memory '{key}': {e}")
            return False

    def list(self, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all memory entries, optionally filtered by type.

        Args:
            memory_type: Optional type filter

        Returns:
            List of memory entry dictionaries
        """
        entries = list(self.index.values())

        if memory_type:
            entries = [e for e in entries if e["memory_type"] == memory_type]

        # Sort by updated timestamp (most recent first)
        entries.sort(key=lambda e: e["updated_at"], reverse=True)

        return entries

    def search(
        self,
        query: str,
        k: int = 5,
        memory_type: Optional[str] = None,
        threshold: float = 0.0
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for memories using semantic similarity.

        Args:
            query: Search query text
            k: Number of top results to return
            memory_type: Optional type filter
            threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            List of (key, score, metadata) tuples sorted by relevance
        """
        # Compute query embedding
        query_emb = self._compute_embedding(query)

        # Collect all memories with embeddings
        results = []

        for key, entry in self.index.items():
            # Filter by type if specified
            if memory_type and entry["memory_type"] != memory_type:
                continue

            # Skip if no embedding
            if not entry.get("has_embedding", False):
                continue

            # Load embedding
            emb_path = EMBEDDINGS_DIR / f"{key}_embedding.pt"
            if not emb_path.exists():
                continue

            try:
                memory_emb = torch.load(emb_path)

                # Compute cosine similarity
                similarity = F.cosine_similarity(
                    query_emb.unsqueeze(0),
                    memory_emb.unsqueeze(0),
                    dim=-1
                ).item()

                if similarity >= threshold:
                    results.append((key, similarity, entry))

            except Exception as e:
                if self.verbose:
                    print(f"⚠ Warning: Could not load embedding for '{key}': {e}")
                continue

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        # Return top k
        return results[:k]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory system statistics.

        Returns:
            Dictionary with statistics about stored memories
        """
        total = len(self.index)
        by_type = {}

        for entry in self.index.values():
            mem_type = entry["memory_type"]
            by_type[mem_type] = by_type.get(mem_type, 0) + 1

        with_embeddings = sum(1 for e in self.index.values() if e.get("has_embedding", False))

        # Calculate total storage size
        total_size = 0
        for entry in self.index.values():
            file_path = Path(entry["file_path"])
            if file_path.exists():
                total_size += file_path.stat().st_size

        return {
            "total_memories": total,
            "by_type": by_type,
            "with_embeddings": with_embeddings,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }

    def clear_all(self, confirm: bool = False) -> bool:
        """
        Clear all memories (DANGEROUS - requires confirmation).

        Args:
            confirm: Must be True to actually delete

        Returns:
            True if cleared, False if not confirmed
        """
        if not confirm:
            if self.verbose:
                print("⚠ Clear operation requires confirm=True")
            return False

        # Delete all files
        for entry in self.index.values():
            file_path = Path(entry["file_path"])
            if file_path.exists():
                file_path.unlink()

            emb_path = EMBEDDINGS_DIR / f"{entry['key']}_embedding.pt"
            if emb_path.exists():
                emb_path.unlink()

        # Clear index
        self.index = {}
        self._save_index()

        if self.verbose:
            print("✓ All memories cleared")

        return True


# Convenience functions for common operations
def create_fact(key: str, content: str, metadata: Optional[Dict] = None) -> bool:
    """Create a fact memory."""
    memory = MemoryTool(verbose=False)
    return memory.create(key, content, memory_type="fact", metadata=metadata)


def create_summary(key: str, content: str, metadata: Optional[Dict] = None) -> bool:
    """Create a summary memory."""
    memory = MemoryTool(verbose=False)
    return memory.create(key, content, memory_type="summary", metadata=metadata)


def save_model(key: str, state_dict: Dict, metadata: Optional[Dict] = None) -> bool:
    """Save a model checkpoint."""
    memory = MemoryTool(verbose=False)
    return memory.create(key, state_dict, memory_type="model", metadata=metadata)


def load_model(key: str) -> Optional[Dict]:
    """Load a model checkpoint."""
    memory = MemoryTool(verbose=False)
    return memory.read(key)


def search_memories(query: str, k: int = 5) -> List[Tuple[str, float, Dict]]:
    """Search memories by semantic similarity."""
    memory = MemoryTool(verbose=False)
    return memory.search(query, k=k)


if __name__ == "__main__":
    # Demo usage
    print("=" * 60)
    print("Memory Tool Demo")
    print("=" * 60)

    # Initialize
    memory = MemoryTool()

    # Create some facts
    print("\n--- Creating Facts ---")
    memory.create(
        "user_preference_concise",
        "The user prefers concise, technical explanations without unnecessary elaboration.",
        memory_type="fact",
        metadata={"source": "user_feedback", "importance": "high"}
    )

    memory.create(
        "project_goal",
        "Building a UMAP-based universal analogy engine for semantic relationships.",
        memory_type="fact",
        metadata={"category": "project"}
    )

    memory.create(
        "training_config",
        "Optimal training uses 300 epochs, learning rate 1e-3, and align_weight=1.0",
        memory_type="fact",
        metadata={"category": "hyperparameters"}
    )

    # Create a summary
    print("\n--- Creating Summary ---")
    memory.create(
        "session_2025_01_15",
        "Fixed critical metric mismatch bug in analogy finding. Changed from cosine to Euclidean distance. Added cluster caching for 10x speedup.",
        memory_type="summary",
        metadata={"date": "2025-01-15", "session_type": "debugging"}
    )

    # List memories
    print("\n--- All Memories ---")
    for entry in memory.list():
        print(f"  • {entry['key']} ({entry['memory_type']}) - {entry['updated_at']}")

    # Search
    print("\n--- Semantic Search: 'user preferences' ---")
    results = memory.search("What does the user prefer?", k=3)
    for key, score, entry in results:
        print(f"  {score:.3f} - {key}")
        content = memory.read(key)
        print(f"         {content[:80]}...")

    # Statistics
    print("\n--- Statistics ---")
    stats = memory.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 60)
