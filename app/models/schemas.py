from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class PagePrediction(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)


class FingerPoint(BaseModel):
    x: float
    y: float


class DetectedObject(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)
    bbox: list[float] = Field(min_length=4, max_length=4)


class AIResponse(BaseModel):
    page: PagePrediction
    objects: list[DetectedObject] = Field(default_factory=list)
    finger: Optional[FingerPoint] = None
