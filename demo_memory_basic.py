"""
Basic Memory Tool Demo (No PyTorch Required)

This demo shows basic CRUD operations without requiring PyTorch.
For full functionality including semantic search and model persistence,
see memory_tool.py (requires PyTorch).
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Simple in-memory demonstration
class SimpleMemoryDemo:
    """Simplified memory demo without external dependencies."""

    def __init__(self):
        self.memories = {}
        print("✓ Simple Memory Demo initialized")

    def create(self, key: str, content: str, metadata: dict = None):
        """Create a memory."""
        if key in self.memories:
            print(f"⚠ Memory '{key}' already exists")
            return False

        self.memories[key] = {
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
        }
        print(f"✓ Created memory '{key}'")
        return True

    def read(self, key: str):
        """Read a memory."""
        if key not in self.memories:
            print(f"⚠ Memory '{key}' not found")
            return None

        return self.memories[key]["content"]

    def update(self, key: str, content: str):
        """Update a memory."""
        if key not in self.memories:
            print(f"⚠ Memory '{key}' not found")
            return False

        self.memories[key]["content"] = content
        self.memories[key]["updated_at"] = datetime.now().isoformat()
        print(f"✓ Updated memory '{key}'")
        return True

    def delete(self, key: str):
        """Delete a memory."""
        if key not in self.memories:
            print(f"⚠ Memory '{key}' not found")
            return False

        del self.memories[key]
        print(f"✓ Deleted memory '{key}'")
        return True

    def list_all(self):
        """List all memories."""
        return list(self.memories.keys())

    def search(self, query: str):
        """Simple keyword search."""
        results = []
        query_lower = query.lower()

        for key, data in self.memories.items():
            content = data["content"].lower()
            if query_lower in content or query_lower in key.lower():
                results.append((key, data["content"]))

        return results


def main():
    print("=" * 70)
    print("Memory Tool - Basic Demo (No Dependencies)")
    print("=" * 70)

    demo = SimpleMemoryDemo()

    # Demo 1: Create memories
    print("\n--- Creating Memories ---")
    demo.create(
        "user_preference",
        "The user prefers concise technical explanations",
        metadata={"category": "preference"}
    )
    demo.create(
        "project_goal",
        "Build a UMAP-based universal analogy engine",
        metadata={"category": "project"}
    )
    demo.create(
        "hyperparameter_lr",
        "Learning rate 1e-3 works best for this project",
        metadata={"category": "config"}
    )

    # Demo 2: Read memories
    print("\n--- Reading Memories ---")
    pref = demo.read("user_preference")
    print(f"User preference: {pref}")

    goal = demo.read("project_goal")
    print(f"Project goal: {goal}")

    # Demo 3: Update
    print("\n--- Updating Memory ---")
    demo.update(
        "project_goal",
        "Build a production-ready UMAP analogy engine with persistent memory"
    )
    updated_goal = demo.read("project_goal")
    print(f"Updated goal: {updated_goal}")

    # Demo 4: Search
    print("\n--- Searching Memories ---")
    results = demo.search("user")
    print(f"Search for 'user':")
    for key, content in results:
        print(f"  - {key}: {content}")

    results = demo.search("UMAP")
    print(f"\nSearch for 'UMAP':")
    for key, content in results:
        print(f"  - {key}: {content}")

    # Demo 5: List all
    print("\n--- All Memories ---")
    all_keys = demo.list_all()
    print(f"Total memories: {len(all_keys)}")
    for key in all_keys:
        print(f"  - {key}")

    # Demo 6: Delete
    print("\n--- Deleting Memory ---")
    demo.delete("hyperparameter_lr")
    remaining = demo.list_all()
    print(f"Remaining memories: {remaining}")

    print("\n" + "=" * 70)
    print("Demo complete!")
    print("\nFor full functionality including:")
    print("  - Vector-based semantic search")
    print("  - Model persistence (PyTorch)")
    print("  - Integration with UMAP analogy engine")
    print("  - Session continuity")
    print("\nInstall dependencies: pip install torch numpy")
    print("Then see: memory_tool.py and memory_integration.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
