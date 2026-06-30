"""WebSocket command channel.

On connect the client receives a snapshot; thereafter it sends CommandMessages
which are validated, applied, and broadcast to the other clients.
"""

import json

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from ..canvas.command_bus import CommandBus
from ..schema.commands import CommandSource, command_adapter

router = APIRouter()

_VALID_SOURCES = {"user", "agent:optimus", "agent:pid_extractor", "agent:commander", "system"}


@router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket, canvas: str = Query(...)) -> None:
    bus: CommandBus = websocket.app.state.bus
    await bus.connect(canvas, websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            if data.get("type") != "command":
                continue
            command = command_adapter.validate_python(data["command"])
            source_raw = data.get("source", "user")
            source: CommandSource = source_raw if source_raw in _VALID_SOURCES else "user"
            await bus.apply(canvas, command, source, origin=websocket)
    except WebSocketDisconnect:
        bus.disconnect(canvas, websocket)
    except Exception:
        bus.disconnect(canvas, websocket)
