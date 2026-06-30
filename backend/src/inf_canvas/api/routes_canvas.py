"""Canvas persistence endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from ..canvas.command_bus import CommandBus
from ..canvas.store import CanvasRepository
from ..schema.canvas import CanvasMeta, CanvasState
from .deps import get_bus, get_repo

router = APIRouter(prefix="/api", tags=["canvas"])


@router.get("/projects")
def list_projects(repo: CanvasRepository = Depends(get_repo)) -> list[CanvasMeta]:
    return repo.list_projects()


@router.get("/projects/{canvas_id}")
async def get_project(canvas_id: str, bus: CommandBus = Depends(get_bus)) -> CanvasState:
    return await bus.get_state(canvas_id)


@router.put("/projects/{canvas_id}")
async def save_project(
    canvas_id: str,
    state: CanvasState,
    bus: CommandBus = Depends(get_bus),
) -> CanvasState:
    if state.meta.id != canvas_id:
        raise HTTPException(status_code=400, detail="canvas id mismatch")
    return await bus.set_state(state)
