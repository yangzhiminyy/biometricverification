"""
Shared bootstrap utilities for configuring modality services.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from .core import (
    AppConfig,
    BiometricServiceRegistry,
    ModalityConfig,
    import_string,
    load_app_config,
)
from .models import ModelManager


def _create_service_factory(
    modality: str,
    modality_config: ModalityConfig,
    dataset_root: Path,
    model_manager: ModelManager,
):
    """Create a lazy factory for the given modality."""

    # The dataset manager can be relatively heavy; instantiate lazily inside the factory.
    dataset_manager_instance = None
    if modality_config.dataset_manager_class:
        dataset_manager_cls = import_string(modality_config.dataset_manager_class)
        dataset_manager_instance = dataset_manager_cls(dataset_root / modality)

    embedding_model = None
    try:
        embedding_model = model_manager.get_embedding_model(modality, modality_config)
    except ValueError:
        embedding_model = None

    detector_instance = None
    detector_cfg = modality_config.extras.get("detector") if modality_config.extras else None
    if detector_cfg:
        detector_class = detector_cfg.get("class")
        detector_params = detector_cfg.get("params", {})
        if detector_class:
            detector_cls = import_string(detector_class)
            detector_instance = detector_cls(**detector_params)

    def factory():
        verifier_cls = import_string(modality_config.verifier_class)
        service_cls = import_string(modality_config.service_class)

        verifier_kwargs = {}
        if modality_config.extras:
            verifier_kwargs = modality_config.extras.get("verifier_kwargs", {})

        if embedding_model is not None:
            verifier_kwargs.setdefault("embedder", embedding_model)
        if detector_instance is not None:
            verifier_kwargs.setdefault("detector", detector_instance)

        verifier = verifier_cls(threshold=modality_config.threshold, **verifier_kwargs)

        return service_cls(verifier, dataset_manager_instance)

    return factory


def initialize_registry(config: AppConfig | None = None) -> Tuple[BiometricServiceRegistry, AppConfig]:
    """
    Build a service registry using the provided or default configuration.

    Returns:
        (registry, config)
    """

    if config is None:
        config = load_app_config()

    registry = BiometricServiceRegistry()
    dataset_root = Path(config.storage.get("dataset_root", "datasets/raw"))
    model_manager = ModelManager()

    for modality, modality_config in config.modalities.items():
        if not modality_config.enabled:
            continue

        factory = _create_service_factory(modality, modality_config, dataset_root, model_manager)
        registry.register(modality, factory)

    return registry, config

