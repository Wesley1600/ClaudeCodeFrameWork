#!/usr/bin/env bash
#
# Build Script
# Compiles the project and generates build artifacts
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
BUILD_TYPE="${BUILD_TYPE:-release}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================="
echo "Building Project"
echo "========================================="
echo "Build directory: $BUILD_DIR"
echo "Build type: $BUILD_TYPE"
echo ""

# Create build directory
echo "Creating build directory..."
mkdir -p "$BUILD_DIR"

# Simulate build process
echo "Compiling source files..."
sleep 1

# Create mock build artifacts
cat > "$BUILD_DIR/main" << 'EOF'
#!/usr/bin/env bash
echo "Mock application running..."
echo "Version: 1.0.0"
EOF
chmod +x "$BUILD_DIR/main"

cat > "$BUILD_DIR/metadata.json" << EOF
{
  "version": "1.0.0",
  "build_type": "$BUILD_TYPE",
  "build_date": "$(date -Iseconds)",
  "artifacts": ["main"]
}
EOF

echo -e "${GREEN}Build completed successfully!${NC}"
echo "Artifacts created in: $BUILD_DIR"
echo ""

# List artifacts
echo "Build artifacts:"
ls -lh "$BUILD_DIR"

exit 0
