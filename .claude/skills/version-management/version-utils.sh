#!/bin/bash

# Version Management Utility Script
# Provides helper functions for managing skill and document versions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not a git repository!"
        exit 1
    fi
}

# Create a new version tag
create_version_tag() {
    local version=$1
    local message=$2
    local path=${3:-.}

    check_git_repo

    if [ -z "$version" ]; then
        print_error "Version number required (e.g., v1.0.0)"
        exit 1
    fi

    # Add 'v' prefix if not present
    if [[ ! $version =~ ^v ]]; then
        version="v$version"
    fi

    # Check if tag already exists
    if git rev-parse "$version" >/dev/null 2>&1; then
        print_warning "Tag $version already exists!"
        read -p "Delete and recreate? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git tag -d "$version"
            print_info "Deleted existing tag $version"
        else
            exit 1
        fi
    fi

    # Create annotated tag
    if [ -z "$message" ]; then
        git tag -a "$version" -m "Release $version"
    else
        git tag -a "$version" -m "$message"
    fi

    print_success "Created tag $version"
}

# List all version tags
list_versions() {
    local path=${1:-.}

    check_git_repo

    print_info "Version tags (newest first):"
    echo

    git tag -l "v*" --sort=-version:refname --format="%(refname:short)%09%(creatordate:short)%09%(subject)" | \
    while IFS=$'\t' read -r tag date subject; do
        echo -e "${GREEN}$tag${NC}\t$date\t$subject"
    done

    echo
    local count=$(git tag -l "v*" | wc -l)
    print_info "Total versions: $count"
}

# Show changes between versions
compare_versions() {
    local from_version=$1
    local to_version=${2:-HEAD}
    local path=${3:-.}

    check_git_repo

    if [ -z "$from_version" ]; then
        print_error "Source version required"
        exit 1
    fi

    print_info "Changes from $from_version to $to_version:"
    echo

    if [ "$path" != "." ]; then
        git log --oneline "$from_version..$to_version" -- "$path"
        echo
        git diff --stat "$from_version..$to_version" -- "$path"
    else
        git log --oneline "$from_version..$to_version"
        echo
        git diff --stat "$from_version..$to_version"
    fi
}

# Rollback to a previous version
rollback_version() {
    local target_version=$1
    local path=$2

    check_git_repo

    if [ -z "$target_version" ]; then
        print_error "Target version required"
        exit 1
    fi

    if [ -z "$path" ]; then
        print_error "Path required (use '.' for entire repo)"
        exit 1
    fi

    # Verify target version exists
    if ! git rev-parse "$target_version" >/dev/null 2>&1; then
        print_error "Version $target_version does not exist"
        exit 1
    fi

    # Create backup tag
    local backup_tag="backup-$(date +%Y%m%d-%H%M%S)"
    git tag -a "$backup_tag" -m "Backup before rollback to $target_version"
    print_success "Created backup tag: $backup_tag"

    # Confirm rollback
    print_warning "About to rollback $path to $target_version"
    read -p "Continue? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Rollback cancelled"
        exit 0
    fi

    # Perform rollback
    git checkout "$target_version" -- "$path"

    print_success "Rolled back $path to $target_version"
    print_info "Review changes with: git diff --staged"
    print_info "Commit with: git commit -m 'Rollback to $target_version'"
}

# Initialize version tracking for a new skill
init_version_tracking() {
    local skill_path=$1

    check_git_repo

    if [ -z "$skill_path" ]; then
        print_error "Skill path required (e.g., .claude/skills/my-skill)"
        exit 1
    fi

    if [ ! -d "$skill_path" ]; then
        print_error "Directory $skill_path does not exist"
        exit 1
    fi

    # Create CHANGELOG.md if it doesn't exist
    local changelog="$skill_path/CHANGELOG.md"
    if [ ! -f "$changelog" ]; then
        cat > "$changelog" << 'EOF'
# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Initial version tracking setup

## [1.0.0] - $(date +%Y-%m-%d)
### Added
- Initial release
EOF
        print_success "Created $changelog"
    fi

    # Add and commit
    git add "$skill_path"

    if git diff --staged --quiet; then
        print_info "No changes to commit"
    else
        git commit -m "Initialize version tracking for $(basename $skill_path)"
        print_success "Committed version tracking initialization"

        # Create initial tag
        read -p "Create v1.0.0 tag? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            create_version_tag "v1.0.0" "Initial release of $(basename $skill_path)"
        fi
    fi
}

# Generate version report
generate_report() {
    local path=${1:-.}

    check_git_repo

    local current_version=$(git describe --tags --abbrev=0 2>/dev/null || echo "No tags")
    local total_versions=$(git tag -l "v*" | wc -l)
    local last_modified=$(git log -1 --format=%cd --date=short -- "$path" 2>/dev/null || echo "N/A")

    echo "# Version Report"
    echo
    echo "**Path:** $path"
    echo "**Current Version:** $current_version"
    echo "**Last Modified:** $last_modified"
    echo "**Total Versions:** $total_versions"
    echo
    echo "## Recent Changes"
    echo
    git log -5 --oneline -- "$path" 2>/dev/null || echo "No commits found"
    echo
    echo "## Version Timeline"
    echo
    git tag -l "v*" --sort=-version:refname --format="- %(refname:short) - %(creatordate:short) - %(subject)" 2>/dev/null || echo "No version tags found"
}

# Update version in SKILL.yaml
update_skill_version() {
    local skill_path=$1
    local new_version=$2

    if [ -z "$skill_path" ] || [ -z "$new_version" ]; then
        print_error "Usage: update_skill_version <skill_path> <version>"
        exit 1
    fi

    local skill_yaml="$skill_path/SKILL.yaml"

    if [ ! -f "$skill_yaml" ]; then
        print_error "$skill_yaml not found"
        exit 1
    fi

    # Remove 'v' prefix if present
    new_version=${new_version#v}

    # Update version in SKILL.yaml
    if grep -q "^version:" "$skill_yaml"; then
        sed -i "s/^version:.*/version: $new_version/" "$skill_yaml"
        print_success "Updated version in $skill_yaml to $new_version"
    else
        print_error "No version field found in $skill_yaml"
        exit 1
    fi
}

# Show help
show_help() {
    cat << EOF
Version Management Utility Script

Usage: $0 <command> [options]

Commands:
    tag <version> [message] [path]     Create a new version tag
    list [path]                        List all version tags
    compare <from> [to] [path]         Compare two versions
    rollback <version> <path>          Rollback to a previous version
    init <skill-path>                  Initialize version tracking for a skill
    report [path]                      Generate version report
    update-skill <skill-path> <version> Update version in SKILL.yaml
    help                               Show this help message

Examples:
    $0 tag v1.2.0 "Added new features"
    $0 list
    $0 compare v1.0.0 v1.1.0 .claude/skills/my-skill
    $0 rollback v1.0.0 .claude/skills/my-skill
    $0 init .claude/skills/new-skill
    $0 report .claude/skills/my-skill
    $0 update-skill .claude/skills/my-skill 1.2.0

Environment:
    Set NO_COLOR=1 to disable colored output
EOF
}

# Main command dispatcher
main() {
    local command=$1
    shift

    case "$command" in
        tag)
            create_version_tag "$@"
            ;;
        list)
            list_versions "$@"
            ;;
        compare)
            compare_versions "$@"
            ;;
        rollback)
            rollback_version "$@"
            ;;
        init)
            init_version_tracking "$@"
            ;;
        report)
            generate_report "$@"
            ;;
        update-skill)
            update_skill_version "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main if script is executed directly
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    main "$@"
fi
