from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DESCRIPTION_PATHS = {
    "parent": DATA_DIR / "descriptions.json",
    "child": DATA_DIR / "descriptions_child.json",
}
DEFAULT_MESSAGE_KEY = "default"
FALLBACK_DESCRIPTION = "아직 어떤 대상인지 잘 모르겠어요. 손끝으로 다시 천천히 가리켜 주세요."


@lru_cache
def load_descriptions(voice_type: str = "parent") -> dict[str, dict[str, str]]:
    path = DESCRIPTION_PATHS[normalize_voice_type(voice_type)]
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def normalize_voice_type(voice_type: str | None) -> str:
    if voice_type in {"child", "kid", "아이"}:
        return "child"
    return "parent"


def get_message(key: str, voice_type: str = "parent") -> str:
    descriptions = load_descriptions(voice_type)
    messages = descriptions.get("_messages", {})
    return messages.get(key, messages.get(DEFAULT_MESSAGE_KEY, FALLBACK_DESCRIPTION))


def get_description(
    page: str | None,
    object_label: str | None,
    voice_type: str = "parent",
) -> str:
    if page is None or object_label is None:
        return get_message(DEFAULT_MESSAGE_KEY, voice_type)

    descriptions = load_descriptions(voice_type)
    return descriptions.get(page, {}).get(
        object_label,
        get_message(DEFAULT_MESSAGE_KEY, voice_type),
    )
