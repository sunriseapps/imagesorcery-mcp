import logging
import re
from typing import Any

from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from mcp import McpError
from mcp.types import ErrorData


class ImprovedValidationMiddleware(Middleware):
    """Middleware that improves validation error messages from FastMCP tools."""
    
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("imagesorcery.validation")
    
    async def on_message(self, context: MiddlewareContext, call_next: CallNext) -> Any:
        """Handle messages with improved validation error reporting."""
        try:
            return await call_next(context)
        except ToolError as e:
            error_msg = str(e)
            
            if "validation error for call[" in error_msg:
                tool_match = re.search(r'call\[(\w+)\]', error_msg)
                tool_name = tool_match.group(1) if tool_match else "unknown"
                
                errors = []
                
                if "Unexpected keyword argument" in error_msg:
                    lines = error_msg.split('\n')
                    for i, line in enumerate(lines):
                        if "Unexpected keyword argument" in line:
                            if i > 0:
                                param_line = lines[i-1].strip()
                                param_name = param_line.split()[0] if param_line else "unknown"
                                errors.append(f"Unexpected parameter '{param_name}' - this parameter is not accepted by the tool '{tool_name}'")
                
                if "Missing required" in error_msg:
                    param_match = re.search(r"Missing required.*?'(\w+)'", error_msg)
                    if param_match:
                        param_name = param_match.group(1)
                        errors.append(f"Missing required parameter '{param_name}'")
                
                if errors:
                    error_message = "Validation error: " + "; ".join(errors)
                else:
                    error_message = f"Validation error in tool '{tool_name}': check that all parameters are correctly named and have the right types"
                
                self.logger.error(error_message)
                self.logger.debug(f"Original error: {error_msg}")
                
                raise McpError(
                    ErrorData(code=-32602, message=error_message)
                ) from e
            
            raise
        except Exception:
            raise
