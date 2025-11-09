"""
Registry for modality-specific models.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from .base import EmbeddingModel


class ModelRegistry:
    """Simple registry to manage model factories per modality."""

    def __init__(self) -> None:
        self._factories: Dict[str, Callable[[], EmbeddingModel]] = {}

    def register(self, modality: str, factory: Callable[[], EmbeddingModel]) -> None:
        key = modality.lower()
        if key in self._factories:
            raise ValueError(f"Model for modality '{modality}' already registered")
        self._factories[key] = factory

    def get(self, modality: str) -> EmbeddingModel:
        key = modality.lower()
        try:
            model = self._factories[key]()
        except KeyError as exc:
            raise KeyError(f"No model registered for modality '{modality}'") from exc
        return model

    def clear(self) -> None:
        self._factories.clear()

