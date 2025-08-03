"""Path manipulation utilities."""

import os
from pathlib import Path
from typing import Optional, Union


def expand_path(path: Union[str, Path]) -> Path:
    """Expand user home directory and resolve path."""
    if isinstance(path, str):
        expanded = os.path.expanduser(path)
        return Path(expanded).resolve()
    return path.expanduser().resolve()


def expand_path_str(path: str) -> str:
    """Expand user home directory and return as string."""
    return str(expand_path(path))


def resolve_relative_path(
    path: Union[str, Path], base_dir: Optional[Union[str, Path]] = None
) -> Path:
    """Resolve path relative to base directory if not absolute."""
    path_obj = Path(path)

    if path_obj.is_absolute():
        return expand_path(path_obj)

    if base_dir:
        base_path = expand_path(base_dir)
        return (base_path / path_obj).resolve()

    return expand_path(path_obj)


def ensure_directory_exists(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if necessary."""
    path_obj = expand_path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def validate_executable_path(path: Union[str, Path]) -> bool:
    """Check if path exists and is executable."""
    path_obj = expand_path(path)
    return path_obj.exists() and os.access(path_obj, os.X_OK)
