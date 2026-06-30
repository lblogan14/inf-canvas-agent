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


def test_group_lifecycle_and_member_pruning():
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
                        "op": "add_group",
                        "id": "g1",
                        "label": "Unit 100",
                        "position": {"x": -10, "y": -10},
                        "width": 200,
                        "height": 150,
                        "memberIds": ["a", "b"],
                    },
                ],
            }
        ),
    )
    assert len(state.groups) == 1
    assert state.groups[0].memberIds == ["a", "b"]

    # update group label + position
    state = apply_command(
        state,
        cmd(
            {
                "op": "update_group",
                "id": "g1",
                "patch": {"label": "Unit 200", "position": {"x": 5, "y": 5}},
            }
        ),
    )
    assert state.groups[0].label == "Unit 200"
    assert state.groups[0].position.x == 5

    # removing a member node prunes it from the group's memberIds
    state = apply_command(state, cmd({"op": "remove_node", "id": "a"}))
    assert state.groups[0].memberIds == ["b"]

    # remove group leaves nodes intact
    state = apply_command(state, cmd({"op": "remove_group", "id": "g1"}))
    assert state.groups == []
    assert [n.id for n in state.nodes] == ["b"]


def test_update_edge_sets_waypoints():
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
    state = apply_command(
        state,
        cmd(
            {
                "op": "update_edge",
                "id": "e1",
                "patch": {"lineType": "process", "waypoints": [{"x": 50, "y": 50}]},
            }
        ),
    )
    data = state.edges[0].data
    assert data is not None and data.waypoints is not None
    assert (data.waypoints[0].x, data.waypoints[0].y) == (50, 50)


def test_reducer_is_pure():
    state = empty_canvas("cv", "Test")
    apply_command(
        state,
        cmd(
            {"op": "add_node", "id": "n1", "equipment": "gate_valve", "position": {"x": 0, "y": 0}}
        ),
    )
    assert state.nodes == []  # original unchanged
