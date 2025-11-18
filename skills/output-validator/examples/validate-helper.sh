#!/bin/bash
# Output Validator Helper Script
# This script demonstrates validation tool detection and execution
# Can be used standalone or as a reference for the skill

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_ERRORS=0
TOTAL_WARNINGS=0
TOTAL_INFO=0

echo -e "${BLUE}=== Output Validator ===${NC}"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect file type
detect_file_type() {
    local file=$1
    case "$file" in
        *.js) echo "javascript" ;;
        *.jsx) echo "javascript" ;;
        *.ts) echo "typescript" ;;
        *.tsx) echo "typescript" ;;
        *.py) echo "python" ;;
        *.go) echo "go" ;;
        *.rs) echo "rust" ;;
        *.rb) echo "ruby" ;;
        *.sh) echo "shell" ;;
        *.md) echo "markdown" ;;
        *.json) echo "json" ;;
        *.yml|*.yaml) echo "yaml" ;;
        Dockerfile*) echo "docker" ;;
        *.css|*.scss) echo "css" ;;
        *) echo "unknown" ;;
    esac
}

# Function to validate JavaScript/TypeScript
validate_javascript() {
    local file=$1
    echo -e "${BLUE}Validating JavaScript/TypeScript: $file${NC}"

    # Check ESLint
    if command_exists npx && [ -f "package.json" ]; then
        echo "  Running ESLint..."
        if npx eslint "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓ ESLint: No issues${NC}"
        else
            echo -e "  ${YELLOW}⚠ ESLint found issues${NC}"
        fi
    fi

    # Check Prettier
    if command_exists npx && [ -f "package.json" ]; then
        echo "  Checking Prettier formatting..."
        if npx prettier --check "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓ Prettier: Formatted correctly${NC}"
        else
            echo -e "  ${YELLOW}⚠ Prettier: Formatting issues (can auto-fix)${NC}"
        fi
    fi

    # Check TypeScript
    if [[ "$file" =~ \.(ts|tsx)$ ]] && command_exists npx; then
        echo "  Running TypeScript compiler..."
        if npx tsc --noEmit "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓ TypeScript: No type errors${NC}"
        else
            echo -e "  ${RED}✗ TypeScript: Type errors found${NC}"
        fi
    fi

    echo ""
}

# Function to validate Python
validate_python() {
    local file=$1
    echo -e "${BLUE}Validating Python: $file${NC}"

    # Check Pylint
    if command_exists pylint; then
        echo "  Running Pylint..."
        if pylint "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓ Pylint: No issues${NC}"
        else
            echo -e "  ${YELLOW}⚠ Pylint found issues${NC}"
        fi
    fi

    # Check Flake8
    if command_exists flake8; then
        echo "  Running Flake8..."
        if flake8 "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓ Flake8: No issues${NC}"
        else
            echo -e "  ${YELLOW}⚠ Flake8 found issues${NC}"
        fi
    fi

    # Check Black formatting
    if command_exists black; then
        echo "  Checking Black formatting..."
        if black --check "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓ Black: Formatted correctly${NC}"
        else
            echo -e "  ${YELLOW}⚠ Black: Formatting issues (can auto-fix)${NC}"
        fi
    fi

    # Check mypy
    if command_exists mypy; then
        echo "  Running mypy type checking..."
        if mypy "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓ mypy: No type errors${NC}"
        else
            echo -e "  ${YELLOW}⚠ mypy found type issues${NC}"
        fi
    fi

    echo ""
}

# Function to validate Shell scripts
validate_shell() {
    local file=$1
    echo -e "${BLUE}Validating Shell script: $file${NC}"

    # Check shellcheck
    if command_exists shellcheck; then
        echo "  Running shellcheck..."
        if shellcheck "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓ shellcheck: No issues${NC}"
        else
            echo -e "  ${YELLOW}⚠ shellcheck found issues${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠ shellcheck not installed${NC}"
    fi

    echo ""
}

# Function to validate Markdown
validate_markdown() {
    local file=$1
    echo -e "${BLUE}Validating Markdown: $file${NC}"

    # Check markdownlint
    if command_exists markdownlint; then
        echo "  Running markdownlint..."
        if markdownlint "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓ markdownlint: No issues${NC}"
        else
            echo -e "  ${YELLOW}⚠ markdownlint found issues${NC}"
        fi
    fi

    # Check write-good
    if command_exists write-good; then
        echo "  Running write-good..."
        if write-good "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓ write-good: No issues${NC}"
        else
            echo -e "  ${YELLOW}⚠ write-good found issues${NC}"
        fi
    fi

    echo ""
}

# Function to display available tools
show_available_tools() {
    echo -e "${BLUE}=== Available Validation Tools ===${NC}"
    echo ""

    echo "JavaScript/TypeScript:"
    command_exists npx && echo "  ✓ npx (for ESLint, Prettier, tsc)" || echo "  ✗ npx not found"

    echo ""
    echo "Python:"
    command_exists pylint && echo "  ✓ pylint" || echo "  ✗ pylint not found"
    command_exists flake8 && echo "  ✓ flake8" || echo "  ✗ flake8 not found"
    command_exists black && echo "  ✓ black" || echo "  ✗ black not found"
    command_exists mypy && echo "  ✓ mypy" || echo "  ✗ mypy not found"

    echo ""
    echo "Shell:"
    command_exists shellcheck && echo "  ✓ shellcheck" || echo "  ✗ shellcheck not found"

    echo ""
    echo "Markdown:"
    command_exists markdownlint && echo "  ✓ markdownlint" || echo "  ✗ markdownlint not found"
    command_exists write-good && echo "  ✓ write-good" || echo "  ✗ write-good not found"

    echo ""
}

# Main validation function
validate_file() {
    local file=$1

    if [ ! -f "$file" ]; then
        echo -e "${RED}Error: File '$file' not found${NC}"
        return 1
    fi

    local file_type=$(detect_file_type "$file")

    case "$file_type" in
        javascript|typescript)
            validate_javascript "$file"
            ;;
        python)
            validate_python "$file"
            ;;
        shell)
            validate_shell "$file"
            ;;
        markdown)
            validate_markdown "$file"
            ;;
        *)
            echo -e "${YELLOW}⚠ Unknown file type: $file${NC}"
            echo ""
            ;;
    esac
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 [--show-tools | file1 file2 ...]"
    echo ""
    echo "Options:"
    echo "  --show-tools    Show available validation tools"
    echo "  file1 file2...  Validate specified files"
    echo ""
    exit 1
fi

if [ "$1" = "--show-tools" ]; then
    show_available_tools
    exit 0
fi

# Validate each file
for file in "$@"; do
    validate_file "$file"
done

echo -e "${BLUE}=== Validation Complete ===${NC}"