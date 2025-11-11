"""
Train face verification model using LFW pairs dataset.
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # add training/.. (project root)

import argparse
import yaml
from typing import Any, Dict, Optional

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.transforms as T

from biometric_platform.core.config import load_app_config
from biometric_platform.core.utils import import_string
from biometric_platform.models.manager import ModelManager
from biometric_platform.models.base import EmbeddingModel
from training.datasets.lfw_pairs_dataset import LFWPairsDataset


def load_config(config_path: str | Path) -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_embedding_model(modality: str, model_manager: ModelManager) -> EmbeddingModel:
    app_config = load_app_config()
    modality_config = app_config.modalities[modality]
    return model_manager.get_embedding_model(modality, modality_config)


def instantiate_embedding_model(model_cfg: Dict[str, Any]) -> Optional[EmbeddingModel]:
    class_path = model_cfg.get("class")
    if not class_path:
        return None
    model_cls = import_string(class_path)
    params = model_cfg.get("params", {})
    model = model_cls(**params)
    if not isinstance(model, EmbeddingModel):
        raise TypeError(f"Model class {class_path} does not implement EmbeddingModel")
    return model


class SiameseWrapper(nn.Module):
    def __init__(self, embedder: EmbeddingModel, device: torch.device, embedding_dim: int) -> None:
        super().__init__()
        self.embedder = embedder
        self.device = device
        self.projection = nn.Linear(embedding_dim, embedding_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        embeddings = []
        for img in x:
            img_np = (img.permute(1, 2, 0).cpu().numpy() * 255.0).astype("uint8")
            embedding = self.embedder.embed(img_np)
            embeddings.append(torch.tensor(embedding, device=self.device, dtype=torch.float32))
        stacked = torch.stack(embeddings)
        return self.projection(stacked)


def contrastive_loss(emb1: torch.Tensor, emb2: torch.Tensor, label: torch.Tensor, margin: float = 1.0) -> torch.Tensor:
    distances = torch.nn.functional.pairwise_distance(emb1, emb2)
    loss_pos = label * torch.pow(distances, 2)
    loss_neg = (1 - label) * torch.pow(torch.clamp(margin - distances, min=0.0), 2)
    return 0.5 * torch.mean(loss_pos + loss_neg)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train siamese network with LFW pairs")
    parser.add_argument("--config", type=str, default="training/configs/face_train.yaml", help="Path to config YAML")
    parser.add_argument("--arrow-dir", type=str, default="datasets/external/lfw_pairs", help="Arrow dataset directory")
    parser.add_argument("--split", type=str, default="train", help="Dataset split (train/test)")
    parser.add_argument("--eval-only", action="store_true", help="Evaluate on dataset without training")
    args = parser.parse_args()

    cfg = load_config(args.config)
    data_cfg = cfg.get("data", {})
    train_cfg = cfg["training"]
    model_cfg = cfg.get("model", {})

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model_manager = ModelManager()
    embedding_model = instantiate_embedding_model(model_cfg) or get_embedding_model("face", model_manager)
    sample_dataset = LFWPairsDataset(
        arrow_dir=args.arrow_dir,
        split=args.split,
        transform=T.Compose([T.Resize((160, 160)), T.ToTensor()]),
    )
    sample_img0, sample_img1, _ = sample_dataset[0]
    embedding_sample = embedding_model.embed((sample_img0.permute(1, 2, 0).numpy() * 255).astype("uint8"))
    embedding_dim = len(embedding_sample)
    wrapper = SiameseWrapper(embedding_model, device, embedding_dim).to(device)

    dataloader = DataLoader(
        sample_dataset,
        batch_size=data_cfg.get("batch_size", 32),
        shuffle=True,
        num_workers=data_cfg.get("num_workers", 4),
    )

    optimizer = None if args.eval_only else optim.Adam(wrapper.parameters(), lr=train_cfg["learning_rate"], weight_decay=train_cfg["weight_decay"])
    margin = train_cfg.get("contrastive_margin", 1.0)

    for epoch in range(1 if args.eval_only else train_cfg["epochs"]):
        wrapper.train(not args.eval_only)
        epoch_loss = 0.0
        with torch.set_grad_enabled(not args.eval_only):
            for img0, img1, label in dataloader:
                img0 = img0.to(device)
                img1 = img1.to(device)
                label = label.to(device)

                emb0 = wrapper(img0)
                emb1 = wrapper(img1)

                loss = contrastive_loss(emb0, emb1, label, margin)

                if not args.eval_only:
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

                epoch_loss += loss.item()

        avg_loss = epoch_loss / len(dataloader)
        if args.eval_only:
            print(f"Evaluation - Loss: {avg_loss:.4f}")
        else:
            print(f"Epoch {epoch + 1}/{train_cfg['epochs']} - Loss: {avg_loss:.4f}")


if __name__ == "__main__":
    main()

