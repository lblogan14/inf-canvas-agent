"""Pydantic mirror of the shared canvas + command contract.

Keep these models in sync with `frontend/src/schema` (the TypeScript source
of truth). Field names use the same camelCase as the JSON wire format.
"""

from .canvas import (
    CanvasEdge,
    CanvasMeta,
    CanvasNode,
    CanvasState,
    LineType,
    PipeData,
    Position,
    empty_canvas,
)
from .commands import (
    AddNodeCommand,
    BatchCommand,
    CanvasCommand,
    ClearCommand,
    CommandMessage,
    CommandSource,
    ConnectCommand,
    DisconnectCommand,
    MoveNodeCommand,
    RemoveNodeCommand,
    SelectCommand,
    ServerMessage,
    SnapshotMessage,
    UpdateEdgeCommand,
    UpdateNodeCommand,
    command_adapter,
)
from .equipment import (
    EQUIPMENT_METADATA,
    EQUIPMENT_TYPES,
    EquipmentMeta,
    EquipmentType,
    PortDef,
)

__all__ = [
    "EQUIPMENT_METADATA",
    "EQUIPMENT_TYPES",
    "AddNodeCommand",
    "BatchCommand",
    "CanvasCommand",
    "CanvasEdge",
    "CanvasMeta",
    "CanvasNode",
    "CanvasState",
    "ClearCommand",
    "CommandMessage",
    "CommandSource",
    "ConnectCommand",
    "DisconnectCommand",
    "EquipmentMeta",
    "EquipmentType",
    "LineType",
    "MoveNodeCommand",
    "PipeData",
    "PortDef",
    "Position",
    "RemoveNodeCommand",
    "SelectCommand",
    "ServerMessage",
    "SnapshotMessage",
    "UpdateEdgeCommand",
    "UpdateNodeCommand",
    "command_adapter",
    "empty_canvas",
]
