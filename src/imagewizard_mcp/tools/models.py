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
        return "model_descriptions.json not found"
    
    try:
        # Load descriptions from JSON file
        with open(descriptions_file, "r", encoding="utf-8") as f:
            descriptions = json.load(f)
        
        # Normalize model name to use forward slashes for consistent lookup
        normalized_model_name = model_name.replace('\\', '/')
        
        # Try direct lookup and also case-insensitive lookup
        if normalized_model_name in descriptions:
            return descriptions[normalized_model_name]
        
        # Try case-insensitive lookup as a fallback
        for key in descriptions:
            if key.lower() == normalized_model_name.lower():
                return descriptions[key]
        
        return f"Model '{model_name}' not found in model_descriptions.json (total descriptions: {len(descriptions)})"
    except Exception as e:
        # Return default description if any error occurs
        print(f"Error in get_model_description: {str(e)}")
        return f"Error in get_model_description: {str(e)}"

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

        # Scan for model files recursively using rglob instead of glob
        for file_path in models_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in model_extensions:
                # Get relative path from models directory
                rel_path = file_path.relative_to(models_dir)
                # Convert to string with forward slashes for consistent naming across platforms
                model_name = str(rel_path).replace('\\', '/')

                available_models.append(
                    {
                        "name": model_name,
                        "description": get_model_description(model_name),
                        "path": str(file_path),
                    }
                )
        return {"models": available_models}
