"""P&ID Extractor graph (LangGraph), two-pass with a descriptor prior.

describe (semantic prior) -> detect_equipment (bounding boxes) -> connect
(constrained to detected refs) -> normalize (dedupe / filter) -> place
(boxes -> canvas coords, de-overlap, build commands) -> summarize.

Relative positions from the source image are preserved because each detection's
normalized box center is scaled into the working area.
"""

from typing import Any

from langgraph.graph import END, START, StateGraph

from inf_canvas.ai.agents.shared import layout, tools
from inf_canvas.ai.models.gemini import GeminiClient
from inf_canvas.schema.canvas import CanvasState
from inf_canvas.schema.commands import CanvasCommand

from . import prompts
from .schemas import ConnectionList, DetectedConnection, DetectedEquipment, EquipmentList
from .states import ExtractorState

# Working area the normalized (0..1) detections are scaled into.
WORK_W = 2400.0
WORK_H = 1500.0

# Two boxes above this intersection-over-union are treated as the same item.
DEDUPE_IOU = 0.6


def _iou(a: DetectedEquipment, b: DetectedEquipment) -> float:
    ax0, ay0, ax1, ay1 = a.box.x0, a.box.y0, a.box.x1, a.box.y1
    bx0, by0, bx1, by1 = b.box.x0, b.box.y0, b.box.x1, b.box.y1
    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    area_a = max(0.0, ax1 - ax0) * max(0.0, ay1 - ay0)
    area_b = max(0.0, bx1 - bx0) * max(0.0, by1 - by0)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _dedupe_equipment(items: list[DetectedEquipment]) -> list[DetectedEquipment]:
    kept: list[DetectedEquipment] = []
    for item in items:
        if any(_iou(item, k) > DEDUPE_IOU for k in kept):
            continue
        kept.append(item)
    return kept


def _filter_connections(
    connections: list[DetectedConnection], refs: set[str]
) -> list[DetectedConnection]:
    seen: set[tuple[str, str]] = set()
    out: list[DetectedConnection] = []
    for c in connections:
        if c.from_ref not in refs or c.to_ref not in refs or c.from_ref == c.to_ref:
            continue
        key = (c.from_ref, c.to_ref)
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def build_extractor_graph(gemini: GeminiClient) -> Any:
    vision = gemini.settings.gemini_model_vision

    def describe(state: ExtractorState) -> ExtractorState:
        part = gemini.image_part(state["image"], state["mime_type"])
        text = gemini.generate_text(
            model=vision,
            contents=[part, prompts.DESCRIBER_USER],
            system_instruction=prompts.DESCRIBER_SYSTEM,
            temperature=0.2,
        )
        return {"description": text}

    def detect_equipment(state: ExtractorState) -> ExtractorState:
        part = gemini.image_part(state["image"], state["mime_type"])
        prompt = f"Diagram notes:\n{state.get('description', '')}\n\n{prompts.EQUIPMENT_USER}"
        result = gemini.generate_structured(
            model=vision,
            contents=[part, prompt],
            schema=EquipmentList,
            system_instruction=prompts.EQUIPMENT_SYSTEM,
            temperature=0.1,
        )
        return {"equipment": result.equipment}

    def connect(state: ExtractorState) -> ExtractorState:
        equipment = state.get("equipment", [])
        if not equipment:
            return {"connections": []}
        listing = "\n".join(
            f"- {e.ref}: {e.type}"
            + (f" '{e.label}'" if e.label else "")
            + f" at ({e.box.cx:.2f}, {e.box.cy:.2f})"
            for e in equipment
        )
        part = gemini.image_part(state["image"], state["mime_type"])
        prompt = (
            f"Diagram notes:\n{state.get('description', '')}\n\n"
            f"Detected equipment (use ONLY these refs):\n{listing}\n\n"
            "Trace every pipe and signal line and list the connections."
        )
        result = gemini.generate_structured(
            model=vision,
            contents=[part, prompt],
            schema=ConnectionList,
            system_instruction=prompts.CONNECTION_SYSTEM,
            temperature=0.1,
        )
        return {"connections": result.connections}

    def normalize(state: ExtractorState) -> ExtractorState:
        equipment = _dedupe_equipment(state.get("equipment", []))
        refs = {e.ref for e in equipment}
        connections = _filter_connections(state.get("connections", []), refs)
        return {"equipment": equipment, "connections": connections}

    def place(state: ExtractorState) -> ExtractorState:
        placed = [
            tools.PlacedNode(
                ref=e.ref, type=e.type, label=e.label, x=e.box.cx * WORK_W, y=e.box.cy * WORK_H
            )
            for e in state.get("equipment", [])
        ]
        layout.resolve_overlaps(placed)
        links = [
            tools.Link(from_ref=c.from_ref, to_ref=c.to_ref, line_type=c.line_type, label=c.label)
            for c in state.get("connections", [])
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
        .add_node("describe", describe)
        .add_node("detect_equipment", detect_equipment)
        .add_node("connect", connect)
        .add_node("normalize", normalize)
        .add_node("place", place)
        .add_node("summarize", summarize)
        .add_edge(START, "describe")
        .add_edge("describe", "detect_equipment")
        .add_edge("detect_equipment", "connect")
        .add_edge("connect", "normalize")
        .add_edge("normalize", "place")
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
