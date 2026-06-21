from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Settings:
    app_name: str = "AI Picture Book Backend"
    app_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = app_dir / "data"
    ai_server_url: str = os.getenv("AI_SERVER_URL", "http://127.0.0.1:8001")
    ai_predict_path: str = os.getenv("AI_PREDICT_PATH", "/predict")
    ai_frame_field_name: str = os.getenv("AI_FRAME_FIELD_NAME", "frame")
    page_confidence_threshold: float = float(
        os.getenv("PAGE_CONFIDENCE_THRESHOLD", "0.75")
    )
    page_classifier_enabled: bool = _get_bool("PAGE_CLASSIFIER_ENABLED", False)
    page_classifier_confidence_threshold: float = float(
        os.getenv("PAGE_CLASSIFIER_CONFIDENCE_THRESHOLD", "0.75")
    )
    page_classifier_image_size: int = int(
        os.getenv("PAGE_CLASSIFIER_IMAGE_SIZE", "224")
    )
    page_classifier_model_path: Path = Path(
        os.getenv(
            "PAGE_CLASSIFIER_MODEL_PATH",
            str(data_dir / "page_classifier" / "page_classifier_mobilenetv2.keras"),
        )
    )
    page_classifier_class_names_path: Path = Path(
        os.getenv(
            "PAGE_CLASSIFIER_CLASS_NAMES_PATH",
            str(data_dir / "page_classifier" / "class_names.json"),
        )
    )
    match_distance_threshold: float = float(os.getenv("MATCH_DISTANCE_THRESHOLD", "80"))
    match_bbox_padding: float = float(os.getenv("MATCH_BBOX_PADDING", "24"))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_api_base_url: str = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
    openai_tts_model: str = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    openai_tts_response_format: str = os.getenv("OPENAI_TTS_RESPONSE_FORMAT", "mp3")
    openai_tts_timeout: float = float(os.getenv("OPENAI_TTS_TIMEOUT", "30"))


settings = Settings()
