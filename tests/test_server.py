import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call

from imagewizard_mcp.server import (
    Tools,
    WizardServer,
    Result,
    serve,
)
from mcp.types import TextContent, Tool


class TestWizardServer:
    """Test the WizardServer class"""

    def test_always_true(self):
        """Test that always_true returns the expected result"""
        server = WizardServer()
        result = server.always_true()

        assert isinstance(result, Result)
        assert result.result is True
        assert result.message == "This tool always returns true"


class TestServerTools:
    """Test the server tool functionality"""

    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test that the server is initialized with the correct name and tools"""
        # Mock the Server constructor
        mock_server = MagicMock()
        
        # Replace the actual call to the function with a mock
        with patch("imagewizard_mcp.server.Server", return_value=mock_server) as mock_server_class:
            # Stop before stdio_server
            with patch("imagewizard_mcp.server.stdio_server") as mock_stdio:
                mock_stdio.return_value.__aenter__.side_effect = Exception("Stop execution")
                
                # Call serve() but it will raise the exception before stdio_server
                with pytest.raises(Exception, match="Stop execution"):
                    await serve()
            
            # Check that Server was initialized with the correct name
            mock_server_class.assert_called_once_with("imagewizard-mcp")
            
            # Verify other methods were called
            assert mock_server.list_tools.called
            assert mock_server.call_tool.called
            assert mock_server.create_initialization_options.called


    @pytest.mark.asyncio
    async def test_list_tools_content(self):
        """Test the content returned by the list_tools function"""
        # Directly test what would be passed to the list_tools decorator
        original_server = MagicMock()
        wizard_server = WizardServer()
        
        # Extract the decorated function by creating a custom decorator
        captured_func = None
        def fake_decorator():
            def wrapper(func):
                nonlocal captured_func
                captured_func = func
                return func
            return wrapper
        
        # Replace list_tools with our fake decorator
        with patch("imagewizard_mcp.server.Server", return_value=original_server) as mock_server_class:
            original_server.list_tools = fake_decorator
            
            # Prevent actual server execution
            with patch("imagewizard_mcp.server.stdio_server") as mock_stdio:
                mock_stdio.return_value.__aenter__.side_effect = Exception("Stop execution")
                
                # Call serve() but it will raise the exception
                with pytest.raises(Exception):
                    await serve()
        
        # If we successfully captured the function, test it
        if captured_func:
            tools = await captured_func()
            assert len(tools) == 1
            assert isinstance(tools[0], Tool)
            assert tools[0].name == Tools.ALWAYS_TRUE.value
            assert "always returns true" in tools[0].description
        else:
            pytest.fail("Failed to capture the list_tools function")


    @pytest.mark.asyncio
    async def test_call_tool_content(self):
        """Test the content returned by the call_tool function"""
        # Directly test what would be passed to the call_tool decorator
        original_server = MagicMock()
        wizard_server = WizardServer()
        
        # Extract the decorated function by creating a custom decorator
        captured_func = None
        def fake_decorator():
            def wrapper(func):
                nonlocal captured_func
                captured_func = func
                return func
            return wrapper
        
        # Replace call_tool with our fake decorator
        with patch("imagewizard_mcp.server.Server", return_value=original_server) as mock_server_class:
            original_server.call_tool = fake_decorator
            
            # Mock WizardServer to return a controlled response
            with patch("imagewizard_mcp.server.WizardServer") as mock_wizard_class:
                mock_instance = mock_wizard_class.return_value
                mock_instance.always_true.return_value = Result(
                    result=True,
                    message="This tool always returns true"
                )
                
                # Prevent actual server execution
                with patch("imagewizard_mcp.server.stdio_server") as mock_stdio:
                    mock_stdio.return_value.__aenter__.side_effect = Exception("Stop execution")
                    
                    # Call serve() but it will raise the exception
                    with pytest.raises(Exception):
                        await serve()
            
        # If we successfully captured the function, test it
        if captured_func:
            # Test valid tool call
            result = await captured_func(Tools.ALWAYS_TRUE.value, {})
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            content = json.loads(result[0].text)
            assert content["result"] is True
            assert content["message"] == "This tool always returns true"
            
            # Test invalid tool call
            with pytest.raises(ValueError, match="Unknown tool"):
                await captured_func("invalid_tool", {})
        else:
            pytest.fail("Failed to capture the call_tool function")


    @pytest.mark.asyncio
    async def test_call_tool_exception_handling(self):
        """Test that exceptions in call_tool are properly handled"""
        # Setup similar to test_call_tool_content, but throw an exception
        original_server = MagicMock()
        
        # Extract the decorated function by creating a custom decorator
        captured_func = None
        def fake_decorator():
            def wrapper(func):
                nonlocal captured_func
                captured_func = func
                return func
            return wrapper
        
        # Replace call_tool with our fake decorator
        with patch("imagewizard_mcp.server.Server", return_value=original_server) as mock_server_class:
            original_server.call_tool = fake_decorator
            
            # Mock WizardServer to throw an exception
            with patch("imagewizard_mcp.server.WizardServer") as mock_wizard_class:
                mock_instance = mock_wizard_class.return_value
                mock_instance.always_true.side_effect = Exception("Test error")
                
                # Prevent actual server execution
                with patch("imagewizard_mcp.server.stdio_server") as mock_stdio:
                    mock_stdio.return_value.__aenter__.side_effect = Exception("Stop execution")
                    
                    # Call serve() but it will raise the exception
                    with pytest.raises(Exception):
                        await serve()
        
        # If we successfully captured the function, test it
        if captured_func:
            # Test that exception is caught and wrapped
            with pytest.raises(ValueError, match="Error processing request"):
                await captured_func(Tools.ALWAYS_TRUE.value, {})
        else:
            pytest.fail("Failed to capture the call_tool function")
