/**
 * The Canvas Command protocol — the single mutation API for the canvas.
 *
 * Toolbar clicks, the Canvas Commander agent, and the P&ID Extractor all
 * produce these same commands. The frontend store and the backend command bus
 * each implement an `apply(state, command)` reducer over this union, so AI and
 * humans share one authoritative state model.
 */

import type { CanvasNode, CanvasState, PipeData, Position } from './canvas';
import type { EquipmentType } from './equipment';

export interface AddNodeCommand {
  op: 'add_node';
  id: string;
  equipment: EquipmentType;
  position: Position;
  label?: string;
  rotation?: number;
  data?: Record<string, unknown>;
}

export interface UpdateNodeCommand {
  op: 'update_node';
  id: string;
  patch: Partial<Pick<CanvasNode, 'label' | 'rotation' | 'data'>>;
}

export interface MoveNodeCommand {
  op: 'move_node';
  id: string;
  position: Position;
}

export interface RemoveNodeCommand {
  op: 'remove_node';
  id: string;
}

export interface ConnectCommand {
  op: 'connect';
  id: string;
  source: string;
  sourcePort: string;
  target: string;
  targetPort: string;
  data?: PipeData;
}

export interface UpdateEdgeCommand {
  op: 'update_edge';
  id: string;
  patch: Partial<PipeData>;
}

export interface DisconnectCommand {
  op: 'disconnect';
  id: string;
}

export interface SelectCommand {
  op: 'select';
  ids: string[];
}

export interface ClearCommand {
  op: 'clear';
}

/** Atomic group — applied all-or-nothing. Used by the P&ID Extractor. */
export interface BatchCommand {
  op: 'batch';
  commands: CanvasCommand[];
}

export type CanvasCommand =
  | AddNodeCommand
  | UpdateNodeCommand
  | MoveNodeCommand
  | RemoveNodeCommand
  | ConnectCommand
  | UpdateEdgeCommand
  | DisconnectCommand
  | SelectCommand
  | ClearCommand
  | BatchCommand;

export type CommandOp = CanvasCommand['op'];

/** Who issued a command — used for UI attribution and logging. */
export type CommandSource =
  'user' | 'agent:optimus' | 'agent:pid_extractor' | 'agent:commander' | 'system';

/** WebSocket message envelopes (server <-> client). */
export interface CommandMessage {
  type: 'command';
  source: CommandSource;
  command: CanvasCommand;
}

export interface SnapshotMessage {
  type: 'snapshot';
  state: CanvasState;
}

export type ServerMessage = CommandMessage | SnapshotMessage;
export type ClientMessage = CommandMessage;
