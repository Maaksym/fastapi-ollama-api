from pydantic import BaseModel, Field
from datetime import datetime


class PromptRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=1000,
    )


class GenerateResponse(BaseModel):
    prompt: str
    answer: str


class AIRequestResponse(BaseModel):
    id: int
    prompt: str
    answer: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }