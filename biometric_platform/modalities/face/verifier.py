"""
Baseline face verifier implementation (placeholder).
"""

from __future__ import annotations

from typing import Any, Iterable, List, Optional

import base64
import binascii
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

from ...core.base import (
    BiometricVerifier,
    EmbeddingStore,
    MatchResult,
    VerificationResult,
)
from ...infrastructure import InMemoryEmbeddingStore
from ...models.base import EmbeddingModel
from ...models.face.detector import MTCNNDetector
from ...models.face.embedding import FaceEmbeddingModel


class FaceVerifier(BiometricVerifier):
    """Face verifier integrating detection and embedding models."""

    modality = "face"

    def __init__(
        self,
        threshold: float = 0.6,
        embedding_store: Optional[EmbeddingStore] = None,
        embedder: Optional[EmbeddingModel] = None,
        detector: Optional[MTCNNDetector] = None,
    ) -> None:
        self._threshold = threshold
        self._store = embedding_store or InMemoryEmbeddingStore(modality=self.modality)
        self._embedder = embedder or FaceEmbeddingModel()
        self._detector = detector or MTCNNDetector()

    def enroll(self, user_id: str, samples: Iterable[Any]) -> None:
        embeddings = [self.generate_embedding(sample) for sample in samples]
        if not embeddings:
            raise ValueError("No samples provided for enrollment")
        self._store.add_embeddings(user_id, embeddings)

    def generate_embedding(self, sample: Any) -> Any:
        image = self._load_image(sample)
        if self._detector:
            faces = self._detector.detect(image)
            if faces:
                image = faces[0]
        embedding = self._embedder.embed(image)
        return embedding.tolist()

    def match(self, sample: Any, top_k: int = 5) -> VerificationResult:
        embedding = self.generate_embedding(sample)
        query_results = self._store.query(embedding, top_k=top_k)

        matches: List[MatchResult] = [
            MatchResult(user_id=user_id, score=score, metadata=metadata)
            for user_id, score, metadata in query_results
        ]
        decision = bool(matches and matches[0].score >= self._threshold)
        return VerificationResult(matches=matches, threshold=self._threshold, modality=self.modality, decision=decision)

    def remove(self, user_id: str) -> None:
        self._store.delete_user(user_id)

    def _load_image(self, sample: Any) -> np.ndarray:
        if isinstance(sample, np.ndarray):
            image = sample
        elif isinstance(sample, list):
            image = np.array(sample)
        elif isinstance(sample, str):
            image = self._decode_string_sample(sample)
        else:
            raise TypeError(f"Unsupported sample type: {type(sample)!r}")

        if image.ndim == 2:
            image = np.stack([image] * 3, axis=-1)
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        return image

    def _decode_string_sample(self, sample: str) -> np.ndarray:
        if sample.startswith("data:"):
            _, _, data_part = sample.partition(",")
            if not data_part:
                raise ValueError("Invalid data URI sample")
            try:
                data_bytes = base64.b64decode(data_part, validate=True)
            except binascii.Error as exc:
                raise ValueError("Invalid base64 data URI") from exc
            return self._image_from_bytes(data_bytes)

        potential_path = Path(sample)
        if potential_path.exists():
            try:
                with Image.open(potential_path) as img:
                    return np.array(img.convert("RGB"))
            except UnidentifiedImageError as exc:
                raise ValueError(f"Unable to load image from path: {sample}") from exc

        try:
            data_bytes = base64.b64decode(sample, validate=True)
            return self._image_from_bytes(data_bytes)
        except binascii.Error as exc:
            raise ValueError("Unsupported string sample format") from exc

    @staticmethod
    def _image_from_bytes(data: bytes) -> np.ndarray:
        try:
            with Image.open(BytesIO(data)) as img:
                return np.array(img.convert("RGB"))
        except UnidentifiedImageError as exc:
            raise ValueError("Unable to decode image bytes") from exc

