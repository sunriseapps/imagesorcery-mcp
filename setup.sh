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

# Run post-installation process
echo "Running post-installation process..."
imagesorcery-mcp --post-install

echo "✅ Setup complete!"
