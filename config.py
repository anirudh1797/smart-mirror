import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from core.hardware.platform_detect import Platform, detect_platform

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


@dataclass
class AppConfig:
    platform: Platform
    db_path: str
    camera_source: int | str
    camera_resolution: tuple[int, int]
    face_detection_model: str  # "hog" (CPU) or "cnn" (GPU)
    face_detection_interval: int  # process every Nth frame
    face_tolerance: float
    sd_model_id: str
    sd_num_inference_steps: int
    sd_image_size: int
    fullscreen: bool
    inactivity_timeout_seconds: int
    assets_dir: Path = field(default_factory=lambda: BASE_DIR / "assets")


def load_config(plat: Platform | None = None) -> AppConfig:
    """Load configuration based on detected platform and environment variables."""
    if plat is None:
        plat = detect_platform()

    is_jetson = plat == Platform.JETSON

    return AppConfig(
        platform=plat,
        db_path=os.getenv(
            "SMART_MIRROR_DB_PATH",
            str(BASE_DIR / "smart_mirror.db"),
        ),
        camera_source=int(os.getenv("SMART_MIRROR_CAMERA_SOURCE", "0")),
        camera_resolution=(1280, 720) if is_jetson else (640, 480),
        face_detection_model="cnn" if is_jetson else "hog",
        face_detection_interval=6,
        face_tolerance=float(os.getenv("SMART_MIRROR_FACE_TOLERANCE", "0.6")),
        sd_model_id=os.getenv(
            "SMART_MIRROR_SD_MODEL_ID",
            "runwayml/stable-diffusion-inpainting",
        ),
        sd_num_inference_steps=int(os.getenv("SMART_MIRROR_SD_STEPS", "20" if is_jetson else "10")),
        sd_image_size=512,
        fullscreen=os.getenv("SMART_MIRROR_FULLSCREEN", "false").lower() == "true",
        inactivity_timeout_seconds=60,
    )
