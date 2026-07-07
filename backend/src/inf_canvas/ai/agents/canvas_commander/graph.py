"""Canvas Commander graph (LangGraph). plan -> compile -> self_check."""

from typing import Any

from langgraph.graph import END, START, StateGraph

from inf_canvas.ai.agents.shared import tools
from inf_canvas.ai.models.base import ModelClient
from inf_canvas.canvas.reducer import apply_command
from inf_canvas.canvas.validation import validate_canvas
from inf_canvas.schema.canvas import CanvasState
from inf_canvas.schema.commands import CanvasCommand, UpdateNodeCommand, UpdateNodePatch

from . import prompts
from .schemas import CommanderPlan, RepairPlan
from .states import CommanderState

NODE_LABELS = {
    "plan": "Planning the changes",
    "compile": "Compiling canvas actions",
    "self_check": "Self-checking the design",
}

# Issue kinds the repair pass can resolve by adding connections / tags.
_FIXABLE_KINDS = {"isolated", "orphan-instr", "nosuction", "nodischarge", "dangling"}


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

    def self_check(state: CommanderState) -> CommanderState:
        """Validate the design we just built and repair connection/tag issues.

        Only runs for generative plans (>= 2 new nodes) so simple edits stay
        fast. Applies the commands to a scratch state, validates, and asks the
        model for one round of fixes (added connections + tags)."""
        plan_obj = state["plan"]
        commands = list(state.get("commands", []))
        if len(plan_obj.add_nodes) < 2 or not commands:
            return {}

        scratch = state["canvas"]
        for cmd in commands:
            scratch = apply_command(scratch, cmd)

        issues = validate_canvas(scratch)
        fixable = [i for i in issues if i.id.split(":", 1)[0] in _FIXABLE_KINDS]
        if not fixable:
            return {}

        listing = "\n".join(
            f"- {n.id} ({n.type})"
            + (f" '{n.label}'" if n.label else "")
            + f" at ({int(n.position.x)},{int(n.position.y)})"
            for n in scratch.nodes
        )
        issue_text = "\n".join(f"- {i.title}" for i in fixable)
        prompt = (
            f"Nodes now on the canvas (use these ids):\n{listing}\n\n"
            f"Validation issues to fix:\n{issue_text}\n\n"
            "Propose connections (and tag fixes) that resolve these issues."
        )
        try:
            repair = model.generate_structured(
                role="flash",
                prompt=prompt,
                schema=RepairPlan,
                system=prompts.REPAIR_SYSTEM,
                temperature=0.2,
            )
        except Exception:
            return {}

        links = [
            tools.Link(from_ref=c.from_ref, to_ref=c.to_ref, line_type=c.line_type, label=c.label)
            for c in repair.connect
        ]
        repair_cmds, _ = tools.build_commands([], links, scratch)
        valid_ids = {n.id for n in scratch.nodes}
        for fix in repair.retag:
            if fix.node_id in valid_ids and fix.label.strip():
                repair_cmds.append(
                    UpdateNodeCommand(
                        op="update_node", id=fix.node_id, patch=UpdateNodePatch(label=fix.label)
                    )
                )
        if not repair_cmds:
            return {}

        added = sum(1 for c in repair_cmds if c.op == "connect")
        reply = state.get("reply") or plan_obj.reply
        reply = (
            f"{reply} Self-check resolved {len(fixable)} issue(s) by adding {added} connection(s)."
        )
        return {"commands": commands + repair_cmds, "reply": reply}

    return (
        StateGraph(CommanderState)
        .add_node("plan", plan)
        .add_node("compile", compile_plan)
        .add_node("self_check", self_check)
        .add_edge(START, "plan")
        .add_edge("plan", "compile")
        .add_edge("compile", "self_check")
        .add_edge("self_check", END)
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
