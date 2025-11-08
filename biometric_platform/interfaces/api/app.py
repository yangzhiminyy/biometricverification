"""
FastAPI application exposing biometric services.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from ...core import BiometricServiceRegistry, load_app_config
from ...modalities.face import FaceService, FaceVerifier

app = FastAPI(title="Biometric Verification API", version="0.1.0")
registry = BiometricServiceRegistry()


def bootstrap_registry() -> None:
    """Register available modality services based on configuration."""
    config = load_app_config()

    if config.modalities["face"].enabled:
        registry.register("face", lambda: FaceService(FaceVerifier()))


bootstrap_registry()


@app.get("/biometric/modalities")
def list_modalities() -> dict[str, list[str]]:
    return {"modalities": registry.available_modalities()}


@app.post("/biometric/{modality}/enroll")
def enroll(modality: str, payload: dict) -> dict:
    try:
        service = registry.get(modality)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return service.enroll(payload)


@app.post("/biometric/{modality}/verify")
def verify(modality: str, payload: dict) -> dict:
    try:
        service = registry.get(modality)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return service.verify(payload)


@app.delete("/biometric/{modality}/{user_id}")
def delete(modality: str, user_id: str) -> dict:
    try:
        service = registry.get(modality)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return service.delete(user_id)


@app.get("/biometric/{modality}/{user_id}")
def get(modality: str, user_id: str) -> dict:
    try:
        service = registry.get(modality)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return service.get(user_id)

