#!/usr/bin/env bash
#
# Complete Build Pipeline
# Executes build → test → deploy with proper error handling
#

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load configuration
if [[ -f "$SCRIPT_DIR/../shared/config.env" ]]; then
    source "$SCRIPT_DIR/../shared/config.env"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Pipeline stage runner
run_stage() {
    local stage_name="$1"
    local script_path="$2"
    local error_code="$3"

    log_info "Starting stage: $stage_name"

    if bash "$script_path"; then
        log_success "$stage_name completed"
        return 0
    else
        log_error "$stage_name failed"
        return "$error_code"
    fi
}

# Main pipeline
main() {
    log_info "========================================="
    log_info "Starting Build Pipeline"
    log_info "========================================="
    log_info "Project: $PROJECT_ROOT"
    log_info "Environment: ${DEPLOY_ENV:-dev}"
    log_info ""

    # Stage 1: Build
    if ! run_stage "Build" "$SCRIPT_DIR/build.sh" 1; then
        log_error "Pipeline failed at BUILD stage"
        return 1
    fi

    # Stage 2: Test
    if ! run_stage "Test" "$SCRIPT_DIR/test.sh" 2; then
        log_error "Pipeline failed at TEST stage"
        return 2
    fi

    # Stage 3: Deploy
    if ! run_stage "Deploy" "$SCRIPT_DIR/deploy.sh" 3; then
        log_error "Pipeline failed at DEPLOY stage"
        return 3
    fi

    log_info ""
    log_info "========================================="
    log_success "Pipeline completed successfully!"
    log_info "========================================="

    return 0
}

# Run main function
main "$@"
