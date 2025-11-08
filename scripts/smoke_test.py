"""
Simple smoke test for the biometric platform.

Usage:
    python scripts/smoke_test.py

The script will:
1. Load application configuration.
2. Instantiate the face modality service via the registry.
3. Enroll a dummy user using placeholder samples.
4. Execute a verification call and print the result.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _ensure_project_root_on_path() -> None:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_ensure_project_root_on_path()

from biometric_platform.bootstrap import initialize_registry  # noqa: E402


def run_smoke_test() -> dict[str, Any]:
    registry, config = initialize_registry()

    service = registry.get("face")

    enroll_payload = {"user_id": "demo_user", "samples": ["sample_frame_1", "sample_frame_2"]}
    enroll_response = service.enroll(enroll_payload)

    verify_payload = {"sample": "sample_frame_1"}
    verify_response = service.verify(verify_payload)

    return {
        "environment": config.environment,
        "modalities": list(config.modalities.keys()),
        "enroll_response": enroll_response,
        "verify_response": verify_response,
    }


if __name__ == "__main__":
    result = run_smoke_test()
    print(json.dumps(result, indent=2, ensure_ascii=False))

