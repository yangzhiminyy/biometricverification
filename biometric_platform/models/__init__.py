"""
Model layer initialization.

Exports model registry utilities and shared abstract interfaces.
"""

from .registry import ModelRegistry
from .manager import ModelManager

__all__ = ["ModelRegistry", "ModelManager"]

