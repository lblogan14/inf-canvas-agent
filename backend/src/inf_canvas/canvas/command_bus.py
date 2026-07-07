"""The command bus: the single place canvas mutations flow through.

Holds the authoritative in-memory state per canvas, applies validated commands
via the reducer, persists through the repository, and broadcasts to all
connected WebSocket clients. Both human edits (via WS) and AI agents (via REST)
go through `apply`.
"""

import asyncio
from datetime import UTC, datetime

from starlette.websockets import WebSocket

from ..schema.canvas import CanvasState, empty_canvas
from ..schema.commands import CanvasCommand, CommandMessage, CommandSource, SnapshotMessage
from .reducer import apply_command
from .store import CanvasRepository


class CommandBus:
    def __init__(self, repo: CanvasRepository) -> None:
        self._repo = repo
        self._states: dict[str, CanvasState] = {}
        self._conns: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def get_state(self, canvas_id: str) -> CanvasState:
        if canvas_id not in self._states:
            self._states[canvas_id] = self._repo.load(canvas_id) or empty_canvas(
                canvas_id, "Untitled"
            )
        return self._states[canvas_id]

    async def set_state(self, state: CanvasState, *, persist: bool = True) -> CanvasState:
        async with self._lock:
            self._states[state.meta.id] = state
            if persist:
                self._repo.save(state)
        return state

    async def delete(self, canvas_id: str) -> bool:
        """Forget a canvas from memory and delete its persisted file."""
        async with self._lock:
            self._states.pop(canvas_id, None)
            return self._repo.delete(canvas_id)

    async def apply(
        self,
        canvas_id: str,
        command: CanvasCommand,
        source: CommandSource,
        *,
        origin: WebSocket | None = None,
    ) -> CanvasState:
        async with self._lock:
            state = await self.get_state(canvas_id)
            new_state = apply_command(state, command)
            if command.op != "select":
                new_state.meta.updatedAt = datetime.now(UTC).isoformat()
                self._states[canvas_id] = new_state
                self._repo.save(new_state)

        await self.broadcast(
            canvas_id,
            CommandMessage(source=source, command=command),
            exclude=origin,
        )
        return new_state

    async def apply_many(
        self,
        canvas_id: str,
        commands: list[CanvasCommand],
        source: CommandSource,
    ) -> int:
        """Apply a list of commands as one batch broadcast. Returns count."""
        if not commands:
            return 0
        from ..schema.commands import BatchCommand

        batch = BatchCommand(op="batch", commands=commands)
        await self.apply(canvas_id, batch, source)
        return len(commands)

    async def apply_sequence(
        self,
        canvas_id: str,
        commands: list[CanvasCommand],
        source: CommandSource,
        delay: float = 0.07,
    ) -> int:
        """Apply commands one at a time (each broadcast) so the canvas builds
        up step-by-step in the UI instead of appearing all at once."""
        for command in commands:
            await self.apply(canvas_id, command, source)
            if delay:
                await asyncio.sleep(delay)
        return len(commands)

    # --- connection management ---------------------------------------------

    async def connect(self, canvas_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._conns.setdefault(canvas_id, set()).add(websocket)
        state = await self.get_state(canvas_id)
        await websocket.send_text(SnapshotMessage(state=state).model_dump_json())

    def disconnect(self, canvas_id: str, websocket: WebSocket) -> None:
        conns = self._conns.get(canvas_id)
        if conns:
            conns.discard(websocket)

    async def broadcast(
        self,
        canvas_id: str,
        message: CommandMessage,
        *,
        exclude: WebSocket | None = None,
    ) -> None:
        payload = message.model_dump_json()
        for ws in list(self._conns.get(canvas_id, set())):
            if ws is exclude:
                continue
            try:
                await ws.send_text(payload)
            except Exception:
                self.disconnect(canvas_id, ws)
