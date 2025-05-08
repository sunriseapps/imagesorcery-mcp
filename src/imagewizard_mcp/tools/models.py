import json
from pathlib import Path
from typing import Dict, List

from fastmcp import FastMCP


def get_model_description(model_name: str) -> str:
    """Get a description for a specific model."""
    # Path to model descriptions JSON file
    descriptions_file = Path("models") / "model_descriptions.json"
    
    # Default description if file doesn't exist or model not found
    default_description = "Unknown model"
    
    # Check if descriptions file exists
    if not descriptions_file.exists():
        return default_description
    
    try:
        # Load descriptions from JSON file
        with open(descriptions_file, "r") as f:
            descriptions = json.load(f)
        
        # Return description for the model or default
        return descriptions.get(model_name, default_description)
    except Exception:
        # Return default description if any error occurs
        return default_description


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def get_models() -> Dict[str, List[Dict[str, str]]]:
        """
        List all available models in the models directory.

        This tool scans the models directory and returns information about
        all available models, including their names and descriptions.

        Returns:
            Dictionary containing a list of available models with their descriptions.
        """
        models_dir = Path("models")
        available_models = []

        # Check if models directory exists
        if not models_dir.exists():
            return {"models": available_models}

        # Define model file extensions to include
        model_extensions = [".pt", ".pth", ".onnx", ".tflite", ".pb"]

        # Scan for model files
        for file_path in models_dir.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in model_extensions:
                model_name = file_path.name

                available_models.append(
                    {
                        "name": model_name,
                        "description": get_model_description(model_name),
                    }
                )

        return {"models": available_models}
