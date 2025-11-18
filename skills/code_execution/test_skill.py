#!/usr/bin/env python3
"""
Test suite for Code Execution Skill
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the skill to the path
sys.path.insert(0, str(Path(__file__).parent))

from main import (
    run_python,
    run_bash,
    write_file,
    read_file,
    analyze_data,
    create_visualization,
    install_package,
    list_files
)


def test_run_python():
    """Test Python code execution"""
    print("Testing run_python...")

    # Test 1: Simple print
    result = run_python("print('Hello, World!')")
    assert result["success"], "Simple print should succeed"
    assert "Hello, World!" in result["output"], "Output should contain the printed text"

    # Test 2: Import and calculation
    result = run_python("""
import math
print(math.pi)
""")
    assert result["success"], "Import and calculation should succeed"
    assert "3.14159" in result["output"], "Output should contain pi value"

    # Test 3: Error handling
    result = run_python("undefined_variable")
    assert not result["success"], "Invalid code should fail"
    assert result["error"] is not None, "Error should be captured"

    print("✓ run_python tests passed")


def test_run_bash():
    """Test Bash command execution"""
    print("Testing run_bash...")

    # Test 1: Simple command
    result = run_bash("echo 'Test'")
    assert result["success"], "Echo command should succeed"
    assert "Test" in result["output"], "Output should contain the echoed text"

    # Test 2: Create directory
    test_dir = "/tmp/test_code_exec_" + str(os.getpid())
    result = run_bash(f"mkdir -p {test_dir}")
    assert result["success"], "mkdir should succeed"

    # Test 3: List directory
    result = run_bash(f"ls {test_dir}")
    assert result["success"], "ls should succeed"

    # Cleanup
    run_bash(f"rm -rf {test_dir}")

    print("✓ run_bash tests passed")


def test_write_file():
    """Test file writing"""
    print("Testing write_file...")

    # Test 1: Write simple file
    test_file = f"/tmp/test_write_{os.getpid()}.txt"
    content = "Test content"
    result = write_file(test_file, content)
    assert result["success"], "File write should succeed"
    assert result["path"] == test_file, "Path should match"

    # Test 2: Verify content
    with open(test_file, 'r') as f:
        read_content = f.read()
    assert read_content == content, "Content should match"

    # Test 3: Write with directory creation
    nested_file = f"/tmp/test_nested_{os.getpid()}/subdir/file.txt"
    result = write_file(nested_file, "Nested content")
    assert result["success"], "Nested file write should succeed"
    assert os.path.exists(nested_file), "Nested file should exist"

    # Cleanup
    os.unlink(test_file)
    os.system(f"rm -rf /tmp/test_nested_{os.getpid()}")

    print("✓ write_file tests passed")


def test_read_file():
    """Test file reading"""
    print("Testing read_file...")

    # Create test file
    test_file = f"/tmp/test_read_{os.getpid()}.txt"
    content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

    with open(test_file, 'w') as f:
        f.write(content)

    # Test 1: Read entire file
    result = read_file(test_file)
    assert result["success"], "File read should succeed"
    assert result["content"] == content, "Content should match"

    # Test 2: Read with offset
    result = read_file(test_file, offset=2)
    assert result["success"], "Read with offset should succeed"
    assert "Line 1" not in result["content"], "First lines should be skipped"
    assert "Line 3" in result["content"], "Later lines should be included"

    # Test 3: Read with limit
    result = read_file(test_file, limit=2)
    assert result["success"], "Read with limit should succeed"
    lines = result["content"].split('\n')
    assert len(lines) <= 3, "Should only read limited lines"  # Including potential empty line

    # Test 4: Non-existent file
    result = read_file("/tmp/nonexistent_file.txt")
    assert not result["success"], "Reading nonexistent file should fail"
    assert result["error"] is not None, "Error should be captured"

    # Cleanup
    os.unlink(test_file)

    print("✓ read_file tests passed")


def test_analyze_data():
    """Test data analysis"""
    print("Testing analyze_data...")

    # Create test CSV
    test_csv = f"/tmp/test_data_{os.getpid()}.csv"
    csv_content = """name,age,salary
Alice,30,50000
Bob,25,45000
Charlie,35,60000
Diana,28,52000
"""

    with open(test_csv, 'w') as f:
        f.write(csv_content)

    # Test 1: Summary analysis
    result = analyze_data(test_csv, "summary")
    assert result["success"], "Summary analysis should succeed"
    assert "Data Shape" in result["result"], "Should contain shape info"

    # Test 2: Statistics analysis
    result = analyze_data(test_csv, "statistics")
    assert result["success"], "Statistics analysis should succeed"
    assert "Descriptive Statistics" in result["result"], "Should contain statistics"

    # Test 3: Custom analysis
    custom_code = f"""
import pandas as pd
df = pd.read_csv('{test_csv}')
print(f"Average salary: ${{df['salary'].mean():.2f}}")
"""
    result = analyze_data(test_csv, "custom", custom_code=custom_code)
    assert result["success"], "Custom analysis should succeed"
    assert "Average salary" in result["result"], "Should contain custom output"

    # Cleanup
    os.unlink(test_csv)

    print("✓ analyze_data tests passed")


def test_list_files():
    """Test file listing"""
    print("Testing list_files...")

    # Create test directory with files
    test_dir = f"/tmp/test_list_{os.getpid()}"
    os.makedirs(test_dir, exist_ok=True)

    # Create test files
    for i in range(3):
        with open(f"{test_dir}/file{i}.txt", 'w') as f:
            f.write(f"Content {i}")

    with open(f"{test_dir}/data.csv", 'w') as f:
        f.write("col1,col2\n1,2")

    # Test 1: List all txt files
    result = list_files("*.txt", path=test_dir)
    assert result["success"], "File listing should succeed"
    assert len(result["files"]) == 3, "Should find 3 txt files"

    # Test 2: List all files
    result = list_files("*", path=test_dir)
    assert result["success"], "File listing should succeed"
    assert len(result["files"]) == 4, "Should find 4 total files"

    # Test 3: List CSV files
    result = list_files("*.csv", path=test_dir)
    assert result["success"], "File listing should succeed"
    assert len(result["files"]) == 1, "Should find 1 CSV file"

    # Cleanup
    os.system(f"rm -rf {test_dir}")

    print("✓ list_files tests passed")


def test_error_handling():
    """Test error handling"""
    print("Testing error handling...")

    # Test 1: Timeout (short timeout for fast test)
    result = run_python("import time; time.sleep(10)", timeout=100)
    assert not result["success"], "Should timeout"
    assert "timed out" in result["error"].lower(), "Should indicate timeout"

    # Test 2: Invalid Python code
    result = run_python("this is not valid python!!!")
    assert not result["success"], "Should fail on invalid code"

    # Test 3: Invalid bash command
    result = run_bash("nonexistentcommand123456")
    assert not result["success"], "Should fail on invalid command"

    # Test 4: Write to invalid path (if running without permissions)
    # Note: This might succeed if running as root, so we check the result format
    result = write_file("/root/forbidden/file.txt", "content")
    assert "success" in result, "Should return success field"
    assert "error" in result, "Should return error field"

    print("✓ Error handling tests passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CODE EXECUTION SKILL - TEST SUITE")
    print("=" * 60 + "\n")

    tests = [
        test_run_python,
        test_run_bash,
        test_write_file,
        test_read_file,
        test_analyze_data,
        test_list_files,
        test_error_handling
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
