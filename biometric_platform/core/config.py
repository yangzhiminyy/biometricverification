"""
Configuration loading utilities.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, validator


class ModalityConfig(BaseModel):
    """Configuration schema for a single biometric modality."""

    enabled: bool = Field(default=True)
    verifier_class: str
    service_class: str
    dataset_manager_class: str | None = Field(default=None)
    model_path: str | None = Field(default=None)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    extras: dict[str, Any] = Field(default_factory=dict)


class AppConfig(BaseModel):
    """Root configuration schema."""

    environment: str = Field(default="development")
    modalities: dict[str, ModalityConfig]
    logging: dict[str, Any] = Field(default_factory=dict)
    storage: dict[str, Any] = Field(default_factory=dict)

    @validator("modalities")
    def ensure_default_modality(cls, value: dict[str, ModalityConfig]) -> dict[str, ModalityConfig]:
        if "face" not in value:
            raise ValueError("modalities must include 'face' configuration")
        return value


def load_yaml_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML content in {path}")
    return data


@lru_cache(maxsize=1)
def load_app_config(config_path: str | Path = "configs/biometric.yaml") -> AppConfig:
    """Load and cache application configuration."""

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    data = load_yaml_file(path)
    return AppConfig(**data)

