"""
Biometric Verification Platform package.

该包提供跨模态生物特征识别的核心能力、接口层与基础设施。
"""

from .core.registry import BiometricServiceRegistry

__all__ = ["BiometricServiceRegistry"]

