from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RecognitionConfig:
    img_size: tuple[int, int] = (160, 160)
    sim_threshold: float = 0.60
    required_frames: int = 15
    margin: float = 0.08
    timeout_seconds: int = 3


@dataclass(frozen=True)
class AppConfig:
    model_path: Path = Path("model_int8.tflite")
    gallery_path: Path = Path("gallery.npy")
    names_path: Path = Path("names.txt")
    attendance_dir: Path = Path("data/attendance_logs")
    database_path: Path = Path("data/attendance.db")
    camera_index: int = 0
    frame_delay_ms: int = 30
    table_refresh_ms: int = 3000
