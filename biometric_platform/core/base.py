"""
Abstract base classes and datamodel definitions for biometric modalities.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Protocol, Sequence


@dataclass(frozen=True)
class MatchResult:
    """Represents a single match candidate."""

    user_id: str
    score: float
    metadata: dict[str, Any]


@dataclass(frozen=True)
class VerificationResult:
    """Standardized verification response."""

    matches: Sequence[MatchResult]
    threshold: float
    modality: str
    decision: bool


class DatasetManager(Protocol):
    """Handles raw and processed biometric datasets."""

    modality: str

    def save_raw_samples(self, user_id: str, samples: Iterable[Any]) -> None: ...

    def list_user_samples(self, user_id: str) -> list[str]: ...

    def delete_user(self, user_id: str) -> None: ...

    def prepare_training_split(self) -> Any: ...


class BiometricVerifier(Protocol):
    """Exposes embedding generation and matching capabilities."""

    modality: str

    def enroll(self, user_id: str, samples: Iterable[Any]) -> None: ...

    def generate_embedding(self, sample: Any) -> Any: ...

    def match(self, sample: Any, top_k: int = 5) -> VerificationResult: ...

    def remove(self, user_id: str) -> None: ...


class BiometricService(Protocol):
    """Orchestrates validation, persistence, and inference for one modality."""

    modality: str

    def enroll(self, payload: dict[str, Any]) -> dict[str, Any]: ...

    def verify(self, payload: dict[str, Any]) -> dict[str, Any]: ...

    def delete(self, user_id: str) -> dict[str, Any]: ...

    def get(self, user_id: str) -> dict[str, Any]: ...

