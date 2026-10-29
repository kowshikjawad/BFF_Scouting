"""FastAPI entrypoint.

Covers PRD Module 4 (Scouting Dashboard / RESTful API layer) and
NFR "similarity search under 500ms".
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.routing import Match

from backend.app.config import settings

# Local Vite dev server origins -- the frontend calls this API from a
# different origin during development.
_DEV_FRONTEND_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.models.db import init_db

    init_db()
    yield


def create_app(frontend_dist: Path | None = None) -> FastAPI:
    """Application factory so tests can spin up isolated instances."""
    app = FastAPI(
        title="ShonarTalent AI",
        description="Bangladeshi Football Scouting & Talent Discovery Platform",
        version="0.1.0",
        lifespan=lifespan,
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

    dist = frontend_dist or Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if (dist / "index.html").is_file():
        if (dist / "assets").is_dir():
            app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def frontend(path: str, request: Request):
            if path == "api" or path.startswith("api/"):
                api_scope = {**request.scope, "path": request.scope["path"].removeprefix("/api/v1")}
                for route in [
                    *players.router.routes,
                    *similarity.router.routes,
                    *eligibility.router.routes,
                ]:
                    match, _ = route.matches(api_scope)
                    if match == Match.PARTIAL:
                        raise HTTPException(
                            status_code=405,
                            detail="Method Not Allowed",
                            headers={"Allow": ", ".join(sorted(route.methods))},
                        )
                raise HTTPException(status_code=404, detail="API route not found")
            candidate = (dist / path).resolve()
            if not candidate.is_relative_to(dist.resolve()):
                raise HTTPException(status_code=404)
            if candidate.is_file():
                return FileResponse(candidate)
            # Missing assets must not return the application HTML.
            if path.startswith("licenses/") or "." in Path(path).name:
                raise HTTPException(status_code=404)
            return FileResponse(dist / "index.html", headers={"Cache-Control": "no-cache"})

    return app


app = create_app()
