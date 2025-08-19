"""
Configuration tool for ImageSorcery MCP.

This tool allows viewing and updating configuration values through the MCP interface.
"""

from typing import Annotated, Any, Dict, Optional, Union

from fastmcp import FastMCP
from pydantic import Field

# Import the central logger and config manager
from imagesorcery_mcp.config import (
    generate_config_documentation,
    get_available_config_keys,
    get_config_manager,
)
from imagesorcery_mcp.logging_config import logger


def _generate_config_tool_docstring() -> str:
    """Generate the dynamic docstring for the config tool."""
    base_doc = """View or update ImageSorcery MCP configuration.

        This tool allows you to:
        - View current configuration values
        - Update configuration values for the current session
        - Persist configuration changes to the config file
        - Reset runtime overrides

        """

    config_doc = generate_config_documentation()

    examples_doc = """

        Examples:
        - Get all config: config(action="get")
        - Get detection confidence: config(action="get", key="detection.confidence_threshold")
        - Set blur strength: config(action="set", key="blur.strength", value=21)
        - Set and persist: config(action="set", key="detection.confidence_threshold", value=0.8, persist=True)
        - Reset overrides: config(action="reset")

        Returns:
            Dictionary containing the requested configuration data or update result"""

    return base_doc + config_doc + examples_doc


def register_tool(mcp: FastMCP):
    @mcp.tool()
    def config(
        action: Annotated[
            str,
            Field(
                description="Action to perform: 'get' to view config, 'set' to update config, 'reset' to reset runtime overrides",
                pattern="^(get|set|reset)$"
            ),
        ] = "get",
        key: Annotated[
            Optional[str],
            Field(
                description=(
                    "Configuration key to get/set. Use dot notation for nested values "
                    "(e.g., 'detection.confidence_threshold', 'blur.strength'). "
                    "Leave empty to get/set entire config."
                )
            ),
        ] = None,
        value: Annotated[
            Optional[Union[str, int, float, bool]],
            Field(
                description="Value to set (only used with action='set')"
            ),
        ] = None,
        persist: Annotated[
            bool,
            Field(
                description="Whether to persist changes to config file (only used with action='set')"
            ),
        ] = False,
    ) -> Dict[str, Any]:
        """Configuration tool - docstring will be set dynamically."""
        logger.info(f"Config tool called with action='{action}', key='{key}', value='{value}', persist={persist}")
        
        config_manager = get_config_manager()
        
        try:
            if action == "get":
                if key is None:
                    # Return entire configuration
                    config_dict = config_manager.get_config_dict()
                    runtime_overrides = config_manager.get_runtime_overrides()
                    
                    result = {
                        "action": "get",
                        "config": config_dict,
                        "runtime_overrides": runtime_overrides,
                        "config_file": str(config_manager.config_file),
                        "message": "Current configuration retrieved successfully"
                    }
                    logger.info("Retrieved entire configuration")
                    return result
                else:
                    # Return specific configuration value
                    config_dict = config_manager.get_config_dict()
                    
                    # Navigate to the requested key
                    if '.' in key:
                        parts = key.split('.')
                        current = config_dict
                        for part in parts:
                            if part not in current:
                                raise KeyError(f"Configuration key '{key}' not found")
                            current = current[part]
                        value_result = current
                    else:
                        if key not in config_dict:
                            raise KeyError(f"Configuration key '{key}' not found")
                        value_result = config_dict[key]
                    
                    result = {
                        "action": "get",
                        "key": key,
                        "value": value_result,
                        "message": f"Configuration value for '{key}' retrieved successfully"
                    }
                    logger.info(f"Retrieved configuration value for key '{key}': {value_result}")
                    return result
            
            elif action == "set":
                if key is None:
                    raise ValueError("Key is required for 'set' action")
                if value is None:
                    raise ValueError("Value is required for 'set' action")
                
                # Prepare update dictionary
                updates = {key: value}
                
                # Update configuration
                updated_config = config_manager.update_config(updates, persist=persist)
                
                # Get the updated value for confirmation
                if '.' in key:
                    parts = key.split('.')
                    current = updated_config
                    for part in parts:
                        current = current[part]
                    new_value = current
                else:
                    new_value = updated_config[key]
                
                result = {
                    "action": "set",
                    "key": key,
                    "old_value": value,  # This is the input value
                    "new_value": new_value,  # This is the validated/processed value
                    "persisted": persist,
                    "message": f"Configuration '{key}' updated successfully" + (" and persisted to file" if persist else " for current session")
                }
                
                logger.info(f"Updated configuration '{key}' to '{new_value}'" + (" (persisted)" if persist else " (runtime only)"))
                return result
            
            elif action == "reset":
                # Reset runtime overrides
                config_manager.reset_runtime_overrides()
                
                result = {
                    "action": "reset",
                    "message": "Runtime configuration overrides reset successfully",
                    "config": config_manager.get_config_dict()
                }
                
                logger.info("Reset runtime configuration overrides")
                return result
            
            else:
                raise ValueError(f"Invalid action '{action}'. Must be 'get', 'set', or 'reset'")
        
        except KeyError as e:
            logger.error(f"Configuration key error: {e}")
            return {
                "action": action,
                "error": str(e),
                "available_keys": get_available_config_keys()
            }
        
        except ValueError as e:
            logger.error(f"Configuration value error: {e}")
            return {
                "action": action,
                "error": str(e),
                "message": "Please check the provided key and value"
            }
        
        except Exception as e:
            logger.error(f"Configuration tool error: {e}", exc_info=True)
            return {
                "action": action,
                "error": f"Configuration operation failed: {str(e)}",
                "message": "An unexpected error occurred while processing the configuration request"
            }

    # Set the dynamic docstring
    config.__doc__ = _generate_config_tool_docstring()
