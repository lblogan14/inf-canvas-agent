"""Canvas Commander graph (LangGraph). plan -> compile."""

from typing import Any

from langgraph.graph import END, START, StateGraph

from inf_canvas.ai.agents.shared import tools
from inf_canvas.ai.models.base import ModelClient
from inf_canvas.schema.canvas import CanvasState
from inf_canvas.schema.commands import CanvasCommand

from . import prompts
from .schemas import CommanderPlan
from .states import CommanderState

NODE_LABELS = {
    "plan": "Planning the changes",
    "compile": "Compiling canvas actions",
}


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


def build_commander_graph(model: ModelClient) -> Any:
    def plan(state: CommanderState) -> CommanderState:
        prompt = f"{_canvas_summary(state['canvas'])}\n\nUser instruction: {state['instruction']}"
        result = model.generate_structured(
            role="flash",
            prompt=prompt,
            schema=CommanderPlan,
            system=prompts.COMMANDER_SYSTEM,
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
    model: ModelClient,
    instruction: str,
    canvas: CanvasState,
) -> tuple[list[CanvasCommand], str]:
    graph = build_commander_graph(model)
    result = graph.invoke({"instruction": instruction, "canvas": canvas})
    return result.get("commands", []), result.get("reply", "Done.")
