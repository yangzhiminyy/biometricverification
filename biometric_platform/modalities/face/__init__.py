"""
Face modality implementation package.
"""

from .service import FaceService
from .verifier import FaceVerifier
from .dataset import FaceDatasetManager

__all__ = ["FaceService", "FaceVerifier", "FaceDatasetManager"]

