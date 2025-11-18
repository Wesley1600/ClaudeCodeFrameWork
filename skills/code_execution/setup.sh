#!/bin/bash

# Setup script for Code Execution Skill
# This script installs all required dependencies

echo "=============================="
echo "Code Execution Skill - Setup"
echo "=============================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is required but not found"
    exit 1
fi

echo ""
echo "Installing Python packages..."
echo ""

# Install required packages
pip3 install --user numpy pandas matplotlib seaborn

if [ $? -eq 0 ]; then
    echo ""
    echo "=============================="
    echo "Setup completed successfully!"
    echo "=============================="
    echo ""
    echo "You can now use the Code Execution Skill."
    echo "Run tests with: python3 test_skill.py"
    echo "Run examples with: python3 examples.py"
else
    echo ""
    echo "=============================="
    echo "Setup failed!"
    echo "=============================="
    echo ""
    echo "Please install the packages manually:"
    echo "  pip3 install -r requirements.txt"
    exit 1
fi
