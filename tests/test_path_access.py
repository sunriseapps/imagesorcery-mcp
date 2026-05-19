import os

import pytest
from fastmcp import Client, FastMCP
from PIL import Image

from imagesorcery_mcp.middlewares.path_access import (
    AVAILABLE_PATHS_ENV,
    get_allowed_directories,
    split_paths,
)
from imagesorcery_mcp.server import mcp as image_sorcery_mcp_server


@pytest.fixture
def mcp_server():
    return image_sorcery_mcp_server


@pytest.fixture
def test_image(tmp_path):
    image_dir = tmp_path / "allowed"
    image_dir.mkdir()
    image_path = image_dir / "image.png"
    Image.new("RGB", (20, 20), color="white").save(image_path)
    return image_path


def test_available_paths_empty_disables_restrictions(monkeypatch):
    monkeypatch.delenv(AVAILABLE_PATHS_ENV, raising=False)

    assert get_allowed_directories() == []

    monkeypatch.setenv(AVAILABLE_PATHS_ENV, "  ")

    assert get_allowed_directories() == []


def test_available_paths_supports_pathsep_and_comma():
    raw_paths = os.pathsep.join(["/tmp/images", "/tmp/output"]) + ",/tmp/masks"

    assert split_paths(raw_paths) == ["/tmp/images", "/tmp/output", "/tmp/masks"]


@pytest.mark.asyncio
async def test_path_inside_allowed_directory_is_accepted(
    mcp_server: FastMCP, test_image, monkeypatch
):
    monkeypatch.setenv(AVAILABLE_PATHS_ENV, str(test_image.parent))

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_metainfo", {"input_path": str(test_image)})

    assert result.data["path"] == str(test_image)


@pytest.mark.asyncio
async def test_relative_traversal_outside_allowed_directory_is_rejected(
    mcp_server: FastMCP, tmp_path, monkeypatch
):
    allowed_dir = tmp_path / "allowed"
    outside_dir = tmp_path / "outside"
    allowed_dir.mkdir()
    outside_dir.mkdir()
    outside_image = outside_dir / "image.png"
    Image.new("RGB", (20, 20), color="white").save(outside_image)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(AVAILABLE_PATHS_ENV, str(allowed_dir))

    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as excinfo:
            await client.call_tool(
                "get_metainfo",
                {"input_path": "allowed/../outside/image.png"},
            )

    assert "outside allowed directories" in str(excinfo.value)


@pytest.mark.asyncio
async def test_symlink_inside_allowed_directory_is_accepted_without_resolving_target(
    mcp_server: FastMCP, tmp_path, monkeypatch
):
    allowed_dir = tmp_path / "allowed"
    outside_dir = tmp_path / "outside"
    allowed_dir.mkdir()
    outside_dir.mkdir()
    outside_image = outside_dir / "image.png"
    Image.new("RGB", (20, 20), color="white").save(outside_image)

    try:
        (allowed_dir / "link").symlink_to(outside_dir, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"Symlink creation is not available: {exc}")

    monkeypatch.setenv(AVAILABLE_PATHS_ENV, str(allowed_dir))

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "get_metainfo",
            {"input_path": str(allowed_dir / "link" / "image.png")},
        )

    assert result.data["path"] == str(allowed_dir / "link" / "image.png")


@pytest.mark.asyncio
async def test_output_path_outside_allowed_directory_is_rejected(
    mcp_server: FastMCP, test_image, tmp_path, monkeypatch
):
    outside_output = tmp_path / "outside" / "output.png"
    monkeypatch.setenv(AVAILABLE_PATHS_ENV, str(test_image.parent))

    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as excinfo:
            await client.call_tool(
                "resize",
                {
                    "input_path": str(test_image),
                    "width": 10,
                    "output_path": str(outside_output),
                },
            )

    assert "outside allowed directories" in str(excinfo.value)


@pytest.mark.asyncio
async def test_nested_mask_path_outside_allowed_directory_is_rejected(
    mcp_server: FastMCP, test_image, tmp_path, monkeypatch
):
    output_path = test_image.parent / "output.png"
    outside_mask_path = tmp_path / "outside" / "mask.png"
    monkeypatch.setenv(AVAILABLE_PATHS_ENV, str(test_image.parent))

    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as excinfo:
            await client.call_tool(
                "fill",
                {
                    "input_path": str(test_image),
                    "areas": [{"mask_path": str(outside_mask_path), "color": [0, 0, 0]}],
                    "output_path": str(output_path),
                },
            )

    assert "areas[0].mask_path" in str(excinfo.value)
    assert "outside allowed directories" in str(excinfo.value)
