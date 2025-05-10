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

# Create model descriptions file
echo "Creating model descriptions file..."
create-model-descriptions

# Download YOLOv8 model
echo "Downloading default models..."
download-yolo-models --ultralytics yoloe-11l-seg-pf.pt
download-yolo-models --ultralytics yoloe-11s-seg-pf.pt

echo "✅ Setup complete!"
