"""Structured-output schemas for the two-pass P&ID extraction (Gemini vision).

Pass 1 detects equipment with bounding boxes; pass 2 extracts connections
restricted to the detected refs. Boxes are normalized 0..1 (x0,y0 top-left,
x1,y1 bottom-right), which the newer Gemini models produce precisely.
"""

from pydantic import BaseModel, Field

from inf_canvas.schema.canvas import LineType
from inf_canvas.schema.equipment import EquipmentType


class Box(BaseModel):
    x0: float = Field(description="Left edge, normalized 0..1.")
    y0: float = Field(description="Top edge, normalized 0..1.")
    x1: float = Field(description="Right edge, normalized 0..1.")
    y1: float = Field(description="Bottom edge, normalized 0..1.")

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def cy(self) -> float:
        return (self.y0 + self.y1) / 2


class DetectedEquipment(BaseModel):
    ref: str = Field(description="Short unique id for this item, e.g. 'E1'.")
    type: EquipmentType
    label: str | None = Field(default=None, description="Tag text if visible, e.g. 'P-101'.")
    box: Box = Field(description="Tight bounding box around the symbol, normalized 0..1.")


class EquipmentList(BaseModel):
    equipment: list[DetectedEquipment]


class DetectedConnection(BaseModel):
    from_ref: str = Field(description="ref of the upstream equipment.")
    to_ref: str = Field(description="ref of the downstream equipment.")
    line_type: LineType | None = None
    label: str | None = None


class ConnectionList(BaseModel):
    connections: list[DetectedConnection]


class TypeFix(BaseModel):
    ref: str
    type: EquipmentType


class ExtractOptions(BaseModel):
    """Per-request extraction controls the user sets before running.

    These override the server defaults so the user can trade accuracy for speed
    on a case-by-case basis (dense sheet vs. quick sketch).
    """

    hint: str = Field(
        default="",
        description="Free-text guidance, e.g. expected symbol count or areas to focus on.",
    )
    effort: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Self-consistency detection rounds; higher = better recall, slower.",
    )
    use_tiling: bool = Field(
        default=False,
        description="Crop into overlapping tiles and detect per tile (dense 100+ symbol sheets).",
    )
    tile_cols: int = Field(default=2, ge=1, le=4, description="Tile grid columns.")
    tile_rows: int = Field(default=2, ge=1, le=4, description="Tile grid rows.")
    use_legend: bool = Field(
        default=False,
        description="Read the drawing's symbol legend first and use it as a prior.",
    )
    use_verify: bool = Field(default=True, description="Set-of-Mark verifier pass.")
    use_line_hybrid: bool = Field(default=True, description="OpenCV line-connection proposals.")


class VerificationResult(BaseModel):
    """Corrections from the Set-of-Mark verifier pass."""

    missing_equipment: list[DetectedEquipment] = Field(
        default_factory=list, description="Equipment visible in the image but not yet detected."
    )
    remove_equipment_refs: list[str] = Field(
        default_factory=list, description="Refs of detected boxes that are wrong / not equipment."
    )
    retype: list[TypeFix] = Field(
        default_factory=list, description="Refs whose equipment type should be corrected."
    )
    missing_connections: list[DetectedConnection] = Field(
        default_factory=list, description="Connections visible in the image but not yet captured."
    )
    remove_connections: list[DetectedConnection] = Field(
        default_factory=list, description="Captured connections that are not actually drawn."
    )
