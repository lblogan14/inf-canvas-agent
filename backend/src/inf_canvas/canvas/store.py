"""Canvas persistence. JSON files now, behind a repository protocol so a real
database can be dropped in later without touching callers.
"""

from pathlib import Path
from typing import Protocol

from ..schema.canvas import CanvasMeta, CanvasState


class CanvasRepository(Protocol):
    def load(self, canvas_id: str) -> CanvasState | None: ...
    def save(self, state: CanvasState) -> None: ...
    def delete(self, canvas_id: str) -> bool: ...
    def list_projects(self) -> list[CanvasMeta]: ...


class JsonFileRepository:
    """Stores each canvas as `<projects_dir>/<id>.json`."""

    def __init__(self, directory: Path) -> None:
        self._dir = directory
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, canvas_id: str) -> Path:
        return self._dir / f"{canvas_id}.json"

    def load(self, canvas_id: str) -> CanvasState | None:
        path = self._path(canvas_id)
        if not path.exists():
            return None
        return CanvasState.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, state: CanvasState) -> None:
        path = self._path(state.meta.id)
        path.write_text(state.model_dump_json(indent=2), encoding="utf-8")

    def delete(self, canvas_id: str) -> bool:
        path = self._path(canvas_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_projects(self) -> list[CanvasMeta]:
        metas: list[CanvasMeta] = []
        for path in sorted(self._dir.glob("*.json")):
            try:
                state = CanvasState.model_validate_json(path.read_text(encoding="utf-8"))
                metas.append(state.meta)
            except Exception:
                continue
        return metas
