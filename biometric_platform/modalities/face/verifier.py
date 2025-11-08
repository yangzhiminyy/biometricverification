"""
Baseline face verifier implementation (placeholder).
"""

from __future__ import annotations

from typing import Any, Iterable, List

from ...core.base import BiometricVerifier, MatchResult, VerificationResult


class FaceVerifier(BiometricVerifier):
    """Placeholder verifier that demonstrates interface usage."""

    modality = "face"

    def __init__(self, threshold: float = 0.6) -> None:
        # TODO: load detection/recognition models, embedding store, etc.
        self._store: dict[str, Any] = {}
        self._threshold = threshold

    def enroll(self, user_id: str, samples: Iterable[Any]) -> None:
        # TODO: implement face preprocessing and embedding generation.
        embeddings = [self.generate_embedding(sample) for sample in samples]
        if not embeddings:
            raise ValueError("No samples provided for enrollment")
        self._store[user_id] = embeddings

    def generate_embedding(self, sample: Any) -> Any:
        # TODO: replace with neural network inference.
        return sample

    def match(self, sample: Any, top_k: int = 5) -> VerificationResult:
        # TODO: compute similarity against stored embeddings.
        match_candidates: List[MatchResult] = []
        for user_id, embeddings in self._store.items():
            score = 1.0 if embeddings else 0.0
            match_candidates.append(MatchResult(user_id=user_id, score=score, metadata={}))
        matches = sorted(match_candidates, key=lambda m: m.score, reverse=True)[:top_k]
        decision = bool(matches and matches[0].score >= self._threshold)
        return VerificationResult(matches=matches, threshold=self._threshold, modality=self.modality, decision=decision)

    def remove(self, user_id: str) -> None:
        self._store.pop(user_id, None)

