"""
Model management utilities for biometric modalities.
"""

from __future__ import annotations

from typing import Any, Optional

from ..core.utils import import_string
from ..core.config import ModalityConfig
from .base import EmbeddingModel


class ModelManager:
    """Loads and caches models based on modality configuration."""

    def __init__(self) -> None:
        self._embedding_cache: dict[str, EmbeddingModel] = {}

    def get_embedding_model(self, modality: str, config: ModalityConfig) -> EmbeddingModel:
        if modality in self._embedding_cache:
            return self._embedding_cache[modality]

        model_info: dict[str, Any] = {}
        if config.model:
            model_info = config.model
        elif config.extras and "embedding_model" in config.extras:
            model_info = {"class": config.extras["embedding_model"]}

        class_path = model_info.get("class")
        if not class_path:
            raise ValueError(f"No embedding model configured for modality '{modality}'")

        model_cls = import_string(class_path)
        kwargs = model_info.get("params", {})
        embedding_model = model_cls(**kwargs)
        if not isinstance(embedding_model, EmbeddingModel):
            raise TypeError(f"Embedding model for '{modality}' must implement EmbeddingModel interface")

        self._embedding_cache[modality] = embedding_model
        return embedding_model

    def clear_cache(self) -> None:
        self._embedding_cache.clear()

