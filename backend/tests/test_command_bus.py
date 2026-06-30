import pytest

from inf_canvas.canvas.command_bus import CommandBus
from inf_canvas.canvas.store import JsonFileRepository
from inf_canvas.schema.commands import command_adapter


@pytest.mark.asyncio
async def test_apply_persists_and_updates_state(tmp_path):
    repo = JsonFileRepository(tmp_path)
    bus = CommandBus(repo)

    cmd = command_adapter.validate_python(
        {"op": "add_node", "id": "n1", "equipment": "compressor", "position": {"x": 5, "y": 5}}
    )
    await bus.apply("cv1", cmd, "user")

    state = await bus.get_state("cv1")
    assert len(state.nodes) == 1
    # persisted to disk
    reloaded = repo.load("cv1")
    assert reloaded is not None
    assert reloaded.nodes[0].id == "n1"


@pytest.mark.asyncio
async def test_apply_many_batches(tmp_path):
    repo = JsonFileRepository(tmp_path)
    bus = CommandBus(repo)
    commands = [
        command_adapter.validate_python(
            {
                "op": "add_node",
                "id": f"n{i}",
                "equipment": "gate_valve",
                "position": {"x": i, "y": 0},
            }
        )
        for i in range(3)
    ]
    count = await bus.apply_many("cv2", commands, "agent:commander")
    assert count == 3
    state = await bus.get_state("cv2")
    assert len(state.nodes) == 3
