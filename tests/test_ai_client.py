import asyncio

from app.services import ai_client


def test_request_prediction_sends_page_hint_to_ai_server(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "page": {"label": "page1", "confidence": 0.96},
                "objects": [],
                "finger": None,
            }

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, files, data):
            captured["url"] = url
            captured["files"] = files
            captured["data"] = data
            return FakeResponse()

    monkeypatch.setattr(ai_client.httpx, "AsyncClient", FakeAsyncClient)

    response = asyncio.run(
        ai_client.request_prediction(
            b"image-bytes",
            filename="frame.jpg",
            content_type="image/jpeg",
            page="page1",
            page_number=1,
        )
    )

    assert response.page.label == "page1"
    assert captured["data"] == {"page": "page1", "pageNumber": "1"}
    assert captured["files"]["frame"][0] == "frame.jpg"
