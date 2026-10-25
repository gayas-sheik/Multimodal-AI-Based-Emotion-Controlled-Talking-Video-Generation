
"""Development FastAPI entry point for direct FLOAT inference."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.conversation import router as conversation_router
from .routes.generate import router as generate_router


# Load environment variables from the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def create_app() -> FastAPI:
    app = FastAPI(
        title="FLOAT Direct Inference API",
        version="0.1.0",
    )

    # Allow only explicitly configured origins.
    origins = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "https://sentioguard-ai-web.pages.dev",
        ).split(",")
        if origin.strip()
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-API-Key"],
    )

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "float-direct-inference",
        }

    app.include_router(generate_router)
    app.include_router(conversation_router)

    return app


app = create_app()
