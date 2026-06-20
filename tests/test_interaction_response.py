from app.api.routes import build_interaction_response
from app.models.schemas import AIResponse


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
    assert response.object == "book_monkey"
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
    assert response.ttsText == "여기는 설명할 곳이 아닌 것 같아. 책이나 놀이도구를 손끝으로 가리켜 줘."
    assert response.description == "음, 아직 잘 모르겠어. 손끝으로 다시 천천히 가리켜 줘."
    assert len(response.objects) == 1
    assert response.objects[0].label == "book_flower"
    assert response.finger is not None
