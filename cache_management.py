"""
Cache Management Utilities for UMAP Analogy Engine

This module provides command-line utilities for managing the operation cache,
including viewing statistics, clearing caches, and configuring cache settings.

Usage:
    python cache_management.py stats           # View cache statistics
    python cache_management.py clear [type]    # Clear cache (all or specific type)
    python cache_management.py config          # View current configuration
    python cache_management.py size            # View cache disk usage
"""

import argparse
import shutil
from pathlib import Path
from operation_cache import (
    CacheConfig,
    get_cache_manager,
    print_cache_stats,
    clear_cache,
)


def view_stats():
    """Display cache statistics."""
    print("\n" + "="*70)
    print("CACHE STATISTICS")
    print("="*70)
    print_cache_stats()


def clear_all_caches(cache_type: str = None):
    """
    Clear caches.

    Args:
        cache_type: Specific cache type to clear, or None to clear all
    """
    if cache_type:
        clear_cache(cache_type)
        print(f"\n✓ Cleared {cache_type} cache")
    else:
        clear_cache()
        print("\n✓ Cleared all caches")


def view_config():
    """Display current cache configuration."""
    print("\n" + "="*70)
    print("CACHE CONFIGURATION")
    print("="*70)

    print("\nCache Directories:")
    print(f"  Root:       {CacheConfig.CACHE_DIR}")
    print(f"  Embeddings: {CacheConfig.EMBEDDINGS_CACHE_DIR}")
    print(f"  Graphs:     {CacheConfig.GRAPH_CACHE_DIR}")
    print(f"  Queries:    {CacheConfig.QUERY_CACHE_DIR}")

    print("\nCache Size Limits:")
    print(f"  Memory Cache: {CacheConfig.MAX_MEMORY_CACHE_SIZE} MB")
    print(f"  Disk Cache:   {CacheConfig.MAX_DISK_CACHE_SIZE} MB")

    print("\nTTL Settings (seconds):")
    print(f"  Default:    {CacheConfig.DEFAULT_TTL}s ({CacheConfig.DEFAULT_TTL/3600:.1f}h)")
    print(f"  Embeddings: {CacheConfig.EMBEDDINGS_TTL}s ({CacheConfig.EMBEDDINGS_TTL/3600:.1f}h)")
    print(f"  Graphs:     {CacheConfig.GRAPH_TTL}s ({CacheConfig.GRAPH_TTL/3600:.1f}h)")
    print(f"  Queries:    {CacheConfig.QUERY_TTL}s ({CacheConfig.QUERY_TTL/60:.1f}m)")

    print("\nLRU Cache Settings:")
    print(f"  Max Items: {CacheConfig.MEMORY_CACHE_MAX_ITEMS}")

    print("\nCache Status:")
    print(f"  Enabled:        {CacheConfig.ENABLE_CACHE}")
    print(f"  Disk Cache:     {CacheConfig.ENABLE_DISK_CACHE}")
    print(f"  Memory Cache:   {CacheConfig.ENABLE_MEMORY_CACHE}")
    print(f"  Statistics:     {CacheConfig.ENABLE_STATS}")
    print("="*70 + "\n")


def view_disk_usage():
    """Display disk usage for cache directories."""
    print("\n" + "="*70)
    print("CACHE DISK USAGE")
    print("="*70)

    CacheConfig.initialize()

    total_size = 0

    cache_dirs = [
        ("Embeddings", CacheConfig.EMBEDDINGS_CACHE_DIR),
        ("Graphs", CacheConfig.GRAPH_CACHE_DIR),
        ("Queries", CacheConfig.QUERY_CACHE_DIR),
    ]

    for name, cache_dir in cache_dirs:
        if cache_dir.exists():
            size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
            size_mb = size / (1024 * 1024)
            file_count = len(list(cache_dir.glob('*.pkl')))
            total_size += size
            print(f"\n{name} Cache:")
            print(f"  Location: {cache_dir}")
            print(f"  Size:     {size_mb:.2f} MB")
            print(f"  Files:    {file_count} cached items")
        else:
            print(f"\n{name} Cache:")
            print(f"  Location: {cache_dir}")
            print(f"  Status:   Not initialized")

    print(f"\nTotal Cache Size: {total_size / (1024 * 1024):.2f} MB")
    print("="*70 + "\n")


def enable_cache():
    """Enable caching globally."""
    CacheConfig.ENABLE_CACHE = True
    print("\n✓ Caching enabled globally")
    print("  Note: This only affects the current session.")
    print("  To persist, modify CacheConfig.ENABLE_CACHE in operation_cache.py\n")


def disable_cache():
    """Disable caching globally."""
    CacheConfig.ENABLE_CACHE = False
    print("\n✓ Caching disabled globally")
    print("  Note: This only affects the current session.")
    print("  To persist, modify CacheConfig.ENABLE_CACHE in operation_cache.py\n")


def main():
    parser = argparse.ArgumentParser(
        description="Manage operation caches for UMAP Analogy Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cache_management.py stats              # View statistics
  python cache_management.py clear              # Clear all caches
  python cache_management.py clear embeddings   # Clear embeddings cache only
  python cache_management.py size               # View disk usage
  python cache_management.py config             # View configuration
  python cache_management.py enable             # Enable caching
  python cache_management.py disable            # Disable caching
        """
    )

    parser.add_argument(
        'action',
        choices=['stats', 'clear', 'config', 'size', 'enable', 'disable'],
        help='Action to perform'
    )

    parser.add_argument(
        'cache_type',
        nargs='?',
        choices=['memory', 'embeddings', 'graph', 'query'],
        help='Specific cache type (for clear action)'
    )

    args = parser.parse_args()

    if args.action == 'stats':
        view_stats()
    elif args.action == 'clear':
        clear_all_caches(args.cache_type)
    elif args.action == 'config':
        view_config()
    elif args.action == 'size':
        view_disk_usage()
    elif args.action == 'enable':
        enable_cache()
    elif args.action == 'disable':
        disable_cache()


if __name__ == "__main__":
    main()
