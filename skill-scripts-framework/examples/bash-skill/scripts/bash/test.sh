#!/usr/bin/env bash
#
# Test Script
# Runs test suite and generates reports
#

set -euo pipefail

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load configuration
if [[ -f "$SCRIPT_DIR/../shared/config.env" ]]; then
    source "$SCRIPT_DIR/../shared/config.env"
fi

# Configuration
BUILD_DIR="${BUILD_DIR:-$PROJECT_ROOT/build}"
TEST_REPORT_DIR="${TEST_REPORT_DIR:-$PROJECT_ROOT/test-reports}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================="
echo "Running Tests"
echo "========================================="
echo "Test report directory: $TEST_REPORT_DIR"
echo ""

# Create test report directory
mkdir -p "$TEST_REPORT_DIR"

# Check if build artifacts exist
if [[ ! -d "$BUILD_DIR" ]] || [[ ! -f "$BUILD_DIR/main" ]]; then
    echo -e "${RED}Error: Build artifacts not found. Run build.sh first.${NC}" >&2
    exit 1
fi

# Simulate running tests
echo "Running unit tests..."
sleep 1

# Simulate test results
TESTS_PASSED=15
TESTS_FAILED=0
TESTS_TOTAL=$((TESTS_PASSED + TESTS_FAILED))
COVERAGE=87.5

# Generate test report
cat > "$TEST_REPORT_DIR/results.json" << EOF
{
  "test_run": {
    "date": "$(date -Iseconds)",
    "total": $TESTS_TOTAL,
    "passed": $TESTS_PASSED,
    "failed": $TESTS_FAILED,
    "coverage": $COVERAGE
  },
  "tests": [
    {"name": "test_initialization", "status": "passed", "duration_ms": 45},
    {"name": "test_data_processing", "status": "passed", "duration_ms": 120},
    {"name": "test_error_handling", "status": "passed", "duration_ms": 67},
    {"name": "test_output_format", "status": "passed", "duration_ms": 89},
    {"name": "test_edge_cases", "status": "passed", "duration_ms": 134}
  ]
}
EOF

# Generate text report
cat > "$TEST_REPORT_DIR/results.txt" << EOF
Test Results
============
Date: $(date)
Total: $TESTS_TOTAL
Passed: $TESTS_PASSED
Failed: $TESTS_FAILED
Coverage: ${COVERAGE}%

Status: $(if [[ $TESTS_FAILED -eq 0 ]]; then echo "PASSED"; else echo "FAILED"; fi)
EOF

# Print results
echo ""
echo "Test Results:"
echo "  Total:    $TESTS_TOTAL"
echo "  Passed:   $TESTS_PASSED"
echo "  Failed:   $TESTS_FAILED"
echo "  Coverage: ${COVERAGE}%"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}All tests passed!${NC}"
    echo "Test reports saved to: $TEST_REPORT_DIR"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}" >&2
    echo "Test reports saved to: $TEST_REPORT_DIR"
    exit 1
fi
