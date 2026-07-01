"""LangGraph state for the P&ID Extractor."""

from typing import TypedDict

from inf_canvas.schema.canvas import CanvasState
from inf_canvas.schema.commands import CanvasCommand

from .schemas import DetectedConnection, DetectedEquipment


class ExtractorState(TypedDict, total=False):
    # inputs
    image: bytes
    mime_type: str
    canvas: CanvasState
    # working
    description: str
    equipment: list[DetectedEquipment]
    connections: list[DetectedConnection]
    # outputs
    commands: list[CanvasCommand]
    summary: str
