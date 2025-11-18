#!/usr/bin/env bash
#
# Cleanup Script
# Removes build artifacts and temporary files
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load configuration
if [[ -f "$SCRIPT_DIR/../shared/config.env" ]]; then
    source "$SCRIPT_DIR/../shared/config.env"
fi

BUILD_DIR="${BUILD_DIR:-$PROJECT_ROOT/build}"
TEST_REPORT_DIR="${TEST_REPORT_DIR:-$PROJECT_ROOT/test-reports}"

echo "========================================="
echo "Cleaning up Project"
echo "========================================="
echo ""

# Function to safely remove directory
safe_remove() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        echo "Removing: $dir"
        rm -rf "$dir"
        echo "  ✓ Removed"
    else
        echo "Skipping: $dir (doesn't exist)"
    fi
}

# Clean build artifacts
safe_remove "$BUILD_DIR"

# Clean test reports
safe_remove "$TEST_REPORT_DIR"

# Clean deployment records (optional)
read -p "Remove deployment records? (y/n): " remove_deployments
if [[ "$remove_deployments" == "y" ]]; then
    safe_remove "$PROJECT_ROOT/deployments"
fi

# Clean logs (optional)
read -p "Remove logs? (y/n): " remove_logs
if [[ "$remove_logs" == "y" ]]; then
    safe_remove "$PROJECT_ROOT/logs"
fi

# Clean temporary files
echo ""
echo "Removing temporary files..."
find "$PROJECT_ROOT" -name "*.tmp" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -name ".DS_Store" -delete 2>/dev/null || true

echo ""
echo "Cleanup completed!"

exit 0
