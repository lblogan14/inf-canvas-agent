from inf_canvas.ai.agents import tools
from inf_canvas.schema.canvas import CanvasNode, Position, empty_canvas


def test_build_commands_creates_nodes_and_edge():
    canvas = empty_canvas("cv", "Test")
    nodes = [
        tools.PlacedNode(ref="A", type="centrifugal_pump", label="P-101", x=0, y=0),
        tools.PlacedNode(ref="B", type="storage_tank", label="T-1", x=400, y=0),
    ]
    links = [tools.Link(from_ref="A", to_ref="B")]
    commands, ref_map = tools.build_commands(nodes, links, canvas)

    adds = [c for c in commands if c.op == "add_node"]
    connects = [c for c in commands if c.op == "connect"]
    assert len(adds) == 2
    assert len(connects) == 1
    # refs mapped to generated ids
    assert connects[0].source == ref_map["A"]
    assert connects[0].target == ref_map["B"]


def test_choose_ports_faces_target():
    # Target is to the right -> source should use a right/outlet-ish port,
    # target should use its left inlet 'in'.
    src_port, dst_port = tools.choose_ports(
        "positive_displacement_pump",
        Position(x=0, y=0),
        "gate_valve",
        Position(x=200, y=0),
    )
    assert src_port == "discharge"  # the right-side outlet
    assert dst_port == "in"  # the left-side inlet


def test_links_can_reference_existing_nodes():
    existing_id = "n_existing"
    canvas = empty_canvas("cv", "Test")
    canvas = canvas.model_copy(
        update={"nodes": [CanvasNode(id=existing_id, type="vessel", position=Position(x=0, y=0))]}
    )
    # connect a new node to the existing one
    commands, _ = tools.build_commands(
        [tools.PlacedNode(ref="B", type="storage_tank", label=None, x=400, y=0)],
        [tools.Link(from_ref=existing_id, to_ref="B")],
        canvas,
    )
    connects = [c for c in commands if c.op == "connect"]
    assert len(connects) == 1
    assert connects[0].source == existing_id
