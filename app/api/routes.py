from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, Query, Response, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.models.interaction import InteractionResponse
from app.models.schemas import AIResponse, DetectedObject, PagePrediction
from app.models.tts import TTSRequest
from app.services.ai_client import AIClientError, request_prediction
from app.services.descriptions import (
    MATCHED_DESCRIPTION_FALLBACK_KEY,
    get_description,
    get_message,
)
from app.services.matching import select_target_object
from app.services.page_classifier import (
    PageClassifierError,
    classify_page,
    should_apply_page_prediction,
)
from app.services.tts_client import TTSClientError, synthesize_speech


router = APIRouter()


def get_reliable_page_label(ai_response: AIResponse) -> str | None:
    page = ai_response.page
    if page.label == "none" or page.confidence < settings.page_confidence_threshold:
        return None
    return page.label


async def get_local_page_prediction(frame_bytes: bytes) -> PagePrediction | None:
    if not settings.page_classifier_enabled:
        return None

    try:
        return await run_in_threadpool(classify_page, frame_bytes)
    except PageClassifierError:
        return None


def apply_local_page_prediction(
    ai_response: AIResponse,
    local_page: PagePrediction | None,
) -> AIResponse:
    if local_page is None or not should_apply_page_prediction(local_page):
        return ai_response
    return ai_response.model_copy(update={"page": local_page})


def select_page_based_object(ai_response: AIResponse) -> DetectedObject | None:
    if ai_response.finger is not None or get_reliable_page_label(ai_response) is None:
        return None
    if not ai_response.objects:
        return None
    return max(ai_response.objects, key=lambda detected: detected.confidence)


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
    description_page_label = get_reliable_page_label(ai_response)
    target = target or select_page_based_object(ai_response)
    if target is not None and ai_response.finger is None:
        message = get_message("matched", voice_type)
    object_label = target.label if target else None
    fallback_key = (
        MATCHED_DESCRIPTION_FALLBACK_KEY if target is not None else "default"
    )
    description = get_description(
        description_page_label,
        object_label,
        voice_type,
        fallback_key,
    )
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
    frame_bytes = await frame.read()

    try:
        ai_response = await request_prediction(
            frame_bytes,
            filename=frame.filename,
            content_type=frame.content_type,
        )
    except AIClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 서버 연동에 실패했습니다. 잠시 후 다시 시도해 주세요.",
        ) from exc

    local_page = await get_local_page_prediction(frame_bytes)
    ai_response = apply_local_page_prediction(ai_response, local_page)

    return build_interaction_response(ai_response, voiceType)


@router.post("/api/interaction/mock", response_model=InteractionResponse)
async def mock_interaction(
    ai_response: AIResponse,
    voiceType: str = Query("parent"),
) -> InteractionResponse:
    return build_interaction_response(ai_response, voiceType)


@router.post("/api/tts")
async def generate_tts_audio(request: TTSRequest) -> Response:
    try:
        audio = await synthesize_speech(request.text, request.voice_type)
    except TTSClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI TTS 음성 생성에 실패했습니다. 잠시 후 다시 시도해 주세요.",
        ) from exc

    return Response(
        content=audio.content,
        media_type=audio.media_type,
        headers={
            "Cache-Control": "no-store",
        },
    )
