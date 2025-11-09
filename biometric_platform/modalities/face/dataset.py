"""
Dataset manager for face modality.
"""

from __future__ import annotations

import base64
import binascii
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
            written_path = self._write_sample(path, sample)
            saved_paths.append(str(written_path))
        return saved_paths

    def _write_sample(self, path: Path, sample: Any) -> Path:
        if isinstance(sample, bytes):
            path.write_bytes(sample)
            return path
        if isinstance(sample, np.ndarray):
            if cv2 is None:
                raise RuntimeError("OpenCV (cv2) is required to write numpy array samples")
            cv2.imwrite(str(path), sample)
            return path
        if isinstance(sample, str):
            source = Path(sample)
            if source.is_file():
                shutil.copy(source, path)
                return path

            decoded = self._try_decode_data(sample)
            if decoded is not None:
                if decoded.extension:
                    path = path.with_suffix(f".{decoded.extension}")
                path.write_bytes(decoded.content)
                return path

            fallback_path = path.with_suffix(".txt")
            fallback_path.write_text(sample, encoding="utf-8")
            return fallback_path
        raise TypeError(f"Unsupported sample type for writing: {type(sample)!r}")

    class DecodedData:
        def __init__(self, content: bytes, extension: str | None = None) -> None:
            self.content = content
            self.extension = extension

    def _try_decode_data(self, sample: str) -> "FaceDatasetManager.DecodedData | None":
        if sample.startswith("data:"):
            header, _, data_part = sample.partition(",")
            if not data_part:
                return None
            try:
                content = base64.b64decode(data_part, validate=True)
            except binascii.Error:
                return None
            extension = None
            if "/" in header:
                mime_part = header.split(";", 1)[0]
                subtype = mime_part.split("/", 1)[-1]
                if subtype:
                    extension = "jpg" if subtype == "jpeg" else subtype
            return self.DecodedData(content, extension)

        try:
            content = base64.b64decode(sample, validate=True)
            return self.DecodedData(content, None)
        except binascii.Error:
            return None

    def list_user_samples(self, user_id: str) -> list[str]:
        user_dir = self._root_dir / user_id
        if not user_dir.exists():
            return []
        return sorted(str(p) for p in user_dir.iterdir() if p.is_file())

    def delete_user(self, user_id: str) -> None:
        user_dir = self._root_dir / user_id
        if user_dir.exists():
            shutil.rmtree(user_dir)

    def prepare_training_split(self) -> dict[str, Any]:
        # TODO: implement dataset splitting strategy.
        return {"train_dir": str(self._root_dir), "val_dir": str(self._root_dir)}

