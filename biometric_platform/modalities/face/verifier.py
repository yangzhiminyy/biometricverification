"""
Baseline face verifier implementation (placeholder).
"""

from __future__ import annotations

from typing import Any, Iterable

from ...core.base import BiometricVerifier, MatchResult, VerificationResult


class FaceVerifier(BiometricVerifier):
    """Placeholder verifier that demonstrates interface usage."""

    modality = "face"

    def __init__(self) -> None:
        # TODO: load detection/recognition models, embedding store, etc.
        self._store: dict[str, Any] = {}
        self._threshold = 0.6

    def enroll(self, user_id: str, samples: Iterable[Any]) -> None:
        # TODO: implement face preprocessing and embedding generation.
        embeddings = list(samples)
        self._store[user_id] = embeddings

    def generate_embedding(self, sample: Any) -> Any:
        # TODO: replace with neural network inference.
        return sample

    def match(self, sample: Any, top_k: int = 5) -> VerificationResult:
        # TODO: compute similarity against stored embeddings.
        matches = [
            MatchResult(user_id=user_id, score=0.0, metadata={})
            for user_id in list(self._store.keys())[:top_k]
        ]
        decision = bool(matches)
        return VerificationResult(matches=matches, threshold=self._threshold, modality=self.modality, decision=decision)

    def remove(self, user_id: str) -> None:
        self._store.pop(user_id, None)

