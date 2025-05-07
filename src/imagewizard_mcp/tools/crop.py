import os
from PIL import Image
from fastmcp import FastMCP

def register_tool(mcp: FastMCP):
    @mcp.tool()
    def crop(input_path: str, left: int, top: int, right: int, bottom: int, output_path: str = None) -> str:
        """
        Crop an image based on provided coordinates.
        
        Args:
            input_path: Path to the input image
            left: Left coordinate of crop box
            top: Top coordinate of crop box
            right: Right coordinate of crop box
            bottom: Bottom coordinate of crop box
            output_path: Path to save the output image. If not provided,
                         will use input filename with '_cropped' suffix.
        
        Returns:
            Path to the cropped image
        """
        # Check if input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Generate output path if not provided
        if not output_path:
            file_name, file_ext = os.path.splitext(input_path)
            output_path = f"{file_name}_cropped{file_ext}"
        
        # Open the image and crop it
        with Image.open(input_path) as img:
            cropped_img = img.crop((left, top, right, bottom))
            
            # Create directory for output if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Save the cropped image
            cropped_img.save(output_path)
            
        return output_path