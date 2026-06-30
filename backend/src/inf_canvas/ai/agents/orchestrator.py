"""Optimus orchestrator (LangGraph).

route (classify intent) -> delegate to the Canvas Commander sub-graph, or answer
directly. The 'commander' node invokes the Commander graph, so this is a graph
delegating to another graph.
"""

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from ...schema.canvas import CanvasState
from ...schema.commands import CanvasCommand
from ..models import prompts
from ..models.gemini import GeminiClient
from ..models.schemas import RouteDecision
from .canvas_commander import run_commander


class OptimusState(TypedDict, total=False):
    message: str
    canvas: CanvasState
    route: str
    reply: str
    commands: list[CanvasCommand]


def build_optimus_graph(gemini: GeminiClient) -> Any:
    def route(state: OptimusState) -> OptimusState:
        decision = gemini.generate_structured(
            model=gemini.settings.gemini_model_pro,
            contents=[state["message"]],
            schema=RouteDecision,
            system_instruction=prompts.OPTIMUS_SYSTEM,
            temperature=0.0,
        )
        return {"route": decision.route}

    def commander(state: OptimusState) -> OptimusState:
        commands, reply = run_commander(gemini, state["message"], state["canvas"])
        return {"commands": commands, "reply": reply}

    def answer(state: OptimusState) -> OptimusState:
        text = gemini.generate_text(
            model=gemini.settings.gemini_model_flash,
            contents=[state["message"]],
            system_instruction=prompts.OPTIMUS_ANSWER_SYSTEM,
        )
        return {"reply": text, "commands": []}

    graph = StateGraph(OptimusState)
    graph.add_node("route", route)
    graph.add_node("commander", commander)
    graph.add_node("answer", answer)
    graph.set_entry_point("route")
    graph.add_conditional_edges(
        "route",
        lambda s: s["route"],
        {"commander": "commander", "answer": "answer"},
    )
    graph.add_edge("commander", END)
    graph.add_edge("answer", END)
    return graph.compile()


def run_optimus(
    gemini: GeminiClient,
    message: str,
    canvas: CanvasState,
) -> tuple[list[CanvasCommand], str]:
    graph = build_optimus_graph(gemini)
    result = graph.invoke({"message": message, "canvas": canvas})
    return result.get("commands", []), result.get("reply", "")
