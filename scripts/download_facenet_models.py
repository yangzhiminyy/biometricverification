import os
from pathlib import Path

import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from torch.hub import download_url_to_file
from PIL import Image


def get_torch_home() -> Path:
    return Path(
        os.path.expanduser(
            os.getenv(
                "TORCH_HOME",
                os.path.join(os.getenv("XDG_CACHE_HOME", "~/.cache"), "torch"),
            )
        )
    )


ARC_FACE_URLS = [
    "https://github.com/timesler/facenet-pytorch/releases/download/v2.2.9/20180402-114759-vggface2.pt",
    "https://ghfast.top/https://github.com/timesler/facenet-pytorch/releases/download/v2.2.9/20180402-114759-vggface2.pt",
]
ARC_FACE_FILENAME = "20180402-114759-vggface2.pt"


def ensure_cache_dir() -> Path:
    cache_root = get_torch_home()
    cache_dir = cache_root / "checkpoints"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def download_arcface_weights(cache_dir: Path) -> None:
    target_path = cache_dir / ARC_FACE_FILENAME
    if target_path.exists():
        return
    last_error = None
    for url in ARC_FACE_URLS:
        try:
            download_url_to_file(url, str(target_path), progress=True)
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            continue
    raise RuntimeError(f"Failed to download ArcFace weights from {ARC_FACE_URLS}") from last_error


def warmup_models(cache_dir: Path, device: str = "cpu") -> None:
    os.environ.setdefault("TORCH_HOME", str(cache_dir.parent))

    mtcnn = MTCNN(image_size=160, margin=0, post_process=False, device=device)
    _ = mtcnn(Image.new("RGB", (160, 160)))

    resnet = InceptionResnetV1(pretrained="vggface2").to(device).eval()
    dummy = torch.zeros(1, 3, 160, 160, device=device)
    with torch.no_grad():
        _ = resnet(dummy)


def main() -> None:
    cache_dir = ensure_cache_dir()
    download_arcface_weights(cache_dir)
    warmup_models(cache_dir)
    print(f"Pretrained weights cached in {cache_dir}")


if __name__ == "__main__":
    main()