# Training Pipeline Overview

This directory hosts scripts and helpers for training biometric models.

## Structure

- `datasets/`: dataset wrappers and preprocessing utilities.
- `configs/`: YAML/JSON training configuration templates.
- `trainers/`: reusable training loops or Lightning modules.
- `scripts/`: entrypoints for preparing data, running training, evaluation.

## Initial Plan

1. Implement face dataset loader reading from `datasets/raw/face`.
2. Build preprocessing script to convert raw images into aligned/normalized samples.
3. Provide training script (`train_face.py`) that loads config, initializes model via `ModelManager`, and runs a basic training loop (placeholder until real model inserted).
4. Add evaluation script to compute verification metrics against validation set.

## Quick Start

```bash
# Prepare processed dataset from raw captures (optional if using pairs dataset)
python training/scripts/prepare_face_dataset.py --raw-root datasets/raw/face --processed-root datasets/processed/face

# Train siamese network with LFW pairs
python training/train_face.py --config training/configs/face_train.yaml --arrow-dir datasets/external/lfw_pairs --split train
```

> NOTE: current training loop uses placeholder embeddings and labels; replace with real model + label encoding when available.

## Arrow dataset conversion
If you downloaded LFW in Arrow/Parquet format (e.g. via Hugging Face `lfw_pairs`), convert it to image folders first:
```bash
python training/scripts/lfw_arrow_to_images.py \
  --arrow-dir datasets/external/lfw_pairs \
  --output datasets/external/lfw_from_arrow \
  --split train \
  --image-column image \
  --identity-column identity
```
Then run `prepare_face_dataset.py` with `--raw-root datasets/external/lfw_from_arrow` to produce processed splits.

Refer to `docs/implementation_plan.md` for task breakdown and integration steps.

