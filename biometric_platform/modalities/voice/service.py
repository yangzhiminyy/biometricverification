"""
Service layer for the voice modality (placeholder).
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from ...core.base import BiometricService, BiometricVerifier, DatasetManager


class VoiceService(BiometricService):
    """Coordinate voice enrollment and verification."""

    modality = "voice"

    def __init__(self, verifier: BiometricVerifier, dataset_manager: DatasetManager | None = None) -> None:
        self._verifier = verifier
        self._dataset_manager = dataset_manager

    def enroll(self, payload: dict[str, Any]) -> dict[str, Any]:
        user_id = payload["user_id"]
        samples_iterable: Iterable[Any] = payload["samples"]
        materialized_samples = list(samples_iterable)

        saved_paths: list[str] = []
        if self._dataset_manager:
            saved_paths = self._dataset_manager.save_raw_samples(user_id, materialized_samples)
        self._verifier.enroll(user_id, materialized_samples)

        response = {"status": "success", "user_id": user_id}
        if saved_paths:
            response["stored_samples"] = saved_paths
        return response

    def verify(self, payload: dict[str, Any]) -> dict[str, Any]:
        sample = payload["sample"]
        top_k = payload.get("top_k", 5)
        result = self._verifier.match(sample, top_k=top_k)
        return {
            "status": "success",
            "decision": result.decision,
            "threshold": result.threshold,
            "matches": [asdict(match) for match in result.matches],
        }

    def delete(self, user_id: str) -> dict[str, Any]:
        self._verifier.remove(user_id)
        if self._dataset_manager:
            self._dataset_manager.delete_user(user_id)
        return {"status": "success", "user_id": user_id}

    def get(self, user_id: str) -> dict[str, Any]:
        response = {"status": "success", "user_id": user_id, "modality": self.modality}
        if self._dataset_manager:
            response["samples"] = self._dataset_manager.list_user_samples(user_id)
        return response

