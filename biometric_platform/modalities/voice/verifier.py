"""
Placeholder voice verifier implementation.
"""

from __future__ import annotations

from typing import Any, Iterable, List, Optional

from ...core.base import (
    BiometricVerifier,
    EmbeddingStore,
    MatchResult,
    VerificationResult,
)
from ...infrastructure import InMemoryEmbeddingStore


class VoiceVerifier(BiometricVerifier):
    """Demonstrates voice verification pipeline with placeholder logic."""

    modality = "voice"

    def __init__(
        self,
        threshold: float = 0.6,
        embedding_store: Optional[EmbeddingStore] = None,
    ) -> None:
        self._threshold = threshold
        self._store = embedding_store or InMemoryEmbeddingStore(modality=self.modality)

    def enroll(self, user_id: str, samples: Iterable[Any]) -> None:
        embeddings = [self.generate_embedding(sample) for sample in samples]
        if not embeddings:
            raise ValueError("No samples provided for enrollment")
        self._store.add_embeddings(user_id, embeddings)

    def generate_embedding(self, sample: Any) -> Any:
        return sample

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

