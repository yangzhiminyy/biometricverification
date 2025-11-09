"""
Abstract interfaces for biometric models.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol

import numpy as np


class EmbeddingModel(ABC):
    """Produces embeddings (feature vectors) from preprocessed inputs."""

    @abstractmethod
    def embed(self, image: np.ndarray) -> np.ndarray:
        """Return an embedding for the given image."""


class Detector(ABC):
    """Detects and aligns biometric regions (e.g., faces) in raw images."""

    @abstractmethod
    def detect(self, image: np.ndarray) -> list[np.ndarray]:
        """Return a list of cropped/aligned regions."""


class Recognizer(Protocol):
    """Protocol for full recognition pipeline."""

    def __call__(self, image: np.ndarray) -> np.ndarray: ...


class ModelConfig(Protocol):
    """Configuration protocol expected by model factory."""

    def get(self, key: str, default: Any = None) -> Any: ...

