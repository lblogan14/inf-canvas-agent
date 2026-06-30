"""Structured-output schema for Canvas Commander plans."""

from pydantic import BaseModel, Field

from inf_canvas.schema.canvas import LineType
from inf_canvas.schema.equipment import EquipmentType


class PlannedNode(BaseModel):
    ref: str = Field(description="Short unique id used to reference this new node in connections.")
    type: EquipmentType
    label: str | None = None
    x: float = Field(description="Absolute canvas X (working area is ~1600 wide).")
    y: float = Field(description="Absolute canvas Y (working area is ~1000 tall).")


class PlannedConnection(BaseModel):
    from_ref: str = Field(description="A new node's ref, or an existing node id.")
    to_ref: str = Field(description="A new node's ref, or an existing node id.")
    line_type: LineType | None = None
    label: str | None = None


class CommanderPlan(BaseModel):
    reply: str = Field(description="Short natural-language summary of what you did.")
    add_nodes: list[PlannedNode] = []
    connect: list[PlannedConnection] = []
    remove_node_ids: list[str] = []
