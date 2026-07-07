"""Geometry helpers for placing extracted equipment.

`resolve_overlaps` nudges nodes apart so symbols don't overlap while keeping
their *relative* arrangement intact — which is exactly what the P&ID Extractor
needs (it must preserve the source diagram's layout, so a full graph re-layout
would be wrong here).
"""

from inf_canvas.schema.equipment import EQUIPMENT_METADATA

from .tools import PlacedNode


def resolve_overlaps(
    nodes: list[PlacedNode],
    padding: float = 28.0,
    iterations: int = 120,
) -> list[PlacedNode]:
    """Iteratively separate overlapping nodes in place. Returns the same list."""
    sizes = {
        id(n): (EQUIPMENT_METADATA[n.type].size.width, EQUIPMENT_METADATA[n.type].size.height)
        for n in nodes
    }
    for _ in range(iterations):
        moved = False
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                a, b = nodes[i], nodes[j]
                wa, ha = sizes[id(a)]
                wb, hb = sizes[id(b)]
                min_dx = (wa + wb) / 2 + padding
                min_dy = (ha + hb) / 2 + padding
                dx = b.x - a.x
                dy = b.y - a.y
                if abs(dx) >= min_dx or abs(dy) >= min_dy:
                    continue
                overlap_x = min_dx - abs(dx)
                overlap_y = min_dy - abs(dy)
                if overlap_x < overlap_y:
                    shift = overlap_x / 2 + 0.5
                    sign = 1.0 if dx >= 0 else -1.0
                    a.x -= sign * shift
                    b.x += sign * shift
                else:
                    shift = overlap_y / 2 + 0.5
                    sign = 1.0 if dy >= 0 else -1.0
                    a.y -= sign * shift
                    b.y += sign * shift
                moved = True
        if not moved:
            break
    return nodes
