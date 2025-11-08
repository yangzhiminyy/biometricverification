import copy

from biometric_platform.bootstrap import initialize_registry
from biometric_platform.core.config import AppConfig, ModalityConfig


def build_test_config() -> AppConfig:
    base_config = AppConfig(
        environment="test",
        modalities={
            "face": ModalityConfig(
                enabled=True,
                verifier_class="biometric_platform.modalities.face.verifier.FaceVerifier",
                service_class="biometric_platform.modalities.face.service.FaceService",
                dataset_manager_class="biometric_platform.modalities.face.dataset.FaceDatasetManager",
                threshold=0.6,
            ),
            "voice": ModalityConfig(
                enabled=False,
                verifier_class="biometric_platform.modalities.voice.verifier.VoiceVerifier",
                service_class="biometric_platform.modalities.voice.service.VoiceService",
                dataset_manager_class="biometric_platform.modalities.voice.dataset.VoiceDatasetManager",
                threshold=0.5,
            ),
        },
    )
    return base_config


def test_initialize_registry_only_registers_enabled_modalities():
    config = build_test_config()
    registry, _ = initialize_registry(config)

    assert registry.available_modalities() == ["face"]


def test_initialize_registry_with_enabled_voice():
    config = build_test_config()
    config.modalities["voice"].enabled = True

    registry, _ = initialize_registry(config)
    assert sorted(registry.available_modalities()) == ["face", "voice"]


def test_service_factory_produces_distinct_instances():
    config = build_test_config()
    registry, _ = initialize_registry(config)

    face_service_1 = registry.get("face")
    face_service_2 = registry.get("face")

    assert face_service_1 is not face_service_2
    assert face_service_1.modality == "face"
    assert face_service_2.modality == "face"

