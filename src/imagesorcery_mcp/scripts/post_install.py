#!/usr/bin/env python3
"""
Script to run post-installation tasks for imagesorcery-mcp.
This script creates the models directory, model descriptions file,
and downloads default models.
"""

import os
import subprocess  # Ensure subprocess is imported
import sys  # Ensure sys is imported
from pathlib import Path

# Import the central logger
from imagesorcery_mcp.logging_config import logger
from imagesorcery_mcp.scripts.create_model_descriptions import create_model_descriptions
from imagesorcery_mcp.scripts.download_clip import download_clip_model
from imagesorcery_mcp.scripts.download_models import download_ultralytics_model


def install_clip():
    """Install CLIP from the Ultralytics GitHub repository."""
    logger.info("Installing CLIP package from GitHub...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "git+https://github.com/ultralytics/CLIP.git"],
            check=True,
            stdout=sys.stdout, # Can be replaced with subprocess.PIPE if console output is not needed
            stderr=subprocess.PIPE  # Capture stderr to analyze it
        )
        logger.info("CLIP package installed successfully")
        print("✅ CLIP package installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install CLIP: {e}")
        error_message = f"❌ Failed to install CLIP package: {e}"
        detailed_warning = ""
        if e.stderr:
            try:
                stderr_output = e.stderr.decode(errors='ignore')
                logger.debug(f"Captured stderr from CLIP installation attempt: {stderr_output}")
                if "No module named pip" in stderr_output:
                    detailed_warning = (
                        "\n   Hint: The Python environment (potentially created by 'uvx' or a minimal 'uv venv') might be missing 'pip'."
                        "\n   To ensure 'clip' package installation for full functionality (e.g., text prompts in 'find' tool):"
                        "\n     1. Recommended: Use 'python -m venv' to create a virtual environment, then 'pip install imagesorcery-mcp' and 'imagesorcery-mcp --post-install'."
                        "\n     2. Or, manually install 'clip' into your active environment: pip install git+https://github.com/ultralytics/CLIP.git"
                        "\n        (If using 'uv venv', you might need: uv pip install git+https://github.com/ultralytics/CLIP.git)"
                    )
            except Exception as decode_exc:
                logger.error(f"Error while decoding/processing stderr for CLIP install: {decode_exc}")
        
        print(error_message + detailed_warning)
        return False
    except FileNotFoundError: # Handle case where pip or python executable is not found
        logger.error("Failed to install CLIP: Python executable or pip not found.")
        print("❌ Failed to install CLIP package: Python executable or pip not found. Ensure Python is in PATH and pip is installed.")
        return False


def create_config_file():
    """Create config.toml from config.default if it doesn't exist."""
    config_file = Path("config.toml")
    if config_file.exists():
        logger.info(f"Configuration file already exists: {config_file}")
        return True

    # Look for config.default in multiple locations
    search_paths = [
        # First check current working directory
        Path.cwd() / "config.default",
        # Then check repository root (relative to this script)
        Path(__file__).parent.parent.parent.parent / "config.default",
        # Also check relative to the package
        Path(__file__).parent.parent / "config.default"
    ]

    config_default_found = None
    for path in search_paths:
        if path.exists():
            config_default_found = path
            break

    if config_default_found:
        import shutil
        shutil.copy2(config_default_found, config_file)
        logger.info(f"Created config.toml from config.default: {config_default_found}")
        print(f"✅ Configuration file created from config.default: {config_file}")
        return True
    else:
        logger.warning(f"config.default not found in any of these locations: {[str(p) for p in search_paths]}")
        logger.info("Creating config.toml using configuration system defaults")

        # Use the configuration system to create a proper config file
        try:
            import toml

            from imagesorcery_mcp.config import ImageSorceryConfig

            # Create default configuration using the configuration system
            default_config = ImageSorceryConfig()
            config_dict = default_config.model_dump()

            # Write to file with proper formatting
            with open(config_file, 'w') as f:
                f.write("# ImageSorcery MCP Configuration\n")
                f.write("# This file contains configuration values for ImageSorcery MCP\n")
                f.write("# Generated from configuration system defaults\n\n")
                toml.dump(config_dict, f)

            logger.info(f"Created config.toml using configuration system defaults: {config_file}")
            print(f"✅ Configuration file created with system defaults: {config_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to create config file using configuration system: {e}")
            print(f"❌ Failed to create configuration file: {e}")
            return False


def run_post_install():
    """Run all post-installation tasks."""
    logger.info(f"Running post-installation tasks from {Path(__file__).resolve()}...")

    # Create configuration file
    logger.info("Creating configuration file...")
    config_created = create_config_file()
    if not config_created:
        logger.error("Failed to create configuration file")
        return False

    # Create models directory
    models_dir = Path("models").resolve()
    os.makedirs(models_dir, exist_ok=True)
    logger.info(f"Created models directory: {models_dir}")

    # Create model descriptions file
    logger.info("Creating model descriptions file...")
    descriptions_file = create_model_descriptions()
    if descriptions_file:
        logger.info(f"Model descriptions file created at: {descriptions_file}")
    else:
        logger.error("Failed to create model descriptions file")
        return False

    # Download default Ultralytics YOLO models
    default_models = [
        "yoloe-11l-seg-pf.pt",
        "yoloe-11s-seg-pf.pt",
        "yoloe-11l-seg.pt",
        "yoloe-11s-seg.pt"
    ]
    
    logger.info("Downloading default Ultralytics YOLO models...")
    for model in default_models:
        logger.info(f"Downloading {model}...")
        success = download_ultralytics_model(model)
        if not success:
            logger.error(f"Failed to download model: {model}")
            return False
    print("✅ Ultralytics YOLO models download completed successfully")

    # Install CLIP package
    logger.info("Installing CLIP package for text prompts...")
    clip_installed_successfully = install_clip()
    if not clip_installed_successfully:
        logger.warning("CLIP Python package installation failed. The 'find' tool's text prompt functionality might be limited or unavailable.")
        print("⚠️ WARNING: CLIP Python package installation failed. Text prompt features of the 'find' tool may not work.")
        print("   Models for CLIP will still be downloaded. If you need this functionality, please try installing the CLIP package manually:")
        print("   pip install git+https://github.com/ultralytics/CLIP.git")
        # We continue with the rest of the post-installation, especially downloading CLIP models.
    
    # Download CLIP model
    logger.info("Downloading CLIP model for text prompts...")
    try:
        # Download the CLIP model file
        success = download_clip_model()
        if not success:
            logger.error("Failed to download CLIP model")
            return False
    except Exception as e:
        logger.error(f"Error downloading CLIP model: {str(e)}")
        return False
    print("✅ CLIP model download completed successfully")
    
    logger.info("Post-installation tasks completed successfully!")
    print("✅ Post-installation tasks completed successfully!")
    return True


def main():
    """Main entry point for the post_install script."""
    logger.info(f"Starting post-installation process from {Path(__file__).resolve()}")
    success = run_post_install()
    if not success:
        logger.error("Post-installation process failed")
        sys.exit(1)
    logger.info("Post-installation process completed")


if __name__ == "__main__":
    main()
