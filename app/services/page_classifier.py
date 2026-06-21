from __future__ import annotations

import json
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from app.core.config import settings
from app.models.schemas import PagePrediction


class PageClassifierError(Exception):
    pass


def _load_keras_model(path: Path):
    try:
        from keras.models import load_model
    except ImportError:
        try:
            from tensorflow.keras.models import load_model
        except ImportError as exc:
            raise PageClassifierError(
                "Keras or TensorFlow is required for local page classification."
            ) from exc

    try:
        return load_model(path)
    except Exception as exc:
        raise PageClassifierError("Failed to load local page classifier model.") from exc


@lru_cache
def load_class_names(
    path: Path = settings.page_classifier_class_names_path,
) -> list[str]:
    try:
        with path.open(encoding="utf-8") as file:
            class_names = json.load(file)
    except OSError as exc:
        raise PageClassifierError("Page classifier class names are unavailable.") from exc

    if not isinstance(class_names, list) or not all(
        isinstance(name, str) for name in class_names
    ):
        raise PageClassifierError("Page classifier class names are invalid.")
    return class_names


@lru_cache
def load_page_classifier(model_path: Path = settings.page_classifier_model_path):
    if not model_path.exists():
        raise PageClassifierError("Local page classifier model is unavailable.")
    return _load_keras_model(model_path)


def prepare_image(
    frame_bytes: bytes,
    image_size: int = settings.page_classifier_image_size,
) -> np.ndarray:
    try:
        import numpy as np
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        raise PageClassifierError(
            "NumPy and Pillow are required for local page classification."
        ) from exc

    try:
        image = Image.open(BytesIO(frame_bytes)).convert("RGB")
    except (OSError, UnidentifiedImageError) as exc:
        raise PageClassifierError("Frame is not a valid image.") from exc

    image = image.resize((image_size, image_size))
    pixels = np.asarray(image, dtype=np.float32)
    return np.expand_dims(pixels, axis=0)


def classify_page(frame_bytes: bytes) -> PagePrediction:
    try:
        import numpy as np
    except ImportError as exc:
        raise PageClassifierError(
            "NumPy is required for local page classification."
        ) from exc

    model = load_page_classifier()
    class_names = load_class_names()
    batch = prepare_image(frame_bytes)

    try:
        predictions = np.asarray(model.predict(batch, verbose=0))
    except Exception as exc:
        raise PageClassifierError("Page classifier prediction failed.") from exc
    if predictions.ndim != 2 or predictions.shape[0] < 1:
        raise PageClassifierError("Page classifier returned invalid predictions.")

    scores = predictions[0]
    class_index = int(np.argmax(scores))
    if class_index >= len(class_names):
        raise PageClassifierError("Page classifier result has an unknown class index.")

    return PagePrediction(
        label=class_names[class_index],
        confidence=float(scores[class_index]),
    )


def should_apply_page_prediction(page: PagePrediction) -> bool:
    return page.confidence >= settings.page_classifier_confidence_threshold
