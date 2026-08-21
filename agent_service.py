from sqlalchemy.ext.asyncio import AsyncSession

from services import generate_ai_answer

from agent_tools import (
    get_history_tool,
    save_note_tool,
    get_notes_tool,
    get_weather_tool,
)

async def choose_tool(message: str) -> str:
    # Приводимо повідомлення до нижнього регістру,
    # щоб простіше було шукати ключові слова
    text = message.lower()

    # Якщо користувач явно просить щось зберегти,
    # не питаємо LLM — одразу вибираємо SAVE_NOTE
    if any(
        phrase in text
        for phrase in (
            "запам'ятай",
            "збережи",
            "запиши",
            "створи нотатку",
        )
    ):
        return "SAVE_NOTE"

    # Якщо користувач явно питає про історію запитів,
    # одразу вибираємо HISTORY
    if any(
        phrase in text
        for phrase in (
            "що я питав",
            "історія запитів",
            "покажи історію",
            "мої попередні запити",
        )
    ):
        return "HISTORY"

    # Якщо користувач питає про погоду,
    # одразу вибираємо weather tool
    if any(
            word in text
            for word in (
                    "погода",
                    "температура",
                    "градусів",
            )
    ):
        return "GET_WEATHER"

    # Якщо користувач прямо просить показати збережені нотатки,
    # одразу вибираємо GET_NOTES.
    # Фрази, які явно означають читання нотаток
    notes_phrases = (
        "покажи мої нотатки",
        "покажи нотатки",
        "мої нотатки",
    )

    if any(
            phrase in text
            for phrase in notes_phrases
    ):
        return "GET_NOTES"

    # Для менш очевидних випадків
    # уже просимо LLM вибрати tool
    prompt = f"""
    Ти AI-агент-класифікатор.

    Вибери РІВНО ОДИН варіант:

    GET_NOTES
    - якщо відповідь може бути у збережених нотатках.

    NONE
    - якщо це звичайне питання,
      яке не потребує читання нотаток.

    Приклади:

    "Як звати клієнта?" -> GET_NOTES
    "Коли треба подзвонити клієнту?" -> GET_NOTES
    "Поясни що таке FastAPI" -> NONE
    "Що таке PostgreSQL?" -> NONE

    Повідомлення користувача:
    {message}

    Відповідай ТІЛЬКИ:
    GET_NOTES
    або
    NONE
    """

    decision = await generate_ai_answer(prompt)

    tool = decision.strip().upper()

    # Захист від дивної відповіді LLM
    if tool not in {"GET_NOTES", "NONE"}:
        return "NONE"

    return tool


async def run_agent(
    message: str,
    db: AsyncSession,
) -> str:
    # AI сам вирішує, який tool потрібен
    tool = await choose_tool(message)
    print("SELECTED TOOL:", tool)
    if tool not in {
        "HISTORY",
        "SAVE_NOTE",
        "GET_NOTES",
        "GET_WEATHER",
        "NONE",
    }:
        tool = "NONE"

    # Якщо AI вибрав HISTORY,
    # викликаємо tool для читання історії
    if tool == "HISTORY":
        return await get_history_tool(
            db=db,
            limit=5,
        )

    # Якщо AI вибрав SAVE_NOTE,
    # очищаємо текст і зберігаємо нотатку
    if tool == "SAVE_NOTE":
        # SAVE_NOTE дозволяємо тільки тоді,
        # коли користувач явно просить щось зберегти
        save_words = (
            "запам'ятай",
            "збережи",
            "запиши",
            "нотатка",
        )

        # Якщо AI помилково вибрав SAVE_NOTE,
        # але користувач не просив нічого зберігати,
        # не виконуємо запис у БД
        if not any(word in message.lower() for word in save_words):
            tool = "NONE"

        else:
            note_text = message

            note_text = note_text.replace("Запам'ятай:", "")
            note_text = note_text.replace("запам'ятай:", "")
            note_text = note_text.replace("Запам'ятай", "")
            note_text = note_text.replace("запам'ятай", "")
            note_text = note_text.strip()

            return await save_note_tool(
                db=db,
                text=note_text,
            )

    if tool == "GET_NOTES":
        # Читаємо збережені нотатки
        notes = await get_notes_tool(
            db=db,
            limit=5,
        )
        print("NOTES FROM DB:")
        print(notes)

        # Передаємо нотатки назад AI,
        # щоб він сформував нормальну відповідь користувачу
        prompt = f"""
        Користувач запитав:
        {message}

        Ось збережені нотатки:
        {notes}

        Відповідай користувачу тільки на основі цих нотаток.
        """

        return await generate_ai_answer(prompt)

    if tool == "GET_WEATHER":
        # Просимо AI витягнути назву міста
        # саме у називному відмінку
        city_prompt = f"""
        Витягни назву міста з повідомлення користувача.

        Поверни місто у НАЗИВНОМУ відмінку.

        Приклади:
        "Яка погода у Варшаві?" -> Варшава
        "Яка температура в Берліні?" -> Берлін
        "Скільки градусів у Києві?" -> Київ

        Повідомлення:
        {message}

        Відповідай ТІЛЬКИ назвою міста.
        """

        city = await generate_ai_answer(city_prompt)
        city = city.strip()

        return await get_weather_tool(city=city)

    # Якщо жоден tool не потрібен,
    # просимо AI просто відповісти користувачу
    return await generate_ai_answer(message)