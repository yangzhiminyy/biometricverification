"""
Download and extract the LFW dataset.
"""

from __future__ import annotations

import argparse
import hashlib
import tarfile
from pathlib import Path

import requests

MIRRORS = {
    "official": "https://cloudflare-ipfs.com/ipfs/bafybeihjswiwdgvmtojhk2jfrne55h4pv2m5d6kffcuifzmz2uvptj6dgm?filename=lfw.tgz",
    "gitee": "https://gitee.com/numoon-edu/lfw/releases/download/dataset/lfw.tgz",
    "westlake": "https://dataset-web-links.s3.cn-northwest-1.amazonaws.com.cn/lfw/lfw.tgz",
}
LFW_MD5 = "0b6e0b685b7cd0f356db14d6359d1306"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=30, headers=HEADERS) as response:
        response.raise_for_status()
        with destination.open("wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)


def verify_md5(file_path: Path, expected_md5: str) -> bool:
    hash_md5 = hashlib.md5()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest() == expected_md5


def extract_tar(file_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(file_path, "r:gz") as tar:
        tar.extractall(path=output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and extract the LFW dataset.")
    parser.add_argument("--output", type=str, default="datasets/external/lfw", help="Output directory for extracted images")
    parser.add_argument("--archive", type=str, default="datasets/external/lfw.tgz", help="Path to archive file")
    parser.add_argument("--mirror", type=str, choices=list(MIRRORS.keys()), default="official", help="Download mirror")
    args = parser.parse_args()

    archive_path = Path(args.archive)
    output_dir = Path(args.output)
    mirror_order = [args.mirror] + [m for m in MIRRORS.keys() if m != args.mirror]

    if not archive_path.exists():
        last_error = None
        for mirror in mirror_order:
            url = MIRRORS[mirror]
            try:
                print(f"Downloading LFW from {url}...")
                download_file(url, archive_path)
                break
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                print(f"Failed to download from {mirror}: {exc}")
                continue
        else:
            raise RuntimeError("All mirrors failed to download LFW") from last_error
    else:
        print(f"Archive already exists at {archive_path}")

    if not verify_md5(archive_path, LFW_MD5):
        raise ValueError("MD5 checksum mismatch; download may be corrupted.")

    print(f"Extracting {archive_path} to {output_dir} ...")
    extract_tar(archive_path, output_dir)
    print("LFW dataset ready.")


if __name__ == "__main__":
    main()

