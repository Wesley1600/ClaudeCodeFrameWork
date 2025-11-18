"""
Test suite for the Memory Tool

This script demonstrates and tests all major features of the memory system:
- CRUD operations
- Vector-based semantic search
- Model persistence
- Session continuity
- Integration with UMAP analogy engine

Run with: python test_memory_tool.py
"""

import torch
import shutil
from pathlib import Path
from memory_tool import MemoryTool, create_fact, create_summary, save_model, load_model, search_memories
from memory_integration import AnalogyMemoryManager


def test_basic_crud():
    """Test basic Create, Read, Update, Delete operations."""
    print("\n" + "=" * 70)
    print("TEST 1: Basic CRUD Operations")
    print("=" * 70)

    # Use a temporary test directory
    test_dir = Path(".memory_test")
    memory = MemoryTool(memory_dir=test_dir, verbose=True)

    # CREATE
    print("\n[CREATE] Creating memories...")
    success = memory.create(
        "test_fact_1",
        "The capital of France is Paris",
        memory_type="fact",
        metadata={"category": "geography", "confidence": "high"}
    )
    assert success, "Failed to create fact"

    success = memory.create(
        "test_summary_1",
        "This is a test session where we validated the memory system works correctly.",
        memory_type="summary",
        metadata={"session_date": "2025-01-15"}
    )
    assert success, "Failed to create summary"

    # READ
    print("\n[READ] Reading memories...")
    fact = memory.read("test_fact_1")
    assert fact == "The capital of France is Paris", f"Unexpected fact content: {fact}"
    print(f"✓ Read fact: {fact}")

    summary = memory.read("test_summary_1")
    assert "validated the memory system" in summary, f"Unexpected summary: {summary}"
    print(f"✓ Read summary: {summary[:50]}...")

    # UPDATE
    print("\n[UPDATE] Updating memory...")
    success = memory.update(
        "test_fact_1",
        "The capital of France is Paris, known as the City of Light",
        metadata={"updated": True}
    )
    assert success, "Failed to update fact"

    updated_fact = memory.read("test_fact_1")
    assert "City of Light" in updated_fact, "Update did not persist"
    print(f"✓ Updated fact: {updated_fact}")

    # LIST
    print("\n[LIST] Listing all memories...")
    all_memories = memory.list()
    assert len(all_memories) == 2, f"Expected 2 memories, found {len(all_memories)}"
    print(f"✓ Found {len(all_memories)} memories")

    # DELETE
    print("\n[DELETE] Deleting memory...")
    success = memory.delete("test_fact_1")
    assert success, "Failed to delete fact"

    deleted_fact = memory.read("test_fact_1")
    assert deleted_fact is None, "Deleted fact still exists"
    print("✓ Successfully deleted fact")

    # Cleanup
    shutil.rmtree(test_dir)
    print("\n✓ ALL CRUD TESTS PASSED")


def test_semantic_search():
    """Test vector-based semantic search."""
    print("\n" + "=" * 70)
    print("TEST 2: Semantic Search")
    print("=" * 70)

    test_dir = Path(".memory_test")
    memory = MemoryTool(memory_dir=test_dir, verbose=True)

    # Create diverse facts
    facts = [
        ("capital_france", "The capital of France is Paris, known for the Eiffel Tower"),
        ("capital_germany", "Berlin is the capital of Germany, famous for its history"),
        ("capital_italy", "Rome is the capital of Italy, home to the Colosseum"),
        ("python_lang", "Python is a high-level programming language created by Guido van Rossum"),
        ("javascript_lang", "JavaScript is a programming language commonly used for web development"),
        ("machine_learning", "Machine learning is a subset of AI focused on pattern recognition"),
    ]

    print("\n[CREATE] Creating test facts...")
    for key, content in facts:
        memory.create(key, content, memory_type="fact")

    # Test search queries
    print("\n[SEARCH] Testing semantic queries...")

    # Query 1: Capital cities
    print("\nQuery: 'What is the capital of European countries?'")
    results = memory.search("What is the capital of European countries?", k=3)
    print(f"Found {len(results)} results:")
    for key, score, _ in results:
        content = memory.read(key)
        print(f"  {score:.3f} - {key}: {content[:60]}...")

    # Verify capital-related results rank higher
    top_keys = [key for key, _, _ in results[:3]]
    capital_count = sum(1 for key in top_keys if "capital" in key)
    assert capital_count >= 2, "Search did not prioritize capital-related facts"
    print("✓ Capital-related facts ranked higher")

    # Query 2: Programming languages
    print("\nQuery: 'programming languages for developers'")
    results = memory.search("programming languages for developers", k=3)
    print(f"Found {len(results)} results:")
    for key, score, _ in results:
        content = memory.read(key)
        print(f"  {score:.3f} - {key}: {content[:60]}...")

    # Verify programming-related results
    top_keys = [key for key, _, _ in results[:3]]
    prog_count = sum(1 for key in top_keys if "lang" in key or "learning" in key)
    assert prog_count >= 1, "Search did not find programming-related facts"
    print("✓ Programming-related facts found")

    # Cleanup
    shutil.rmtree(test_dir)
    print("\n✓ ALL SEARCH TESTS PASSED")


def test_model_persistence():
    """Test saving and loading PyTorch models."""
    print("\n" + "=" * 70)
    print("TEST 3: Model Persistence")
    print("=" * 70)

    test_dir = Path(".memory_test")
    memory = MemoryTool(memory_dir=test_dir, verbose=True)

    # Create a mock model state dict
    print("\n[CREATE] Saving model...")
    mock_state_dict = {
        "encoder.weight": torch.randn(100, 50),
        "encoder.bias": torch.randn(100),
        "decoder.weight": torch.randn(50, 100),
    }

    success = memory.create(
        "test_model_v1",
        mock_state_dict,
        memory_type="model",
        metadata={"epochs": 300, "loss": 0.123},
        compute_embedding=False
    )
    assert success, "Failed to save model"
    print("✓ Model saved successfully")

    # Load the model
    print("\n[READ] Loading model...")
    loaded_state_dict = memory.read("test_model_v1")
    assert loaded_state_dict is not None, "Failed to load model"
    assert "encoder.weight" in loaded_state_dict, "Model state incomplete"

    # Verify tensor values match
    original_tensor = mock_state_dict["encoder.weight"]
    loaded_tensor = loaded_state_dict["encoder.weight"]
    assert torch.allclose(original_tensor, loaded_tensor), "Model tensors don't match"
    print(f"✓ Model loaded successfully (encoder.weight shape: {loaded_tensor.shape})")

    # Save embeddings
    print("\n[CREATE] Saving embeddings...")
    mock_embeddings = torch.randn(1000, 50)
    success = memory.create(
        "test_embeddings_v1",
        mock_embeddings,
        memory_type="embedding",
        metadata={"num_points": 1000, "dimensions": 50},
        compute_embedding=False
    )
    assert success, "Failed to save embeddings"

    # Load embeddings
    loaded_embeddings = memory.read("test_embeddings_v1")
    assert torch.allclose(mock_embeddings, loaded_embeddings), "Embeddings don't match"
    print(f"✓ Embeddings loaded successfully (shape: {loaded_embeddings.shape})")

    # Cleanup
    shutil.rmtree(test_dir)
    print("\n✓ ALL MODEL PERSISTENCE TESTS PASSED")


def test_analogy_integration():
    """Test integration with UMAP analogy engine."""
    print("\n" + "=" * 70)
    print("TEST 4: Analogy Engine Integration")
    print("=" * 70)

    test_dir = Path(".memory_test")
    manager = AnalogyMemoryManager(memory_dir=test_dir, verbose=True)

    # Save experiment
    print("\n[EXPERIMENT] Saving experiment...")
    success = manager.save_experiment(
        experiment_name="test_gender_analogy",
        config={
            "n_neighbors": 15,
            "d_low": 50,
            "epochs": 300,
            "relations": ["gender", "plural"],
        },
        results={
            "accuracy": 0.87,
            "final_loss": 0.123,
        },
        description="Test experiment for gender and plural analogies"
    )
    assert success, "Failed to save experiment"
    print("✓ Experiment saved")

    # Save analogy pattern
    print("\n[PATTERN] Saving analogy pattern...")
    success = manager.save_analogy_pattern(
        pattern_name="test_gender",
        description="Gender transformation patterns",
        examples=[
            ("king", "queen", "man", "woman"),
            ("boy", "girl", "father", "mother"),
        ],
        metadata={"language": "english"}
    )
    assert success, "Failed to save pattern"
    print("✓ Pattern saved")

    # Save session summary
    print("\n[SESSION] Saving session summary...")
    success = manager.save_session_summary(
        session_id="test_session_2025_01_15",
        summary="Test session for memory tool validation",
        tasks_completed=["Implemented CRUD", "Added search", "Tested persistence"],
        key_findings=["Memory tool works correctly", "Vector search is functional"],
        metadata={"duration_hours": 2.0}
    )
    assert success, "Failed to save session"
    print("✓ Session summary saved")

    # Save mock trained model
    print("\n[MODEL] Saving trained model...")
    mock_model_state = {"encoder.weight": torch.randn(100, 50)}
    mock_embeddings = torch.randn(1000, 50)
    mock_axes = [
        {"centroids": torch.randn(1, 50), "mean_direction": torch.randn(50), "scale": 0.5},
    ]

    success = manager.save_trained_model(
        model_state=mock_model_state,
        embeddings=mock_embeddings,
        relation_axes=mock_axes,
        model_name="test_model_v1",
        metadata={"epochs": 300}
    )
    assert success, "Failed to save trained model"
    print("✓ Trained model saved")

    # Load trained model
    print("\n[LOAD] Loading trained model...")
    model_bundle = manager.load_trained_model("test_model_v1")
    assert model_bundle is not None, "Failed to load model bundle"
    assert "model_state" in model_bundle, "Model bundle incomplete"
    assert "embeddings" in model_bundle, "Embeddings missing from bundle"
    assert "relation_axes" in model_bundle, "Axes missing from bundle"
    print("✓ Model bundle loaded successfully")

    # Search experiments
    print("\n[SEARCH] Searching experiments...")
    results = manager.search_experiments("gender analogy", k=3)
    assert len(results) > 0, "No experiments found"
    print(f"✓ Found {len(results)} relevant experiments")

    # Get continuity summary
    print("\n[CONTINUITY] Getting continuity summary...")
    summary = manager.get_continuity_summary()
    assert len(summary) > 0, "Continuity summary is empty"
    print(summary)
    print("✓ Continuity summary generated")

    # Cleanup
    shutil.rmtree(test_dir)
    print("\n✓ ALL INTEGRATION TESTS PASSED")


def test_statistics():
    """Test memory statistics."""
    print("\n" + "=" * 70)
    print("TEST 5: Statistics")
    print("=" * 70)

    test_dir = Path(".memory_test")
    memory = MemoryTool(memory_dir=test_dir, verbose=True)

    # Create various memory types
    print("\n[CREATE] Creating diverse memories...")
    memory.create("fact1", "Test fact 1", memory_type="fact")
    memory.create("fact2", "Test fact 2", memory_type="fact")
    memory.create("summary1", "Test summary", memory_type="summary")
    memory.create("model1", {"test": torch.randn(10, 10)}, memory_type="model", compute_embedding=False)

    # Get statistics
    print("\n[STATS] Getting statistics...")
    stats = memory.get_stats()

    assert stats["total_memories"] == 4, f"Expected 4 memories, got {stats['total_memories']}"
    assert stats["by_type"]["fact"] == 2, "Incorrect fact count"
    assert stats["by_type"]["summary"] == 1, "Incorrect summary count"
    assert stats["by_type"]["model"] == 1, "Incorrect model count"

    print(f"✓ Total memories: {stats['total_memories']}")
    print(f"✓ By type: {stats['by_type']}")
    print(f"✓ With embeddings: {stats['with_embeddings']}")
    print(f"✓ Storage: {stats['total_size_mb']} MB")

    # Cleanup
    shutil.rmtree(test_dir)
    print("\n✓ ALL STATISTICS TESTS PASSED")


def run_all_tests():
    """Run all test suites."""
    print("\n" + "=" * 70)
    print("MEMORY TOOL - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    tests = [
        ("Basic CRUD Operations", test_basic_crud),
        ("Semantic Search", test_semantic_search),
        ("Model Persistence", test_model_persistence),
        ("Analogy Integration", test_analogy_integration),
        ("Statistics", test_statistics),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ TEST FAILED: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ TEST ERROR: {test_name}")
            print(f"   Exception: {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Memory tool is ready for production.")
    else:
        print(f"\n⚠ {failed} test(s) failed. Please review the errors above.")

    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
