from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass(frozen=True)
class TTSVoiceConfig:
    voice: str
    instructions: str


@dataclass(frozen=True)
class TTSAudioResponse:
    content: bytes
    media_type: str


class TTSClientError(RuntimeError):
    pass


VOICE_CONFIGS: dict[str, TTSVoiceConfig] = {
    "child": TTSVoiceConfig(
        voice="coral",
        instructions="Speak in Korean in a cheerful, friendly, childlike tone for a young listener.",
    ),
    "mom": TTSVoiceConfig(
        voice="marin",
        instructions="Speak in Korean in a warm, calm, reassuring tone like a gentle mother reading aloud.",
    ),
    "dad": TTSVoiceConfig(
        voice="cedar",
        instructions="Speak in Korean in a steady, kind, supportive tone like a calm father reading aloud.",
    ),
}

MEDIA_TYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "opus": "audio/ogg",
    "aac": "audio/aac",
    "flac": "audio/flac",
    "pcm": "audio/pcm",
}


def normalize_tts_voice_type(voice_type: str | None) -> str:
    if voice_type in {"mom", "mother", "엄마"}:
        return "mom"
    if voice_type in {"dad", "father", "아빠"}:
        return "dad"
    return "child"


def build_tts_payload(text: str, voice_type: str) -> dict[str, str]:
    normalized_voice_type = normalize_tts_voice_type(voice_type)
    voice_config = VOICE_CONFIGS[normalized_voice_type]

    return {
        "model": settings.openai_tts_model,
        "input": text,
        "voice": voice_config.voice,
        "instructions": voice_config.instructions,
        "response_format": settings.openai_tts_response_format,
    }


async def synthesize_speech(text: str, voice_type: str) -> TTSAudioResponse:
    if not settings.openai_api_key:
        raise TTSClientError("OPENAI_API_KEY is not configured.")

    payload = build_tts_payload(text, voice_type)

    async with httpx.AsyncClient(timeout=settings.openai_tts_timeout) as client:
        response = await client.post(
            f"{settings.openai_api_base_url.rstrip('/')}/audio/speech",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    if response.is_success:
        return TTSAudioResponse(
            content=response.content,
            media_type=MEDIA_TYPES.get(
                settings.openai_tts_response_format,
                "application/octet-stream",
            ),
        )

    raise TTSClientError(f"OpenAI TTS request failed with status {response.status_code}.")
