from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.models.interaction import InteractionResponse
from app.models.schemas import AIResponse
from app.services.ai_client import AIClientError, request_prediction
from app.services.descriptions import get_description
from app.services.matching import select_target_object


router = APIRouter()


def build_interaction_response(ai_response: AIResponse) -> InteractionResponse:
    target, distance, message = select_target_object(
        ai_response.finger,
        ai_response.objects,
    )
    page_label = ai_response.page.label
    object_label = target.label if target else None
    description = get_description(page_label, object_label)

    return InteractionResponse(
        matched=target is not None,
        page=page_label,
        object=object_label,
        description=description,
        ttsText=description,
        message=message,
        distance=distance,
    )


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/api/interaction/detect", response_model=InteractionResponse)
async def detect_interaction(
    frame: UploadFile = File(...),
) -> InteractionResponse:
    try:
        ai_response = await request_prediction(frame)
    except AIClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 서버 연동에 실패했습니다. 잠시 후 다시 시도해 주세요.",
        ) from exc

    return build_interaction_response(ai_response)


@router.post("/api/interaction/mock", response_model=InteractionResponse)
async def mock_interaction(ai_response: AIResponse) -> InteractionResponse:
    return build_interaction_response(ai_response)
