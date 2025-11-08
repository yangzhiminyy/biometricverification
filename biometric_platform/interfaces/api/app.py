"""
FastAPI application exposing biometric services.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException

from ...core import BiometricServiceRegistry, load_app_config, import_string

app = FastAPI(title="Biometric Verification API", version="0.1.0")
registry = BiometricServiceRegistry()


def bootstrap_registry() -> None:
    """Register available modality services based on configuration."""
    config = load_app_config()

    dataset_root = Path(config.storage.get("dataset_root", "datasets/raw"))

    for modality, modality_config in config.modalities.items():
        if not modality_config.enabled:
            continue

        verifier_cls = import_string(modality_config.verifier_class)
        service_cls = import_string(modality_config.service_class)
        dataset_manager = None

        if modality_config.dataset_manager_class:
            dataset_manager_cls = import_string(modality_config.dataset_manager_class)
            modality_dataset_root = dataset_root / modality
            dataset_manager = dataset_manager_cls(modality_dataset_root)

        def factory(
            svc_cls=service_cls,
            ver_cls=verifier_cls,
            dataset_manager_instance=dataset_manager,
            modality_threshold=modality_config.threshold,
        ):
            verifier = ver_cls(threshold=modality_threshold)
            return svc_cls(verifier, dataset_manager_instance)

        registry.register(modality, factory)


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

