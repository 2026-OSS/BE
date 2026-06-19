from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


DESCRIPTION_PATH = Path(__file__).resolve().parent.parent / "data" / "descriptions.json"
DEFAULT_MESSAGE_KEY = "default"
FALLBACK_DESCRIPTION = "아직 어떤 대상인지 잘 모르겠어요. 손끝으로 다시 천천히 가리켜 주세요."


@lru_cache
def load_descriptions() -> dict[str, dict[str, str]]:
    with DESCRIPTION_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def get_message(key: str) -> str:
    descriptions = load_descriptions()
    messages = descriptions.get("_messages", {})
    return messages.get(key, messages.get(DEFAULT_MESSAGE_KEY, FALLBACK_DESCRIPTION))


def get_description(page: str | None, object_label: str | None) -> str:
    if page is None or object_label is None:
        return get_message(DEFAULT_MESSAGE_KEY)

    descriptions = load_descriptions()
    return descriptions.get(page, {}).get(object_label, get_message(DEFAULT_MESSAGE_KEY))
