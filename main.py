from fastapi import FastAPI

from routers.ai import router as ai_router


app = FastAPI()


app.include_router(ai_router)


@app.get("/health/")
def health_check():
    return {"status": "ok"}