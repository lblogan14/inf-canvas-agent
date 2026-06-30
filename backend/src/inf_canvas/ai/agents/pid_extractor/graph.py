"""P&ID Extractor graph (LangGraph).

detect (Gemini vision) -> place (normalize boxes to canvas coords, de-overlap,
build commands) -> summarize. Relative positions from the source image are
preserved because every detection's normalized center is scaled into the
working area.
"""

from typing import Any

from langgraph.graph import END, START, StateGraph

from inf_canvas.ai.agents.shared import layout, tools
from inf_canvas.ai.models.gemini import GeminiClient
from inf_canvas.schema.canvas import CanvasState
from inf_canvas.schema.commands import CanvasCommand

from . import prompts
from .schemas import PIDExtraction
from .states import ExtractorState

# Working area the normalized (0..1) detections are scaled into.
WORK_W = 2400.0
WORK_H = 1500.0


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

    return (
        StateGraph(ExtractorState)
        .add_node("detect", detect)
        .add_node("place", place)
        .add_node("summarize", summarize)
        .add_edge(START, "detect")
        .add_edge("detect", "place")
        .add_edge("place", "summarize")
        .add_edge("summarize", END)
        .compile()
    )


def run_extractor(
    gemini: GeminiClient,
    image: bytes,
    mime_type: str,
    canvas: CanvasState,
) -> tuple[list[CanvasCommand], str]:
    graph = build_extractor_graph(gemini)
    result = graph.invoke({"image": image, "mime_type": mime_type, "canvas": canvas})
    return result.get("commands", []), result.get("summary", "")
