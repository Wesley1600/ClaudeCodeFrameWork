#!/usr/bin/env bash
#
# Deploy Script
# Deploys the application to the target environment
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
DEPLOY_ENV="${DEPLOY_ENV:-dev}"
DEPLOY_DRY_RUN="${DEPLOY_DRY_RUN:-}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================="
echo "Deploying Application"
echo "========================================="
echo "Environment: $DEPLOY_ENV"
echo "Dry run: ${DEPLOY_DRY_RUN:-no}"
echo ""

# Validate environment
case "$DEPLOY_ENV" in
    dev|development)
        echo "Deploying to DEVELOPMENT environment"
        ;;
    staging)
        echo "Deploying to STAGING environment"
        ;;
    prod|production)
        echo -e "${YELLOW}WARNING: Deploying to PRODUCTION environment${NC}"
        if [[ -z "$DEPLOY_DRY_RUN" ]]; then
            read -p "Are you sure? (yes/no): " confirm
            if [[ "$confirm" != "yes" ]]; then
                echo "Deployment cancelled."
                exit 0
            fi
        fi
        ;;
    *)
        echo -e "${RED}Error: Unknown environment '$DEPLOY_ENV'${NC}" >&2
        echo "Valid environments: dev, staging, prod"
        exit 1
        ;;
esac

# Check if build artifacts exist
if [[ ! -d "$BUILD_DIR" ]] || [[ ! -f "$BUILD_DIR/main" ]]; then
    echo -e "${RED}Error: Build artifacts not found. Run build.sh first.${NC}" >&2
    exit 1
fi

# Simulate deployment steps
echo ""
echo "Step 1: Preparing deployment..."
sleep 1

echo "Step 2: Uploading artifacts..."
if [[ -n "$DEPLOY_DRY_RUN" ]]; then
    echo -e "${YELLOW}[DRY RUN] Would upload artifacts to $DEPLOY_ENV${NC}"
else
    sleep 1
    echo "  - Uploaded: main"
    echo "  - Uploaded: metadata.json"
fi

echo "Step 3: Running health checks..."
if [[ -n "$DEPLOY_DRY_RUN" ]]; then
    echo -e "${YELLOW}[DRY RUN] Would run health checks${NC}"
else
    sleep 1
    echo "  ✓ Application responds"
    echo "  ✓ Database connected"
    echo "  ✓ All services healthy"
fi

echo "Step 4: Finalizing deployment..."
if [[ -n "$DEPLOY_DRY_RUN" ]]; then
    echo -e "${YELLOW}[DRY RUN] Would finalize deployment${NC}"
else
    sleep 1
fi

# Create deployment record
DEPLOY_RECORD_DIR="$PROJECT_ROOT/deployments"
mkdir -p "$DEPLOY_RECORD_DIR"

cat > "$DEPLOY_RECORD_DIR/latest.json" << EOF
{
  "environment": "$DEPLOY_ENV",
  "timestamp": "$(date -Iseconds)",
  "version": "1.0.0",
  "dry_run": ${DEPLOY_DRY_RUN:-false},
  "status": "success"
}
EOF

echo ""
if [[ -n "$DEPLOY_DRY_RUN" ]]; then
    echo -e "${YELLOW}Dry run completed successfully!${NC}"
else
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo "Environment: $DEPLOY_ENV"
    echo "Deployment record: $DEPLOY_RECORD_DIR/latest.json"
fi

exit 0
