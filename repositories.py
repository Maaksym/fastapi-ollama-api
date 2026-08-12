from sqlalchemy.ext.asyncio import AsyncSession

from models import AIRequest

from sqlalchemy import select


async def save_ai_request(
    db: AsyncSession,
    prompt: str,
    answer: str,
) -> AIRequest:
    ai_request = AIRequest(
        prompt=prompt,
        answer=answer,
    )

    db.add(ai_request)
    await db.commit()
    await db.refresh(ai_request)

    return ai_request


async def get_ai_requests(
    db: AsyncSession,
    limit: int = 10,
):
    result = await db.execute(
        select(AIRequest)
        .order_by(AIRequest.id.desc())
        .limit(limit)
    )

    return result.scalars().all()