import pytest

from agent_service import choose_tool


@pytest.mark.asyncio
async def test_choose_tool_save_note():
    # Перевіряємо, що команда "запам'ятай"
    # правильно вибирає SAVE_NOTE.
    result = await choose_tool(
        "Запам'ятай: клієнта звати Андрій"
    )

    assert result == "SAVE_NOTE"


@pytest.mark.asyncio
async def test_choose_tool_history():
    # Перевіряємо, що запит про історію
    # правильно вибирає HISTORY.
    result = await choose_tool(
        "Що я питав раніше?"
    )

    assert result == "HISTORY"


@pytest.mark.asyncio
async def test_choose_tool_get_notes():
    # Спочатку описуємо очікувану поведінку.
    result = await choose_tool(
        "Покажи мої нотатки"
    )

    assert result == "GET_NOTES"