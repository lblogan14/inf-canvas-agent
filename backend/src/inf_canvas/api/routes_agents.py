"""Agent endpoints. Each runs an agent (in a threadpool, since the Gemini SDK is
sync) and applies the resulting commands through the command bus, which
broadcasts them live to all connected canvases.
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from ..ai.agents import run_commander, run_extractor, run_optimus
from ..ai.models.gemini import GeminiClient, GeminiError, get_gemini_client
from ..canvas.command_bus import CommandBus
from .deps import get_bus

router = APIRouter(prefix="/api/agents", tags=["agents"])


class OptimusRequest(BaseModel):
    canvasId: str
    message: str


class CommanderRequest(BaseModel):
    canvasId: str
    instruction: str


class AgentResponse(BaseModel):
    message: str
    commandsApplied: int


def _gemini() -> GeminiClient:
    try:
        return get_gemini_client()
    except GeminiError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err


@router.post("/optimus")
async def optimus(req: OptimusRequest, bus: CommandBus = Depends(get_bus)) -> AgentResponse:
    gemini = _gemini()
    canvas = await bus.get_state(req.canvasId)
    commands, reply = await run_in_threadpool(run_optimus, gemini, req.message, canvas)
    applied = await bus.apply_many(req.canvasId, commands, "agent:optimus")
    return AgentResponse(message=reply or "Done.", commandsApplied=applied)


@router.post("/commander")
async def commander(req: CommanderRequest, bus: CommandBus = Depends(get_bus)) -> AgentResponse:
    gemini = _gemini()
    canvas = await bus.get_state(req.canvasId)
    commands, reply = await run_in_threadpool(run_commander, gemini, req.instruction, canvas)
    applied = await bus.apply_many(req.canvasId, commands, "agent:commander")
    return AgentResponse(message=reply or "Done.", commandsApplied=applied)


@router.post("/pid/extract")
async def pid_extract(
    canvas_id: str = Form(...),
    image: UploadFile = File(...),
    bus: CommandBus = Depends(get_bus),
) -> AgentResponse:
    gemini = _gemini()
    data = await image.read()
    mime = image.content_type or "image/png"
    canvas = await bus.get_state(canvas_id)
    commands, summary = await run_in_threadpool(run_extractor, gemini, data, mime, canvas)
    applied = await bus.apply_many(canvas_id, commands, "agent:pid_extractor")
    return AgentResponse(message=summary or "Extraction complete.", commandsApplied=applied)
