"""LangGraph state for the P&ID Extractor."""

from typing import TypedDict

from inf_canvas.schema.canvas import CanvasState
from inf_canvas.schema.commands import CanvasCommand

from .schemas import DetectedConnection, DetectedEquipment, ExtractOptions


class ExtractorState(TypedDict, total=False):
    # inputs
    image: bytes
    mime_type: str
    canvas: CanvasState
    opts: ExtractOptions
    # working
    description: str
    legend: str
    equipment: list[DetectedEquipment]
    connections: list[DetectedConnection]
    # outputs
    commands: list[CanvasCommand]
    summary: str
