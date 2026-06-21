from __future__ import annotations

import httpx

from app.core.config import settings
from app.models.schemas import AIResponse


class AIClientError(Exception):
    pass


async def request_prediction(
    frame_bytes: bytes,
    filename: str | None = None,
    content_type: str | None = None,
) -> AIResponse:
    if not settings.ai_server_url:
        raise AIClientError("AI_SERVER_URL is not configured.")

    url = settings.ai_server_url.rstrip("/") + settings.ai_predict_path
    files = {
        settings.ai_frame_field_name: (
            filename or "frame",
            frame_bytes,
            content_type or "application/octet-stream",
        )
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, files=files)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise AIClientError("AI server request failed.") from exc

    try:
        return AIResponse.model_validate(response.json())
    except ValueError as exc:
        raise AIClientError("AI server returned invalid response.") from exc
