from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.models.schemas import DetectedObject, FingerPoint


class InteractionResponse(BaseModel):
    matched: bool
    page: Optional[str] = None
    object: Optional[str] = None
    objects: list[DetectedObject] = Field(default_factory=list)
    finger: Optional[FingerPoint] = None
    description: str
    ttsText: str
    message: str
    distance: Optional[float] = None
