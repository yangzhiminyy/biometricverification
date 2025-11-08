"""
FastAPI application exposing biometric services.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from ...bootstrap import initialize_registry
from .schemas import (
    DeleteResponse,
    EnrollmentRequest,
    EnrollmentResponse,
    GetResponse,
    ModalitiesResponse,
    VerificationRequest,
    VerificationResponse,
)

app = FastAPI(title="Biometric Verification API", version="0.1.0")
registry, _config = initialize_registry()


@app.get("/biometric/modalities", response_model=ModalitiesResponse)
def list_modalities() -> dict[str, list[str]]:
    return {"modalities": registry.available_modalities()}


@app.post("/biometric/{modality}/enroll", response_model=EnrollmentResponse)
def enroll(modality: str, payload: EnrollmentRequest) -> dict:
    try:
        service = registry.get(modality)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return service.enroll(payload.dict())


@app.post("/biometric/{modality}/verify", response_model=VerificationResponse)
def verify(modality: str, payload: VerificationRequest) -> dict:
    try:
        service = registry.get(modality)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return service.verify(payload.dict())


@app.delete("/biometric/{modality}/{user_id}", response_model=DeleteResponse)
def delete(modality: str, user_id: str) -> dict:
    try:
        service = registry.get(modality)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return service.delete(user_id)


@app.get("/biometric/{modality}/{user_id}", response_model=GetResponse)
def get(modality: str, user_id: str) -> dict:
    try:
        service = registry.get(modality)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return service.get(user_id)

