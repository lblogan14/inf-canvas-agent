"""Equipment taxonomy + port metadata (Python mirror of the TS equipment.ts).

The agents rely on `EQUIPMENT_METADATA` to know valid equipment types, their
canvas footprint, and which ports exist (used for connection routing).
"""

from typing import Literal

from pydantic import BaseModel

EquipmentType = Literal[
    "centrifugal_pump",
    "positive_displacement_pump",
    "gate_valve",
    "globe_valve",
    "control_valve",
    "check_valve",
    "ball_valve",
    "vessel",
    "column",
    "storage_tank",
    "shell_tube_heat_exchanger",
    "compressor",
    "instrument",
]

EQUIPMENT_TYPES: tuple[EquipmentType, ...] = (
    "centrifugal_pump",
    "positive_displacement_pump",
    "gate_valve",
    "globe_valve",
    "control_valve",
    "check_valve",
    "ball_valve",
    "vessel",
    "column",
    "storage_tank",
    "shell_tube_heat_exchanger",
    "compressor",
    "instrument",
)

PortRole = Literal["inlet", "outlet", "inout"]
PortSide = Literal["top", "right", "bottom", "left"]


class PortDef(BaseModel):
    id: str
    role: PortRole
    side: PortSide
    label: str | None = None


class Size(BaseModel):
    width: float
    height: float


class EquipmentMeta(BaseModel):
    type: EquipmentType
    label: str
    symbol: str
    size: Size
    ports: list[PortDef]


def _meta(
    type_: EquipmentType,
    label: str,
    symbol: str,
    width: float,
    height: float,
    ports: list[tuple[str, PortRole, PortSide]],
) -> EquipmentMeta:
    return EquipmentMeta(
        type=type_,
        label=label,
        symbol=symbol,
        size=Size(width=width, height=height),
        ports=[PortDef(id=p[0], role=p[1], side=p[2]) for p in ports],
    )


_IN_OUT: list[tuple[str, PortRole, PortSide]] = [
    ("in", "inlet", "left"),
    ("out", "outlet", "right"),
]

EQUIPMENT_METADATA: dict[EquipmentType, EquipmentMeta] = {
    "centrifugal_pump": _meta(
        "centrifugal_pump",
        "Centrifugal Pump",
        "pump",
        80,
        80,
        [("suction", "inlet", "left"), ("discharge", "outlet", "top")],
    ),
    "positive_displacement_pump": _meta(
        "positive_displacement_pump",
        "Positive Displacement Pump",
        "pump",
        80,
        80,
        [("suction", "inlet", "left"), ("discharge", "outlet", "right")],
    ),
    "gate_valve": _meta("gate_valve", "Gate Valve", "valve", 60, 40, _IN_OUT),
    "globe_valve": _meta("globe_valve", "Globe Valve", "valve", 60, 40, _IN_OUT),
    "control_valve": _meta("control_valve", "Control Valve", "valve", 60, 56, _IN_OUT),
    "check_valve": _meta("check_valve", "Check Valve", "valve", 60, 40, _IN_OUT),
    "ball_valve": _meta("ball_valve", "Ball Valve", "valve", 60, 40, _IN_OUT),
    "vessel": _meta(
        "vessel",
        "Vessel / Drum",
        "vessel",
        100,
        140,
        [
            ("top", "inout", "top"),
            ("bottom", "outlet", "bottom"),
            ("side_in", "inlet", "left"),
            ("side_out", "outlet", "right"),
        ],
    ),
    "column": _meta(
        "column",
        "Column / Tower",
        "vessel",
        90,
        200,
        [
            ("overhead", "outlet", "top"),
            ("bottoms", "outlet", "bottom"),
            ("feed", "inlet", "left"),
        ],
    ),
    "storage_tank": _meta(
        "storage_tank",
        "Storage Tank",
        "tank",
        140,
        120,
        [("fill", "inlet", "top"), ("draw", "outlet", "bottom")],
    ),
    "shell_tube_heat_exchanger": _meta(
        "shell_tube_heat_exchanger",
        "Shell & Tube Heat Exchanger",
        "heat_exchanger",
        120,
        80,
        [
            ("shell_in", "inlet", "left"),
            ("shell_out", "outlet", "right"),
            ("tube_in", "inlet", "top"),
            ("tube_out", "outlet", "bottom"),
        ],
    ),
    "compressor": _meta(
        "compressor",
        "Compressor",
        "compressor",
        90,
        80,
        [("suction", "inlet", "left"), ("discharge", "outlet", "right")],
    ),
    "instrument": _meta(
        "instrument",
        "Instrument",
        "instrument",
        56,
        56,
        [("signal", "inout", "bottom")],
    ),
}
