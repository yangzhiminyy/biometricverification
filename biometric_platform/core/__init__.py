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
from .config import AppConfig, load_app_config
from .registry import BiometricServiceRegistry

__all__ = [
    "AppConfig",
    "BiometricService",
    "BiometricServiceRegistry",
    "BiometricVerifier",
    "DatasetManager",
    "MatchResult",
    "VerificationResult",
    "load_app_config",
]

