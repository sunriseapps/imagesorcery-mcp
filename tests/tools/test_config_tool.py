"""
End-to-end tests for the config tool through MCP client interface.
"""

import os
import tempfile
from pathlib import Path

import pytest
import toml
from fastmcp import Client
from fastmcp.exceptions import ToolError

from imagesorcery_mcp.server import mcp


class TestConfigToolE2E:
    """End-to-end tests for the config tool through MCP client."""

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

        # Reset global config manager
        import imagesorcery_mcp.config
        imagesorcery_mcp.config._config_manager = None

    @pytest.mark.asyncio
    async def test_config_tool_registration(self):
        """Test that config tool is properly registered in the server."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            config_tool = next((tool for tool in tools if tool.name == "config"), None)

            assert config_tool is not None, "Config tool should be registered"
            assert config_tool.name == "config"

            # Check input schema has required parameters
            schema = config_tool.inputSchema
            assert "properties" in schema
            assert "action" in schema["properties"]
            assert "key" in schema["properties"]
            assert "value" in schema["properties"]
            assert "persist" in schema["properties"]

    @pytest.mark.asyncio
    async def test_config_get_all(self):
        """Test getting entire configuration through MCP client."""
        async with Client(mcp) as client:
            # Call config tool to get all configuration
            result = await client.call_tool("config", {"action": "get"})

            assert result.is_error is False, f"Config tool should not error: {result.content}"

            # Parse the result content
            content = result.content[0].text
            assert "action" in content
            assert "config" in content
            assert "runtime_overrides" in content

            # Verify it contains expected configuration sections
            assert "detection" in content
            assert "blur" in content
            assert "text" in content

    @pytest.mark.asyncio
    async def test_config_get_specific_key(self):
        """Test getting specific configuration value through MCP client."""
        async with Client(mcp) as client:
            # Call config tool to get specific key
            result = await client.call_tool("config", {
                "action": "get",
                "key": "detection.confidence_threshold"
            })

            assert result.is_error is False, f"Config tool should not error: {result.content}"

            content = result.content[0].text
            assert "action" in content
            assert "key" in content
            assert "value" in content
            assert "detection.confidence_threshold" in content

    @pytest.mark.asyncio
    async def test_config_set_runtime(self):
        """Test setting configuration value for runtime only through MCP client."""
        async with Client(mcp) as client:
            # Set a runtime configuration value
            result = await client.call_tool("config", {
                "action": "set",
                "key": "detection.confidence_threshold",
                "value": 0.8,
                "persist": False
            })

            assert result.is_error is False, f"Config tool should not error: {result.content}"

            content = result.content[0].text
            assert "action" in content
            assert "set" in content
            assert "detection.confidence_threshold" in content
            assert "0.8" in content
            assert "current session" in content

            # Verify the change by getting the value back
            get_result = await client.call_tool("config", {
                "action": "get",
                "key": "detection.confidence_threshold"
            })

            assert get_result.is_error is False
            get_content = get_result.content[0].text
            assert "0.8" in get_content

    @pytest.mark.asyncio
    async def test_config_set_persistent(self):
        """Test setting configuration value persistently through MCP client."""
        async with Client(mcp) as client:
            # Set a persistent configuration value
            result = await client.call_tool("config", {
                "action": "set",
                "key": "blur.strength",
                "value": 21,
                "persist": True
            })

            assert result.is_error is False, f"Config tool should not error: {result.content}"

            content = result.content[0].text
            assert "action" in content
            assert "set" in content
            assert "blur.strength" in content
            assert "21" in content
            assert "persisted to file" in content

            # Verify the config file was updated
            assert Path("config.toml").exists()
            with open("config.toml", "r") as f:
                config_data = toml.load(f)
            assert config_data["blur"]["strength"] == 21

    @pytest.mark.asyncio
    async def test_config_set_invalid_value(self):
        """Test setting invalid configuration value through MCP client."""
        async with Client(mcp) as client:
            # Try to set an invalid confidence threshold
            result = await client.call_tool("config", {
                "action": "set",
                "key": "detection.confidence_threshold",
                "value": 1.5  # Invalid: > 1.0
            })

            assert result.is_error is False  # Tool doesn't error, but returns error in content

            content = result.content[0].text
            assert "error" in content
            assert "Invalid configuration update" in content

    @pytest.mark.asyncio
    async def test_config_reset(self):
        """Test resetting runtime configuration overrides through MCP client."""
        async with Client(mcp) as client:
            # First set some runtime values
            await client.call_tool("config", {
                "action": "set",
                "key": "detection.confidence_threshold",
                "value": 0.9,
                "persist": False
            })

            await client.call_tool("config", {
                "action": "set",
                "key": "text.font_scale",
                "value": 2.0,
                "persist": False
            })

            # Reset runtime overrides
            result = await client.call_tool("config", {"action": "reset"})

            assert result.is_error is False, f"Config tool should not error: {result.content}"

            content = result.content[0].text
            assert "action" in content
            assert "reset" in content
            assert "Runtime configuration overrides reset successfully" in content

            # Verify values are back to defaults
            get_result = await client.call_tool("config", {
                "action": "get",
                "key": "detection.confidence_threshold"
            })

            get_content = get_result.content[0].text
            assert "0.75" in get_content  # Back to default

    @pytest.mark.asyncio
    async def test_config_get_nonexistent_key(self):
        """Test getting non-existent configuration key through MCP client."""
        async with Client(mcp) as client:
            result = await client.call_tool("config", {
                "action": "get",
                "key": "nonexistent.key"
            })

            assert result.is_error is False  # Tool doesn't error, but returns error in content

            content = result.content[0].text
            assert "error" in content
            assert "Configuration key 'nonexistent.key' not found" in content
            assert "available_keys" in content

    @pytest.mark.asyncio
    async def test_config_invalid_action(self):
        """Test config tool with invalid action through MCP client."""
        async with Client(mcp) as client:
            # Invalid action should raise ToolError due to input validation
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("config", {"action": "invalid"})

            assert "Input validation error" in str(exc_info.value)
            assert "invalid" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_config_set_missing_parameters(self):
        """Test config tool with missing required parameters through MCP client."""
        async with Client(mcp) as client:
            # Test setting without key
            result = await client.call_tool("config", {
                "action": "set",
                "value": 0.8
            })

            assert result.is_error is False  # Tool doesn't error, but returns error in content

            content = result.content[0].text
            assert "error" in content
            assert "Key is required for 'set' action" in content
