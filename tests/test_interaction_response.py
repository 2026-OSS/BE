from app.api.routes import (
    apply_local_page_prediction,
    apply_page_hint,
    build_interaction_response,
    normalize_page_hint,
)
from app.models.schemas import AIResponse, PagePrediction


def test_build_interaction_response_includes_raw_detection_fields():
    ai_response = AIResponse.model_validate(
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

    response = build_interaction_response(ai_response, "child")

    assert response.page == "page2"
    assert response.pageConfidence == 0.96
    assert response.object == "book_monkey"
    assert response.objectConfidence == 0.95
    assert response.matched is True
    assert response.ttsText == "꼬마 원숭이가 코코넛 화분에 꽃을 심고 있어."
    assert response.message == "찾았어."
    assert response.objects[0].label == "book_monkey"
    assert response.finger is not None
    assert response.finger.x == 210
    assert response.finger.y == 180


def test_build_interaction_response_keeps_raw_fields_when_not_matched():
    ai_response = AIResponse.model_validate(
        {
            "page": {"label": "page1", "confidence": 0.91},
            "objects": [
                {
                    "class": "book_flower",
                    "confidence": 0.88,
                    "bbox": [120, 85, 300, 410],
                }
            ],
            "finger": {"x": 500, "y": 500},
        }
    )

    response = build_interaction_response(ai_response, "child")

    assert response.matched is False
    assert response.object is None
    assert response.objectConfidence is None
    assert response.ttsText == "여기는 설명할 곳이 아닌 것 같아. 책이나 놀이도구를 손끝으로 가리켜 줘."
    assert response.description == "음, 아직 잘 모르겠어. 손끝으로 다시 천천히 가리켜 줘."
    assert len(response.objects) == 1
    assert response.objects[0].label == "book_flower"
    assert response.finger is not None


def test_build_interaction_response_uses_matched_fallback_when_page_is_none():
    ai_response = AIResponse.model_validate(
        {
            "page": {"label": "none", "confidence": 0.72},
            "objects": [
                {
                    "class": "book_monkey",
                    "confidence": 0.95,
                    "bbox": [120, 85, 420, 510],
                }
            ],
            "finger": {"x": 359, "y": 424},
        }
    )

    response = build_interaction_response(ai_response, "child")

    assert response.matched is True
    assert response.page == "none"
    assert response.object == "book_monkey"
    assert response.message == "찾았어."
    assert (
        response.description
        == "찾았어. 책 페이지가 더 잘 보이게 다시 비춰 주면 자세히 말해 줄게."
    )
    assert response.ttsText == response.description


def test_build_interaction_response_uses_fallback_when_page_confidence_is_low():
    ai_response = AIResponse.model_validate(
        {
            "page": {"label": "page2", "confidence": 0.42},
            "objects": [
                {
                    "class": "book_monkey",
                    "confidence": 0.95,
                    "bbox": [120, 85, 420, 510],
                }
            ],
            "finger": {"x": 210, "y": 180},
        }
    )

    response = build_interaction_response(ai_response, "child")

    assert response.matched is True
    assert response.page == "page2"
    assert response.object == "book_monkey"
    assert (
        response.description
        == "찾았어. 책 페이지가 더 잘 보이게 다시 비춰 주면 자세히 말해 줄게."
    )
    assert response.ttsText == response.description


def test_build_interaction_response_uses_page_object_when_finger_is_missing():
    ai_response = AIResponse.model_validate(
        {
            "page": {"label": "page2", "confidence": 0.96},
            "objects": [
                {
                    "class": "book_flowerpot",
                    "confidence": 0.88,
                    "bbox": [120, 85, 420, 510],
                },
                {
                    "class": "book_monkey",
                    "confidence": 0.95,
                    "bbox": [430, 85, 650, 510],
                },
            ],
            "finger": None,
        }
    )

    response = build_interaction_response(ai_response, "child")

    assert response.matched is True
    assert response.page == "page2"
    assert response.object == "book_monkey"
    assert response.finger is None
    assert response.message == "찾았어."
    assert response.ttsText == "꼬마 원숭이가 코코넛 화분에 꽃을 심고 있어."


def test_build_interaction_response_keeps_no_finger_when_page_confidence_is_low():
    ai_response = AIResponse.model_validate(
        {
            "page": {"label": "page2", "confidence": 0.42},
            "objects": [
                {
                    "class": "book_monkey",
                    "confidence": 0.95,
                    "bbox": [120, 85, 420, 510],
                }
            ],
            "finger": None,
        }
    )

    response = build_interaction_response(ai_response, "child")

    assert response.matched is False
    assert response.object is None
    assert response.message == "손끝이 잘 안 보여. 손을 화면 안에 넣고 다시 가리켜 줘."
    assert response.ttsText == response.message


def test_apply_local_page_prediction_overrides_page_when_confident():
    ai_response = AIResponse.model_validate(
        {
            "page": {"label": "none", "confidence": 0.8},
            "objects": [],
            "finger": None,
        }
    )
    local_page = PagePrediction(label="page3", confidence=0.93)

    updated = apply_local_page_prediction(ai_response, local_page)

    assert updated.page.label == "page3"
    assert updated.page.confidence == 0.93
    assert ai_response.page.label == "none"


def test_apply_local_page_prediction_keeps_ai_page_when_local_confidence_is_low():
    ai_response = AIResponse.model_validate(
        {
            "page": {"label": "page1", "confidence": 0.82},
            "objects": [],
            "finger": None,
        }
    )
    local_page = PagePrediction(label="page2", confidence=0.42)

    updated = apply_local_page_prediction(ai_response, local_page)

    assert updated.page.label == "page1"
    assert updated.page.confidence == 0.82


def test_normalize_page_hint_uses_page_before_page_number():
    assert normalize_page_hint(" page2 ", 3) == "page2"


def test_normalize_page_hint_uses_page_number_when_page_is_missing():
    assert normalize_page_hint(None, 2) == "page2"


def test_apply_page_hint_replaces_none_page():
    ai_response = AIResponse.model_validate(
        {
            "page": {"label": "none", "confidence": 0.82},
            "objects": [],
            "finger": None,
        }
    )

    updated = apply_page_hint(ai_response, "page2", None)

    assert updated.page.label == "page2"
    assert updated.page.confidence == 0.82


def test_apply_page_hint_replaces_low_confidence_page():
    ai_response = AIResponse.model_validate(
        {
            "page": {"label": "page1", "confidence": 0.42},
            "objects": [],
            "finger": None,
        }
    )

    updated = apply_page_hint(ai_response, None, 2)

    assert updated.page.label == "page2"
    assert updated.page.confidence == 0.75


def test_apply_page_hint_keeps_reliable_ai_page():
    ai_response = AIResponse.model_validate(
        {
            "page": {"label": "page1", "confidence": 0.91},
            "objects": [],
            "finger": None,
        }
    )

    updated = apply_page_hint(ai_response, "page2", None)

    assert updated.page.label == "page1"
    assert updated.page.confidence == 0.91
