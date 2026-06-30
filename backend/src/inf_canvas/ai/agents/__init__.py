"""AI agents (each built as a LangGraph graph in its own package):

- orchestrator: Optimus, routes the user request to a specialist.
- pid_extractor: image -> equipment + connections -> canvas commands.
- canvas_commander: NL instruction -> canvas commands.

Each agent package follows the same layout: states.py, schemas.py, prompts.py,
graph.py. Cross-agent building blocks live in `shared/`.
"""

from .canvas_commander import run_commander
from .orchestrator import run_optimus
from .pid_extractor import run_extractor

__all__ = ["run_commander", "run_extractor", "run_optimus"]
