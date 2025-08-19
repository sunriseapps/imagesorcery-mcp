import pytest
from fastmcp import Client, FastMCP

from imagesorcery_mcp.server import mcp as image_sorcery_mcp_server


@pytest.fixture
def mcp_server():
    # Use the existing server instance
    return image_sorcery_mcp_server


class TestRemoveBackgroundPromptDefinition:
    """Tests for the remove-background prompt definition and metadata."""

    @pytest.mark.asyncio
    async def test_remove_background_in_prompts_list(self, mcp_server: FastMCP):
        """Tests that remove-background prompt is in the list of available prompts."""
        async with Client(mcp_server) as client:
            prompts = await client.list_prompts()
            # Verify that prompts list is not empty
            assert prompts, "Prompts list should not be empty"

            # Check if remove-background is in the list of prompts
            prompt_names = [prompt.name for prompt in prompts]
            assert "remove-background" in prompt_names, (
                "remove-background prompt should be in the list of available prompts"
            )

    @pytest.mark.asyncio
    async def test_remove_background_description(self, mcp_server: FastMCP):
        """Tests that remove-background prompt has the correct description."""
        async with Client(mcp_server) as client:
            prompts = await client.list_prompts()
            remove_bg_prompt = next(
                (prompt for prompt in prompts if prompt.name == "remove-background"), None
            )

            # Check description
            assert remove_bg_prompt.description, (
                "remove-background prompt should have a description"
            )
            assert "background removal" in remove_bg_prompt.description.lower(), (
                "Description should mention background removal"
            )

    @pytest.mark.asyncio
    async def test_remove_background_parameters(self, mcp_server: FastMCP):
        """Tests that remove-background prompt has the correct parameter structure."""
        async with Client(mcp_server) as client:
            prompts = await client.list_prompts()
            remove_bg_prompt = next(
                (prompt for prompt in prompts if prompt.name == "remove-background"), None
            )

            # Check arguments schema
            assert hasattr(remove_bg_prompt, "arguments"), (
                "remove-background prompt should have an arguments field"
            )
            assert isinstance(remove_bg_prompt.arguments, list), (
                "arguments should be a list of PromptArgument objects"
            )

            # Get argument names for easier checking
            arg_names = [arg.name for arg in remove_bg_prompt.arguments]

            # Check required parameters
            required_params = ["image_path"]
            for param in required_params:
                assert param in arg_names, (
                    f"remove-background prompt should have a '{param}' argument"
                )

            # Check optional parameters
            assert "target_objects" in arg_names, (
                "remove-background prompt should have a 'target_objects' argument"
            )
            assert "output_path" in arg_names, (
                "remove-background prompt should have an 'output_path' argument"
            )

            # Check parameter requirements
            image_path_arg = next(arg for arg in remove_bg_prompt.arguments if arg.name == "image_path")
            target_objects_arg = next(arg for arg in remove_bg_prompt.arguments if arg.name == "target_objects")
            output_path_arg = next(arg for arg in remove_bg_prompt.arguments if arg.name == "output_path")

            assert image_path_arg.required, "image_path should be required"
            assert not target_objects_arg.required, "target_objects should be optional"
            assert not output_path_arg.required, "output_path should be optional"


class TestRemoveBackgroundPromptExecution:
    """Tests for the remove-background prompt execution and results."""

    @pytest.mark.asyncio
    async def test_remove_background_prompt_execution(self, mcp_server: FastMCP):
        """Tests the remove-background prompt execution and return value."""
        async with Client(mcp_server) as client:
            result = await client.get_prompt(
                "remove-background",
                {
                    "image_path": "/test/path/image.jpg",
                    "target_objects": "person",
                    "output_path": "/test/path/output.png",
                },
            )

            # Check that the prompt returned a result
            assert result.messages, "Prompt should return messages"
            assert len(result.messages) > 0, "Prompt should return at least one message"

            # Check the content of the returned prompt
            prompt_content = result.messages[0].content.text
            assert "Step 1:" in prompt_content, "Prompt should contain step-by-step instructions"
            assert "detect" not in prompt_content, "Prompt should not mention detect tool when target_objects specified"
            assert "fill" in prompt_content, "Prompt should mention fill tool"
            assert "find" in prompt_content, "Prompt should mention find tool when target_objects specified"
            assert "person" in prompt_content, "Prompt should include the target objects"
            assert "/test/path/image.jpg" in prompt_content, "Prompt should include the input path"
            assert "/test/path/output.png" in prompt_content, "Prompt should include the output path"

    @pytest.mark.asyncio
    async def test_remove_background_default_parameters(self, mcp_server: FastMCP):
        """Tests the remove-background prompt with default parameters."""
        async with Client(mcp_server) as client:
            result = await client.get_prompt(
                "remove-background",
                {
                    "image_path": "/test/path/photo.jpg",
                },
            )

            # Check that the prompt returned a result
            assert result.messages, "Prompt should return messages"
            prompt_content = result.messages[0].content.text

            # Check default behavior (no target_objects specified)
            assert "find" not in prompt_content, (
                "Prompt should not use find tool when no target_objects specified"
            )
            assert "detect" in prompt_content, (
                "Prompt should use detect tool when no target_objects specified"
            )
            assert "/test/path/photo_no_background.png" in prompt_content, (
                "Prompt should auto-generate output path"
            )

    @pytest.mark.asyncio
    async def test_remove_background_custom_target(self, mcp_server: FastMCP):
        """Tests the remove-background prompt with custom target objects."""
        async with Client(mcp_server) as client:
            result = await client.get_prompt(
                "remove-background",
                {
                    "image_path": "/test/path/car.jpg",
                    "target_objects": "red car",
                },
            )

            # Check that the prompt returned a result
            assert result.messages, "Prompt should return messages"
            prompt_content = result.messages[0].content.text

            # Check custom target objects is used
            assert "red car" in prompt_content, (
                "Prompt should use custom target_objects 'red car'"
            )
            assert "preserving the red car" in prompt_content, (
                "Prompt should mention preserving the custom target"
            )
            assert "find" in prompt_content, (
                "Prompt should include find tool when target_objects specified"
            )
            assert "detect" not in prompt_content, (
                "Prompt should not include detect tool when target_objects specified"
            )
