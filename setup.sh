#!/bin/bash
set -e

echo "Setting up imagesorcery-mcp..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Detect OS and activate the appropriate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/macOS
    source venv/bin/activate
fi

# Install package dependencies
echo "Installing package dependencies..."
pip install -e "."

# Install development dependencies
# echo "Installing development dependencies..."
# pip install -e ".[dev]"

# Create models directory
mkdir -p models

# Create model descriptions file
echo "Creating model descriptions file..."
create-model-descriptions

# Download YOLOv8 model
echo "Downloading default models..."
download-yolo-models --ultralytics yoloe-11l-seg-pf.pt
download-yolo-models --ultralytics yoloe-11s-seg-pf.pt
download-yolo-models --ultralytics yoloe-11l-seg.pt
download-yolo-models --ultralytics yoloe-11s-seg.pt

# Download CLIP model
echo "Downloading CLIP model for text prompts..."
download-clip-models

echo "✅ Setup complete!"
