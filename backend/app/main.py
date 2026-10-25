"""Development FastAPI entry point for direct FLOAT inference."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.conversation import router as conversation_router
from .routes.generate import router as generate_router


def create_app() -> FastAPI:
    app = FastAPI(title="FLOAT Direct Inference API", version="0.1.0")
    origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "float-direct-inference"}

    app.include_router(generate_router)
    app.include_router(conversation_router)
    return app


app = create_app()
