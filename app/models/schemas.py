from __future__ import annotations

from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class APIModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class PagePrediction(APIModel):
    label: str = Field(validation_alias=AliasChoices("label", "page"))
    confidence: float = Field(ge=0, le=1)


class FingerPoint(APIModel):
    x: float
    y: float


class DetectedObject(APIModel):
    label: str = Field(validation_alias=AliasChoices("label", "class", "class_name"))
    confidence: float = Field(ge=0, le=1)
    bbox: list[float] = Field(min_length=4, max_length=4)

    @field_validator("bbox")
    @classmethod
    def validate_bbox_order(cls, bbox: list[float]) -> list[float]:
        x1, y1, x2, y2 = bbox
        if x1 > x2 or y1 > y2:
            raise ValueError("bbox must use [x1, y1, x2, y2] order")
        return bbox


class AIResponse(APIModel):
    page: PagePrediction
    objects: list[DetectedObject] = Field(default_factory=list)
    finger: Optional[FingerPoint] = None
