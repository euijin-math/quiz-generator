#To Run: uv run uvicorn app.main:app --reload

from fastapi import FastAPI

from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)


@app.get("/health")
def get_health():
    return {"status": "ok", "app": settings.app_name, "env": settings.environment}


