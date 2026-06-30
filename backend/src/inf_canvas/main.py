"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import routes_agents, routes_canvas, ws
from .canvas.command_bus import CommandBus
from .canvas.store import JsonFileRepository
from .config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    repo = JsonFileRepository(settings.projects_path)
    bus = CommandBus(repo)

    app = FastAPI(title="Inf-Canvas Agent API", version="0.1.0")
    app.state.settings = settings
    app.state.repo = repo
    app.state.bus = bus

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routes_canvas.router)
    app.include_router(routes_agents.router)
    app.include_router(ws.router)

    @app.get("/api/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "aiEnabled": settings.has_api_key}

    return app


app = create_app()
