"""Optimus orchestrator graph (LangGraph).

route (classify intent) -> delegate to the Canvas Commander sub-graph, or answer
directly. The 'commander' node invokes the Commander graph, so this is a graph
delegating to another graph.
"""

from typing import Any

from langgraph.graph import END, START, StateGraph

from inf_canvas.ai.agents.canvas_commander.graph import run_commander
from inf_canvas.ai.models.gemini import GeminiClient
from inf_canvas.schema.canvas import CanvasState
from inf_canvas.schema.commands import CanvasCommand

from . import prompts
from .schemas import RouteDecision
from .states import OptimusState


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
    gemini: GeminiClient,
    message: str,
    canvas: CanvasState,
) -> tuple[list[CanvasCommand], str]:
    graph = build_optimus_graph(gemini)
    result = graph.invoke({"message": message, "canvas": canvas})
    return result.get("commands", []), result.get("reply", "")
