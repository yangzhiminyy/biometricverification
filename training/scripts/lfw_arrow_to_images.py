"""
Convert LFW arrow/parquet dataset into directory of images grouped by identity.
"""

from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
from typing import Any, Optional

from datasets import load_from_disk
from PIL import Image


def ensure_pil(image_field: Any) -> Image.Image:
    if isinstance(image_field, Image.Image):
        return image_field

    if isinstance(image_field, dict):
        path = image_field.get("path")
        if path and Path(path).exists():
            return Image.open(path).convert("RGB")
        data = image_field.get("bytes")
        if data:
            return Image.open(BytesIO(data)).convert("RGB")

    if isinstance(image_field, (bytes, bytearray)):
        return Image.open(BytesIO(image_field)).convert("RGB")

    raise TypeError("Cannot decode image field; please specify --image-column appropriately.")


def resolve_identity(
    example: dict[str, Any],
    identity_column: Optional[str],
    path_column: Optional[str],
) -> str:
    if identity_column and identity_column in example:
        identity_value = example[identity_column]
        if isinstance(identity_value, list | tuple):
            identity_value = identity_value[0]
        if identity_value is not None:
            return str(identity_value)

    if path_column and path_column in example:
        path_value = example[path_column]
        if isinstance(path_value, (list, tuple)):
            path_value = path_value[0]
        if path_value:
            return Path(path_value).parent.name

    raise ValueError("Could not determine identity for sample; consider setting --identity-column or --path-column.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert LFW arrow dataset to image folders.")
    parser.add_argument("--arrow-dir", type=str, required=True, help="Path to directory containing Arrow dataset (load_from_disk format)")
    parser.add_argument("--split", type=str, default=None, help="Dataset split name (if dataset contains splits)")
    parser.add_argument("--output", type=str, default="datasets/external/lfw_from_arrow", help="Destination root for extracted images")
    parser.add_argument("--image-column", type=str, default="image", help="Column name storing image data")
    parser.add_argument("--identity-column", type=str, default="identity", help="Column containing identity (set empty string to disable)")
    parser.add_argument("--path-column", type=str, default="path", help="Column containing original file path (fallback when identity missing)")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Log progress every N samples")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit on number of samples to export")
    args = parser.parse_args()

    dataset = load_from_disk(args.arrow_dir)
    if isinstance(dataset, dict):
        if args.split:
            if args.split not in dataset:
                raise ValueError(f"Split '{args.split}' not found in dataset at {args.arrow_dir}. Available: {list(dataset.keys())}")
            ds = dataset[args.split]
        else:
            raise ValueError("Dataset contains multiple splits; please specify --split")
    else:
        if args.split:
            print("[INFO] Single dataset detected; ignoring --split parameter.")
        ds = dataset

    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)
    image_column = args.image_column
    identity_column = args.identity_column or None
    path_column = args.path_column or None

    for idx, example in enumerate(ds):
        if args.limit and idx >= args.limit:
            break
        try:
            identity = resolve_identity(example, identity_column, path_column)
        except ValueError:
            if "label" in example:
                identity = str(example["label"])
            else:
                print(f"[WARN] Skip sample {idx}: cannot determine identity")
                continue

        if image_column not in example:
            print(f"[WARN] Skip sample {idx}: column '{image_column}' not found.")
            continue

        try:
            image = ensure_pil(example[image_column])
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Failed to decode image for sample {idx}: {exc}")
            continue

        identity_dir = output_root / identity
        identity_dir.mkdir(parents=True, exist_ok=True)
        image_path = identity_dir / f"{identity}_{idx:06d}.jpg"
        image.save(image_path, format="JPEG")

        if idx % 500 == 0:
            print(f"Processed {idx} samples... (latest identity: {identity})")

    print(f"Conversion complete. Images saved to {output_root}")


if __name__ == "__main__":
    main()

