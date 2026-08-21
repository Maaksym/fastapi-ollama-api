from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_agent_save_note(monkeypatch):
    # Підміняємо run_agent(),
    # щоб functional test не залежав від Ollama і PostgreSQL.
    async def fake_run_agent(message: str, db) -> str:
        return "Нотатку збережено. ID: 1"

    monkeypatch.setattr(
        "routers.agent.run_agent",
        fake_run_agent,
    )

    # Викликаємо endpoint так, як це зробив би клієнт.
    response = client.post(
        "/agent/query/",
        json={
            "message": "Запам'ятай: клієнта звати Андрій"
        },
    )

    # Перевіряємо HTTP status.
    assert response.status_code == 200

    # Перевіряємо JSON-відповідь endpoint.
    assert response.json() == {
        "message": "Запам'ятай: клієнта звати Андрій",
        "answer": "Нотатку збережено. ID: 1",
    }