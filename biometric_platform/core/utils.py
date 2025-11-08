"""
Shared utilities for the biometric platform.
"""

from __future__ import annotations

import importlib
from typing import Any, TypeVar

T = TypeVar("T")


def import_string(path: str) -> Any:
    """Import dotted module path and return the referenced attribute."""

    if "." not in path:
        raise ValueError(f"Invalid import path: '{path}'")
    module_path, attr = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, attr)

