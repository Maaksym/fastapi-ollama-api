from sqlalchemy.ext.asyncio import AsyncSession

from agent_service import run_agent
from database import get_db
from schemas import AgentRequest, AgentResponse

from fastapi import APIRouter, BackgroundTasks, Depends
from services import generate_ai_answer

router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


@router.post(
    "/query/",
    response_model=AgentResponse,
)

# Отримує запит користувача,
# передає message та database session у run_agent(),
# отримує відповідь агента
# і повертає її користувачу у форматі AgentResponse.
async def agent_query(
    request: AgentRequest,
    db: AsyncSession = Depends(get_db),
):
    # Передаємо повідомлення користувача агенту
    # і даємо йому доступ до database session
    answer = await run_agent(
        message=request.message,
        db=db,
    )

    # Повертаємо оригінальне повідомлення
    # і результат роботи агента
    return {
        "message": request.message,
        "answer": answer,
    }

@router.post("/background/")
async def background_agent(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
):
    # Додаємо AI-задачу у фонове виконання
    background_tasks.add_task(
        process_background_message,
        request.message,
    )

    # Відповідь повертається одразу,
    # не чекаючи завершення AI
    return {
        "status": "accepted",
        "message": request.message,
    }


async def process_background_message(message: str):
    # Ця функція виконається вже після того,
    # як API поверне відповідь користувачу.

    answer = await generate_ai_answer(message)

    # Поки просто виводимо результат у консоль.
    # Пізніше його можна зберігати у БД.
    print("BACKGROUND RESULT:")
    print(answer)