"""
Placeholder backbone for face embedding model.
"""

from __future__ import annotations

from typing import Optional

import numpy as np


class SimpleBackbone:
    """A very naive embedding generator (to be replaced with real model)."""

    def __init__(self, embedding_dim: int = 512, seed: Optional[int] = None) -> None:
        self.embedding_dim = embedding_dim
        if seed is not None:
            np.random.seed(seed)

    def forward(self, image: np.ndarray) -> np.ndarray:
        """Produce deterministic pseudo-embeddings."""
        flat = image.flatten().astype(np.float32)
        if flat.size == 0:
            return np.zeros(self.embedding_dim, dtype=np.float32)
        mean = flat.mean()
        std = flat.std() or 1.0
        normalized = (flat - mean) / std
        padded = np.pad(normalized, (0, max(0, self.embedding_dim - normalized.size)))
        return padded[: self.embedding_dim]

