"""Equipment taxonomy + port metadata (Python mirror of equipment.ts).

The agents rely on `EQUIPMENT_METADATA` to know valid equipment types, their
canvas footprint, and which ports exist (used for connection routing). Keep in
lockstep with frontend/src/schema/equipment.ts.
"""

from typing import Literal

from pydantic import BaseModel

EquipmentType = Literal[
    "centrifugal_pump",
    "positive_displacement_pump",
    "compressor",
    "blower",
    "fan",
    "motor",
    "turbine",
    "gate_valve",
    "globe_valve",
    "ball_valve",
    "butterfly_valve",
    "check_valve",
    "control_valve",
    "three_way_valve",
    "relief_valve",
    "vessel",
    "column",
    "reactor",
    "mixer",
    "storage_tank",
    "shell_tube_heat_exchanger",
    "air_cooler",
    "cooling_tower",
    "filter",
    "instrument",
]

EQUIPMENT_TYPES: tuple[EquipmentType, ...] = (
    "centrifugal_pump",
    "positive_displacement_pump",
    "compressor",
    "blower",
    "fan",
    "motor",
    "turbine",
    "gate_valve",
    "globe_valve",
    "ball_valve",
    "butterfly_valve",
    "check_valve",
    "control_valve",
    "three_way_valve",
    "relief_valve",
    "vessel",
    "column",
    "reactor",
    "mixer",
    "storage_tank",
    "shell_tube_heat_exchanger",
    "air_cooler",
    "cooling_tower",
    "filter",
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
        "pump_centrifugal",
        80,
        80,
        [("suction", "inlet", "left"), ("discharge", "outlet", "top")],
    ),
    "positive_displacement_pump": _meta(
        "positive_displacement_pump",
        "Positive Displacement Pump",
        "pump_pd",
        80,
        80,
        [("suction", "inlet", "left"), ("discharge", "outlet", "right")],
    ),
    "compressor": _meta(
        "compressor",
        "Compressor",
        "compressor",
        92,
        80,
        [("suction", "inlet", "left"), ("discharge", "outlet", "right")],
    ),
    "blower": _meta("blower", "Blower", "blower", 82, 80, _IN_OUT),
    "fan": _meta("fan", "Fan", "blower", 80, 80, _IN_OUT),
    "motor": _meta("motor", "Motor", "motor", 70, 70, [("shaft", "inout", "right")]),
    "turbine": _meta("turbine", "Turbine / Expander", "turbine", 92, 72, _IN_OUT),
    "gate_valve": _meta("gate_valve", "Gate Valve", "valve_gate", 64, 40, _IN_OUT),
    "globe_valve": _meta("globe_valve", "Globe Valve", "valve_globe", 64, 40, _IN_OUT),
    "ball_valve": _meta("ball_valve", "Ball Valve", "valve_ball", 64, 40, _IN_OUT),
    "butterfly_valve": _meta(
        "butterfly_valve", "Butterfly Valve", "valve_butterfly", 64, 40, _IN_OUT
    ),
    "check_valve": _meta("check_valve", "Check Valve", "valve_check", 64, 40, _IN_OUT),
    "control_valve": _meta("control_valve", "Control Valve", "valve_control", 64, 58, _IN_OUT),
    "three_way_valve": _meta(
        "three_way_valve",
        "Three-Way Valve",
        "valve_threeway",
        56,
        56,
        [("in", "inlet", "left"), ("out", "outlet", "right"), ("branch", "outlet", "bottom")],
    ),
    "relief_valve": _meta(
        "relief_valve",
        "Relief Valve",
        "valve_relief",
        54,
        66,
        [("in", "inlet", "bottom"), ("out", "outlet", "left")],
    ),
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
        "column",
        92,
        200,
        [
            ("overhead", "outlet", "top"),
            ("bottoms", "outlet", "bottom"),
            ("feed", "inlet", "left"),
        ],
    ),
    "reactor": _meta(
        "reactor",
        "Reactor",
        "reactor",
        110,
        150,
        [
            ("feed", "inlet", "top"),
            ("product", "outlet", "bottom"),
            ("jacket_in", "inlet", "left"),
            ("jacket_out", "outlet", "right"),
        ],
    ),
    "mixer": _meta(
        "mixer",
        "Mixer / Agitated Tank",
        "mixer",
        112,
        120,
        [("in", "inlet", "left"), ("out", "outlet", "bottom")],
    ),
    "storage_tank": _meta(
        "storage_tank",
        "Storage Tank",
        "tank",
        140,
        116,
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
    "air_cooler": _meta("air_cooler", "Air Cooler", "air_cooler", 120, 84, _IN_OUT),
    "cooling_tower": _meta(
        "cooling_tower",
        "Cooling Tower",
        "cooling_tower",
        120,
        110,
        [("in", "inlet", "top"), ("out", "outlet", "bottom")],
    ),
    "filter": _meta(
        "filter",
        "Filter",
        "filter",
        72,
        96,
        [("in", "inlet", "top"), ("out", "outlet", "bottom")],
    ),
    "instrument": _meta(
        "instrument", "Instrument", "instrument", 56, 56, [("signal", "inout", "bottom")]
    ),
}
