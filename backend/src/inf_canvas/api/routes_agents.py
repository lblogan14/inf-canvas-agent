"""Agent endpoints. Each streams the LangGraph run as Server-Sent Events so the
UI can show live progress, then applies the resulting commands through the
command bus (which broadcasts them to all canvases).
"""

from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..ai.agents.canvas_commander import NODE_LABELS as COMMANDER_LABELS
from ..ai.agents.canvas_commander import build_commander_graph
from ..ai.agents.orchestrator import NODE_LABELS as OPTIMUS_LABELS
from ..ai.agents.orchestrator import build_optimus_graph
from ..ai.agents.pid_extractor import NODE_LABELS as EXTRACTOR_LABELS
from ..ai.agents.pid_extractor import build_extractor_graph
from ..ai.models import ModelError, get_model_client
from ..ai.models.base import ModelClient
from ..canvas.command_bus import CommandBus
from .deps import get_bus
from .streaming import stream_graph_events

router = APIRouter(prefix="/api/agents", tags=["agents"])

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}


class OptimusRequest(BaseModel):
    canvasId: str
    message: str


class CommanderRequest(BaseModel):
    canvasId: str
    instruction: str


def _model() -> ModelClient:
    try:
        return get_model_client()
    except ModelError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err


@router.post("/optimus")
async def optimus(req: OptimusRequest, bus: CommandBus = Depends(get_bus)) -> StreamingResponse:
    model = _model()
    canvas = await bus.get_state(req.canvasId)
    graph = build_optimus_graph(model)

    async def on_done(state: dict[str, Any]) -> dict[str, Any]:
        # Build step-by-step so the canvas fills in visibly.
        applied = await bus.apply_sequence(req.canvasId, state.get("commands", []), "agent:optimus")
        return {"message": state.get("reply") or "Done.", "commandsApplied": applied}

    return StreamingResponse(
        stream_graph_events(
            graph, {"message": req.message, "canvas": canvas}, OPTIMUS_LABELS, on_done
        ),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


@router.post("/commander")
async def commander(req: CommanderRequest, bus: CommandBus = Depends(get_bus)) -> StreamingResponse:
    model = _model()
    canvas = await bus.get_state(req.canvasId)
    graph = build_commander_graph(model)

    async def on_done(state: dict[str, Any]) -> dict[str, Any]:
        # Build step-by-step so the canvas fills in visibly.
        applied = await bus.apply_sequence(
            req.canvasId, state.get("commands", []), "agent:commander"
        )
        return {"message": state.get("reply") or "Done.", "commandsApplied": applied}

    return StreamingResponse(
        stream_graph_events(
            graph, {"instruction": req.instruction, "canvas": canvas}, COMMANDER_LABELS, on_done
        ),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


@router.post("/pid/extract")
async def pid_extract(
    canvas_id: str = Form(...),
    image: UploadFile = File(...),
    bus: CommandBus = Depends(get_bus),
) -> StreamingResponse:
    model = _model()
    data = await image.read()
    mime = image.content_type or "image/png"
    canvas = await bus.get_state(canvas_id)
    graph = build_extractor_graph(model)

    async def on_done(state: dict[str, Any]) -> dict[str, Any]:
        applied = await bus.apply_many(canvas_id, state.get("commands", []), "agent:pid_extractor")
        return {
            "message": state.get("summary") or "Extraction complete.",
            "commandsApplied": applied,
        }

    return StreamingResponse(
        stream_graph_events(
            graph,
            {"image": data, "mime_type": mime, "canvas": canvas},
            EXTRACTOR_LABELS,
            on_done,
        ),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
