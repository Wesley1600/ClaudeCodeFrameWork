"""
Memory Tool Integration with UMAP Analogy Engine

This module demonstrates how to integrate the persistent memory system
with the UMAP analogy engine to:
1. Save trained models and relation axes
2. Store experiment results and hyperparameters
3. Build a knowledge base of analogy patterns
4. Enable continuity across training sessions

Example:
    >>> from memory_integration import AnalogyMemoryManager
    >>>
    >>> # Create manager
    >>> manager = AnalogyMemoryManager()
    >>>
    >>> # Save a trained model
    >>> manager.save_trained_model(model, Z, axes, "model_v1",
    ...                            metadata={"epochs": 300, "accuracy": 0.87})
    >>>
    >>> # Load it later
    >>> model_data = manager.load_trained_model("model_v1")
    >>>
    >>> # Search for similar experiments
    >>> results = manager.search_experiments("gender relation analogy")
"""

import torch
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from memory_tool import MemoryTool


class AnalogyMemoryManager:
    """
    High-level interface for managing UMAP analogy engine memories.

    This class provides convenient methods for:
    - Saving/loading trained models with relation axes
    - Tracking experiment configurations and results
    - Building a searchable knowledge base of analogy patterns
    - Maintaining session history and task summaries
    """

    def __init__(self, memory_dir: Optional[Path] = None, verbose: bool = True):
        """
        Initialize the analogy memory manager.

        Args:
            memory_dir: Custom memory directory (default: .memory/)
            verbose: Print status messages
        """
        self.memory = MemoryTool(memory_dir=memory_dir, verbose=verbose)
        self.verbose = verbose

    def save_trained_model(
        self,
        model_state: Dict[str, Any],
        embeddings: torch.Tensor,
        relation_axes: List[Optional[Dict]],
        model_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a complete trained model with embeddings and relation axes.

        Args:
            model_state: Model state dictionary (model.state_dict())
            embeddings: Low-dimensional embeddings tensor (N, d)
            relation_axes: List of relation axis dictionaries
            model_name: Unique name for this model
            metadata: Additional metadata (epochs, hyperparameters, metrics, etc.)

        Returns:
            True if successful
        """
        metadata = metadata or {}
        metadata.update({
            "saved_at": datetime.now().isoformat(),
            "embedding_shape": list(embeddings.shape),
            "num_relations": len(relation_axes),
        })

        # Create a bundle with all components
        model_bundle = {
            "model_state": model_state,
            "embeddings": embeddings,
            "relation_axes": relation_axes,
            "metadata": metadata,
        }

        success = self.memory.create(
            f"model_{model_name}",
            model_bundle,
            memory_type="model",
            metadata=metadata,
            compute_embedding=False
        )

        if success and self.verbose:
            print(f"✓ Saved model '{model_name}' with {len(relation_axes)} relations")

        return success

    def load_trained_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a previously saved model bundle.

        Args:
            model_name: Name of the model to load

        Returns:
            Dictionary with keys: model_state, embeddings, relation_axes, metadata
            or None if not found
        """
        model_bundle = self.memory.read(f"model_{model_name}")

        if model_bundle and self.verbose:
            metadata = model_bundle.get("metadata", {})
            print(f"✓ Loaded model '{model_name}' (saved: {metadata.get('saved_at', 'unknown')})")

        return model_bundle

    def save_relation_axes(
        self,
        relation_axes: List[Optional[Dict]],
        relation_names: List[str],
        axes_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save relation axes separately (useful for sharing across models).

        Args:
            relation_axes: List of relation axis dictionaries
            relation_names: Names of the relations
            axes_name: Unique name for this axis set
            metadata: Additional metadata

        Returns:
            True if successful
        """
        metadata = metadata or {}
        metadata.update({
            "relation_names": relation_names,
            "num_relations": len(relation_axes),
        })

        axes_bundle = {
            "axes": relation_axes,
            "names": relation_names,
            "metadata": metadata,
        }

        return self.memory.create(
            f"axes_{axes_name}",
            axes_bundle,
            memory_type="embedding",
            metadata=metadata,
            compute_embedding=False
        )

    def save_experiment(
        self,
        experiment_name: str,
        config: Dict[str, Any],
        results: Dict[str, Any],
        description: str = ""
    ) -> bool:
        """
        Save an experiment configuration and results.

        Args:
            experiment_name: Unique experiment identifier
            config: Hyperparameters and configuration
            results: Results and metrics
            description: Text description of the experiment

        Returns:
            True if successful
        """
        experiment_data = {
            "name": experiment_name,
            "description": description,
            "config": config,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

        # Save as fact (will be searchable)
        return self.memory.create(
            f"experiment_{experiment_name}",
            experiment_data,
            memory_type="fact",
            metadata={"category": "experiment", "date": experiment_data["timestamp"]},
            compute_embedding=True  # Enable semantic search
        )

    def save_session_summary(
        self,
        session_id: str,
        summary: str,
        tasks_completed: List[str],
        key_findings: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a session summary for continuity across conversations.

        Args:
            session_id: Unique session identifier (e.g., date or UUID)
            summary: High-level summary of the session
            tasks_completed: List of completed tasks
            key_findings: Important discoveries or insights
            metadata: Additional session metadata

        Returns:
            True if successful
        """
        metadata = metadata or {}
        metadata.update({
            "tasks_count": len(tasks_completed),
            "findings_count": len(key_findings),
        })

        session_content = f"""
Session Summary: {session_id}
================================

{summary}

Tasks Completed:
{chr(10).join(f"- {task}" for task in tasks_completed)}

Key Findings:
{chr(10).join(f"- {finding}" for finding in key_findings)}
        """.strip()

        return self.memory.create(
            f"session_{session_id}",
            session_content,
            memory_type="summary",
            metadata=metadata,
            compute_embedding=True
        )

    def save_analogy_pattern(
        self,
        pattern_name: str,
        description: str,
        examples: List[Tuple[str, str, str, str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a discovered analogy pattern.

        Args:
            pattern_name: Name of the pattern (e.g., "gender_relation")
            description: Description of the pattern
            examples: List of (word_a, word_b, word_c, word_d) tuples
                     representing "a:b :: c:d" analogies
            metadata: Additional metadata

        Returns:
            True if successful
        """
        pattern_content = f"""
Analogy Pattern: {pattern_name}
================================

{description}

Examples:
{chr(10).join(f"- {a}:{b} :: {c}:{d}" for a, b, c, d in examples)}
        """.strip()

        metadata = metadata or {}
        metadata.update({
            "pattern_type": "analogy",
            "num_examples": len(examples),
        })

        return self.memory.create(
            f"pattern_{pattern_name}",
            pattern_content,
            memory_type="fact",
            metadata=metadata,
            compute_embedding=True
        )

    def search_experiments(
        self,
        query: str,
        k: int = 5
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for experiments by semantic similarity.

        Args:
            query: Search query (e.g., "gender relation with high accuracy")
            k: Number of results to return

        Returns:
            List of (key, score, metadata) tuples
        """
        return self.memory.search(query, k=k, memory_type="fact")

    def search_sessions(
        self,
        query: str,
        k: int = 5
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search past sessions by content.

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of (key, score, metadata) tuples
        """
        return self.memory.search(query, k=k, memory_type="summary")

    def get_recent_sessions(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the N most recent sessions.

        Args:
            n: Number of sessions to retrieve

        Returns:
            List of session metadata dictionaries
        """
        sessions = self.memory.list(memory_type="summary")
        return sessions[:n]

    def get_all_models(self) -> List[Dict[str, Any]]:
        """
        List all saved models.

        Returns:
            List of model metadata dictionaries
        """
        return self.memory.list(memory_type="model")

    def compare_models(
        self,
        model_names: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare metadata and performance of multiple models.

        Args:
            model_names: List of model names to compare

        Returns:
            Dictionary mapping model names to their metadata
        """
        comparison = {}

        for name in model_names:
            bundle = self.load_trained_model(name)
            if bundle:
                comparison[name] = bundle.get("metadata", {})

        return comparison

    def get_continuity_summary(self) -> str:
        """
        Generate a summary of recent activity for session continuity.

        Returns:
            Formatted text summary
        """
        # Get recent sessions
        recent_sessions = self.get_recent_sessions(n=3)

        # Get statistics
        stats = self.memory.get_stats()

        summary_parts = [
            "=== Memory Continuity Summary ===",
            f"\nTotal Memories: {stats['total_memories']}",
            f"Storage: {stats['total_size_mb']} MB",
            "\nMemories by Type:",
        ]

        for mem_type, count in stats["by_type"].items():
            summary_parts.append(f"  - {mem_type}: {count}")

        if recent_sessions:
            summary_parts.append("\nRecent Sessions:")
            for session in recent_sessions:
                summary_parts.append(
                    f"  - {session['key']} ({session['updated_at']})"
                )

        return "\n".join(summary_parts)


def demo_integration():
    """Demonstrate memory integration with UMAP analogy engine."""
    print("=" * 70)
    print("Memory Integration Demo - UMAP Analogy Engine")
    print("=" * 70)

    # Initialize manager
    manager = AnalogyMemoryManager()

    # Example 1: Save an experiment configuration
    print("\n--- Saving Experiment ---")
    manager.save_experiment(
        experiment_name="gender_analogy_v1",
        config={
            "n_neighbors": 15,
            "min_dist": 0.1,
            "d_low": 50,
            "epochs": 300,
            "align_weight": 1.0,
            "relations": ["gender", "plural"],
        },
        results={
            "accuracy": 0.87,
            "final_loss": 0.123,
            "training_time_minutes": 12.5,
        },
        description="First attempt at gender and plural analogies with 50-dim embeddings"
    )

    # Example 2: Save analogy patterns
    print("\n--- Saving Analogy Patterns ---")
    manager.save_analogy_pattern(
        pattern_name="gender_relations",
        description="Gender transformation patterns in English",
        examples=[
            ("king", "queen", "man", "woman"),
            ("king", "queen", "boy", "girl"),
            ("prince", "princess", "actor", "actress"),
        ],
        metadata={"language": "english", "relation_type": "gender"}
    )

    # Example 3: Save a session summary
    print("\n--- Saving Session Summary ---")
    manager.save_session_summary(
        session_id="2025_01_15_debugging",
        summary="Fixed critical metric mismatch bug and optimized training performance",
        tasks_completed=[
            "Identified cosine vs Euclidean distance bug in analogy finding",
            "Implemented cluster caching for 10x speedup",
            "Added comprehensive documentation to all functions",
            "Validated on synthetic dataset",
        ],
        key_findings=[
            "Cosine similarity doesn't work for absolute position analogies",
            "Cluster caching dramatically improves training speed",
            "Auto-alignment calibration should run before training, not during",
        ],
        metadata={"duration_hours": 3.5, "bugs_fixed": 10}
    )

    # Example 4: Save a mock trained model
    print("\n--- Saving Mock Model ---")
    mock_model_state = {"encoder.weight": torch.randn(100, 50)}
    mock_embeddings = torch.randn(1000, 50)
    mock_axes = [
        {"centroids": torch.randn(1, 50), "mean_direction": torch.randn(50), "scale": 0.5},
        {"centroids": torch.randn(1, 50), "mean_direction": torch.randn(50), "scale": 0.3},
    ]

    manager.save_trained_model(
        model_state=mock_model_state,
        embeddings=mock_embeddings,
        relation_axes=mock_axes,
        model_name="demo_v1",
        metadata={
            "epochs": 300,
            "accuracy": 0.87,
            "relations": ["gender", "plural"],
        }
    )

    # Example 5: Search for experiments
    print("\n--- Searching Experiments ---")
    results = manager.search_experiments("gender analogy accuracy", k=3)
    for key, score, metadata in results:
        print(f"  {score:.3f} - {key}")

    # Example 6: Get continuity summary
    print("\n--- Continuity Summary ---")
    print(manager.get_continuity_summary())

    # Example 7: List all models
    print("\n--- Available Models ---")
    models = manager.get_all_models()
    for model_entry in models:
        print(f"  • {model_entry['key']}")
        print(f"    Updated: {model_entry['updated_at']}")
        print(f"    Metadata: {model_entry['metadata']}")

    print("\n" + "=" * 70)
    print("Demo complete! Memory system is ready for production use.")
    print("=" * 70)


if __name__ == "__main__":
    demo_integration()
