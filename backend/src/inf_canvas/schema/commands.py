"""Canvas Command protocol (Pydantic mirror of commands.ts).

A discriminated union on `op`; `command_adapter` validates raw dicts coming off
the wire into the correct member type.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, TypeAdapter

from .canvas import CanvasState, PipeData, Position
from .equipment import EquipmentType


class AddNodeCommand(BaseModel):
    op: Literal["add_node"]
    id: str
    equipment: EquipmentType
    position: Position
    label: str | None = None
    rotation: float | None = None
    data: dict[str, Any] | None = None


class UpdateNodePatch(BaseModel):
    label: str | None = None
    rotation: float | None = None
    data: dict[str, Any] | None = None


class UpdateNodeCommand(BaseModel):
    op: Literal["update_node"]
    id: str
    patch: UpdateNodePatch


class MoveNodeCommand(BaseModel):
    op: Literal["move_node"]
    id: str
    position: Position


class RemoveNodeCommand(BaseModel):
    op: Literal["remove_node"]
    id: str


class ConnectCommand(BaseModel):
    op: Literal["connect"]
    id: str
    source: str
    sourcePort: str
    target: str
    targetPort: str
    data: PipeData | None = None


class UpdateEdgeCommand(BaseModel):
    op: Literal["update_edge"]
    id: str
    patch: PipeData


class DisconnectCommand(BaseModel):
    op: Literal["disconnect"]
    id: str


class SelectCommand(BaseModel):
    op: Literal["select"]
    ids: list[str]


class ClearCommand(BaseModel):
    op: Literal["clear"]


class BatchCommand(BaseModel):
    op: Literal["batch"]
    commands: list[CanvasCommand]


CanvasCommand = Annotated[
    AddNodeCommand
    | UpdateNodeCommand
    | MoveNodeCommand
    | RemoveNodeCommand
    | ConnectCommand
    | UpdateEdgeCommand
    | DisconnectCommand
    | SelectCommand
    | ClearCommand
    | BatchCommand,
    Field(discriminator="op"),
]

BatchCommand.model_rebuild()

command_adapter: TypeAdapter[CanvasCommand] = TypeAdapter(CanvasCommand)

CommandSource = Literal[
    "user",
    "agent:optimus",
    "agent:pid_extractor",
    "agent:commander",
    "system",
]


class CommandMessage(BaseModel):
    type: Literal["command"] = "command"
    source: CommandSource
    command: CanvasCommand


class SnapshotMessage(BaseModel):
    type: Literal["snapshot"] = "snapshot"
    state: CanvasState


ServerMessage = CommandMessage | SnapshotMessage
