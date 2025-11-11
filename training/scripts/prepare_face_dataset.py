"""
Prepare face dataset: split raw images into train/val and copy to processed directory.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from random import Random
from typing import List

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def collect_user_images(raw_root: Path) -> dict[str, List[Path]]:
    user_images: dict[str, List[Path]] = {}
    for user_dir in raw_root.iterdir():
        if not user_dir.is_dir():
            continue
        images = [p for p in user_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS]
        if images:
            user_images[user_dir.name] = images
    return user_images


def split_images(images: List[Path], val_ratio: float, rng: Random) -> tuple[List[Path], List[Path]]:
    shuffled = images[:]
    rng.shuffle(shuffled)
    val_count = max(1, int(len(shuffled) * val_ratio))
    val_images = shuffled[:val_count]
    train_images = shuffled[val_count:]
    if not train_images:
        train_images = val_images
    return train_images, val_images


def copy_images(images: List[Path], target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for image in images:
        shutil.copy(image, target_dir / image.name)


def prepare_dataset(raw_root: Path, processed_root: Path, val_ratio: float, seed: int) -> None:
    rng = Random(seed)
    users = collect_user_images(raw_root)
    if not users:
        raise ValueError(f"No images found in raw dataset directory: {raw_root}")

    for split in ("train", "val"):
        split_dir = processed_root / split
        if split_dir.exists():
            shutil.rmtree(split_dir)

    for user_id, images in users.items():
        train_images, val_images = split_images(images, val_ratio, rng)
        copy_images(train_images, processed_root / "train" / user_id)
        copy_images(val_images, processed_root / "val" / user_id)

    print(f"Prepared dataset at {processed_root}. Users: {len(users)}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare face dataset for training.")
    parser.add_argument("--raw-root", type=str, default="datasets/raw/face", help="Path to raw face dataset")
    parser.add_argument("--processed-root", type=str, default="datasets/processed/face", help="Output directory")
    parser.add_argument("--val-ratio", type=float, default=0.2, help="Validation split ratio")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for shuffling")
    args = parser.parse_args()

    raw_root = Path(args.raw_root)
    processed_root = Path(args.processed_root)
    processed_root.mkdir(parents=True, exist_ok=True)

    prepare_dataset(raw_root, processed_root, args.val_ratio, args.seed)


if __name__ == "__main__":
    main()

