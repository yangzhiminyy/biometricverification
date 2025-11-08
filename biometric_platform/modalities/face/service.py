"""
Service layer for the face modality.
"""

from __future__ import annotations

from typing import Any

from ...core.base import BiometricService, BiometricVerifier


class FaceService(BiometricService):
    """Facade coordinating face-specific enrollment and verification."""

    modality = "face"

    def __init__(self, verifier: BiometricVerifier) -> None:
        self._verifier = verifier

    def enroll(self, payload: dict[str, Any]) -> dict[str, Any]:
        user_id = payload["user_id"]
        samples = payload["samples"]
        self._verifier.enroll(user_id, samples)
        return {"status": "success", "user_id": user_id}

    def verify(self, payload: dict[str, Any]) -> dict[str, Any]:
        sample = payload["sample"]
        top_k = payload.get("top_k", 5)
        result = self._verifier.match(sample, top_k=top_k)
        return {
            "status": "success",
            "decision": result.decision,
            "threshold": result.threshold,
            "matches": [match.__dict__ for match in result.matches],
        }

    def delete(self, user_id: str) -> dict[str, Any]:
        self._verifier.remove(user_id)
        return {"status": "success", "user_id": user_id}

    def get(self, user_id: str) -> dict[str, Any]:
        # TODO: integrate with dataset manager / metadata store.
        return {"status": "success", "user_id": user_id, "modality": self.modality}

