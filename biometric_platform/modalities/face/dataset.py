"""
Dataset manager for face modality.
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Any, Iterable

import numpy as np

try:
    import cv2  # type: ignore
except ImportError:  # pragma: no cover
    cv2 = None  # type: ignore[assignment]

from ...core.base import DatasetManager


class FaceDatasetManager(DatasetManager):
    """Persist raw face samples to disk and provide simple metadata access."""

    modality = "face"

    def __init__(self, root_dir: str | Path | None = None) -> None:
        default_dir = Path("datasets") / "raw" / self.modality
        self._root_dir = Path(root_dir) if root_dir else default_dir
        self._root_dir.mkdir(parents=True, exist_ok=True)

    @property
    def root_dir(self) -> Path:
        return self._root_dir

    def save_raw_samples(self, user_id: str, samples: Iterable[Any]) -> list[str]:
        user_dir = self._root_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)

        saved_paths: list[str] = []
        for sample in samples:
            filename = f"{uuid.uuid4().hex}.png"
            path = user_dir / filename
            self._write_sample(path, sample)
            saved_paths.append(str(path))
        return saved_paths

    def _write_sample(self, path: Path, sample: Any) -> None:
        if isinstance(sample, bytes):
            path.write_bytes(sample)
            return
        if isinstance(sample, np.ndarray):
            if cv2 is None:
                raise RuntimeError("OpenCV (cv2) is required to write numpy array samples")
            cv2.imwrite(str(path), sample)
            return
        if isinstance(sample, str):
            source = Path(sample)
            if source.is_file():
                shutil.copy(source, path)
                return
            # Treat string as placeholder content for smoke tests.
            path.write_text(sample, encoding="utf-8")
            return
        raise TypeError(f"Unsupported sample type for writing: {type(sample)!r}")

    def list_user_samples(self, user_id: str) -> list[str]:
        user_dir = self._root_dir / user_id
        if not user_dir.exists():
            return []
        return sorted(str(p) for p in user_dir.glob("*.png"))

    def delete_user(self, user_id: str) -> None:
        user_dir = self._root_dir / user_id
        if user_dir.exists():
            shutil.rmtree(user_dir)

    def prepare_training_split(self) -> dict[str, Any]:
        # TODO: implement dataset splitting strategy.
        return {"train_dir": str(self._root_dir), "val_dir": str(self._root_dir)}

