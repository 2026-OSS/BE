from __future__ import annotations

from pydantic import AliasChoices, BaseModel, Field


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    voice_type: str = Field(
        default="child",
        validation_alias=AliasChoices("voice_type", "voiceType"),
    )
