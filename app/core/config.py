from __future__ import annotations

import os


class Settings:
    app_name: str = "AI Picture Book Backend"
    ai_server_url: str | None = os.getenv("AI_SERVER_URL")
    ai_predict_path: str = os.getenv("AI_PREDICT_PATH", "/predict")
    ai_frame_field_name: str = os.getenv("AI_FRAME_FIELD_NAME", "frame")
    match_distance_threshold: float = float(os.getenv("MATCH_DISTANCE_THRESHOLD", "80"))
    match_bbox_padding: float = float(os.getenv("MATCH_BBOX_PADDING", "24"))


settings = Settings()
