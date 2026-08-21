from fastapi.testclient import TestClient

from main import app


def test_agent_memory_e2e():
    # Використовуємо TestClient як context manager.
    # Обидва HTTP-запити виконуються в одному життєвому циклі
    # тестового FastAPI application.
    with TestClient(app) as client:

        # Крок 1.
        # Реально зберігаємо нотатку через API.
        save_response = client.post(
            "/agent/query/",
            json={
                "message": "Запам'ятай: клієнта звати Андрій"
            },
        )

        assert save_response.status_code == 200

        # Крок 2.
        # Реально читаємо memory другим HTTP-запитом.
        read_response = client.post(
            "/agent/query/",
            json={
                "message": "Як звати клієнта?"
            },
        )

        assert read_response.status_code == 200

        answer = read_response.json()["answer"]

        # Перевіряємо, що агент отримав
        # раніше збережену інформацію.
        assert "Андрій" in answer