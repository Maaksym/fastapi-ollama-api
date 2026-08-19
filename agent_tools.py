from sqlalchemy.ext.asyncio import AsyncSession

from repositories import get_ai_requests

from sqlalchemy import select

from models import Note

import httpx

async def get_history_tool(
    db: AsyncSession,
    limit: int = 5,
) -> str:
    requests = await get_ai_requests(
        db=db,
        limit=limit,
    )

    if not requests:
        return "Історія запитів порожня"

    result = []

    for item in requests:
        result.append(
            f"Prompt: {item.prompt}\nAnswer: {item.answer}"
        )

    return "\n\n".join(result)


async def save_note_tool(
    db: AsyncSession,
    text: str,
) -> str:
    # Створюємо нову нотатку як SQLAlchemy-об'єкт
    note = Note(
        text=text,
    )

    # Додаємо нотатку в database session
    db.add(note)

    # Зберігаємо зміни в PostgreSQL
    await db.commit()

    # Оновлюємо object даними з БД, наприклад id
    await db.refresh(note)

    # Повертаємо результат агенту
    return f"Нотатку збережено. ID: {note.id}"


async def get_notes_tool(
    db: AsyncSession,
    limit: int = 5,
) -> str:
    # Читаємо останні нотатки з PostgreSQL
    result = await db.execute(
        select(Note)
        .order_by(Note.id.desc())
        .limit(limit)
    )

    # Отримуємо список Note-об'єктів
    notes = result.scalars().all()

    # Якщо нотаток немає
    if not notes:
        return "Нотаток поки немає."

    # Перетворюємо нотатки у текст,
    # який потім зможе прочитати AI
    return "\n".join(
        f"- {note.text}"
        for note in notes
    )


async def get_weather_tool(city: str) -> str:
    # Спочатку шукаємо координати міста
    async with httpx.AsyncClient() as client:
        geo_response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "uk",
            },
        )

        geo_response.raise_for_status()
        geo_data = geo_response.json()

        # Якщо місто не знайдено
        if not geo_data.get("results"):
            return f"Не вдалося знайти місто: {city}"

        # Беремо перший знайдений результат
        location = geo_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]
        city_name = location["name"]

        # Тепер за координатами отримуємо поточну погоду
        weather_response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m",
            },
        )

        weather_response.raise_for_status()
        weather_data = weather_response.json()

    # Дістаємо температуру з відповіді API
    temperature = weather_data["current"]["temperature_2m"]

    # Повертаємо результат агенту
    return f"Зараз у місті {city_name}: {temperature} °C"