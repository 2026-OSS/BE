from __future__ import annotations

from math import sqrt

from app.core.config import settings
from app.models.schemas import DetectedObject, FingerPoint
from app.services.descriptions import get_message


def expand_bbox(bbox: list[float], padding: float) -> list[float]:
    x1, y1, x2, y2 = bbox
    return [x1 - padding, y1 - padding, x2 + padding, y2 + padding]


def is_inside_bbox(
    finger: FingerPoint,
    bbox: list[float],
    padding: float = 0.0,
) -> bool:
    x1, y1, x2, y2 = expand_bbox(bbox, padding)
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
    bbox_padding: float = settings.match_bbox_padding,
    voice_type: str = "parent",
) -> tuple[DetectedObject | None, float | None, str]:
    if not objects:
        return None, None, get_message("no_objects", voice_type)

    if finger is None:
        return None, None, get_message("no_finger", voice_type)

    inside_objects = [
        detected
        for detected in objects
        if is_inside_bbox(finger, detected.bbox, bbox_padding)
    ]
    if inside_objects:
        target = max(inside_objects, key=lambda detected: detected.confidence)
        return target, 0.0, get_message("matched", voice_type)

    nearest = min(objects, key=lambda detected: distance_to_center(finger, detected.bbox))
    distance = distance_to_center(finger, nearest.bbox)
    if distance <= threshold:
        return nearest, distance, get_message("matched", voice_type)

    return None, distance, get_message("not_target_area", voice_type)
