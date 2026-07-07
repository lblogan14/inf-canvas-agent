from pathlib import Path

from inf_canvas.canvas.store import JsonFileRepository
from inf_canvas.schema.canvas import empty_canvas


def test_save_load_roundtrip(tmp_path: Path):
    repo = JsonFileRepository(tmp_path)
    state = empty_canvas("cv1", "My Canvas")
    repo.save(state)

    loaded = repo.load("cv1")
    assert loaded is not None
    assert loaded.meta.name == "My Canvas"


def test_list_projects(tmp_path: Path):
    repo = JsonFileRepository(tmp_path)
    repo.save(empty_canvas("a", "A"))
    repo.save(empty_canvas("b", "B"))
    metas = repo.list_projects()
    assert {m.id for m in metas} == {"a", "b"}


def test_load_missing_returns_none(tmp_path: Path):
    repo = JsonFileRepository(tmp_path)
    assert repo.load("nope") is None


def test_delete_removes_project(tmp_path: Path):
    repo = JsonFileRepository(tmp_path)
    repo.save(empty_canvas("a", "A"))
    assert repo.delete("a") is True
    assert repo.load("a") is None
    assert repo.delete("a") is False  # already gone
