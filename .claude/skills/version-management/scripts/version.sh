#!/bin/bash
# Version Management Helper Script
# Provides utilities for managing skill versions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
error() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Show usage
usage() {
    cat << EOF
Usage: version.sh <command> [options]

Commands:
    init <skill-name>           Initialize version management for a skill
    list [skill-name]           List all versions (optionally filter by skill)
    tag <skill-name> <version>  Create a new version tag
    rollback <skill-name> <ver> Rollback to a specific version
    diff <skill> <v1> <v2>      Show differences between versions
    changelog <skill-name>      Generate changelog from commits
    current <skill-name>        Show current version
    help                        Show this help message

Examples:
    version.sh init my-skill
    version.sh list my-skill
    version.sh tag my-skill 1.2.3
    version.sh rollback my-skill 1.2.0
    version.sh diff my-skill 1.2.0 1.2.3
    version.sh changelog my-skill
EOF
    exit 0
}

# Initialize version management for a skill
init_skill() {
    local skill_name="$1"
    local skill_dir="$SKILLS_DIR/$skill_name"

    if [ -z "$skill_name" ]; then
        error "Skill name is required"
    fi

    if [ ! -d "$skill_dir" ]; then
        error "Skill directory not found: $skill_dir"
    fi

    if [ ! -f "$skill_dir/SKILL.md" ]; then
        error "SKILL.md not found in $skill_dir"
    fi

    info "Initializing version management for '$skill_name'..."

    # Create initial CHANGELOG.md if it doesn't exist
    if [ ! -f "$skill_dir/CHANGELOG.md" ]; then
        cat > "$skill_dir/CHANGELOG.md" << EOF
# Changelog

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - $(date +%Y-%m-%d)

### Added
- Initial version of the skill
- Core functionality implemented
EOF
        success "Created CHANGELOG.md"
    else
        info "CHANGELOG.md already exists"
    fi

    # Create .version metadata file
    cat > "$skill_dir/.version" << EOF
{
  "name": "$skill_name",
  "version": "0.1.0",
  "released": "$(date +%Y-%m-%d)",
  "stable": true,
  "deprecated": false
}
EOF
    success "Created .version metadata file"

    # Add and commit
    cd "$skill_dir"
    git add CHANGELOG.md .version 2>/dev/null || true

    if git diff --cached --quiet; then
        info "No changes to commit"
    else
        git commit -m "Initialize version management for $skill_name v0.1.0"
        success "Committed initial version files"
    fi

    # Create initial tag
    local tag_name="skill/$skill_name/v0.1.0"
    if git tag -l "$tag_name" | grep -q "$tag_name"; then
        warning "Tag $tag_name already exists"
    else
        git tag -a "$tag_name" -m "Initial version of $skill_name"
        success "Created tag: $tag_name"
    fi

    success "Version management initialized for '$skill_name'"
    info "Current version: 0.1.0"
}

# List all versions
list_versions() {
    local skill_name="$1"
    local pattern="skill/"

    if [ -n "$skill_name" ]; then
        pattern="skill/$skill_name/"
    fi

    pattern="${pattern}v*"

    info "Available versions:"
    git tag -l "$pattern" --sort=-version:refname --format='%(refname:short)%09%(creatordate:short)%09%(contents:subject)' | \
        column -t -s $'\t' || echo "No versions found"
}

# Create a new version tag
create_tag() {
    local skill_name="$1"
    local version="$2"
    local skill_dir="$SKILLS_DIR/$skill_name"

    if [ -z "$skill_name" ] || [ -z "$version" ]; then
        error "Skill name and version are required"
    fi

    # Validate version format (X.Y.Z)
    if ! echo "$version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
        error "Invalid version format. Use semantic versioning (e.g., 1.2.3)"
    fi

    if [ ! -d "$skill_dir" ]; then
        error "Skill directory not found: $skill_dir"
    fi

    local tag_name="skill/$skill_name/v$version"

    # Check if tag already exists
    if git tag -l "$tag_name" | grep -q "$tag_name"; then
        error "Tag $tag_name already exists"
    fi

    info "Creating version tag: $tag_name"

    # Update .version file if it exists
    if [ -f "$skill_dir/.version" ]; then
        cd "$skill_dir"
        # Update version in .version file using sed
        sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$version\"/" .version
        sed -i "s/\"released\": \"[^\"]*\"/\"released\": \"$(date +%Y-%m-%d)\"/" .version

        git add .version
        git commit -m "Update version to $version" 2>/dev/null || true
    fi

    # Create the tag
    read -p "Enter release notes (or press Enter for default): " notes
    if [ -z "$notes" ]; then
        notes="Release $version"
    fi

    git tag -a "$tag_name" -m "$notes"
    success "Created tag: $tag_name"

    info "Don't forget to update CHANGELOG.md and push the tag:"
    echo "  git push origin $tag_name"
}

# Rollback to a specific version
rollback_version() {
    local skill_name="$1"
    local version="$2"
    local skill_dir="$SKILLS_DIR/$skill_name"

    if [ -z "$skill_name" ] || [ -z "$version" ]; then
        error "Skill name and version are required"
    fi

    if [ ! -d "$skill_dir" ]; then
        error "Skill directory not found: $skill_dir"
    fi

    local tag_name="skill/$skill_name/v$version"

    # Check if tag exists
    if ! git tag -l "$tag_name" | grep -q "$tag_name"; then
        error "Tag $tag_name does not exist"
    fi

    warning "This will rollback '$skill_name' to version $version"
    read -p "Are you sure? (y/N): " confirm

    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        info "Rollback cancelled"
        exit 0
    fi

    # Create backup tag
    local backup_tag="skill/$skill_name/backup-$(date +%Y%m%d-%H%M%S)"
    git tag -a "$backup_tag" -m "Backup before rollback to $version"
    success "Created backup tag: $backup_tag"

    # Rollback files
    cd "$skill_dir"
    git checkout "$tag_name" -- . 2>/dev/null || error "Failed to checkout version $version"

    # Commit the rollback
    git add .
    git commit -m "Rollback $skill_name to v$version" 2>/dev/null || info "No changes to commit"

    success "Rolled back to version $version"
    warning "Remember to update CHANGELOG.md to document this rollback"
}

# Show diff between versions
diff_versions() {
    local skill_name="$1"
    local version1="$2"
    local version2="$3"

    if [ -z "$skill_name" ] || [ -z "$version1" ] || [ -z "$version2" ]; then
        error "Skill name and two versions are required"
    fi

    local tag1="skill/$skill_name/v$version1"
    local tag2="skill/$skill_name/v$version2"

    # Check if tags exist
    if ! git tag -l "$tag1" | grep -q "$tag1"; then
        error "Tag $tag1 does not exist"
    fi

    if ! git tag -l "$tag2" | grep -q "$tag2"; then
        error "Tag $tag2 does not exist"
    fi

    info "Differences between $version1 and $version2:"
    echo ""

    git diff "$tag1".."$tag2" -- "$SKILLS_DIR/$skill_name/"
}

# Generate changelog from commits
generate_changelog() {
    local skill_name="$1"

    if [ -z "$skill_name" ]; then
        error "Skill name is required"
    fi

    # Get the last tag
    local last_tag=$(git tag -l "skill/$skill_name/v*" --sort=-version:refname | head -n 1)

    if [ -z "$last_tag" ]; then
        error "No versions found for $skill_name"
    fi

    info "Commits since $last_tag:"
    echo ""

    git log "$last_tag"..HEAD --pretty=format:"- %s (%h)" -- "$SKILLS_DIR/$skill_name/" | \
        grep -v "^$" || echo "No commits since last version"
}

# Show current version
show_current() {
    local skill_name="$1"
    local skill_dir="$SKILLS_DIR/$skill_name"

    if [ -z "$skill_name" ]; then
        error "Skill name is required"
    fi

    if [ ! -d "$skill_dir" ]; then
        error "Skill directory not found: $skill_dir"
    fi

    # Try to get version from .version file
    if [ -f "$skill_dir/.version" ]; then
        local version=$(grep '"version"' "$skill_dir/.version" | sed 's/.*"version": "\([^"]*\)".*/\1/')
        if [ -n "$version" ]; then
            success "Current version: $version"
            return
        fi
    fi

    # Otherwise, get latest tag
    local latest_tag=$(git tag -l "skill/$skill_name/v*" --sort=-version:refname | head -n 1)

    if [ -n "$latest_tag" ]; then
        local version=$(echo "$latest_tag" | sed 's/.*\/v//')
        success "Latest tagged version: $version"
    else
        warning "No version found for $skill_name"
    fi
}

# Main command dispatcher
case "${1:-}" in
    init)
        init_skill "$2"
        ;;
    list)
        list_versions "$2"
        ;;
    tag)
        create_tag "$2" "$3"
        ;;
    rollback)
        rollback_version "$2" "$3"
        ;;
    diff)
        diff_versions "$2" "$3" "$4"
        ;;
    changelog)
        generate_changelog "$2"
        ;;
    current)
        show_current "$2"
        ;;
    help|--help|-h|"")
        usage
        ;;
    *)
        error "Unknown command: $1"
        ;;
esac
