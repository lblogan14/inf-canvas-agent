"""Canvas data model (Pydantic mirror of canvas.ts)."""

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel

from .equipment import EquipmentType

LineType = Literal["process", "signal", "electrical", "pneumatic"]


class Position(BaseModel):
    x: float
    y: float


class CanvasNode(BaseModel):
    id: str
    type: EquipmentType
    position: Position
    label: str | None = None
    rotation: float | None = None
    data: dict[str, Any] | None = None


class PipeData(BaseModel):
    lineType: LineType | None = None
    label: str | None = None
    animated: bool | None = None


class CanvasEdge(BaseModel):
    id: str
    source: str
    sourcePort: str
    target: str
    targetPort: str
    data: PipeData | None = None


class CanvasMeta(BaseModel):
    id: str
    name: str
    createdAt: str | None = None
    updatedAt: str | None = None


class CanvasState(BaseModel):
    meta: CanvasMeta
    nodes: list[CanvasNode] = []
    edges: list[CanvasEdge] = []


def empty_canvas(canvas_id: str, name: str) -> CanvasState:
    now = datetime.now(UTC).isoformat()
    return CanvasState(meta=CanvasMeta(id=canvas_id, name=name, createdAt=now, updatedAt=now))
