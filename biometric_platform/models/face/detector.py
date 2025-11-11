"""
Face detection and alignment utilities using MTCNN.
"""

from __future__ import annotations

from typing import List

import numpy as np
from PIL import Image

try:  # pragma: no cover
    from facenet_pytorch import MTCNN
except ImportError as exc:  # pragma: no cover
    raise ImportError("facenet-pytorch is required for MTCNNDetector") from exc


class MTCNNDetector:
    """Wraps facenet-pytorch MTCNN for face alignment."""

    def __init__(
        self,
        image_size: int = 160,
        margin: int = 0,
        post_process: bool = False,
        device: str = "cpu",
        keep_all: bool = False,
    ) -> None:
        self.keep_all = keep_all
        self.image_size = image_size
        self.mtcnn = MTCNN(
            image_size=image_size,
            margin=margin,
            post_process=post_process,
            device=device,
            keep_all=keep_all,
        )

    def detect(self, image: np.ndarray) -> List[np.ndarray]:
        """Return aligned face crops for the given image."""

        if image.ndim == 2:
            image = np.stack([image] * 3, axis=-1)
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)

        pil_image = Image.fromarray(image)
        if self.keep_all:
            faces = self.mtcnn(pil_image)
            if faces is None:
                return []
            if isinstance(faces, list):
                tensors = faces
            else:
                tensors = list(faces)
        else:
            tensor = self.mtcnn(pil_image)
            if tensor is None:
                return []
            tensors = [tensor]

        crops: List[np.ndarray] = []
        for tensor in tensors:
            arr = tensor.permute(1, 2, 0).cpu().numpy()
            arr = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
            crops.append(arr)
        return crops

