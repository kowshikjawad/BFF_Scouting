"""FastAPI entrypoint.

Covers PRD Module 4 (Scouting Dashboard / RESTful API layer) and
NFR "similarity search under 500ms".
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings

# Local Vite dev server origins -- the frontend calls this API from a
# different origin during development.
_DEV_FRONTEND_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


def create_app() -> FastAPI:
    """Application factory so tests can spin up isolated instances."""
    app = FastAPI(
        title="ShonarTalent AI",
        description="Bangladeshi Football Scouting & Talent Discovery Platform",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_DEV_FRONTEND_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "env": settings.app_env}

    # Routes for FR-2 (eligibility), FR-3 (similarity), FR-4 (dashboard).
    # Imported lazily here to keep the entrypoint decoupled from heavy deps.
    from backend.api import eligibility, players, similarity

    app.include_router(players.router, prefix="/api/v1", tags=["players"])
    app.include_router(similarity.router, prefix="/api/v1", tags=["similarity"])
    app.include_router(eligibility.router, prefix="/api/v1", tags=["eligibility"])

    return app


app = create_app()