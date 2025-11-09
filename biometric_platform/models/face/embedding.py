"""
Face embedding model built on top of backbone.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from ..base import EmbeddingModel
from .backbone import SimpleBackbone


class FaceEmbeddingModel(EmbeddingModel):
    """Wraps backbone and exposes embedding interface."""

    def __init__(self, embedding_dim: int = 512, seed: Optional[int] = None) -> None:
        self.backbone = SimpleBackbone(embedding_dim=embedding_dim, seed=seed)

    def embed(self, image: np.ndarray) -> np.ndarray:
        if image.ndim == 3 and image.shape[2] == 3:
            image = image.astype(np.float32) / 255.0
        feature = self.backbone.forward(image)
        norm = np.linalg.norm(feature) or 1.0
        return (feature / norm).astype(np.float32)

