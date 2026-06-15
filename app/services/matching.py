from __future__ import annotations

from math import sqrt

from app.core.config import settings
from app.models.schemas import DetectedObject, FingerPoint


def is_inside_bbox(finger: FingerPoint, bbox: list[float]) -> bool:
    x1, y1, x2, y2 = bbox
    return x1 <= finger.x <= x2 and y1 <= finger.y <= y2


def bbox_center(bbox: list[float]) -> tuple[float, float]:
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def distance_to_center(finger: FingerPoint, bbox: list[float]) -> float:
    center_x, center_y = bbox_center(bbox)
    return sqrt((finger.x - center_x) ** 2 + (finger.y - center_y) ** 2)


def select_target_object(
    finger: FingerPoint | None,
    objects: list[DetectedObject],
    threshold: float = settings.match_distance_threshold,
) -> tuple[DetectedObject | None, float | None, str]:
    if finger is None:
        return None, None, "손끝 좌표를 인식하지 못했습니다."

    if not objects:
        return None, None, "탐지된 객체가 없습니다."

    inside_objects = [
        detected for detected in objects if is_inside_bbox(finger, detected.bbox)
    ]
    if inside_objects:
        target = max(inside_objects, key=lambda detected: detected.confidence)
        return target, 0.0, "대상을 찾았습니다."

    nearest = min(objects, key=lambda detected: distance_to_center(finger, detected.bbox))
    distance = distance_to_center(finger, nearest.bbox)
    if distance <= threshold:
        return nearest, distance, "대상을 찾았습니다."

    return None, distance, "대상을 조금 더 가까이 가리켜 주세요."
