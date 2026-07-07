"""Optimus orchestrator graph (LangGraph).

route (classify intent) -> delegate to the Canvas Commander sub-graph, or answer
directly. Provider-agnostic: uses a ModelClient by role.
"""

from typing import Any

from langgraph.graph import END, START, StateGraph

from inf_canvas.ai.agents.canvas_commander.graph import run_commander
from inf_canvas.ai.models.base import ModelClient
from inf_canvas.schema.canvas import CanvasState
from inf_canvas.schema.commands import CanvasCommand

from . import prompts
from .schemas import RouteDecision
from .states import OptimusState

NODE_LABELS = {
    "route": "Routing your request",
    "commander": "Building on the canvas",
    "answer": "Composing a reply",
}


def build_optimus_graph(model: ModelClient) -> Any:
    def route(state: OptimusState) -> OptimusState:
        decision = model.generate_structured(
            role="pro",
            prompt=state["message"],
            schema=RouteDecision,
            system=prompts.OPTIMUS_SYSTEM,
            temperature=0.0,
        )
        return {"route": decision.route}

    def commander(state: OptimusState) -> OptimusState:
        commands, reply = run_commander(model, state["message"], state["canvas"])
        return {"commands": commands, "reply": reply}

    def answer(state: OptimusState) -> OptimusState:
        text = model.generate_text(
            role="flash", prompt=state["message"], system=prompts.OPTIMUS_ANSWER_SYSTEM
        )
        return {"reply": text, "commands": []}

    return (
        StateGraph(OptimusState)
        .add_node("route", route)
        .add_node("commander", commander)
        .add_node("answer", answer)
        .add_edge(START, "route")
        .add_conditional_edges(
            "route",
            lambda s: s["route"],
            {"commander": "commander", "answer": "answer"},
        )
        .add_edge("commander", END)
        .add_edge("answer", END)
        .compile()
    )


def run_optimus(
    model: ModelClient,
    message: str,
    canvas: CanvasState,
) -> tuple[list[CanvasCommand], str]:
    graph = build_optimus_graph(model)
    result = graph.invoke({"message": message, "canvas": canvas})
    return result.get("commands", []), result.get("reply", "")
