from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class InteractionResponse(BaseModel):
    matched: bool
    page: Optional[str] = None
    object: Optional[str] = None
    description: str
    ttsText: str
    message: str
    distance: Optional[float] = None
