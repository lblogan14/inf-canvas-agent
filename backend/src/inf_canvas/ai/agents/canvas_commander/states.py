"""LangGraph state for the Canvas Commander."""

from typing import TypedDict

from inf_canvas.schema.canvas import CanvasState
from inf_canvas.schema.commands import CanvasCommand

from .schemas import CommanderPlan


class CommanderState(TypedDict, total=False):
    # inputs
    instruction: str
    canvas: CanvasState
    # working / outputs
    plan: CommanderPlan
    commands: list[CanvasCommand]
    reply: str
