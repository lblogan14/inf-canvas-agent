"""P&ID Extractor graph (LangGraph), two-pass with descriptor prior, a
Set-of-Mark verifier pass, and an OpenCV line-detection hybrid.

describe -> detect_equipment (boxes) -> connect (constrained to refs)
        -> verify (Set-of-Mark critic, optional) -> line_augment (OpenCV, optional)
        -> normalize (dedupe/filter) -> place (boxes -> canvas) -> summarize

Relative positions from the source image are preserved because each detection's
normalized box center is scaled into the working area.
"""

from typing import Any

from langgraph.graph import END, START, StateGraph

from inf_canvas.ai.agents.shared import annotate, layout, lines, tools
from inf_canvas.ai.models.gemini import GeminiClient
from inf_canvas.schema.canvas import CanvasState
from inf_canvas.schema.commands import CanvasCommand

from . import prompts
from .schemas import (
    ConnectionList,
    DetectedConnection,
    DetectedEquipment,
    EquipmentList,
    VerificationResult,
)
from .states import ExtractorState

# Working area the normalized (0..1) detections are scaled into.
WORK_W = 2400.0
WORK_H = 1500.0

# Two boxes above this intersection-over-union are treated as the same item.
DEDUPE_IOU = 0.6


def _iou(a: DetectedEquipment, b: DetectedEquipment) -> float:
    ix0, iy0 = max(a.box.x0, b.box.x0), max(a.box.y0, b.box.y0)
    ix1, iy1 = min(a.box.x1, b.box.x1), min(a.box.y1, b.box.y1)
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    area_a = max(0.0, a.box.x1 - a.box.x0) * max(0.0, a.box.y1 - a.box.y0)
    area_b = max(0.0, b.box.x1 - b.box.x0) * max(0.0, b.box.y1 - b.box.y0)
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


def _apply_verification(
    equipment: list[DetectedEquipment],
    connections: list[DetectedConnection],
    result: VerificationResult,
) -> tuple[list[DetectedEquipment], list[DetectedConnection]]:
    by_ref: dict[str, DetectedEquipment] = {e.ref: e for e in equipment}
    for ref in result.remove_equipment_refs:
        by_ref.pop(ref, None)
    for fix in result.retype:
        if fix.ref in by_ref:
            by_ref[fix.ref] = by_ref[fix.ref].model_copy(update={"type": fix.type})
    for item in result.missing_equipment:
        ref = item.ref
        while ref in by_ref:
            ref = f"{ref}_v"
        by_ref[ref] = item if ref == item.ref else item.model_copy(update={"ref": ref})

    refs = set(by_ref)
    remove = {(c.from_ref, c.to_ref) for c in result.remove_connections}
    kept = [c for c in connections if (c.from_ref, c.to_ref) not in remove]
    existing = {(c.from_ref, c.to_ref) for c in kept}
    for c in result.missing_connections:
        key = (c.from_ref, c.to_ref)
        if (
            c.from_ref in refs
            and c.to_ref in refs
            and c.from_ref != c.to_ref
            and key not in existing
        ):
            kept.append(c)
            existing.add(key)
    return list(by_ref.values()), kept


def _boxes(equipment: list[DetectedEquipment]) -> list[tuple[str, float, float, float, float]]:
    return [(e.ref, e.box.x0, e.box.y0, e.box.x1, e.box.y1) for e in equipment]


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

    def verify(state: ExtractorState) -> ExtractorState:
        equipment = state.get("equipment", [])
        if not gemini.settings.extractor_verify or not equipment:
            return {}
        connections = state.get("connections", [])
        try:
            marked = annotate.annotate_boxes(state["image"], _boxes(equipment))
        except Exception:
            return {}
        eq_listing = "\n".join(
            f"- {e.ref}: {e.type}" + (f" '{e.label}'" if e.label else "") for e in equipment
        )
        conn_listing = "\n".join(f"- {c.from_ref} -> {c.to_ref}" for c in connections) or "(none)"
        prompt = (
            f"Current equipment:\n{eq_listing}\n\n"
            f"Current connections:\n{conn_listing}\n\n"
            "Review the red boxes against the drawing and return only corrections."
        )
        try:
            result = gemini.generate_structured(
                model=vision,
                contents=[gemini.image_part(marked, "image/png"), prompt],
                schema=VerificationResult,
                system_instruction=prompts.VERIFIER_SYSTEM,
                temperature=0.1,
            )
        except Exception:
            return {}
        equipment, connections = _apply_verification(equipment, connections, result)
        return {"equipment": equipment, "connections": connections}

    def line_augment(state: ExtractorState) -> ExtractorState:
        equipment = state.get("equipment", [])
        if not gemini.settings.extractor_line_hybrid or len(equipment) < 2:
            return {}
        try:
            proposed = lines.propose_connections(state["image"], _boxes(equipment))
        except Exception:
            return {}
        connections = list(state.get("connections", []))
        existing = {frozenset((c.from_ref, c.to_ref)) for c in connections}
        added = False
        for a, b in proposed:
            key = frozenset((a, b))
            if key in existing:
                continue
            existing.add(key)
            connections.append(DetectedConnection(from_ref=a, to_ref=b, line_type="process"))
            added = True
        return {"connections": connections} if added else {}

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
        .add_node("verify", verify)
        .add_node("line_augment", line_augment)
        .add_node("normalize", normalize)
        .add_node("place", place)
        .add_node("summarize", summarize)
        .add_edge(START, "describe")
        .add_edge("describe", "detect_equipment")
        .add_edge("detect_equipment", "connect")
        .add_edge("connect", "verify")
        .add_edge("verify", "line_augment")
        .add_edge("line_augment", "normalize")
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
