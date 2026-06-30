from inf_canvas.ai.agents import layout, tools
from inf_canvas.schema.equipment import EQUIPMENT_METADATA


def _overlaps(a: tools.PlacedNode, b: tools.PlacedNode, padding: float = 28.0) -> bool:
    sa = EQUIPMENT_METADATA[a.type].size
    sb = EQUIPMENT_METADATA[b.type].size
    min_dx = (sa.width + sb.width) / 2 + padding
    min_dy = (sa.height + sb.height) / 2 + padding
    return abs(b.x - a.x) < min_dx - 1 and abs(b.y - a.y) < min_dy - 1


def test_resolve_overlaps_separates_stacked_nodes():
    nodes = [
        tools.PlacedNode(ref="a", type="centrifugal_pump", label=None, x=100, y=100),
        tools.PlacedNode(ref="b", type="centrifugal_pump", label=None, x=105, y=102),
        tools.PlacedNode(ref="c", type="centrifugal_pump", label=None, x=110, y=98),
    ]
    layout.resolve_overlaps(nodes)
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            assert not _overlaps(nodes[i], nodes[j])


def test_resolve_overlaps_preserves_already_spaced():
    nodes = [
        tools.PlacedNode(ref="a", type="gate_valve", label=None, x=0, y=0),
        tools.PlacedNode(ref="b", type="gate_valve", label=None, x=600, y=0),
    ]
    layout.resolve_overlaps(nodes)
    assert nodes[0].x == 0 and nodes[1].x == 600  # untouched
