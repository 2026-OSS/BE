import importlib

from app.core import config as config_module


def test_settings_defaults_to_local_ai_server(monkeypatch):
    monkeypatch.delenv("AI_SERVER_URL", raising=False)
    monkeypatch.delenv("AI_PREDICT_PATH", raising=False)
    monkeypatch.delenv("AI_FRAME_FIELD_NAME", raising=False)
    monkeypatch.delenv("PAGE_CLASSIFIER_ENABLED", raising=False)

    module = importlib.reload(config_module)

    assert module.settings.ai_server_url == "http://127.0.0.1:8001"
    assert module.settings.page_classifier_enabled is False


def test_settings_respects_ai_server_url_override(monkeypatch):
    monkeypatch.setenv("AI_SERVER_URL", "http://127.0.0.1:9000")

    module = importlib.reload(config_module)

    assert module.settings.ai_server_url == "http://127.0.0.1:9000"


def test_settings_can_enable_page_classifier(monkeypatch):
    monkeypatch.setenv("PAGE_CLASSIFIER_ENABLED", "true")

    module = importlib.reload(config_module)

    assert module.settings.page_classifier_enabled is True
