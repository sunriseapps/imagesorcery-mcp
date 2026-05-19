import logging
import os
from pathlib import Path
from typing import Any, Iterator

from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from mcp import McpError
from mcp.types import ErrorData

AVAILABLE_PATHS_ENV = "IMAGESORCERY_AVAILABLE_PATHS"


class PathAccessMiddleware(Middleware):
    """Restrict tool file paths to configured directories."""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("imagesorcery.path_access")

    async def on_call_tool(
        self,
        context: MiddlewareContext,
        call_next: CallNext,
    ) -> Any:
        allowed_dirs = get_allowed_directories()
        if not allowed_dirs:
            return await call_next(context)

        arguments = getattr(context.message, "arguments", None) or {}
        for argument_name, path_value in iter_path_arguments(arguments):
            resolved_path = resolve_path(path_value)
            if not is_path_allowed(resolved_path, allowed_dirs):
                allowed = ", ".join(str(path) for path in allowed_dirs)
                error_message = (
                    f"Path argument '{argument_name}' is outside allowed directories: "
                    f"{resolved_path}. Allowed directories: {allowed}"
                )
                self.logger.warning(error_message)
                raise McpError(ErrorData(code=-32602, message=error_message))

        return await call_next(context)


def get_allowed_directories() -> list[Path]:
    raw_paths = os.getenv(AVAILABLE_PATHS_ENV, "")
    if not raw_paths.strip():
        return []

    allowed_dirs = []
    for raw_path in split_paths(raw_paths):
        if not raw_path:
            continue
        allowed_dirs.append(resolve_path(raw_path))
    return allowed_dirs


def split_paths(raw_paths: str) -> list[str]:
    normalized = raw_paths.replace(",", os.pathsep)
    return [part.strip() for part in normalized.split(os.pathsep) if part.strip()]


def iter_path_arguments(value: Any, prefix: str = "") -> Iterator[tuple[str, str]]:
    if isinstance(value, dict):
        for key, item in value.items():
            name = f"{prefix}.{key}" if prefix else str(key)
            if is_path_argument(str(key)) and isinstance(item, str) and item.strip():
                yield name, item
            else:
                yield from iter_path_arguments(item, name)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            name = f"{prefix}[{index}]" if prefix else f"[{index}]"
            yield from iter_path_arguments(item, name)


def is_path_argument(name: str) -> bool:
    return name == "path" or name.endswith("_path")


def resolve_path(path: str) -> Path:
    return Path(os.path.abspath(os.path.expanduser(path)))


def is_path_allowed(path: Path, allowed_dirs: list[Path]) -> bool:
    return any(path == allowed_dir or path.is_relative_to(allowed_dir) for allowed_dir in allowed_dirs)
