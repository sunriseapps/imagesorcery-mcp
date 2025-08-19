from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

# Import the central logger
from imagesorcery_mcp.logging_config import logger


def register_prompt(mcp: FastMCP):
    @mcp.prompt(name="remove-background")
    def remove_background(
        image_path: Annotated[
            str, Field(description="Full path to the input image (must be a full path)")
        ],
        target_objects: Annotated[
            str,
            Field(
                description="Description of the objects to keep in the foreground (e.g., 'person', 'car and person', 'main subject')"
            ),
        ] = "",
        output_path: Annotated[
            str,
            Field(
                description="Full path for the output image with background removed (optional, will auto-generate if not provided)"
            ),
        ] = "",
    ) -> str:
        """
        Guides the AI through a comprehensive background removal workflow.
        
        This prompt provides a step-by-step approach to remove backgrounds from images
        using object detection and masking tools. It's designed to work with the
        ImageSorcery MCP server's detect and fill tools.
        
        The workflow includes:
        1. Object detection to identify the target object
        2. Mask generation for precise selection
        3. Background removal using fill operations
        4. Optional refinement steps
        
        Args:
            image_path: Full path to the input image
            target_objects: Description of what to keep (default: empty for auto-detection)
            output_path: Where to save the result (auto-generated if empty)

        Returns:
            A detailed prompt guiding the AI through the background removal process
        """
        logger.info(f"Remove background prompt requested for image: {image_path}")
        logger.debug(f"Target objects: {target_objects}, Output path: {output_path}")
        
        # Generate output path if not provided
        if not output_path:
            if image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                base_path = image_path.rsplit('.', 1)[0]
                output_path = f"{base_path}_no_background.png"
            else:
                output_path = f"{image_path}_no_background.png"

        # Build the prompt based on whether target_objects is specified
        if target_objects:
            prompt = f"""I need to remove the background from an image while preserving the {target_objects}. Please follow this step-by-step workflow:

**Step 1: Find Target Objects**
Use the `find` tool to locate the specific objects:
- Call `find` on '{image_path}' with:
  - description: "{target_objects}"
  - confidence: 0.3 (lower threshold for better recall)
  - return_geometry: true
  - geometry_format: "mask"
- This will use text-based object identification to locate the {target_objects}

**Step 2: Remove Background**
Use the `fill` tool to remove the background:
- Call `fill` on '{image_path}' with:
  - areas: Use mask files from find
  - color: null
  - output_path: '{output_path}'

**Step 3: Clean Up**
- Remove the temporary mask files created during the process

**Important Notes:**
- Save the final result as a PNG file to preserve transparency

Please execute this workflow step by step."""
        else:
            prompt = f"""I need to remove the background from an image. Please follow this step-by-step workflow:

**Step 1: Detect Objects**
Use the `detect` tool to identify objects in the image:
- Call `detect` on '{image_path}' with:
  - confidence: 0.5 (to catch more objects)
  - return_geometry: true
  - geometry_format: "mask"
- Review the detected objects and identify the main subjects to preserve

**Step 3: Remove Background**
Use the `fill` tool to remove the background:
- Call `fill` on '{image_path}' with:
  - areas: Use mask files from detect
  - color: null
  - output_path: '{output_path}'

**Step 4: Clean Up**
- Remove the temporary mask files created during the process

**Important Notes:**
- Save the final result as a PNG file to preserve transparency

Please execute this workflow step by step."""

        logger.info(f"Generated remove background prompt for targets: {target_objects or 'auto-detect'}")
        return prompt
