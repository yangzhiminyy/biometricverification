"""
Adapter for integrating pretrained face models.

This is a placeholder demonstrating the expected interface.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

try:
    from facenet_pytorch import InceptionResnetV1
except ImportError:  # pragma: no cover
    InceptionResnetV1 = None  # type: ignore

from ..base import EmbeddingModel


class PretrainedFaceEmbedding(EmbeddingModel):
    """Wraps a pretrained InsightFace/FaceNet style model."""

    def __init__(self, device: str = "cpu", pretrained: str = "vggface2") -> None:
        if InceptionResnetV1 is None:
            raise ImportError("facenet-pytorch is required for PretrainedFaceEmbedding")
        self.model = InceptionResnetV1(pretrained=pretrained).eval().to(device)
        self.device = device

    def embed(self, image: np.ndarray) -> np.ndarray:
        import torch
        import torchvision.transforms as T

        transform = T.Compose(
            [
                T.ToTensor(),
                T.Resize((160, 160)),
                T.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
            ]
        )
        if isinstance(image, np.ndarray):
            if image.ndim == 2:
                image = np.stack([image] * 3, axis=-1)
            tensor = transform(image).unsqueeze(0).to(self.device)
        else:
            raise TypeError("Unsupported image type for pretrained embedding.")

        with torch.no_grad():
            embedding = self.model(tensor)
        feature = embedding.cpu().numpy().squeeze()
        norm = np.linalg.norm(feature) or 1.0
        return (feature / norm).astype(np.float32)

