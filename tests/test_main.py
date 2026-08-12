from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_text(monkeypatch):
    async def fake_generate_ai_answer(prompt: str) -> str:
        return "Тестова відповідь"

    monkeypatch.setattr(
        "routers.ai.generate_ai_answer",
        fake_generate_ai_answer,
    )

    response = client.post(
        "/ai/generate/",
        json={"prompt": "Поясни FastAPI"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "prompt": "Поясни FastAPI",
        "answer": "Тестова відповідь",
    }


def test_generate_text_with_empty_prompt():
    response = client.post(
        "/ai/generate/",
        json={
            "prompt": "",
        },
    )

    assert response.status_code == 422


def test_generate_text_with_too_long_prompt():
    response = client.post(
        "/ai/generate/",
        json={
            "prompt": "a" * 1001,
        },
    )

    assert response.status_code == 422


def test_generate_text_without_prompt():
    response = client.post(
        "/ai/generate/",
        json={},
    )

    assert response.status_code == 422


def test_generate_text_when_ai_service_fails(monkeypatch):
    async def fake_generate_ai_answer(prompt: str) -> str:
        raise Exception("Ollama is unavailable")

    monkeypatch.setattr(
        "routers.ai.generate_ai_answer",
        fake_generate_ai_answer,
    )

    response = client.post(
        "/ai/generate/",
        json={"prompt": "Поясни FastAPI"},
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "AI service unavailable",
    }