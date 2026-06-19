from app.services.descriptions import (
    get_description,
    get_message,
    normalize_voice_type,
)


def test_parent_voice_uses_default_descriptions():
    description = get_description("page1", "book_monkey", "mom")

    assert description == "꼬마 원숭이가 있어요."


def test_dad_voice_uses_default_descriptions():
    description = get_description("page2", "tactile_flowerpot", "dad")

    assert description == "오돌토돌한 코코넛 화분이에요. 울퉁불퉁한 곳을 손끝으로 천천히 만져보세요."


def test_child_voice_uses_child_descriptions():
    description = get_description("page1", "book_monkey", "child")

    assert description == "꼬마 원숭이가 있어."


def test_child_voice_uses_child_messages():
    message = get_message("no_finger", "child")

    assert message == "손끝이 잘 안 보여. 손을 화면 안에 넣고 다시 가리켜 줘."


def test_normalizes_korean_child_voice_type():
    assert normalize_voice_type("아이") == "child"
