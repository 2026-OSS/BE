from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from app.models.interaction import InteractionResponse
from app.models.schemas import AIResponse
from app.services.ai_client import AIClientError, request_prediction
from app.services.descriptions import get_description
from app.services.matching import select_target_object


router = APIRouter()


def build_interaction_response(
    ai_response: AIResponse,
    voice_type: str = "parent",
) -> InteractionResponse:
    target, distance, message = select_target_object(
        ai_response.finger,
        ai_response.objects,
        voice_type=voice_type,
    )
    page_label = ai_response.page.label
    object_label = target.label if target else None
    description = get_description(page_label, object_label, voice_type)
    tts_text = description if target is not None else message

    return InteractionResponse(
        matched=target is not None,
        page=page_label,
        object=object_label,
        objects=ai_response.objects,
        finger=ai_response.finger,
        description=description,
        ttsText=tts_text,
        message=message,
        distance=distance,
    )


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/api/interaction/detect", response_model=InteractionResponse)
async def detect_interaction(
    frame: UploadFile = File(...),
    voiceType: str = Form("parent"),
) -> InteractionResponse:
    try:
        ai_response = await request_prediction(frame)
    except AIClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 서버 연동에 실패했습니다. 잠시 후 다시 시도해 주세요.",
        ) from exc

    return build_interaction_response(ai_response, voiceType)


@router.post("/api/interaction/mock", response_model=InteractionResponse)
async def mock_interaction(
    ai_response: AIResponse,
    voiceType: str = Query("parent"),
) -> InteractionResponse:
    return build_interaction_response(ai_response, voiceType)
