"""LangGraph state for the Optimus orchestrator."""

from typing import TypedDict

from inf_canvas.schema.canvas import CanvasState
from inf_canvas.schema.commands import CanvasCommand


class OptimusState(TypedDict, total=False):
    # inputs
    message: str
    canvas: CanvasState
    # working / outputs
    route: str
    reply: str
    commands: list[CanvasCommand]
