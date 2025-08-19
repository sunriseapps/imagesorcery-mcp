"""
Configuration management for ImageSorcery MCP.

This module provides a centralized configuration system that loads settings
from TOML files and allows runtime updates through the MCP config tool.
"""

import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class DetectionConfig(BaseModel):
    """Detection tool configuration."""
    confidence_threshold: float = Field(0.75, ge=0.0, le=1.0)
    default_model: str = "yoloe-11l-seg-pf.pt"


class FindConfig(BaseModel):
    """Find tool configuration."""
    confidence_threshold: float = Field(0.75, ge=0.0, le=1.0)
    default_model: str = "yoloe-11l-seg-pf.pt"


class BlurConfig(BaseModel):
    """Blur tool configuration."""
    strength: int = Field(15, ge=1)

    @field_validator('strength')
    @classmethod
    def strength_must_be_odd(cls, v):
        if v % 2 == 0:
            raise ValueError('Blur strength must be an odd number')
        return v


class TextConfig(BaseModel):
    """Text drawing configuration."""
    font_scale: float = Field(1.0, gt=0.0)


class DrawingConfig(BaseModel):
    """Drawing configuration."""
    color: List[int] = Field([0, 0, 0], min_length=3, max_length=3)
    thickness: int = Field(1, ge=1)

    @field_validator('color')
    @classmethod
    def color_values_valid(cls, v):
        for val in v:
            if not (0 <= val <= 255):
                raise ValueError('Color values must be between 0 and 255')
        return v


class OCRConfig(BaseModel):
    """OCR configuration."""
    language: str = "en"


class ResizeConfig(BaseModel):
    """Resize configuration."""
    interpolation: str = Field("linear", pattern="^(nearest|linear|area|cubic|lanczos)$")


class ImageSorceryConfig(BaseModel):
    """Main configuration class for ImageSorcery MCP."""
    detection: DetectionConfig = DetectionConfig()
    find: FindConfig = FindConfig()
    blur: BlurConfig = BlurConfig()
    text: TextConfig = TextConfig()
    drawing: DrawingConfig = DrawingConfig()
    ocr: OCRConfig = OCRConfig()
    resize: ResizeConfig = ResizeConfig()


class ConfigManager:
    """Configuration manager for ImageSorcery MCP."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config_file = Path("config.toml")
        self._config: Optional[ImageSorceryConfig] = None
        self._runtime_overrides: Dict[str, Any] = {}
        self._load_config()
    
    def _ensure_config_file_exists(self):
        """Ensure config.toml exists, create from default if needed."""
        if not self.config_file.exists():
            # Look for config.default in the package directory
            default_config_path = Path(__file__).parent.parent.parent / "config.default"
            if default_config_path.exists():
                shutil.copy2(default_config_path, self.config_file)
                logger.info("Created config.toml from default configuration")
            else:
                # Create a basic config file with defaults
                default_config = ImageSorceryConfig()
                self._save_config_to_file(default_config.model_dump())
                logger.info("Created config.toml with default values")
    
    def _load_config(self):
        """Load configuration from file."""
        self._ensure_config_file_exists()
        
        config_data = {}
        try:
            with open(self.config_file, 'r') as f:
                config_data = toml.load(f)
            logger.info(f"Loaded configuration from: {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load configuration from {self.config_file}: {e}")
            config_data = {}
        
        # Apply runtime overrides
        self._apply_runtime_overrides(config_data)
        
        # Create configuration object
        self._config = ImageSorceryConfig(**config_data)
        logger.info("Configuration loaded successfully")
    
    def _apply_runtime_overrides(self, config_data: Dict[str, Any]):
        """Apply runtime overrides to configuration data."""
        for key, value in self._runtime_overrides.items():
            if '.' in key:
                # Handle nested keys like "detection.confidence_threshold"
                parts = key.split('.')
                current = config_data
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                # Handle top-level keys
                if key not in config_data:
                    config_data[key] = {}
                config_data[key] = value
    
    def _save_config_to_file(self, config_data: Dict[str, Any]):
        """Save configuration data to file."""
        try:
            with open(self.config_file, 'w') as f:
                toml.dump(config_data, f)
            logger.info(f"Configuration saved to: {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration to {self.config_file}: {e}")
            raise
    
    @property
    def config(self) -> ImageSorceryConfig:
        """Get the current configuration."""
        if self._config is None:
            self._load_config()
        return self._config
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as a dictionary."""
        return self.config.model_dump()
    
    def update_config(self, updates: Dict[str, Any], persist: bool = False) -> Dict[str, Any]:
        """Update configuration values.
        
        Args:
            updates: Dictionary of configuration updates
            persist: If True, save changes to config file
            
        Returns:
            Updated configuration as dictionary
        """
        # Validate updates by creating a temporary config object
        current_config = self.config.model_dump()
        
        # Apply updates to current config
        for key, value in updates.items():
            if '.' in key:
                # Handle nested keys like "detection.confidence_threshold"
                parts = key.split('.')
                current = current_config
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                # Handle section updates
                if isinstance(value, dict):
                    if key not in current_config:
                        current_config[key] = {}
                    current_config[key].update(value)
                else:
                    current_config[key] = value
        
        # Validate the updated configuration
        try:
            ImageSorceryConfig(**current_config)
        except Exception as e:
            raise ValueError(f"Invalid configuration update: {e}") from e
        
        if persist:
            # Save to file
            self._save_config_to_file(current_config)
            # Clear runtime overrides since they're now persisted
            self._runtime_overrides.clear()
        else:
            # Store as runtime overrides
            self._runtime_overrides.update(updates)
        
        # Reload configuration
        self._load_config()
        
        return self.get_config_dict()
    
    def reset_runtime_overrides(self):
        """Reset all runtime overrides and reload from file."""
        self._runtime_overrides.clear()
        self._load_config()
    
    def get_runtime_overrides(self) -> Dict[str, Any]:
        """Get current runtime overrides."""
        return self._runtime_overrides.copy()


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> ImageSorceryConfig:
    """Get the current configuration."""
    return get_config_manager().config


def get_config_schema_info() -> Dict[str, Any]:
    """Get configuration schema information for documentation and validation."""
    schema_info = {
        "detection.confidence_threshold": {
            "description": "Default confidence threshold for object detection (0.0-1.0)",
            "type": "float",
            "constraints": "0.0 ≤ value ≤ 1.0"
        },
        "detection.default_model": {
            "description": "Default model for detection tool",
            "type": "string",
            "constraints": "Valid model filename"
        },
        "find.confidence_threshold": {
            "description": "Default confidence threshold for object finding (0.0-1.0)",
            "type": "float",
            "constraints": "0.0 ≤ value ≤ 1.0"
        },
        "find.default_model": {
            "description": "Default model for find tool",
            "type": "string",
            "constraints": "Valid model filename"
        },
        "blur.strength": {
            "description": "Default blur strength (must be odd number)",
            "type": "integer",
            "constraints": "Odd number ≥ 1"
        },
        "text.font_scale": {
            "description": "Default font scale for text drawing",
            "type": "float",
            "constraints": "Value > 0.0"
        },
        "drawing.color": {
            "description": "Default color in BGR format [B,G,R]",
            "type": "list[int]",
            "constraints": "3 integers, each 0-255"
        },
        "drawing.thickness": {
            "description": "Default line thickness",
            "type": "integer",
            "constraints": "Value ≥ 1"
        },
        "ocr.language": {
            "description": "Default OCR language code",
            "type": "string",
            "constraints": "Valid language code (e.g., 'en', 'fr', 'ru')"
        },
        "resize.interpolation": {
            "description": "Default resize interpolation method",
            "type": "string",
            "constraints": "One of: nearest, linear, area, cubic, lanczos"
        }
    }
    return schema_info


def get_available_config_keys() -> List[str]:
    """Get list of all available configuration keys."""
    return list(get_config_schema_info().keys())


def generate_config_documentation() -> str:
    """Generate configuration documentation from schema."""
    schema_info = get_config_schema_info()

    lines = ["Available configuration keys:"]
    for key, info in schema_info.items():
        lines.append(f"- {key}: {info['description']}")

    return "\n".join(lines)
