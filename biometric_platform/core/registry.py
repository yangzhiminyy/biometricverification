"""
Registry and factory utilities for biometric modality services.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Dict, Type

from .base import BiometricService


class BiometricServiceRegistry:
    """Service locator / registry for modality-specific services."""

    def __init__(self) -> None:
        self._factories: Dict[str, Callable[[], BiometricService]] = {}

    def register(self, modality: str, factory: Callable[[], BiometricService]) -> None:
        key = modality.lower()
        if key in self._factories:
            raise ValueError(f"Modality '{modality}' already registered")
        self._factories[key] = factory

    def get(self, modality: str) -> BiometricService:
        key = modality.lower()
        try:
            service = self._factories[key]()
        except KeyError as exc:
            raise KeyError(f"Modality '{modality}' is not registered") from exc
        return service

    def available_modalities(self) -> list[str]:
        return sorted(self._factories.keys())

    def clear(self) -> None:
        self._factories.clear()

