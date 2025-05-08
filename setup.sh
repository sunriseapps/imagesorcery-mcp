#!/bin/bash
set -e

echo "Setting up imagewizard-mcp..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install package with development dependencies
echo "Installing package dependencies..."
pip install -e ".[dev]"

# Create models directory
mkdir -p models

# Download YOLOv8 model
echo "Downloading YOLOv8 model..."
download-yolo-models --model-size m

echo "✅ Setup
