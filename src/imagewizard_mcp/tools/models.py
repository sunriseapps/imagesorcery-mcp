import json
from pathlib import Path
from typing import Dict, List

from fastmcp import FastMCP

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def get_model_description(model_name: str) -> str:
    """Get a description for a specific model."""
    logger.debug(f"Attempting to get description for model: {model_name}")
    # Path to model descriptions JSON file
    descriptions_file = Path("models") / "model_descriptions.json"
    
    # Check if descriptions file exists
    if not descriptions_file.exists():
        logger.warning(f"Model descriptions file not found: {descriptions_file}")
        return "model_descriptions.json not found"
    
    try:
        # Load descriptions from JSON file
        logger.debug(f"Loading model descriptions from: {descriptions_file}")
        with open(descriptions_file, "r", encoding="utf-8") as f:
            descriptions = json.load(f)
        logger.debug(f"Loaded {len(descriptions)} model descriptions")
        
        # Normalize model name to use forward slashes for consistent lookup
        normalized_model_name = model_name.replace('\\', '/')
        logger.debug(f"Normalized model name for lookup: {normalized_model_name}")
        
        # Try direct lookup and also case-insensitive lookup
        if normalized_model_name in descriptions:
            logger.debug(f"Found direct match for model description: {normalized_model_name}")
            return descriptions[normalized_model_name]
        
        # Try case-insensitive lookup as a fallback
        for key in descriptions:
            if key.lower() == normalized_model_name.lower():
                logger.debug(f"Found case-insensitive match for model description: {key}")
                return descriptions[key]
        
        logger.warning(f"Model '{model_name}' not found in model_descriptions.json (total descriptions: {len(descriptions)})")
        return f"Model '{model_name}' not found in model_descriptions.json (total descriptions: {len(descriptions)})"
    except Exception as e:
        # Return default description if any error occurs
        logger.error(f"Error in get_model_description for {model_name}: {str(e)}", exc_info=True)
        return "model_descriptions.json parse issue"

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
        logger.info("Get models tool requested")
        models_dir = Path("models")
        available_models = []

        # Check if models directory exists
        if not models_dir.exists():
            logger.warning(f"Models directory not found: {models_dir}")
            return {"models": available_models}
        logger.info(f"Scanning models directory: {models_dir}")

        # Define model file extensions to include
        model_extensions = [".pt", ".pth", ".onnx", ".tflite", ".pb"]
        logger.debug(f"Looking for files with extensions: {model_extensions}")

        # Scan for model files recursively using rglob instead of glob
        for file_path in models_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in model_extensions:
                # Get relative path from models directory
                rel_path = file_path.relative_to(models_dir)
                # Convert to string with forward slashes for consistent naming across platforms
                model_name = str(rel_path).replace('\\', '/')

                description = get_model_description(model_name)
                
                available_models.append(
                    {
                        "name": model_name,
                        "description": description,
                        "path": str(file_path),
                    }
                )
                logger.debug(f"Found model: {model_name} with description: {description}")
        
        logger.info(f"Found {len(available_models)} available models")
        return {"models": available_models}
