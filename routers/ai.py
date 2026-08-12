import asyncio
import logging

from services import generate_ai_answer

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

from repositories import get_ai_requests, save_ai_request
from schemas import AIRequestResponse, GenerateResponse, PromptRequest


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)

logger = logging.getLogger(__name__)


@router.post("/generate/", response_model=GenerateResponse)
async def generate_text(
    request: PromptRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        answer = await asyncio.wait_for(
            generate_ai_answer(request.prompt),
            timeout=120,
        )

        await save_ai_request(
            db=db,
            prompt=request.prompt,
            answer=answer,
        )

        return {
            "prompt": request.prompt,
            "answer": answer,
        }

    except asyncio.TimeoutError:
        logger.warning("AI request timed out")
        raise HTTPException(
            status_code=504,
            detail="AI service timeout",
        )

    except Exception:
        logger.exception("AI service request failed")
        raise HTTPException(
            status_code=502,
            detail="AI service unavailable",
        )


@router.get(
    "/history/",
    response_model=list[AIRequestResponse],
)
async def get_history(
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await get_ai_requests(
        db=db,
        limit=limit,
    )