"""P&ID rule-checker (Python mirror of frontend/src/canvas/validation.ts).

Pure functions over a CanvasState → a list of issues. Used to let agents
self-check a design they just built (see the Commander's self-check pass) and
kept in lockstep with the frontend validator so humans and AI see the same
findings.
"""

from dataclasses import dataclass, field
from typing import Literal

from inf_canvas.schema.canvas import CanvasNode, CanvasState
from inf_canvas.schema.equipment import EQUIPMENT_METADATA, EquipmentType

IssueSeverity = Literal["error", "warning"]

# Category grouping (the Python EquipmentMeta has no `category`, so classify by
# type here; keep aligned with the frontend equipment categories).
_PUMPS: frozenset[EquipmentType] = frozenset({"centrifugal_pump", "positive_displacement_pump"})
_COMPRESSORS: frozenset[EquipmentType] = frozenset({"compressor", "blower", "fan"})
_INSTRUMENTS: frozenset[EquipmentType] = frozenset({"instrument"})


@dataclass
class Issue:
    id: str
    severity: IssueSeverity
    title: str
    target_ids: list[str] = field(default_factory=list)
    detail: str | None = None


def _label(n: CanvasNode) -> str:
    return (n.label or "").strip() or EQUIPMENT_METADATA[n.type].label


def validate_canvas(state: CanvasState) -> list[Issue]:
    errors: list[Issue] = []
    warnings: list[Issue] = []

    nodes_by_id = {n.id: n for n in state.nodes}
    degree: dict[str, int] = {}
    ports_used: dict[str, set[str]] = {}

    def use(node_id: str, port: str) -> None:
        degree[node_id] = degree.get(node_id, 0) + 1
        ports_used.setdefault(node_id, set()).add(port)

    # --- edge-level checks -------------------------------------------------
    for e in state.edges:
        s = nodes_by_id.get(e.source)
        t = nodes_by_id.get(e.target)
        if s is None or t is None:
            errors.append(
                Issue(
                    id=f"dangling:{e.id}",
                    severity="error",
                    title="Connection references a missing node",
                    target_ids=[e.id],
                )
            )
            continue
        if e.source == e.target:
            errors.append(
                Issue(
                    id=f"selfloop:{e.id}",
                    severity="error",
                    title=f"{_label(s)} is connected to itself",
                    target_ids=[e.id, e.source],
                )
            )
            continue
        use(e.source, e.sourcePort)
        use(e.target, e.targetPort)

        line_type = (e.data.lineType if e.data else None) or "process"
        s_instr = s.type in _INSTRUMENTS
        t_instr = t.type in _INSTRUMENTS
        if line_type == "signal" and not s_instr and not t_instr:
            warnings.append(
                Issue(
                    id=f"signal-noinstr:{e.id}",
                    severity="warning",
                    title="Signal line not connected to an instrument",
                    detail=f"{_label(s)} -> {_label(t)}",
                    target_ids=[e.id],
                )
            )
        if line_type == "process" and (s_instr or t_instr):
            warnings.append(
                Issue(
                    id=f"process-toinstr:{e.id}",
                    severity="warning",
                    title="Process line connected to an instrument",
                    detail=f"Expected a signal line: {_label(s)} -> {_label(t)}",
                    target_ids=[e.id],
                )
            )

    # --- duplicate tags ----------------------------------------------------
    by_tag: dict[str, list[str]] = {}
    for n in state.nodes:
        tag = (n.label or "").strip()
        if tag:
            by_tag.setdefault(tag, []).append(n.id)
    for tag, ids in by_tag.items():
        if len(ids) > 1:
            errors.append(
                Issue(
                    id=f"duptag:{tag}",
                    severity="error",
                    title=f'Duplicate tag "{tag}"',
                    detail=f"{len(ids)} equipment items share this tag",
                    target_ids=ids,
                )
            )

    # --- node-level checks -------------------------------------------------
    for n in state.nodes:
        meta = EQUIPMENT_METADATA[n.type]
        deg = degree.get(n.id, 0)

        if deg == 0:
            if n.type in _INSTRUMENTS:
                warnings.append(
                    Issue(
                        id=f"orphan-instr:{n.id}",
                        severity="warning",
                        title=f"Instrument {_label(n)} has no signal connection",
                        target_ids=[n.id],
                    )
                )
            else:
                warnings.append(
                    Issue(
                        id=f"isolated:{n.id}",
                        severity="warning",
                        title=f"{_label(n)} is not connected to anything",
                        target_ids=[n.id],
                    )
                )
        elif n.type in _PUMPS or n.type in _COMPRESSORS:
            used = ports_used.get(n.id, set())
            inlets = [p.id for p in meta.ports if p.role == "inlet"]
            outlets = [p.id for p in meta.ports if p.role == "outlet"]
            if inlets and not any(pid in used for pid in inlets):
                warnings.append(
                    Issue(
                        id=f"nosuction:{n.id}",
                        severity="warning",
                        title=f"{_label(n)} has no suction (inlet) connection",
                        target_ids=[n.id],
                    )
                )
            if outlets and not any(pid in used for pid in outlets):
                warnings.append(
                    Issue(
                        id=f"nodischarge:{n.id}",
                        severity="warning",
                        title=f"{_label(n)} has no discharge (outlet) connection",
                        target_ids=[n.id],
                    )
                )

        if not (n.label or "").strip():
            warnings.append(
                Issue(
                    id=f"untagged:{n.id}",
                    severity="warning",
                    title=f"{meta.label} is untagged",
                    detail="Add a tag (e.g. P-101)",
                    target_ids=[n.id],
                )
            )

    return errors + warnings
