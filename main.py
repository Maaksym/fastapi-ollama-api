from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from routers.ai import router as ai_router

app = FastAPI()

Instrumentator().instrument(app).expose(app)

app.include_router(ai_router)


@app.get("/health/")
def health_check():
    return {"status": "ok"}