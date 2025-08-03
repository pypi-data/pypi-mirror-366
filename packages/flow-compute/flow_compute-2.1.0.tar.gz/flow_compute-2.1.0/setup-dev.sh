#!/bin/bash
# Setup development environment for Flow SDK using uv

echo "Setting up Flow SDK development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -e ".[dev]"

echo "Development environment setup complete!"
echo "To activate the environment, run: source .venv/bin/activate"