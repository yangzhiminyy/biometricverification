"""
Baseline face verifier implementation (placeholder).
"""

from __future__ import annotations

from typing import Any, Iterable, List, Optional

import numpy as np

from ...core.base import (
    BiometricVerifier,
    EmbeddingStore,
    MatchResult,
    VerificationResult,
)
from ...infrastructure import InMemoryEmbeddingStore
from ...models.base import EmbeddingModel
from ...models.face.embedding import FaceEmbeddingModel


class FaceVerifier(BiometricVerifier):
    """Placeholder verifier that demonstrates interface usage."""

    modality = "face"

    def __init__(
        self,
        threshold: float = 0.6,
        embedding_store: Optional[EmbeddingStore] = None,
        embedder: Optional[EmbeddingModel] = None,
    ) -> None:
        self._threshold = threshold
        self._store = embedding_store or InMemoryEmbeddingStore(modality=self.modality)
        self._embedder = embedder or FaceEmbeddingModel()

    def enroll(self, user_id: str, samples: Iterable[Any]) -> None:
        # TODO: implement face preprocessing and embedding generation.
        embeddings = [self.generate_embedding(sample) for sample in samples]
        if not embeddings:
            raise ValueError("No samples provided for enrollment")
        self._store.add_embeddings(user_id, embeddings)

    def generate_embedding(self, sample: Any) -> Any:
        if isinstance(sample, list):
            sample_array = np.array(sample, dtype=np.float32)
        else:
            sample_array = np.asarray(sample, dtype=np.float32)
        embedding = self._embedder.embed(sample_array)
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

