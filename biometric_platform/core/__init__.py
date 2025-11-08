"""
Core abstractions, configuration management, and registries.
"""

from .base import (
    BiometricService,
    BiometricVerifier,
    DatasetManager,
    MatchResult,
    VerificationResult,
)
from .config import AppConfig, load_app_config, ModalityConfig
from .registry import BiometricServiceRegistry
from .utils import import_string

__all__ = [
    "AppConfig",
    "BiometricService",
    "BiometricServiceRegistry",
    "BiometricVerifier",
    "DatasetManager",
    "MatchResult",
    "ModalityConfig",
    "VerificationResult",
    "import_string",
    "load_app_config",
]

