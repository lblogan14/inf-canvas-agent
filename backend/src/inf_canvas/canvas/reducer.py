"""Pure reducer over the Canvas Command protocol (mirror of reducer.ts).

`apply_command` returns a new CanvasState and never mutates its input.
"""

from ..schema.canvas import CanvasEdge, CanvasGroup, CanvasNode, CanvasState
from ..schema.commands import (
    AddGroupCommand,
    AddNodeCommand,
    BatchCommand,
    CanvasCommand,
    ClearCommand,
    ConnectCommand,
    DisconnectCommand,
    MoveNodeCommand,
    RemoveGroupCommand,
    RemoveNodeCommand,
    SelectCommand,
    UpdateEdgeCommand,
    UpdateGroupCommand,
    UpdateNodeCommand,
)


def apply_command(state: CanvasState, command: CanvasCommand) -> CanvasState:
    match command:
        case AddNodeCommand():
            if any(n.id == command.id for n in state.nodes):
                return state
            node = CanvasNode(
                id=command.id,
                type=command.equipment,
                position=command.position,
                label=command.label,
                rotation=command.rotation,
                data=command.data,
            )
            return state.model_copy(update={"nodes": [*state.nodes, node]})

        case UpdateNodeCommand():
            nodes = []
            for n in state.nodes:
                if n.id != command.id:
                    nodes.append(n)
                    continue
                patch = command.patch
                merged_data = n.data
                if patch.data is not None:
                    merged_data = {**(n.data or {}), **patch.data}
                nodes.append(
                    n.model_copy(
                        update={
                            "label": patch.label if patch.label is not None else n.label,
                            "rotation": patch.rotation
                            if patch.rotation is not None
                            else n.rotation,
                            "data": merged_data,
                        }
                    )
                )
            return state.model_copy(update={"nodes": nodes})

        case MoveNodeCommand():
            nodes = [
                n.model_copy(update={"position": command.position}) if n.id == command.id else n
                for n in state.nodes
            ]
            return state.model_copy(update={"nodes": nodes})

        case RemoveNodeCommand():
            return state.model_copy(
                update={
                    "nodes": [n for n in state.nodes if n.id != command.id],
                    "edges": [
                        e for e in state.edges if e.source != command.id and e.target != command.id
                    ],
                    "groups": [
                        g.model_copy(
                            update={"memberIds": [m for m in g.memberIds if m != command.id]}
                        )
                        for g in state.groups
                    ],
                }
            )

        case ConnectCommand():
            if any(e.id == command.id for e in state.edges):
                return state
            edge = CanvasEdge(
                id=command.id,
                source=command.source,
                sourcePort=command.sourcePort,
                target=command.target,
                targetPort=command.targetPort,
                data=command.data,
            )
            return state.model_copy(update={"edges": [*state.edges, edge]})

        case UpdateEdgeCommand():
            edges = [
                e.model_copy(update={"data": command.patch}) if e.id == command.id else e
                for e in state.edges
            ]
            return state.model_copy(update={"edges": edges})

        case DisconnectCommand():
            return state.model_copy(
                update={"edges": [e for e in state.edges if e.id != command.id]}
            )

        case ClearCommand():
            return state.model_copy(update={"nodes": [], "edges": [], "groups": []})

        case SelectCommand():
            # Selection is a client-side concern; no persisted change.
            return state

        case AddGroupCommand():
            if any(g.id == command.id for g in state.groups):
                return state
            group = CanvasGroup(
                id=command.id,
                label=command.label,
                position=command.position,
                width=command.width,
                height=command.height,
                memberIds=command.memberIds,
                color=command.color,
            )
            return state.model_copy(update={"groups": [*state.groups, group]})

        case UpdateGroupCommand():
            group_patch = {k: v for k, v in command.patch if v is not None}
            groups = [
                g.model_copy(update=group_patch) if g.id == command.id else g
                for g in state.groups
            ]
            return state.model_copy(update={"groups": groups})

        case RemoveGroupCommand():
            return state.model_copy(
                update={"groups": [g for g in state.groups if g.id != command.id]}
            )

        case BatchCommand():
            new_state = state
            for sub in command.commands:
                new_state = apply_command(new_state, sub)
            return new_state

    return state
