"""Structured-output schemas for the Gemini calls.

These are the JSON shapes the models are constrained to return. They are
deliberately simple (flat refs + normalized coordinates) so extraction is
reliable; the agents convert them into validated CanvasCommands.
"""

from typing import Literal

from pydantic import BaseModel, Field

from ...schema.canvas import LineType
from ...schema.equipment import EquipmentType

# --- P&ID Extractor ---------------------------------------------------------


class DetectedEquipment(BaseModel):
    ref: str = Field(description="Short unique id for this item, e.g. 'E1'.")
    type: EquipmentType
    label: str | None = Field(default=None, description="Tag text if visible, e.g. 'P-101'.")
    x: float = Field(description="Center X, normalized 0..1 (left to right).")
    y: float = Field(description="Center Y, normalized 0..1 (top to bottom).")


class DetectedConnection(BaseModel):
    from_ref: str = Field(description="ref of the upstream equipment.")
    to_ref: str = Field(description="ref of the downstream equipment.")
    line_type: LineType | None = None
    label: str | None = None


class PIDExtraction(BaseModel):
    equipment: list[DetectedEquipment]
    connections: list[DetectedConnection]


# --- Canvas Commander -------------------------------------------------------


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


# --- Optimus router ---------------------------------------------------------


class RouteDecision(BaseModel):
    route: Literal["commander", "answer"]
    rationale: str | None = None
