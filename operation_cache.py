"""
Operation Caching System for UMAP Analogy Engine

This module provides a comprehensive caching system for expensive operations including:
- Embeddings loading (GloVe, Word2Vec)
- kNN graph / fuzzy simplicial set construction
- Forward pass results (low-dimensional embeddings)
- Analogy query results
- Distance matrix computations

Features:
- Multiple cache backends (memory, disk)
- LRU eviction policy
- TTL (time-to-live) support
- Cache statistics (hit/miss rates)
- Configurable cache size limits
- Thread-safe operations
- Easy integration via decorators
"""

import hashlib
import json
import os
import pickle
import time
from collections import OrderedDict
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Union
import threading

# Optional imports - only needed for tensor caching
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


# ============================================================================
# Cache Configuration
# ============================================================================

class CacheConfig:
    """Global cache configuration."""

    # Cache directories
    CACHE_DIR = Path.home() / ".cache" / "umap_analogy_engine"
    EMBEDDINGS_CACHE_DIR = CACHE_DIR / "embeddings"
    GRAPH_CACHE_DIR = CACHE_DIR / "graphs"
    QUERY_CACHE_DIR = CACHE_DIR / "queries"

    # Cache size limits (in MB)
    MAX_MEMORY_CACHE_SIZE = 500  # 500 MB for in-memory cache
    MAX_DISK_CACHE_SIZE = 5000   # 5 GB for disk cache

    # TTL settings (in seconds)
    DEFAULT_TTL = 3600  # 1 hour
    EMBEDDINGS_TTL = 86400  # 24 hours (embeddings rarely change)
    GRAPH_TTL = 3600  # 1 hour
    QUERY_TTL = 1800  # 30 minutes

    # LRU cache sizes
    MEMORY_CACHE_MAX_ITEMS = 100

    # Enable/disable caching
    ENABLE_CACHE = True
    ENABLE_DISK_CACHE = True
    ENABLE_MEMORY_CACHE = True

    # Statistics
    ENABLE_STATS = True

    @classmethod
    def initialize(cls):
        """Initialize cache directories."""
        if cls.ENABLE_DISK_CACHE:
            cls.EMBEDDINGS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cls.GRAPH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cls.QUERY_CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Cache Statistics
# ============================================================================

class CacheStats:
    """Thread-safe cache statistics tracker."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.total_load_time = 0.0
        self.total_save_time = 0.0
        self._lock = threading.Lock()

    def record_hit(self):
        """Record a cache hit."""
        with self._lock:
            self.hits += 1

    def record_miss(self):
        """Record a cache miss."""
        with self._lock:
            self.misses += 1

    def record_eviction(self):
        """Record a cache eviction."""
        with self._lock:
            self.evictions += 1

    def record_load_time(self, time_seconds: float):
        """Record time spent loading from cache."""
        with self._lock:
            self.total_load_time += time_seconds

    def record_save_time(self, time_seconds: float):
        """Record time spent saving to cache."""
        with self._lock:
            self.total_save_time += time_seconds

    def get_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def get_summary(self) -> Dict[str, Any]:
        """Get cache statistics summary."""
        with self._lock:
            return {
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "hit_rate": self.get_hit_rate(),
                "total_load_time": self.total_load_time,
                "total_save_time": self.total_save_time,
                "total_queries": self.hits + self.misses,
            }

    def reset(self):
        """Reset all statistics."""
        with self._lock:
            self.hits = 0
            self.misses = 0
            self.evictions = 0
            self.total_load_time = 0.0
            self.total_save_time = 0.0

    def __repr__(self):
        stats = self.get_summary()
        return (f"CacheStats(hits={stats['hits']}, misses={stats['misses']}, "
                f"hit_rate={stats['hit_rate']:.2%}, evictions={stats['evictions']})")


# ============================================================================
# Cache Key Generation
# ============================================================================

def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate a unique cache key from function arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        A SHA256 hash string representing the cache key
    """
    # Create a string representation of all arguments
    key_parts = []

    for arg in args:
        # Handle tensors/arrays if libraries are available
        if TORCH_AVAILABLE and isinstance(arg, torch.Tensor):
            arr = arg.detach().cpu().numpy()
            key_parts.append(f"tensor_{arr.shape}_{arr.flatten()[:10].tobytes().hex()}")
        elif NUMPY_AVAILABLE and isinstance(arg, np.ndarray):
            key_parts.append(f"array_{arg.shape}_{arg.flatten()[:10].tobytes().hex()}")
        elif isinstance(arg, (list, tuple)):
            key_parts.append(str(arg))
        elif isinstance(arg, dict):
            key_parts.append(json.dumps(arg, sort_keys=True))
        elif isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        elif hasattr(arg, '__dict__'):
            # For objects, use their dict representation
            key_parts.append(json.dumps(arg.__dict__, sort_keys=True, default=str))
        else:
            key_parts.append(str(arg))

    # Add keyword arguments
    for key, value in sorted(kwargs.items()):
        if TORCH_AVAILABLE and isinstance(value, torch.Tensor):
            arr = value.detach().cpu().numpy()
            key_parts.append(f"{key}=tensor_{arr.shape}_{arr.flatten()[:10].tobytes().hex()}")
        elif NUMPY_AVAILABLE and isinstance(value, np.ndarray):
            key_parts.append(f"{key}=array_{value.shape}_{value.flatten()[:10].tobytes().hex()}")
        else:
            key_parts.append(f"{key}={value}")

    # Create hash
    key_string = "|".join(key_parts)
    return hashlib.sha256(key_string.encode()).hexdigest()


# ============================================================================
# In-Memory LRU Cache
# ============================================================================

class LRUCache:
    """Thread-safe LRU (Least Recently Used) cache with TTL support."""

    def __init__(self, max_items: int = 100, default_ttl: int = 3600):
        """
        Initialize LRU cache.

        Args:
            max_items: Maximum number of items to store
            default_ttl: Default time-to-live in seconds
        """
        self.max_items = max_items
        self.default_ttl = default_ttl
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._ttls: Dict[str, float] = {}
        self._lock = threading.Lock()
        self.stats = CacheStats()

    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
            if key not in self._cache:
                if CacheConfig.ENABLE_STATS:
                    self.stats.record_miss()
                return None

            # Check TTL
            if self._is_expired(key):
                del self._cache[key]
                del self._timestamps[key]
                del self._ttls[key]
                if CacheConfig.ENABLE_STATS:
                    self.stats.record_miss()
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)

            if CacheConfig.ENABLE_STATS:
                self.stats.record_hit()

            return self._cache[key]

    def put(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Put item into cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None uses default)
        """
        with self._lock:
            # Remove oldest item if at capacity
            if key not in self._cache and len(self._cache) >= self.max_items:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                del self._timestamps[oldest_key]
                del self._ttls[oldest_key]
                if CacheConfig.ENABLE_STATS:
                    self.stats.record_eviction()

            # Add/update item
            self._cache[key] = value
            self._cache.move_to_end(key)
            self._timestamps[key] = time.time()
            self._ttls[key] = ttl if ttl is not None else self.default_ttl

    def _is_expired(self, key: str) -> bool:
        """Check if cache entry has expired."""
        if key not in self._timestamps:
            return True
        age = time.time() - self._timestamps[key]
        return age > self._ttls[key]

    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._ttls.clear()

    def size(self) -> int:
        """Get number of cached items."""
        with self._lock:
            return len(self._cache)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.stats.get_summary()


# ============================================================================
# Disk Cache
# ============================================================================

class DiskCache:
    """Persistent disk-based cache using pickle."""

    def __init__(self, cache_dir: Path, default_ttl: int = 3600):
        """
        Initialize disk cache.

        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.stats = CacheStats()
        self._lock = threading.Lock()

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key."""
        return self.cache_dir / f"{key}.pkl"

    def _get_metadata_path(self, key: str) -> Path:
        """Get metadata file path for cache key."""
        return self.cache_dir / f"{key}.meta"

    def get(self, key: str) -> Optional[Any]:
        """
        Get item from disk cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)

        if not cache_path.exists():
            if CacheConfig.ENABLE_STATS:
                self.stats.record_miss()
            return None

        # Check TTL
        if meta_path.exists():
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
                age = time.time() - metadata['timestamp']
                if age > metadata['ttl']:
                    # Expired
                    cache_path.unlink()
                    meta_path.unlink()
                    if CacheConfig.ENABLE_STATS:
                        self.stats.record_miss()
                    return None

        # Load from disk
        try:
            start_time = time.time()
            with open(cache_path, 'rb') as f:
                value = pickle.load(f)
            load_time = time.time() - start_time

            if CacheConfig.ENABLE_STATS:
                self.stats.record_hit()
                self.stats.record_load_time(load_time)

            return value
        except Exception as e:
            print(f"Error loading from cache: {e}")
            if CacheConfig.ENABLE_STATS:
                self.stats.record_miss()
            return None

    def put(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Put item into disk cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None uses default)
        """
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)

        try:
            start_time = time.time()

            # Save data
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)

            # Save metadata
            metadata = {
                'timestamp': time.time(),
                'ttl': ttl if ttl is not None else self.default_ttl,
            }
            with open(meta_path, 'w') as f:
                json.dump(metadata, f)

            save_time = time.time() - start_time

            if CacheConfig.ENABLE_STATS:
                self.stats.record_save_time(save_time)
        except Exception as e:
            print(f"Error saving to cache: {e}")

    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            for file_path in self.cache_dir.glob("*"):
                file_path.unlink()

    def size(self) -> int:
        """Get number of cached items."""
        return len(list(self.cache_dir.glob("*.pkl")))

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.stats.get_summary()


# ============================================================================
# Unified Cache Manager
# ============================================================================

class CacheManager:
    """
    Unified cache manager that handles both memory and disk caching.
    """

    def __init__(self):
        """Initialize cache manager."""
        CacheConfig.initialize()

        # Initialize caches
        self.memory_cache = LRUCache(
            max_items=CacheConfig.MEMORY_CACHE_MAX_ITEMS,
            default_ttl=CacheConfig.DEFAULT_TTL
        )

        self.embeddings_cache = DiskCache(
            cache_dir=CacheConfig.EMBEDDINGS_CACHE_DIR,
            default_ttl=CacheConfig.EMBEDDINGS_TTL
        )

        self.graph_cache = DiskCache(
            cache_dir=CacheConfig.GRAPH_CACHE_DIR,
            default_ttl=CacheConfig.GRAPH_TTL
        )

        self.query_cache = LRUCache(
            max_items=50,
            default_ttl=CacheConfig.QUERY_TTL
        )

    def get(self, key: str, cache_type: str = "memory") -> Optional[Any]:
        """
        Get item from cache.

        Args:
            key: Cache key
            cache_type: Type of cache ("memory", "embeddings", "graph", "query")

        Returns:
            Cached value or None
        """
        if not CacheConfig.ENABLE_CACHE:
            return None

        cache = self._get_cache(cache_type)
        return cache.get(key) if cache else None

    def put(self, key: str, value: Any, cache_type: str = "memory", ttl: Optional[int] = None):
        """
        Put item into cache.

        Args:
            key: Cache key
            value: Value to cache
            cache_type: Type of cache ("memory", "embeddings", "graph", "query")
            ttl: Time-to-live in seconds
        """
        if not CacheConfig.ENABLE_CACHE:
            return

        cache = self._get_cache(cache_type)
        if cache:
            cache.put(key, value, ttl)

    def _get_cache(self, cache_type: str):
        """Get cache instance by type."""
        cache_map = {
            "memory": self.memory_cache,
            "embeddings": self.embeddings_cache,
            "graph": self.graph_cache,
            "query": self.query_cache,
        }
        return cache_map.get(cache_type)

    def clear_all(self):
        """Clear all caches."""
        self.memory_cache.clear()
        self.embeddings_cache.clear()
        self.graph_cache.clear()
        self.query_cache.clear()

    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics from all caches."""
        return {
            "memory": self.memory_cache.get_stats(),
            "embeddings": self.embeddings_cache.get_stats(),
            "graph": self.graph_cache.get_stats(),
            "query": self.query_cache.get_stats(),
        }

    def print_stats(self):
        """Print cache statistics."""
        all_stats = self.get_all_stats()
        print("\n" + "="*60)
        print("CACHE STATISTICS")
        print("="*60)
        for cache_name, stats in all_stats.items():
            print(f"\n{cache_name.upper()} Cache:")
            print(f"  Hits: {stats['hits']}")
            print(f"  Misses: {stats['misses']}")
            print(f"  Hit Rate: {stats['hit_rate']:.2%}")
            print(f"  Evictions: {stats['evictions']}")
            print(f"  Total Queries: {stats['total_queries']}")
            if stats['total_load_time'] > 0:
                print(f"  Total Load Time: {stats['total_load_time']:.2f}s")
            if stats['total_save_time'] > 0:
                print(f"  Total Save Time: {stats['total_save_time']:.2f}s")
        print("="*60 + "\n")


# ============================================================================
# Global Cache Manager Instance
# ============================================================================

_global_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return _global_cache_manager


# ============================================================================
# Caching Decorators
# ============================================================================

def cached(cache_type: str = "memory", ttl: Optional[int] = None,
           key_prefix: str = ""):
    """
    Decorator to cache function results.

    Args:
        cache_type: Type of cache to use ("memory", "embeddings", "graph", "query")
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache keys

    Example:
        @cached(cache_type="embeddings", ttl=86400)
        def load_embeddings(file_path):
            # Expensive loading operation
            return embeddings
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CacheConfig.ENABLE_CACHE:
                return func(*args, **kwargs)

            # Generate cache key
            cache_key = key_prefix + func.__name__ + "_" + generate_cache_key(*args, **kwargs)

            # Try to get from cache
            manager = get_cache_manager()
            cached_value = manager.get(cache_key, cache_type)

            if cached_value is not None:
                return cached_value

            # Compute value
            value = func(*args, **kwargs)

            # Store in cache
            manager.put(cache_key, value, cache_type, ttl)

            return value

        return wrapper
    return decorator


def clear_cache(cache_type: Optional[str] = None):
    """
    Clear cache.

    Args:
        cache_type: Type of cache to clear (None clears all)
    """
    manager = get_cache_manager()
    if cache_type:
        cache = manager._get_cache(cache_type)
        if cache:
            cache.clear()
    else:
        manager.clear_all()


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return get_cache_manager().get_all_stats()


def print_cache_stats():
    """Print cache statistics."""
    get_cache_manager().print_stats()
