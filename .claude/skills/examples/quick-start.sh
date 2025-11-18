#!/bin/bash

# Automated UI Testing - Quick Start Script
# This script helps you quickly set up and run UI tests

set -e

echo "🚀 Automated UI Testing - Quick Start"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo -e "${GREEN}✅ Node.js version: $(node -v)${NC}"
echo ""

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
npm install

# Install Playwright browsers
echo ""
echo -e "${BLUE}🌐 Installing Playwright browsers...${NC}"
npx playwright install --with-deps chromium firefox webkit

# Create test results directory
mkdir -p test-results

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "======================================"
echo "📋 Available Commands:"
echo "======================================"
echo ""
echo "Run all tests:"
echo -e "  ${YELLOW}npm test${NC}"
echo ""
echo "Run tests in headed mode (see browser):"
echo -e "  ${YELLOW}npm run test:headed${NC}"
echo ""
echo "Run tests in debug mode:"
echo -e "  ${YELLOW}npm run test:debug${NC}"
echo ""
echo "Run tests for specific browser:"
echo -e "  ${YELLOW}npm run test:chromium${NC}"
echo -e "  ${YELLOW}npm run test:firefox${NC}"
echo -e "  ${YELLOW}npm run test:webkit${NC}"
echo ""
echo "Run mobile tests:"
echo -e "  ${YELLOW}npm run test:mobile${NC}"
echo ""
echo "View HTML report:"
echo -e "  ${YELLOW}npm run report${NC}"
echo ""
echo "======================================"
echo ""

# Ask if user wants to run a test
read -p "Would you like to run a sample test now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${BLUE}🧪 Running sample tests...${NC}"
    echo ""
    npm test || true

    echo ""
    echo -e "${GREEN}✅ Tests completed!${NC}"
    echo ""
    echo "View the HTML report by running:"
    echo -e "  ${YELLOW}npm run report${NC}"
fi

echo ""
echo -e "${GREEN}🎉 You're all set! Happy testing!${NC}"
echo ""
