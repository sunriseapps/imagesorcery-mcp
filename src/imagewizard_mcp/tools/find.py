import os
import sys
from pathlib import Path
from typing import Annotated, Dict, List, Union

from fastmcp import FastMCP
from pydantic import Field


def get_model_path(model_name):
    """Get the path to a model in the models directory."""
    model_path = Path("models") / model_name
    if model_path.exists():
        return str(model_path)
    return None


def check_clip_installed():
    """Check if CLIP is installed and the model is available."""
    try:
        import clip  # noqa: F401
        
        # Check if the MobileCLIP model is available in the root directory
        clip_model_path = Path("mobileclip_blt.ts")
        if clip_model_path.exists():
            return True, None
        
        return False, "MobileCLIP model not found. Please run 'download-clip-models' to download it."
    except ImportError:
        return False, "CLIP is not installed. Please install it with 'pip install git+https://github.com/ultralytics/CLIP.git'"


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def find(
        input_path: Annotated[str, Field(description="Path to the input image")],
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
        It requires pre-downloaded models that support text prompts. Use the download-yolo-models
        and download-clip-models commands to download required models before using this tool.
        
        Returns:
            Dictionary containing the input image path and a list of found objects
            with their confidence scores and bounding box coordinates.
        """
        print(f"Starting find tool with model: {model_name}, description: {description}")
        sys.stdout.flush()  # Ensure output is visible immediately
        
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Add .pt extension if it doesn't exist
        if not model_name.endswith(".pt"):
            model_name = f"{model_name}.pt"

        # Try to find the model
        model_path = get_model_path(model_name)
        print(f"Model path: {model_path}")
        sys.stdout.flush()

        # If model not found, raise an error with helpful message
        if not model_path:
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
            raise ValueError(
                f"The model {model_name} does not support text prompts. "
                f"Please use a model that supports text prompts, such as "
                f"yoloe-11l-seg.pt"
            )
            
        # Check if CLIP is installed and the model is available
        clip_installed, clip_error = check_clip_installed()
        if not clip_installed:
            raise RuntimeError(
                f"Cannot use text prompts: {clip_error}\n"
                "Text prompts require CLIP and the MobileCLIP model.\n"
                "Run 'download-clip-models' to set up the required dependencies."
            )

        try:
            # Set environment variable to use the models directory
            os.environ["YOLO_CONFIG_DIR"] = str(Path("models").absolute())
            
            # Set environment variable to use the models directory for CLIP
            clip_model_path = Path("mobileclip_blt.ts").absolute()
            if not clip_model_path.exists():
                raise RuntimeError(
                    f"CLIP model not found at {clip_model_path}. "
                    "Please run 'download-clip-models' to download it."
                )
            os.environ["CLIP_MODEL_PATH"] = str(clip_model_path)
            
            print("Loading ultralytics...")
            sys.stdout.flush()

            # Import here to avoid loading ultralytics if not needed
            from ultralytics import YOLO

            print("Loading model...")
            sys.stdout.flush()
            
            # Load the model from the found path
            model = YOLO(model_path)
            print("Model loaded successfully")
            sys.stdout.flush()
            
            # For YOLOe models, we need to set the classes using the text description
            print("Setting up text prompts...")
            sys.stdout.flush()
            
            # Convert the description to a list (YOLOe expects a list of class names)
            class_names = [description]
            
            try:
                # Set the classes for the model
                print("Getting text embeddings...")
                sys.stdout.flush()
                text_embeddings = model.get_text_pe(class_names)
                print("Setting classes...")
                sys.stdout.flush()
                model.set_classes(class_names, text_embeddings)
                print("Classes set successfully")
                sys.stdout.flush()
            except Exception as e:
                print(f"Error setting classes: {str(e)}")
                sys.stdout.flush()
                raise RuntimeError(
                    f"Error setting up text prompts: {str(e)}\n"
                    "This may be due to missing CLIP dependencies.\n"
                    "Please run 'download-clip-models' to set up the required dependencies."
                ) from e
            
            # Run inference on the image
            print(f"Running inference on {input_path}...")
            sys.stdout.flush()
            results = model.predict(input_path, conf=confidence, verbose=True)
            print("Inference completed")
            sys.stdout.flush()
            
            found_objects = []
            
            # Process results
            if results and len(results) > 0:
                print(f"Processing {len(results)} results")
                sys.stdout.flush()
                
                if hasattr(results[0], 'boxes') and len(results[0].boxes) > 0:
                    print(f"Found {len(results[0].boxes)} boxes")
                    sys.stdout.flush()
                    
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
                else:
                    print("No boxes found in results")
                    sys.stdout.flush()
            else:
                print("No results returned from model")
                sys.stdout.flush()
            
            # Sort by confidence (highest first)
            found_objects.sort(key=lambda x: x["confidence"], reverse=True)
            
            # Return only the best match if return_all_matches is False and we have matches
            if not return_all_matches and found_objects:
                found_objects = [found_objects[0]]
            
            print(f"Returning {len(found_objects)} found objects")
            sys.stdout.flush()
            
            return {
                "image_path": input_path,
                "query": description,
                "found_objects": found_objects,
                "found": len(found_objects) > 0
            }

        except Exception as e:
            print(f"Error in find tool: {str(e)}")
            sys.stdout.flush()
            
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
