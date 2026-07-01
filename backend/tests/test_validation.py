from inf_canvas.canvas.validation import validate_canvas
from inf_canvas.schema.canvas import CanvasEdge, CanvasNode, CanvasState, PipeData, Position


def _state(nodes: list[CanvasNode], edges: list[CanvasEdge] | None = None) -> CanvasState:
    from inf_canvas.schema.canvas import CanvasMeta

    return CanvasState(
        meta=CanvasMeta(id="cv_v", name="V"), nodes=nodes, edges=edges or [], groups=[]
    )


def _pump(node_id: str, label: str | None = None) -> CanvasNode:
    return CanvasNode(id=node_id, type="centrifugal_pump", position=Position(x=0, y=0), label=label)


def test_isolated_node_flagged():
    issues = validate_canvas(_state([_pump("p1", "P-101")]))
    assert any(i.id == "isolated:p1" for i in issues)


def test_duplicate_tags_error():
    issues = validate_canvas(_state([_pump("p1", "P-101"), _pump("p2", "P-101")]))
    dup = next(i for i in issues if i.id == "duptag:P-101")
    assert dup.severity == "error"
    assert sorted(dup.target_ids) == ["p1", "p2"]


def test_pump_missing_discharge():
    v = CanvasNode(id="v", type="vessel", position=Position(x=0, y=0), label="V-1")
    e = CanvasEdge(id="e1", source="v", sourcePort="side_out", target="p1", targetPort="suction")
    issues = validate_canvas(_state([v, _pump("p1", "P-101")], [e]))
    ids = {i.id for i in issues}
    assert "nodischarge:p1" in ids
    assert "nosuction:p1" not in ids


def test_dangling_edge_error():
    e = CanvasEdge(id="e1", source="p1", sourcePort="discharge", target="ghost", targetPort="in")
    issues = validate_canvas(_state([_pump("p1", "P-101")], [e]))
    assert any(i.id == "dangling:e1" and i.severity == "error" for i in issues)


def test_signal_line_not_touching_instrument():
    p = _pump("p1", "P-101")
    v = CanvasNode(id="v", type="vessel", position=Position(x=0, y=0), label="V-1")
    e = CanvasEdge(
        id="e1",
        source="p1",
        sourcePort="discharge",
        target="v",
        targetPort="side_in",
        data=PipeData(lineType="signal"),
    )
    issues = validate_canvas(_state([p, v], [e]))
    assert any(i.id == "signal-noinstr:e1" for i in issues)


def test_clean_design_has_no_issues():
    v = CanvasNode(id="v", type="vessel", position=Position(x=0, y=0), label="V-1")
    p = _pump("p1", "P-101")
    t = CanvasNode(id="t", type="storage_tank", position=Position(x=0, y=0), label="T-1")
    e1 = CanvasEdge(id="e1", source="v", sourcePort="side_out", target="p1", targetPort="suction")
    e2 = CanvasEdge(id="e2", source="p1", sourcePort="discharge", target="t", targetPort="fill")
    assert validate_canvas(_state([v, p, t], [e1, e2])) == []
