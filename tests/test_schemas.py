import pytest
from pydantic import ValidationError

from app.models.schemas import AIResponse, DetectedObject
from app.models.tts import TTSRequest


def test_ai_response_accepts_class_field_for_detected_object():
    response = AIResponse.model_validate(
        {
            "page": {"label": "page2", "confidence": 0.96},
            "objects": [
                {
                    "class": "book_monkey",
                    "confidence": 0.95,
                    "bbox": [120, 85, 300, 410],
                }
            ],
            "finger": {"x": 210, "y": 180},
        }
    )

    assert response.objects[0].label == "book_monkey"


def test_ai_response_accepts_page_field_for_page_prediction():
    response = AIResponse.model_validate(
        {
            "page": {"page": "page2", "confidence": 0.96},
            "objects": [],
            "finger": {"x": 210, "y": 180},
        }
    )

    assert response.page.label == "page2"


def test_detected_object_rejects_invalid_bbox_order():
    with pytest.raises(ValidationError):
        DetectedObject(
            label="book_monkey",
            confidence=0.95,
            bbox=[300, 85, 120, 410],
        )


def test_tts_request_accepts_voice_type_alias():
    request = TTSRequest.model_validate(
        {
            "text": "꼬마 원숭이가 있어.",
            "voiceType": "mom",
        }
    )

    assert request.voice_type == "mom"
