"""
Test script to verify caching functionality for the UMAP Analogy Engine.

This script tests:
1. Embeddings loading cache
2. Graph construction cache
3. Analogy query cache
4. Cache statistics tracking

Run with: python test_caching.py
"""

import time
import torch
import numpy as np
from operation_cache import (
    cached,
    clear_cache,
    get_cache_manager,
    print_cache_stats,
    CacheConfig,
)
from umap_analogy_engine import build_fuzzy_simplicial_set


def test_basic_caching():
    """Test basic caching functionality with a simple function."""
    print("\n" + "="*70)
    print("TEST 1: Basic Caching Functionality")
    print("="*70)

    call_count = [0]  # Use list to allow modification in nested function

    @cached(cache_type="memory", ttl=60)
    def expensive_computation(x: int, y: int) -> int:
        """Simulate an expensive computation."""
        call_count[0] += 1
        time.sleep(0.1)  # Simulate work
        return x + y

    # First call - should compute
    print("\n1. First call (should compute)...")
    start = time.time()
    result1 = expensive_computation(5, 10)
    time1 = time.time() - start
    print(f"   Result: {result1}, Time: {time1:.4f}s, Calls: {call_count[0]}")

    # Second call - should use cache
    print("\n2. Second call (should use cache)...")
    start = time.time()
    result2 = expensive_computation(5, 10)
    time2 = time.time() - start
    print(f"   Result: {result2}, Time: {time2:.4f}s, Calls: {call_count[0]}")

    # Different arguments - should compute
    print("\n3. Different arguments (should compute)...")
    start = time.time()
    result3 = expensive_computation(3, 7)
    time3 = time.time() - start
    print(f"   Result: {result3}, Time: {time3:.4f}s, Calls: {call_count[0]}")

    # Verify results
    assert result1 == 15, "First result incorrect"
    assert result2 == 15, "Second result incorrect"
    assert result3 == 10, "Third result incorrect"
    assert call_count[0] == 2, f"Expected 2 calls, got {call_count[0]}"
    assert time2 < time1 / 2, "Cache didn't speed up second call"

    print("\n✓ Basic caching test passed!")
    return True


def test_graph_cache():
    """Test graph construction caching."""
    print("\n" + "="*70)
    print("TEST 2: Graph Construction Caching")
    print("="*70)

    # Create synthetic data
    N, D = 100, 50
    X = torch.randn(N, D)

    # First call - should compute
    print("\n1. First graph construction (should compute)...")
    start = time.time()
    edge_i1, edge_j1, edge_w1 = build_fuzzy_simplicial_set(X, n_neighbors=10)
    time1 = time.time() - start
    print(f"   Edges: {len(edge_i1)}, Time: {time1:.4f}s")

    # Second call - should use cache
    print("\n2. Second graph construction (should use cache)...")
    start = time.time()
    edge_i2, edge_j2, edge_w2 = build_fuzzy_simplicial_set(X, n_neighbors=10)
    time2 = time.time() - start
    print(f"   Edges: {len(edge_i2)}, Time: {time2:.4f}s")

    # Verify results match
    assert torch.equal(edge_i1, edge_i2), "Edge sources don't match"
    assert torch.equal(edge_j1, edge_j2), "Edge targets don't match"
    assert torch.equal(edge_w1, edge_w2), "Edge weights don't match"
    assert time2 < time1 / 2, f"Cache didn't speed up (time1={time1:.4f}, time2={time2:.4f})"

    print(f"\n✓ Graph caching test passed! Speedup: {time1/time2:.1f}x")
    return True


def test_tensor_caching():
    """Test caching with tensor arguments."""
    print("\n" + "="*70)
    print("TEST 3: Tensor Caching")
    print("="*70)

    @cached(cache_type="memory", ttl=60)
    def process_tensor(t: torch.Tensor) -> torch.Tensor:
        """Process a tensor."""
        time.sleep(0.05)
        return t * 2

    # Create a tensor
    t1 = torch.randn(10, 20)

    # First call
    print("\n1. First tensor processing...")
    start = time.time()
    result1 = process_tensor(t1)
    time1 = time.time() - start
    print(f"   Shape: {result1.shape}, Time: {time1:.4f}s")

    # Second call with same tensor
    print("\n2. Second call with same tensor...")
    start = time.time()
    result2 = process_tensor(t1)
    time2 = time.time() - start
    print(f"   Shape: {result2.shape}, Time: {time2:.4f}s")

    # Verify results match
    assert torch.equal(result1, result2), "Results don't match"
    assert time2 < time1 / 2, "Cache didn't speed up"

    print("\n✓ Tensor caching test passed!")
    return True


def test_cache_stats():
    """Test cache statistics tracking."""
    print("\n" + "="*70)
    print("TEST 4: Cache Statistics")
    print("="*70)

    manager = get_cache_manager()

    # Clear cache first
    manager.memory_cache.stats.reset()

    @cached(cache_type="memory", ttl=60)
    def simple_func(x: int) -> int:
        return x * 2

    # Generate some cache hits and misses
    print("\n1. Generating cache activity...")
    simple_func(1)  # Miss
    simple_func(1)  # Hit
    simple_func(1)  # Hit
    simple_func(2)  # Miss
    simple_func(2)  # Hit

    stats = manager.memory_cache.get_stats()
    print(f"\n2. Statistics:")
    print(f"   Hits:     {stats['hits']}")
    print(f"   Misses:   {stats['misses']}")
    print(f"   Hit Rate: {stats['hit_rate']:.1%}")

    # Verify statistics
    assert stats['hits'] == 3, f"Expected 3 hits, got {stats['hits']}"
    assert stats['misses'] == 2, f"Expected 2 misses, got {stats['misses']}"
    assert abs(stats['hit_rate'] - 0.6) < 0.01, f"Expected 60% hit rate, got {stats['hit_rate']:.1%}"

    print("\n✓ Cache statistics test passed!")
    return True


def test_cache_eviction():
    """Test LRU cache eviction."""
    print("\n" + "="*70)
    print("TEST 5: LRU Cache Eviction")
    print("="*70)

    from operation_cache import LRUCache

    # Create a small cache
    cache = LRUCache(max_items=3, default_ttl=60)

    # Add items
    print("\n1. Adding 5 items to cache with max_items=3...")
    for i in range(5):
        cache.put(f"key_{i}", f"value_{i}")
        print(f"   Added key_{i}, cache size: {cache.size()}")

    # Check size
    size = cache.size()
    print(f"\n2. Final cache size: {size}")
    assert size == 3, f"Expected cache size 3, got {size}"

    # Check oldest items were evicted
    print("\n3. Checking eviction...")
    assert cache.get("key_0") is None, "key_0 should be evicted"
    assert cache.get("key_1") is None, "key_1 should be evicted"
    assert cache.get("key_2") is not None, "key_2 should exist"
    assert cache.get("key_3") is not None, "key_3 should exist"
    assert cache.get("key_4") is not None, "key_4 should exist"

    print("   ✓ Oldest items (key_0, key_1) were evicted")
    print("   ✓ Newest items (key_2, key_3, key_4) remain")

    print("\n✓ LRU eviction test passed!")
    return True


def run_all_tests():
    """Run all cache tests."""
    print("\n" + "="*70)
    print("OPERATION CACHE TEST SUITE")
    print("="*70)

    # Clear all caches before testing
    print("\nClearing all caches before testing...")
    clear_cache()

    tests = [
        test_basic_caching,
        test_graph_cache,
        test_tensor_caching,
        test_cache_stats,
        test_cache_eviction,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\n✗ Test {test.__name__} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test.__name__, False))

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {name}")

    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    # Print final cache statistics
    print_cache_stats()

    return all(p for _, p in results)


if __name__ == "__main__":
    success = run_all_tests()

    if success:
        print("\n🎉 All tests passed! Caching system is working correctly.\n")
        exit(0)
    else:
        print("\n❌ Some tests failed. Please review the errors above.\n")
        exit(1)
