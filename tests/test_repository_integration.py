import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from repositories import save_ai_request, get_ai_requests


# Окрема тестова база даних.
# Важливо: не використовуємо основну fastapi_ai.
import os

# Локально використовуємо порт 5433.
# У GitHub Actions TEST_DATABASE_URL буде переданий через environment.
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5433/fastapi_ai_test",
)

@pytest.mark.asyncio
async def test_save_and_get_ai_request():
    # Створюємо engine для тестової PostgreSQL.
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    # Створюємо фабрику асинхронних database sessions.
    TestSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Відкриваємо справжню session до test DB.
    async with TestSessionLocal() as db:
        # Реально записуємо дані через repository.
        saved_request = await save_ai_request(
            db=db,
            prompt="Integration test prompt",
            answer="Integration test answer",
        )

        # Реально читаємо дані назад із PostgreSQL.
        requests = await get_ai_requests(
            db=db,
            limit=1,
        )

        # Перевіряємо, що запис отримав ID від БД.
        assert saved_request.id is not None

        # Перевіряємо, що щось прочитали.
        assert len(requests) == 1

        # Перевіряємо дані, які повернула БД.
        assert requests[0].prompt == "Integration test prompt"
        assert requests[0].answer == "Integration test answer"

    # Закриваємо engine після тесту.
    await engine.dispose()