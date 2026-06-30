"""Structured-output schema for P&ID extraction (Gemini vision)."""

from pydantic import BaseModel, Field

from inf_canvas.schema.canvas import LineType
from inf_canvas.schema.equipment import EquipmentType


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
