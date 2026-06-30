"""P&ID Extractor agent (LangGraph).

detect (Gemini vision) -> place (normalize boxes to canvas coords, build
commands) -> summarize. Relative positions from the source image are preserved
because every detection's normalized center is scaled into the working area.
"""

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from ...schema.canvas import CanvasState
from ...schema.commands import CanvasCommand
from ..models import prompts
from ..models.gemini import GeminiClient
from ..models.schemas import PIDExtraction
from . import layout, tools

# Working area the normalized (0..1) detections are scaled into. Generous so
# closely-spaced symbols have room before overlap resolution kicks in.
WORK_W = 2400.0
WORK_H = 1500.0


class ExtractorState(TypedDict, total=False):
    image: bytes
    mime_type: str
    canvas: CanvasState
    extraction: PIDExtraction
    commands: list[CanvasCommand]
    summary: str


def build_extractor_graph(gemini: GeminiClient) -> Any:
    def detect(state: ExtractorState) -> ExtractorState:
        part = gemini.image_part(state["image"], state["mime_type"])
        extraction = gemini.generate_structured(
            model=gemini.settings.gemini_model_vision,
            contents=[part, prompts.PID_EXTRACTOR_USER],
            schema=PIDExtraction,
            system_instruction=prompts.PID_EXTRACTOR_SYSTEM,
            temperature=0.1,
        )
        return {"extraction": extraction}

    def place(state: ExtractorState) -> ExtractorState:
        extraction = state["extraction"]
        placed = [
            tools.PlacedNode(ref=e.ref, type=e.type, label=e.label, x=e.x * WORK_W, y=e.y * WORK_H)
            for e in extraction.equipment
        ]
        # Separate overlapping symbols while keeping their relative layout.
        layout.resolve_overlaps(placed)
        links = [
            tools.Link(from_ref=c.from_ref, to_ref=c.to_ref, line_type=c.line_type, label=c.label)
            for c in extraction.connections
        ]
        commands, _ = tools.build_commands(placed, links, state["canvas"])
        return {"commands": commands}

    def summarize(state: ExtractorState) -> ExtractorState:
        commands = state["commands"]
        nodes = sum(1 for c in commands if c.op == "add_node")
        edges = sum(1 for c in commands if c.op == "connect")
        return {
            "summary": f"Extracted {nodes} equipment items and {edges} connections from the P&ID, "
            "preserving their relative layout."
        }

    graph = StateGraph(ExtractorState)
    graph.add_node("detect", detect)
    graph.add_node("place", place)
    graph.add_node("summarize", summarize)
    graph.set_entry_point("detect")
    graph.add_edge("detect", "place")
    graph.add_edge("place", "summarize")
    graph.add_edge("summarize", END)
    return graph.compile()


def run_extractor(
    gemini: GeminiClient,
    image: bytes,
    mime_type: str,
    canvas: CanvasState,
) -> tuple[list[CanvasCommand], str]:
    graph = build_extractor_graph(gemini)
    result = graph.invoke({"image": image, "mime_type": mime_type, "canvas": canvas})
    return result.get("commands", []), result.get("summary", "")
