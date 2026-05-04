from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from server.api import (
    audit,
    cognitions,
    experiences,
    feedback,
    guidance,
    reviews,
    seed_skills,
    skills,
)
from server.config import get_settings
from server.storage.sqlite import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    initialize_database(settings.database_url)
    yield


app = FastAPI(
    title="Agent Growth Layer",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(guidance.router)
app.include_router(seed_skills.router)
app.include_router(experiences.router)
app.include_router(cognitions.router)
app.include_router(feedback.router)
app.include_router(skills.router)
app.include_router(audit.router)
app.include_router(reviews.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
