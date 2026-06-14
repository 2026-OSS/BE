from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


DESCRIPTION_PATH = Path(__file__).resolve().parent.parent / "data" / "descriptions.json"
DEFAULT_DESCRIPTION = "대상을 인식하지 못했습니다."


@lru_cache
def load_descriptions() -> dict[str, dict[str, str]]:
    with DESCRIPTION_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def get_description(page: str | None, object_label: str | None) -> str:
    if page is None or object_label is None:
        return DEFAULT_DESCRIPTION

    descriptions = load_descriptions()
    return descriptions.get(page, {}).get(object_label, DEFAULT_DESCRIPTION)
