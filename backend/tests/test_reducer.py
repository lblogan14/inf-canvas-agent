from inf_canvas.canvas.reducer import apply_command
from inf_canvas.schema.canvas import empty_canvas
from inf_canvas.schema.commands import command_adapter


def cmd(data: dict[str, object]):
    return command_adapter.validate_python(data)


def test_add_node():
    state = empty_canvas("cv", "Test")
    state = apply_command(
        state,
        cmd(
            {
                "op": "add_node",
                "id": "n1",
                "equipment": "centrifugal_pump",
                "position": {"x": 1, "y": 2},
            }
        ),
    )
    assert len(state.nodes) == 1
    assert state.nodes[0].type == "centrifugal_pump"


def test_remove_node_drops_edges():
    state = empty_canvas("cv", "Test")
    state = apply_command(
        state,
        cmd(
            {
                "op": "batch",
                "commands": [
                    {
                        "op": "add_node",
                        "id": "a",
                        "equipment": "vessel",
                        "position": {"x": 0, "y": 0},
                    },
                    {
                        "op": "add_node",
                        "id": "b",
                        "equipment": "storage_tank",
                        "position": {"x": 1, "y": 0},
                    },
                    {
                        "op": "connect",
                        "id": "e1",
                        "source": "a",
                        "sourcePort": "bottom",
                        "target": "b",
                        "targetPort": "fill",
                    },
                ],
            }
        ),
    )
    assert len(state.edges) == 1
    state = apply_command(state, cmd({"op": "remove_node", "id": "a"}))
    assert [n.id for n in state.nodes] == ["b"]
    assert state.edges == []


def test_reducer_is_pure():
    state = empty_canvas("cv", "Test")
    apply_command(
        state,
        cmd(
            {"op": "add_node", "id": "n1", "equipment": "gate_valve", "position": {"x": 0, "y": 0}}
        ),
    )
    assert state.nodes == []  # original unchanged
