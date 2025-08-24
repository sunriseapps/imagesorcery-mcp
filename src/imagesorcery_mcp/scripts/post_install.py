#!/usr/bin/env python3
"""
Script to run post-installation tasks for imagesorcery-mcp.
This script creates the models directory, model descriptions file,
and downloads default models.
"""

import os
import subprocess  # Ensure subprocess is imported
import sys  # Ensure sys is imported
import uuid
from pathlib import Path

# Import the central logger
from imagesorcery_mcp.logging_config import logger

# For loading .env file
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logger.warning("python-dotenv not available. .env file will not be loaded automatically.")
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
    """Ensure config.toml exists, create with default values if needed."""
    config_file = Path("config.toml")
    if config_file.exists():
        logger.info(f"⏩ Configuration file already exists: {config_file}")
        return True

    logger.info("Creating config.toml using configuration system defaults")
    # The config manager will create it with defaults if it doesn't exist
    from imagesorcery_mcp.config import get_config_manager
    get_config_manager()
    print(f"✅ Configuration file created with default values: {config_file}")
    return True


def create_user_id_file():
    """Ensure .user_id file exists in the project root, create a new UUID if needed."""
    user_id_file = Path(".user_id")
    if user_id_file.exists():
        logger.info(f"⏩ .user_id file already exists: {user_id_file}")
        return True

    logger.info("Creating .user_id file for telemetry...")
    try:
        user_id = str(uuid.uuid4())
        user_id_file.write_text(user_id)
        logger.info(f"Generated new .user_id file with user_id: {user_id_file}")
        print(f"✅ .user_id file created: {user_id_file}")
        return True
    except Exception as e:
        logger.error(f"Failed to create .user_id file: {e}")
        print(f"❌ Failed to create .user_id file: {e}")
        return False


def run_post_install():
    """Run all post-installation tasks."""
    logger.info(f"Running post-installation tasks from {Path(__file__).resolve()}...")

    # Get API keys from environment variables (for Step 4)
    amplitude_api_key = os.environ.get("IMAGESORCERY_AMPLITUDE_API_KEY", "")
    posthog_api_key = os.environ.get("IMAGESORCERY_POSTHOG_API_KEY", "")
    
    logger.debug(f"Amplitude API key from environment: {'*' * 8 if amplitude_api_key else 'Not set'}")
    logger.debug(f"PostHog API key from environment: {'*' * 8 if posthog_api_key else 'Not set'}")

    # Create configuration file
    logger.info("Creating configuration file...")
    config_created = create_config_file()
    if not config_created:
        logger.error("Failed to create configuration file")
        return False

    # Create user ID file for telemetry
    logger.info("Creating user ID file...")
    user_id_created = create_user_id_file()
    if not user_id_created:
        logger.error("Failed to create user ID file")
        # Do not return False here, as telemetry is not critical for core functionality
        # and other post-install tasks should still proceed.

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
    # Load .env file if available
    if DOTENV_AVAILABLE:
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv()
            logger.info(f"Loaded environment variables from {env_file}")
        else:
            logger.info(".env file not found, skipping dotenv loading")
    else:
        logger.info("python-dotenv not available, skipping .env file loading")
    
    logger.info(f"Starting post-installation process from {Path(__file__).resolve()}")
    success = run_post_install()
    if not success:
        logger.error("Post-installation process failed")
        sys.exit(1)
    logger.info("Post-installation process completed")


if __name__ == "__main__":
    main()
