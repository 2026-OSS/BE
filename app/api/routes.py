from __future__ import annotations

from typing import Optional

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

PAGE_OBJECT_LABELS = {
    "page1": {
        "book_monkey",
        "book_flower",
        "book_stone",
        "tactile_monkey",
        "tactile_flower",
        "tactile_stone",
        "braille",
        "text",
    },
    "page2": {
        "book_monkey",
        "book_flowerpot",
        "tactile_monkey",
        "tactile_flowerpot",
        "braille",
        "text",
    },
    "page3": {
        "book_monkey",
        "book_flower",
        "book_flowerpot",
        "tactile_monkey",
        "tactile_flower",
        "tactile_flowerpot",
        "braille",
        "text",
    },
}


def normalize_selected_page(selected_page: str | None) -> str | None:
    if selected_page is None:
        return None

    normalized = selected_page.strip().lower()
    return normalized if normalized in PAGE_OBJECT_LABELS else None


def filter_objects_by_page(
    objects: list[DetectedObject],
    selected_page: str | None,
) -> list[DetectedObject]:
    normalized_page = normalize_selected_page(selected_page)
    if normalized_page is None:
        return objects

    allowed_labels = PAGE_OBJECT_LABELS[normalized_page]
    return [
        detected for detected in objects if detected.label in allowed_labels
    ]


def apply_selected_page(
    ai_response: AIResponse,
    selected_page: str | None,
) -> AIResponse:
    normalized_page = normalize_selected_page(selected_page)
    if normalized_page is None:
        return ai_response

    filtered_objects = filter_objects_by_page(ai_response.objects, normalized_page)
    selected_page_prediction = PagePrediction(label=normalized_page, confidence=1.0)
    return ai_response.model_copy(
        update={
            "page": selected_page_prediction,
            "objects": filtered_objects,
        }
    )


def get_reliable_page_label(ai_response: AIResponse) -> str | None:
    page = ai_response.page
    if page.label == "none" or page.confidence < settings.page_confidence_threshold:
        return None
    return page.label


def infer_page_label_from_objects(objects: list[DetectedObject]) -> str | None:
    labels = {detected.label for detected in objects}

    has_stone = "book_stone" in labels or "tactile_stone" in labels
    has_flower = "book_flower" in labels or "tactile_flower" in labels
    has_flowerpot = "book_flowerpot" in labels or "tactile_flowerpot" in labels

    if has_stone:
        return "page1"
    if has_flower and has_flowerpot:
        return "page3"
    if has_flowerpot:
        return "page2"
    if has_flower:
        return "page1"
    return None


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
    return None


def build_interaction_response(
    ai_response: AIResponse,
    voice_type: str = "parent",
) -> InteractionResponse:
    target, distance, message = select_target_object(
        ai_response.finger,
        ai_response.objects,
        voice_type=voice_type,
    )
    reliable_page_label = get_reliable_page_label(ai_response)
    inferred_page_label = reliable_page_label or infer_page_label_from_objects(
        ai_response.objects
    )
    target = target or select_page_based_object(ai_response)
    object_label = target.label if target else None
    fallback_key = (
        MATCHED_DESCRIPTION_FALLBACK_KEY if target is not None else "default"
    )
    description = get_description(
        inferred_page_label,
        object_label,
        voice_type,
        fallback_key,
    )
    tts_text = description if target is not None else message
    response_page_label = inferred_page_label or ai_response.page.label

    return InteractionResponse(
        matched=target is not None,
        page=response_page_label,
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
    selectedPage: Optional[str] = Form(None),
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
    ai_response = apply_selected_page(ai_response, selectedPage)

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
