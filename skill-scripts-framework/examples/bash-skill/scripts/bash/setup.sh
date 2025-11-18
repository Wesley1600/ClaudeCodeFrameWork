#!/usr/bin/env bash
#
# Setup Script
# Sets up the development environment
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "========================================="
echo "Setting up Development Environment"
echo "========================================="
echo "Project root: $PROJECT_ROOT"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p "$PROJECT_ROOT"/{build,test-reports,deployments,logs}

# Check dependencies
echo ""
echo "Checking dependencies..."

check_command() {
    if command -v "$1" &> /dev/null; then
        echo "  ✓ $1 found"
        return 0
    else
        echo "  ✗ $1 not found"
        return 1
    fi
}

MISSING_DEPS=0
check_command bash || ((MISSING_DEPS++))
check_command grep || ((MISSING_DEPS++))
check_command sed || ((MISSING_DEPS++))
check_command awk || ((MISSING_DEPS++))

if [[ $MISSING_DEPS -gt 0 ]]; then
    echo ""
    echo "WARNING: Some dependencies are missing"
else
    echo ""
    echo "All dependencies satisfied"
fi

# Initialize configuration if it doesn't exist
if [[ ! -f "$SCRIPT_DIR/../shared/config.env" ]]; then
    echo ""
    echo "Creating default configuration..."
    cat > "$SCRIPT_DIR/../shared/config.env" << 'EOF'
# Build Automation Configuration

# Build settings
BUILD_DIR="build"
BUILD_TYPE="release"

# Test settings
TEST_REPORT_DIR="test-reports"

# Deployment settings
DEPLOY_ENV="dev"

# Logging
LOG_LEVEL="info"
EOF
    echo "  Created: scripts/shared/config.env"
fi

echo ""
echo "Setup completed successfully!"
echo ""
echo "Directory structure:"
tree -L 2 "$PROJECT_ROOT" 2>/dev/null || find "$PROJECT_ROOT" -maxdepth 2 -type d

exit 0
