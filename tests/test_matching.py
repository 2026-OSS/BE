from app.models.schemas import DetectedObject, FingerPoint
from app.services.matching import (
    bbox_center,
    distance_to_center,
    is_inside_bbox,
    select_target_object,
)


def test_is_inside_bbox_returns_true_for_inner_point():
    finger = FingerPoint(x=210, y=180)

    assert is_inside_bbox(finger, [120, 85, 300, 410]) is True


def test_is_inside_bbox_returns_false_for_outer_point():
    finger = FingerPoint(x=90, y=180)

    assert is_inside_bbox(finger, [120, 85, 300, 410]) is False


def test_bbox_center():
    assert bbox_center([100, 100, 300, 500]) == (200, 300)


def test_distance_to_center():
    finger = FingerPoint(x=200, y=200)

    assert distance_to_center(finger, [100, 100, 300, 300]) == 0


def test_select_target_prefers_inside_bbox():
    finger = FingerPoint(x=150, y=150)
    objects = [
        DetectedObject(label="book_monkey", confidence=0.8, bbox=[100, 100, 200, 200]),
        DetectedObject(label="book_flower", confidence=0.99, bbox=[250, 250, 350, 350]),
    ]

    target, distance, message = select_target_object(finger, objects)

    assert target is not None
    assert target.label == "book_monkey"
    assert distance == 0
    assert message == "대상을 찾았습니다."


def test_select_target_uses_nearest_object_within_threshold():
    finger = FingerPoint(x=230, y=150)
    objects = [
        DetectedObject(label="book_monkey", confidence=0.9, bbox=[100, 100, 200, 200]),
    ]

    target, distance, _ = select_target_object(finger, objects, threshold=100)

    assert target is not None
    assert target.label == "book_monkey"
    assert distance == 80


def test_select_target_returns_none_when_too_far():
    finger = FingerPoint(x=500, y=500)
    objects = [
        DetectedObject(label="book_monkey", confidence=0.9, bbox=[100, 100, 200, 200]),
    ]

    target, distance, message = select_target_object(finger, objects, threshold=80)

    assert target is None
    assert distance is not None
    assert message == "대상을 조금 더 가까이 가리켜 주세요."
