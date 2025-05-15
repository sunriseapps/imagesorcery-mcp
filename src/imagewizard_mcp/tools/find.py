import os
from pathlib import Path
from typing import Annotated, Dict, List, Union

from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def get_model_path(model_name):
    """Get the path to a model in the models directory."""
    logger.info(f"Attempting to get path for model: {model_name}")
    model_path = Path("models") / model_name
    if model_path.exists():
        logger.info(f"Model found at: {model_path}")
        return str(model_path)
    logger.warning(f"Model not found in models directory: {model_name}")
    return None


def check_clip_installed():
    """Check if CLIP is installed and the model is available."""
    logger.info("Checking if CLIP is installed and MobileCLIP model is available")
    try:
        import clip  # noqa: F401
        logger.info("CLIP is installed")
        
        # Check if the MobileCLIP model is available in the root directory
        clip_model_path = Path("mobileclip_blt.ts")
        if clip_model_path.exists():
            logger.info(f"MobileCLIP model found at: {clip_model_path}")
            return True, None
        
        logger.warning(f"MobileCLIP model not found at: {clip_model_path}")
        return False, "MobileCLIP model not found. Please run 'download-clip-models' to download it."
    except ImportError:
        logger.warning("CLIP is not installed")
        return False, "CLIP is not installed. Please install it with 'pip install git+https://github.com/ultralytics/CLIP.git'"


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def find(
        input_path: Annotated[str, Field(description="Full path to the input image (must be a full path)")],
        description: Annotated[
            str, Field(description="Text description of the object to find")
        ],
        confidence: Annotated[
            float,
            Field(
                description="Confidence threshold for detection (0.0 to 1.0)",
                ge=0.0,
                le=1.0,
            ),
        ] = 0.3,
        model_name: Annotated[
            str,
            Field(
                description="Model name to use for finding objects (must support text prompts)",
            ),
        ] = "yoloe-11l-seg.pt",  # Default model that supports text prompts
        return_all_matches: Annotated[
            bool,
            Field(
                description="If True, returns all matching objects; if False, returns only the best match"
            ),
        ] = False,
    ) -> Dict[str, Union[str, List[Dict[str, Union[str, float, List[float]]]]]]:
        """
        Find objects in an image based on a text description.
        
        This tool uses open-vocabulary detection models to find objects matching a text description.
        It requires pre-downloaded YOLOE models that support text prompts (e.g. yoloe-11l-seg.pt).
        
        Returns:
            Dictionary containing the input image path and a list of found objects
            with their confidence scores and bounding box coordinates.
        """
        logger.info(f"Find tool requested for image: {input_path}, description: '{description}', model: {model_name}, confidence: {confidence}, return_all_matches: {return_all_matches}")
        
        # Check if input file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}. Please provide a full path to the file.")

        # Add .pt extension if it doesn't exist
        if not model_name.endswith(".pt"):
            original_model_name = model_name
            model_name = f"{model_name}.pt"
            logger.info(f"Added .pt extension to model name: {original_model_name} -> {model_name}")

        # Try to find the model
        model_path = get_model_path(model_name)
        logger.info(f"Resolved model path: {model_path}")

        # If model not found, raise an error with helpful message
        if not model_path:
            logger.error(f"Model {model_name} not found.")
            # List available models
            available_models = []
            models_dir = Path("models")
            
            # Find all .pt files in the models directory and its subdirectories
            if models_dir.exists():
                for file in models_dir.glob("**/*.pt"):
                    available_models.append(str(file.relative_to(models_dir)))

            # Filter for models that support text prompts
            text_prompt_models = [
                model for model in available_models 
                if "yoloe" in model.lower() and not model.lower().endswith("-pf.pt")
            ]

            error_msg = (
                f"Model {model_name} not found. "
                f"Available models supporting text prompts: "
                f"{', '.join(text_prompt_models) if text_prompt_models else 'None'}\n"
                "To use this tool, you need to download a model that supports text prompts first using:\n"
                "download-yolo-models --ultralytics MODEL_NAME\n"
                "Recommended models: yoloe-11l-seg.pt\n"
                "Models will be downloaded to the 'models' directory "
                "in the project root."
            )
            raise RuntimeError(error_msg)

        # Check if the model supports text prompts
        if not ("yoloe" in model_name.lower() and not model_name.lower().endswith("-pf.pt")):
            logger.error(f"Model {model_name} does not support text prompts.")
            raise ValueError(
                f"The model {model_name} does not support text prompts. "
                f"Please use a model that supports text prompts, such as "
                f"yoloe-11l-seg.pt"
            )
            
        # Check if CLIP is installed and the model is available
        clip_installed, clip_error = check_clip_installed()
        if not clip_installed:
            logger.error(f"CLIP not installed or MobileCLIP model missing: {clip_error}")
            raise RuntimeError(
                f"Cannot use text prompts: {clip_error}\n"
                "Text prompts require CLIP and the MobileCLIP model.\n"
                "Run 'download-clip-models' to set up the required dependencies."
            )

        try:
            # Set environment variable to use the models directory
            os.environ["YOLO_CONFIG_DIR"] = str(Path("models").absolute())
            logger.info(f"Set YOLO_CONFIG_DIR environment variable to: {os.environ['YOLO_CONFIG_DIR']}")
            
            # Set environment variable for CLIP model path
            clip_model_path = Path("mobileclip_blt.ts").absolute()
            if not clip_model_path.exists():
                 logger.error(f"CLIP model not found at expected path: {clip_model_path}")
                 raise RuntimeError(
                    f"CLIP model not found at {clip_model_path}. "
                    "Please run 'download-clip-models' to download it."
                )
            os.environ["CLIP_MODEL_PATH"] = str(clip_model_path)
            logger.info(f"Set CLIP_MODEL_PATH environment variable to: {os.environ['CLIP_MODEL_PATH']}")
            
            logger.info("Importing Ultralytics")
            # Import here to avoid loading ultralytics if not needed
            from ultralytics import YOLO
            logger.info("Ultralytics imported successfully")

            logger.info("Loading model...")
            
            # Load the model from the found path
            model = YOLO(model_path)
            logger.info("Model loaded successfully")
            
            # For YOLOe models, we need to set the classes using the text description
            logger.info("Setting up text prompts...")
            
            # Convert the description to a list (YOLOe expects a list of class names)
            class_names = [description]
            logger.debug(f"Class names for text prompts: {class_names}")
            
            try:
                # Set the classes for the model
                logger.info("Getting text embeddings...")
                text_embeddings = model.get_text_pe(class_names)
                logger.info("Setting classes...")
                model.set_classes(class_names, text_embeddings)
                logger.info("Classes set successfully")
            except Exception as e:
                logger.error(f"Error setting classes: {str(e)}", exc_info=True)
                raise RuntimeError(
                    f"Error setting up text prompts: {str(e)}\n"
                    "This may be due to missing CLIP dependencies.\n"
                    "Please run 'download-clip-models' to set up the required dependencies."
                ) from e
            
            # Run inference on the image
            logger.info(f"Running inference on {input_path} with confidence {confidence}")
            results = model.predict(input_path, conf=confidence, verbose=True)
            logger.info("Inference completed")
            
            found_objects = []
            
            # Process results
            if results and len(results) > 0:
                logger.info(f"Processing {len(results)} results")
                
                if hasattr(results[0], 'boxes') and len(results[0].boxes) > 0:
                    logger.info(f"Found {len(results[0].boxes)} boxes")
                    
                    for box in results[0].boxes:
                        # Get class name
                        class_id = int(box.cls.item())
                        class_name = results[0].names[class_id]
                        
                        # Get confidence score
                        conf = float(box.conf.item())
                        
                        # Get bounding box coordinates (x1, y1, x2, y2)
                        x1, y1, x2, y2 = [float(coord) for coord in box.xyxy[0].tolist()]
                        
                        found_objects.append({
                            "description": description,
                            "match": class_name,
                            "confidence": conf,
                            "bbox": [x1, y1, x2, y2]
                        })
                        logger.debug(f"Found object: match={class_name}, confidence={conf:.2f}, bbox=[{x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f}]")
                else:
                    logger.info("No boxes found in results")
            else:
                logger.info("No results returned from model")
            
            # Sort by confidence (highest first)
            found_objects.sort(key=lambda x: x["confidence"], reverse=True)
            
            # Return only the best match if return_all_matches is False and we have matches
            if not return_all_matches and found_objects:
                logger.info("Returning only the best match")
                found_objects = [found_objects[0]]
            
            logger.info(f"Returning {len(found_objects)} found objects")
            
            return {
                "image_path": input_path,
                "query": description,
                "found_objects": found_objects,
                "found": len(found_objects) > 0
            }

        except Exception as e:
            logger.error(f"Error in find tool: {str(e)}", exc_info=True)
            
            # Provide more helpful error message
            error_msg = f"Error finding objects: {str(e)}\n"

            if "not found" in str(e).lower():
                error_msg += (
                    "The model could not be found. "
                    "Please download it first using: "
                    "download-yolo-models --ultralytics MODEL_NAME"
                )
            elif "permission denied" in str(e).lower():
                error_msg += (
                    "Permission denied when trying to access or create the models "
                    "directory.\n"
                    "Try running the command with appropriate permissions."
                )
            elif "no module named" in str(e).lower():
                error_msg += (
                    "Required dependencies are missing. "
                    "Please install them using: "
                    "pip install git+https://github.com/ultralytics/CLIP.git"
                )
            elif "mobileclip" in str(e).lower():
                error_msg += (
                    "MobileCLIP model is missing. "
                    "Please download it using: "
                    "download-clip-models"
                )

            raise RuntimeError(error_msg) from e
