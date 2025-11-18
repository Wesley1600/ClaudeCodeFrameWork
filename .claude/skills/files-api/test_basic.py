"""
Basic tests for the Files API skill

Tests initialization and basic functionality without requiring API calls.
"""

import os
import sys
import json
from pathlib import Path

# Add the skill directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from files_manager import FilesManager, AuthenticationError


def test_initialization_without_api_key():
    """Test that initialization fails without API key"""
    print("Test 1: Initialization without API key...")

    # Temporarily remove API key if it exists
    original_key = os.environ.get("ANTHROPIC_API_KEY")
    if original_key:
        del os.environ["ANTHROPIC_API_KEY"]

    try:
        manager = FilesManager()
        print("  ✗ Should have raised AuthenticationError")
        return False
    except AuthenticationError as e:
        print(f"  ✓ Correctly raised AuthenticationError: {e}")
        # Restore API key if it existed
        if original_key:
            os.environ["ANTHROPIC_API_KEY"] = original_key
        return True


def test_initialization_with_mock_key():
    """Test initialization with a mock API key"""
    print("\nTest 2: Initialization with mock API key...")

    # Set a mock API key
    os.environ["ANTHROPIC_API_KEY"] = "mock_api_key_for_testing"

    try:
        manager = FilesManager()
        print("  ✓ Manager initialized successfully")
        print(f"    Storage dir: {manager.storage_dir}")
        print(f"    Database: {manager.db_path}")

        # Check that directories were created
        assert manager.storage_dir.exists(), "Storage directory not created"
        print("  ✓ Storage directory created")

        assert manager.db_path.exists(), "Database file not created"
        print("  ✓ Database file created")

        # Check database structure
        with open(manager.db_path, 'r') as f:
            db = json.load(f)
        assert "files" in db, "Database missing 'files' key"
        assert isinstance(db["files"], list), "'files' should be a list"
        print("  ✓ Database structure valid")

        # Check config
        assert manager.config_path.exists(), "Config file not created"
        print("  ✓ Config file created")

        return True

    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_storage_stats():
    """Test storage statistics with empty database"""
    print("\nTest 3: Storage statistics...")

    os.environ["ANTHROPIC_API_KEY"] = "mock_api_key_for_testing"

    try:
        manager = FilesManager()
        stats = manager.get_storage_stats()

        print("  ✓ Got storage stats:")
        print(f"    Total files: {stats['total_files']}")
        print(f"    Total size: {stats['total_size_mb']} MB")

        assert stats['total_files'] >= 0, "Invalid file count"
        assert stats['total_size_bytes'] >= 0, "Invalid size"

        return True

    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_search_functionality():
    """Test search with empty database"""
    print("\nTest 4: Search functionality...")

    os.environ["ANTHROPIC_API_KEY"] = "mock_api_key_for_testing"

    try:
        manager = FilesManager()

        # Search by filename
        results = manager.search_files(filename="test")
        print(f"  ✓ Search by filename returned {len(results)} results")

        # Search by purpose
        results = manager.search_files(purpose="test")
        print(f"  ✓ Search by purpose returned {len(results)} results")

        # Search by metadata
        results = manager.search_files(metadata_filter={"key": "value"})
        print(f"  ✓ Search by metadata returned {len(results)} results")

        return True

    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def test_local_file_operations():
    """Test local file operations without API calls"""
    print("\nTest 5: Local file operations...")

    os.environ["ANTHROPIC_API_KEY"] = "mock_api_key_for_testing"

    try:
        manager = FilesManager()

        # Create a test file
        test_file = manager.storage_dir / "test.txt"
        test_file.write_text("Test content")
        print("  ✓ Created test file")

        # Verify it exists
        assert test_file.exists(), "Test file not created"
        print("  ✓ Test file verified")

        # Clean up
        test_file.unlink()
        print("  ✓ Test file cleaned up")

        return True

    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False


def main():
    """Run all basic tests"""
    print("=" * 60)
    print("BASIC TESTS FOR FILES API SKILL")
    print("=" * 60)

    tests = [
        test_initialization_without_api_key,
        test_initialization_with_mock_key,
        test_storage_stats,
        test_search_functionality,
        test_local_file_operations
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test {test_func.__name__} crashed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
