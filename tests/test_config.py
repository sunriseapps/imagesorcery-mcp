"""
Tests for the configuration management system.
"""

import os
import tempfile
from pathlib import Path

import pytest
import toml

from imagesorcery_mcp.config import (
    ConfigManager,
    ImageSorceryConfig,
    get_config,
    get_config_manager,
)


class TestImageSorceryConfig:
    """Tests for the ImageSorceryConfig model."""

    def test_default_values(self):
        """Test that default configuration values are correct."""
        config = ImageSorceryConfig()
        
        # Detection defaults
        assert config.detection.confidence_threshold == 0.75
        assert config.detection.default_model == "yoloe-11l-seg-pf.pt"
        
        # Find defaults
        assert config.find.confidence_threshold == 0.75
        assert config.find.default_model == "yoloe-11l-seg.pt"
        
        # Blur defaults
        assert config.blur.strength == 15
        
        # Text defaults
        assert config.text.font_scale == 1.0
        
        # Drawing defaults
        assert config.drawing.color == [0, 0, 0]
        assert config.drawing.thickness == 1
        
        # OCR defaults
        assert config.ocr.language == "en"
        
        # Resize defaults
        assert config.resize.interpolation == "linear"

        # Telemetry defaults
        assert config.telemetry.enabled is False

    def test_validation_confidence_threshold(self):
        """Test validation of confidence thresholds."""
        # Valid values
        config = ImageSorceryConfig(detection={"confidence_threshold": 0.5})
        assert config.detection.confidence_threshold == 0.5
        
        # Invalid values
        with pytest.raises(ValueError):
            ImageSorceryConfig(detection={"confidence_threshold": 1.5})
        
        with pytest.raises(ValueError):
            ImageSorceryConfig(detection={"confidence_threshold": -0.1})

    def test_validation_blur_strength(self):
        """Test validation of blur strength."""
        # Valid odd values
        config = ImageSorceryConfig(blur={"strength": 21})
        assert config.blur.strength == 21
        
        # Invalid even values
        with pytest.raises(ValueError):
            ImageSorceryConfig(blur={"strength": 20})

    def test_validation_drawing_color(self):
        """Test validation of drawing color."""
        # Valid color
        config = ImageSorceryConfig(drawing={"color": [255, 128, 0]})
        assert config.drawing.color == [255, 128, 0]
        
        # Invalid color values
        with pytest.raises(ValueError):
            ImageSorceryConfig(drawing={"color": [256, 0, 0]})
        
        with pytest.raises(ValueError):
            ImageSorceryConfig(drawing={"color": [-1, 0, 0]})
        
        # Invalid color length
        with pytest.raises(ValueError):
            ImageSorceryConfig(drawing={"color": [255, 0]})

    def test_validation_interpolation(self):
        """Test validation of resize interpolation."""
        # Valid interpolation methods
        for method in ["nearest", "linear", "area", "cubic", "lanczos"]:
            config = ImageSorceryConfig(resize={"interpolation": method})
            assert config.resize.interpolation == method
        
        # Invalid interpolation method
        with pytest.raises(ValueError):
            ImageSorceryConfig(resize={"interpolation": "invalid"})

    def test_validation_telemetry_enabled(self):
        """Test validation of telemetry enabled flag."""
        # Valid values
        config = ImageSorceryConfig(telemetry={"enabled": True})
        assert config.telemetry.enabled is True

        config = ImageSorceryConfig(telemetry={"enabled": False})
        assert config.telemetry.enabled is False

        # Invalid values
        with pytest.raises(ValueError):
            ImageSorceryConfig(telemetry={"enabled": "not_a_bool"})


class TestConfigManager:
    """Tests for the ConfigManager class."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_config_file_creation(self):
        """Test that config file is created if it doesn't exist."""
        ConfigManager()

        # Check that config.toml was created
        assert Path("config.toml").exists()
        
        # Check that it contains valid TOML
        with open("config.toml", "r") as f:
            config_data = toml.load(f)
        
        assert "detection" in config_data
        assert "blur" in config_data

    def test_config_loading_from_file(self):
        """Test loading configuration from existing file."""
        # Create a config file with custom values
        config_data = {
            "detection": {"confidence_threshold": 0.8},
            "blur": {"strength": 21}
        }
        
        with open("config.toml", "w") as f:
            toml.dump(config_data, f)
        
        config_manager = ConfigManager()
        config = config_manager.config
        
        assert config.detection.confidence_threshold == 0.8
        assert config.blur.strength == 21

    def test_runtime_updates(self):
        """Test runtime configuration updates."""
        config_manager = ConfigManager()
        
        # Update configuration
        updates = {
            "detection.confidence_threshold": 0.9,
            "text.font_scale": 2.0
        }
        
        updated_config = config_manager.update_config(updates, persist=False)
        
        assert updated_config["detection"]["confidence_threshold"] == 0.9
        assert updated_config["text"]["font_scale"] == 2.0
        
        # Check that file wasn't modified
        with open("config.toml", "r") as f:
            file_config = toml.load(f)
        
        # Should still have defaults since we didn't persist
        assert file_config.get("detection", {}).get("confidence_threshold", 0.75) == 0.75

    def test_persistent_updates(self):
        """Test persistent configuration updates."""
        config_manager = ConfigManager()
        
        # Update configuration with persistence
        updates = {
            "detection.confidence_threshold": 0.85,
            "ocr.language": "fr"
        }
        
        config_manager.update_config(updates, persist=True)
        
        # Check that file was modified
        with open("config.toml", "r") as f:
            file_config = toml.load(f)
        
        assert file_config["detection"]["confidence_threshold"] == 0.85
        assert file_config["ocr"]["language"] == "fr"

    def test_persistent_telemetry_update(self):
        """Test persistent telemetry configuration update."""
        config_manager = ConfigManager()

        # Update telemetry with persistence
        updates = {
            "telemetry.enabled": True
        }

        config_manager.update_config(updates, persist=True)

        # Check that file was modified
        with open("config.toml", "r") as f:
            file_config = toml.load(f)

        assert file_config["telemetry"]["enabled"] is True

        # Verify the runtime config also reflects the change
        config = config_manager.config
        assert config.telemetry.enabled is True

    def test_validation_in_updates(self):
        """Test that updates are validated."""
        config_manager = ConfigManager()
        
        # Invalid confidence threshold
        with pytest.raises(ValueError):
            config_manager.update_config({"detection.confidence_threshold": 1.5})
        
        # Invalid blur strength
        with pytest.raises(ValueError):
            config_manager.update_config({"blur.strength": 20})

    def test_reset_runtime_overrides(self):
        """Test resetting runtime overrides."""
        config_manager = ConfigManager()
        
        # Make runtime changes
        config_manager.update_config({
            "detection.confidence_threshold": 0.9,
            "text.font_scale": 2.0
        }, persist=False)
        
        # Verify changes
        config = config_manager.config
        assert config.detection.confidence_threshold == 0.9
        assert config.text.font_scale == 2.0
        
        # Reset
        config_manager.reset_runtime_overrides()
        
        # Verify reset
        config = config_manager.config
        assert config.detection.confidence_threshold == 0.75  # Back to default
        assert config.text.font_scale == 1.0  # Back to default

    def test_get_runtime_overrides(self):
        """Test getting current runtime overrides."""
        config_manager = ConfigManager()
        
        # Initially no overrides
        assert config_manager.get_runtime_overrides() == {}
        
        # Add some overrides
        config_manager.update_config({
            "detection.confidence_threshold": 0.9
        }, persist=False)
        
        overrides = config_manager.get_runtime_overrides()
        assert overrides["detection.confidence_threshold"] == 0.9


class TestGlobalConfigFunctions:
    """Tests for global configuration functions."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Reset global config manager
        import imagesorcery_mcp.config
        imagesorcery_mcp.config._config_manager = None

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
        
        # Reset global config manager
        import imagesorcery_mcp.config
        imagesorcery_mcp.config._config_manager = None

    def test_get_config_manager(self):
        """Test get_config_manager function."""
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        
        # Should return the same instance
        assert manager1 is manager2

    def test_get_config(self):
        """Test get_config function."""
        config = get_config()
        
        assert isinstance(config, ImageSorceryConfig)
        assert config.detection.confidence_threshold == 0.75
