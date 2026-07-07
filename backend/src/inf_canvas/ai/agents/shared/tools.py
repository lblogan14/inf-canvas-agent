"""Canvas toolbox shared by the agents.

Turns a placement plan (nodes with positions + links) into validated
CanvasCommands, choosing sensible ports for each connection based on the
relative geometry of the two nodes.
"""

import math
import uuid
from dataclasses import dataclass

from inf_canvas.schema.canvas import CanvasState, LineType, PipeData, Position
from inf_canvas.schema.commands import (
    AddNodeCommand,
    CanvasCommand,
    ConnectCommand,
    RemoveNodeCommand,
)
from inf_canvas.schema.equipment import EQUIPMENT_METADATA, EquipmentType, PortDef, PortSide


@dataclass
class PlacedNode:
    ref: str
    type: EquipmentType
    label: str | None
    x: float
    y: float


@dataclass
class Link:
    from_ref: str
    to_ref: str
    line_type: LineType | None = None
    label: str | None = None


_SIDE_VEC: dict[PortSide, tuple[float, float]] = {
    "top": (0.0, -1.0),
    "bottom": (0.0, 1.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
}


def _new_node_id() -> str:
    return f"n_{uuid.uuid4().hex[:8]}"


def _new_edge_id() -> str:
    return f"e_{uuid.uuid4().hex[:8]}"


def _best_port(ports: list[PortDef], dx: float, dy: float, prefer: tuple[str, ...]) -> str:
    """Pick the port whose side best faces direction (dx, dy)."""
    mag = math.hypot(dx, dy) or 1.0
    ux, uy = dx / mag, dy / mag

    def score(p: PortDef) -> float:
        sx, sy = _SIDE_VEC[p.side]
        s = sx * ux + sy * uy
        if p.role in prefer:
            s += 0.5
        return s

    return max(ports, key=score).id


def choose_ports(
    src_type: EquipmentType,
    src_pos: Position,
    dst_type: EquipmentType,
    dst_pos: Position,
) -> tuple[str, str]:
    dx = dst_pos.x - src_pos.x
    dy = dst_pos.y - src_pos.y
    src_port = _best_port(EQUIPMENT_METADATA[src_type].ports, dx, dy, ("outlet", "inout"))
    dst_port = _best_port(EQUIPMENT_METADATA[dst_type].ports, -dx, -dy, ("inlet", "inout"))
    return src_port, dst_port


def build_commands(
    nodes: list[PlacedNode],
    links: list[Link],
    existing: CanvasState,
) -> tuple[list[CanvasCommand], dict[str, str]]:
    """Build add_node + connect commands. Returns (commands, ref->node_id map).

    `links` may reference either a new node's ref or an existing node id.
    """
    ref_to_id: dict[str, str] = {}
    positions: dict[str, Position] = {n.id: n.position for n in existing.nodes}
    types: dict[str, EquipmentType] = {n.id: n.type for n in existing.nodes}
    existing_ids = set(types)
    commands: list[CanvasCommand] = []

    for pn in nodes:
        node_id = _new_node_id()
        ref_to_id[pn.ref] = node_id
        pos = Position(x=pn.x, y=pn.y)
        positions[node_id] = pos
        types[node_id] = pn.type
        commands.append(
            AddNodeCommand(
                op="add_node", id=node_id, equipment=pn.type, position=pos, label=pn.label
            )
        )

    def resolve(ref: str) -> str | None:
        if ref in ref_to_id:
            return ref_to_id[ref]
        if ref in existing_ids:
            return ref
        return None

    for link in links:
        src = resolve(link.from_ref)
        dst = resolve(link.to_ref)
        if not src or not dst or src == dst:
            continue
        src_port, dst_port = choose_ports(types[src], positions[src], types[dst], positions[dst])
        commands.append(
            ConnectCommand(
                op="connect",
                id=_new_edge_id(),
                source=src,
                sourcePort=src_port,
                target=dst,
                targetPort=dst_port,
                data=PipeData(lineType=link.line_type or "process", label=link.label),
            )
        )

    return commands, ref_to_id


def removals(node_ids: list[str], existing: CanvasState) -> list[CanvasCommand]:
    existing_ids = {n.id for n in existing.nodes}
    return [
        RemoveNodeCommand(op="remove_node", id=node_id)
        for node_id in node_ids
        if node_id in existing_ids
    ]
