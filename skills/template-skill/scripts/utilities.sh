#!/bin/bash
# Bash utilities for Claude Skills

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log functions with colored output
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Check if a file exists
file_exists() {
    if [ -f "$1" ]; then
        return 0
    else
        return 1
    fi
}

# Check if a directory exists
dir_exists() {
    if [ -d "$1" ]; then
        return 0
    else
        return 1
    fi
}

# Create a directory if it doesn't exist
ensure_dir() {
    if ! dir_exists "$1"; then
        mkdir -p "$1"
        log_success "Created directory: $1"
    fi
}

# Count lines in a file
count_lines() {
    if file_exists "$1"; then
        wc -l < "$1"
    else
        log_error "File not found: $1"
        return 1
    fi
}

# Get file size in human-readable format
get_file_size() {
    if file_exists "$1"; then
        du -h "$1" | cut -f1
    else
        log_error "File not found: $1"
        return 1
    fi
}

# Search for a pattern in files
search_pattern() {
    local pattern=$1
    local directory=${2:-.}

    if command -v rg &> /dev/null; then
        rg "$pattern" "$directory"
    elif command -v grep &> /dev/null; then
        grep -r "$pattern" "$directory"
    else
        log_error "Neither rg nor grep found"
        return 1
    fi
}

# Create a backup of a file
backup_file() {
    local file=$1
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup="${file}.backup.${timestamp}"

    if file_exists "$file"; then
        cp "$file" "$backup"
        log_success "Created backup: $backup"
    else
        log_error "File not found: $file"
        return 1
    fi
}

# Count files in a directory
count_files() {
    local directory=${1:-.}
    if dir_exists "$directory"; then
        find "$directory" -type f | wc -l
    else
        log_error "Directory not found: $directory"
        return 1
    fi
}

# List files with specific extension
list_by_extension() {
    local extension=$1
    local directory=${2:-.}

    if dir_exists "$directory"; then
        find "$directory" -type f -name "*.$extension"
    else
        log_error "Directory not found: $directory"
        return 1
    fi
}

# Export functions for use in other scripts
export -f log_info
export -f log_success
export -f log_warn
export -f log_error
export -f file_exists
export -f dir_exists
export -f ensure_dir
