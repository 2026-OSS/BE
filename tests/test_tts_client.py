from app.services.tts_client import build_tts_payload, normalize_tts_voice_type


def test_normalize_tts_voice_type_supports_korean_labels():
    assert normalize_tts_voice_type("아이") == "child"
    assert normalize_tts_voice_type("엄마") == "mom"
    assert normalize_tts_voice_type("아빠") == "dad"


def test_build_tts_payload_uses_child_voice_defaults():
    payload = build_tts_payload("꼬마 원숭이가 있어.", "child")

    assert payload["model"] == "gpt-4o-mini-tts"
    assert payload["voice"] == "coral"
    assert payload["response_format"] == "mp3"
    assert "childlike tone" in payload["instructions"]


def test_build_tts_payload_uses_parent_voice_mapping():
    mom_payload = build_tts_payload("꽃이 다시 싱싱해졌어.", "mom")
    dad_payload = build_tts_payload("꽃이 다시 싱싱해졌어.", "dad")

    assert mom_payload["voice"] == "marin"
    assert dad_payload["voice"] == "cedar"
