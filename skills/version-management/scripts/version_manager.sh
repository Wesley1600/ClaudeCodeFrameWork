#!/bin/bash
# version_manager.sh
# Version management script for Claude Code skills
# Handles version creation, tagging, rollback, and changelog management

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VERSION_DIR=".versions"
CHANGELOG_FILE="CHANGELOG.md"
METADATA_FILE="metadata.json"

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

# Validate semantic version format
validate_version() {
    local version="$1"
    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "Invalid version format: $version"
        log_error "Expected format: MAJOR.MINOR.PATCH (e.g., 1.2.3)"
        return 1
    fi
    return 0
}

# Parse version components
parse_version() {
    local version="$1"
    echo "$version" | sed -E 's/^v?([0-9]+)\.([0-9]+)\.([0-9]+)$/\1 \2 \3/'
}

# Bump version number
bump_version() {
    local current="$1"
    local bump_type="$2"

    read -r major minor patch <<< "$(parse_version "$current")"

    case "$bump_type" in
        major)
            echo "$((major + 1)).0.0"
            ;;
        minor)
            echo "${major}.$((minor + 1)).0"
            ;;
        patch)
            echo "${major}.${minor}.$((patch + 1))"
            ;;
        *)
            log_error "Invalid bump type: $bump_type"
            log_error "Expected: major, minor, or patch"
            return 1
            ;;
    esac
}

# Initialize version management for a skill
init_version_management() {
    local skill_path="$1"
    local initial_version="${2:-0.1.0}"

    log_info "Initializing version management for skill at: $skill_path"

    # Validate skill path
    if [[ ! -d "$skill_path" ]]; then
        log_error "Skill directory not found: $skill_path"
        return 1
    fi

    if [[ ! -f "$skill_path/SKILL.md" ]]; then
        log_error "SKILL.md not found in: $skill_path"
        return 1
    fi

    # Validate initial version
    validate_version "$initial_version" || return 1

    # Create version directory
    local version_root="$skill_path/$VERSION_DIR"
    mkdir -p "$version_root"

    # Initialize changelog if it doesn't exist
    if [[ ! -f "$version_root/$CHANGELOG_FILE" ]]; then
        cat > "$version_root/$CHANGELOG_FILE" <<EOF
# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [$initial_version] - $(date -u +"%Y-%m-%d")

### Added
- Initial version of skill
- Version management initialized

EOF
        log_success "Created $CHANGELOG_FILE"
    fi

    # Create initial version
    create_version "$skill_path" "$initial_version" "Initial version"

    log_success "Version management initialized"
    log_info "Version directory: $version_root"
    log_info "Initial version: v$initial_version"
}

# Create a new version snapshot
create_version() {
    local skill_path="$1"
    local version="$2"
    local description="${3:-No description provided}"

    validate_version "$version" || return 1

    local version_root="$skill_path/$VERSION_DIR"
    local version_dir="$version_root/v$version"

    # Check if version already exists
    if [[ -d "$version_dir" ]]; then
        log_error "Version v$version already exists"
        log_info "Use a different version number or delete the existing version"
        return 1
    fi

    log_info "Creating version v$version..."

    # Create version directory
    mkdir -p "$version_dir"

    # Copy current files
    cp "$skill_path/SKILL.md" "$version_dir/"

    # Copy scripts directory if it exists
    if [[ -d "$skill_path/scripts" ]]; then
        cp -r "$skill_path/scripts" "$version_dir/"
        log_success "Copied scripts directory"
    fi

    # Copy templates directory if it exists
    if [[ -d "$skill_path/templates" ]]; then
        cp -r "$skill_path/templates" "$version_dir/"
        log_success "Copied templates directory"
    fi

    # Copy resources directory if it exists
    if [[ -d "$skill_path/resources" ]]; then
        cp -r "$skill_path/resources" "$version_dir/"
        log_success "Copied resources directory"
    fi

    # Get git commit hash if in a git repo
    local commit_hash="unknown"
    if git rev-parse --git-dir > /dev/null 2>&1; then
        commit_hash=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    fi

    # Get author from git config or use default
    local author="Claude <noreply@anthropic.com>"
    if git config user.name > /dev/null 2>&1; then
        local git_name=$(git config user.name)
        local git_email=$(git config user.email)
        author="$git_name <$git_email>"
    fi

    # Create metadata file
    local tracked_files=("SKILL.md")
    [[ -d "$skill_path/scripts" ]] && tracked_files+=("scripts/")
    [[ -d "$skill_path/templates" ]] && tracked_files+=("templates/")
    [[ -d "$skill_path/resources" ]] && tracked_files+=("resources/")

    # Build files array for JSON
    local files_json="["
    for file in "${tracked_files[@]}"; do
        files_json+="\"$file\","
    done
    files_json="${files_json%,}]"  # Remove trailing comma

    cat > "$version_dir/$METADATA_FILE" <<EOF
{
  "version": "$version",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "author": "$author",
  "commit": "$commit_hash",
  "description": "$description",
  "files_tracked": $files_json
}
EOF

    log_success "Created metadata file"
    log_success "Version v$version created successfully"
    log_info "Location: $version_dir"
    log_info "Files tracked: ${tracked_files[*]}"

    # Create git tag if in a git repo
    if git rev-parse --git-dir > /dev/null 2>&1; then
        if git tag -a "v$version" -m "$description" 2>/dev/null; then
            log_success "Created git tag: v$version"
        else
            log_warning "Git tag v$version already exists or could not be created"
        fi
    fi
}

# List all versions
list_versions() {
    local skill_path="$1"
    local version_root="$skill_path/$VERSION_DIR"

    if [[ ! -d "$version_root" ]]; then
        log_error "Version management not initialized for this skill"
        log_info "Run: init_version_management \"$skill_path\""
        return 1
    fi

    echo ""
    echo "Version History for skill at: $skill_path"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "%-10s | %-20s | %s\n" "VERSION" "DATE" "DESCRIPTION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Find all version directories and sort
    for version_dir in "$version_root"/v*/; do
        if [[ -f "$version_dir/$METADATA_FILE" ]]; then
            local version=$(jq -r '.version' "$version_dir/$METADATA_FILE")
            local timestamp=$(jq -r '.timestamp' "$version_dir/$METADATA_FILE")
            local description=$(jq -r '.description' "$version_dir/$METADATA_FILE")

            # Format timestamp
            local date_formatted=$(date -d "$timestamp" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "$timestamp")

            # Truncate description if too long
            if [[ ${#description} -gt 50 ]]; then
                description="${description:0:47}..."
            fi

            printf "%-10s | %-20s | %s\n" "v$version" "$date_formatted" "$description"
        fi
    done | sort -V

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Show version details
show_version() {
    local skill_path="$1"
    local version="$2"

    # Remove 'v' prefix if present
    version="${version#v}"

    local version_dir="$skill_path/$VERSION_DIR/v$version"

    if [[ ! -d "$version_dir" ]]; then
        log_error "Version v$version not found"
        return 1
    fi

    if [[ ! -f "$version_dir/$METADATA_FILE" ]]; then
        log_error "Metadata file not found for version v$version"
        return 1
    fi

    echo ""
    echo "Version Details: v$version"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Parse and display metadata
    local metadata=$(cat "$version_dir/$METADATA_FILE")

    echo "Version:     $(echo "$metadata" | jq -r '.version')"
    echo "Date:        $(echo "$metadata" | jq -r '.timestamp')"
    echo "Author:      $(echo "$metadata" | jq -r '.author')"
    echo "Commit:      $(echo "$metadata" | jq -r '.commit')"
    echo ""
    echo "Description:"
    echo "  $(echo "$metadata" | jq -r '.description')"
    echo ""
    echo "Files Tracked:"
    echo "$metadata" | jq -r '.files_tracked[]' | sed 's/^/  - /'
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Rollback to a previous version
rollback_version() {
    local skill_path="$1"
    local target_version="$2"
    local create_backup="${3:-yes}"

    # Remove 'v' prefix if present
    target_version="${target_version#v}"

    local version_dir="$skill_path/$VERSION_DIR/v$target_version"

    if [[ ! -d "$version_dir" ]]; then
        log_error "Target version v$target_version not found"
        return 1
    fi

    log_warning "ROLLBACK OPERATION"
    log_warning "This will replace current files with version v$target_version"
    echo ""

    # Create backup if requested
    if [[ "$create_backup" == "yes" ]]; then
        local backup_dir="$skill_path/$VERSION_DIR/backup-$(date -u +"%Y%m%d-%H%M%S")"
        mkdir -p "$backup_dir"

        log_info "Creating backup of current state..."
        cp "$skill_path/SKILL.md" "$backup_dir/" 2>/dev/null || true
        [[ -d "$skill_path/scripts" ]] && cp -r "$skill_path/scripts" "$backup_dir/" 2>/dev/null || true
        [[ -d "$skill_path/templates" ]] && cp -r "$skill_path/templates" "$backup_dir/" 2>/dev/null || true
        [[ -d "$skill_path/resources" ]] && cp -r "$skill_path/resources" "$backup_dir/" 2>/dev/null || true

        log_success "Backup created at: $backup_dir"
    fi

    log_info "Restoring files from v$target_version..."

    # Restore files
    cp "$version_dir/SKILL.md" "$skill_path/"
    log_success "Restored SKILL.md"

    # Restore scripts
    if [[ -d "$version_dir/scripts" ]]; then
        rm -rf "$skill_path/scripts"
        cp -r "$version_dir/scripts" "$skill_path/"
        log_success "Restored scripts/"
    fi

    # Restore templates
    if [[ -d "$version_dir/templates" ]]; then
        rm -rf "$skill_path/templates"
        cp -r "$version_dir/templates" "$skill_path/"
        log_success "Restored templates/"
    fi

    # Restore resources
    if [[ -d "$version_dir/resources" ]]; then
        rm -rf "$skill_path/resources"
        cp -r "$version_dir/resources" "$skill_path/"
        log_success "Restored resources/"
    fi

    log_success "Rollback to v$target_version completed successfully"

    if [[ "$create_backup" == "yes" ]]; then
        log_info "Previous state backed up to: $backup_dir"
    fi
}

# Main command dispatcher
main() {
    local command="${1:-help}"

    case "$command" in
        init)
            if [[ $# -lt 2 ]]; then
                log_error "Usage: $0 init <skill_path> [initial_version]"
                return 1
            fi
            init_version_management "${2}" "${3:-0.1.0}"
            ;;
        create)
            if [[ $# -lt 3 ]]; then
                log_error "Usage: $0 create <skill_path> <version> [description]"
                return 1
            fi
            create_version "${2}" "${3}" "${4:-No description provided}"
            ;;
        list)
            if [[ $# -lt 2 ]]; then
                log_error "Usage: $0 list <skill_path>"
                return 1
            fi
            list_versions "${2}"
            ;;
        show)
            if [[ $# -lt 3 ]]; then
                log_error "Usage: $0 show <skill_path> <version>"
                return 1
            fi
            show_version "${2}" "${3}"
            ;;
        rollback)
            if [[ $# -lt 3 ]]; then
                log_error "Usage: $0 rollback <skill_path> <version> [create_backup]"
                return 1
            fi
            rollback_version "${2}" "${3}" "${4:-yes}"
            ;;
        bump)
            if [[ $# -lt 3 ]]; then
                log_error "Usage: $0 bump <current_version> <major|minor|patch>"
                return 1
            fi
            bump_version "${2}" "${3}"
            ;;
        help|--help|-h)
            cat <<EOF
Version Manager - Claude Code Skill Version Management

USAGE:
    $0 <command> [arguments]

COMMANDS:
    init <skill_path> [version]           Initialize version management (default: 0.1.0)
    create <skill_path> <version> [desc]  Create new version snapshot
    list <skill_path>                     List all versions
    show <skill_path> <version>           Show version details
    rollback <skill_path> <version>       Rollback to previous version
    bump <version> <major|minor|patch>    Calculate next version number
    help                                  Show this help message

EXAMPLES:
    $0 init ./skills/my-skill 0.1.0
    $0 create ./skills/my-skill 1.0.0 "Initial release"
    $0 list ./skills/my-skill
    $0 show ./skills/my-skill 1.0.0
    $0 rollback ./skills/my-skill 1.0.0
    $0 bump 1.0.0 minor

EOF
            ;;
        *)
            log_error "Unknown command: $command"
            log_info "Run '$0 help' for usage information"
            return 1
            ;;
    esac
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
