"""Canvas Commander graph (LangGraph).

plan (Gemini Flash, given the current canvas) -> compile (plan -> commands).
"""

from typing import Any

from langgraph.graph import END, START, StateGraph

from inf_canvas.ai.agents.shared import tools
from inf_canvas.ai.models.gemini import GeminiClient
from inf_canvas.schema.canvas import CanvasState
from inf_canvas.schema.commands import CanvasCommand

from . import prompts
from .schemas import CommanderPlan
from .states import CommanderState


def _canvas_summary(canvas: CanvasState) -> str:
    if not canvas.nodes:
        return "The canvas is currently empty."
    lines = [
        f"- {n.id} ({n.type})"
        + (f" '{n.label}'" if n.label else "")
        + f" at ({int(n.position.x)},{int(n.position.y)})"
        for n in canvas.nodes
    ]
    return "Current canvas nodes:\n" + "\n".join(lines)


def build_commander_graph(gemini: GeminiClient) -> Any:
    def plan(state: CommanderState) -> CommanderState:
        prompt = f"{_canvas_summary(state['canvas'])}\n\nUser instruction: {state['instruction']}"
        result = gemini.generate_structured(
            model=gemini.settings.gemini_model_flash,
            contents=[prompt],
            schema=CommanderPlan,
            system_instruction=prompts.COMMANDER_SYSTEM,
            temperature=0.3,
        )
        return {"plan": result}

    def compile_plan(state: CommanderState) -> CommanderState:
        plan_obj = state["plan"]
        placed = [
            tools.PlacedNode(ref=n.ref, type=n.type, label=n.label, x=n.x, y=n.y)
            for n in plan_obj.add_nodes
        ]
        links = [
            tools.Link(from_ref=c.from_ref, to_ref=c.to_ref, line_type=c.line_type, label=c.label)
            for c in plan_obj.connect
        ]
        commands, _ = tools.build_commands(placed, links, state["canvas"])
        commands.extend(tools.removals(plan_obj.remove_node_ids, state["canvas"]))
        return {"commands": commands, "reply": plan_obj.reply}

    return (
        StateGraph(CommanderState)
        .add_node("plan", plan)
        .add_node("compile", compile_plan)
        .add_edge(START, "plan")
        .add_edge("plan", "compile")
        .add_edge("compile", END)
        .compile()
    )


def run_commander(
    gemini: GeminiClient,
    instruction: str,
    canvas: CanvasState,
) -> tuple[list[CanvasCommand], str]:
    graph = build_commander_graph(gemini)
    result = graph.invoke({"instruction": instruction, "canvas": canvas})
    return result.get("commands", []), result.get("reply", "Done.")
