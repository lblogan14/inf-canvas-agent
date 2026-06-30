/**
 * Pure reducer over the Canvas Command protocol.
 *
 * `applyCommand` returns a NEW CanvasState (never mutates its input), which
 * keeps it trivially testable and CRDT-friendly later. The backend mirrors this
 * logic in Python; keep the two in sync.
 */

import type { CanvasEdge, CanvasGroup, CanvasNode, CanvasState } from './canvas';
import type { CanvasCommand } from './commands';

function replaceNode(
  nodes: CanvasNode[],
  id: string,
  fn: (n: CanvasNode) => CanvasNode,
): CanvasNode[] {
  return nodes.map((n) => (n.id === id ? fn(n) : n));
}

export function applyCommand(state: CanvasState, command: CanvasCommand): CanvasState {
  switch (command.op) {
    case 'add_node': {
      if (state.nodes.some((n) => n.id === command.id)) return state;
      const node: CanvasNode = {
        id: command.id,
        type: command.equipment,
        position: command.position,
        ...(command.label !== undefined ? { label: command.label } : {}),
        ...(command.rotation !== undefined ? { rotation: command.rotation } : {}),
        ...(command.data !== undefined ? { data: command.data } : {}),
      };
      return { ...state, nodes: [...state.nodes, node] };
    }

    case 'update_node': {
      return {
        ...state,
        nodes: replaceNode(state.nodes, command.id, (n) => ({
          ...n,
          ...(command.patch.label !== undefined ? { label: command.patch.label } : {}),
          ...(command.patch.rotation !== undefined ? { rotation: command.patch.rotation } : {}),
          ...(command.patch.data !== undefined
            ? { data: { ...n.data, ...command.patch.data } }
            : {}),
        })),
      };
    }

    case 'move_node': {
      return {
        ...state,
        nodes: replaceNode(state.nodes, command.id, (n) => ({ ...n, position: command.position })),
      };
    }

    case 'remove_node': {
      return {
        ...state,
        nodes: state.nodes.filter((n) => n.id !== command.id),
        edges: state.edges.filter((e) => e.source !== command.id && e.target !== command.id),
        groups: state.groups.map((g) => ({
          ...g,
          memberIds: g.memberIds.filter((mid) => mid !== command.id),
        })),
      };
    }

    case 'connect': {
      if (state.edges.some((e) => e.id === command.id)) return state;
      const edge: CanvasEdge = {
        id: command.id,
        source: command.source,
        sourcePort: command.sourcePort,
        target: command.target,
        targetPort: command.targetPort,
        ...(command.data !== undefined ? { data: command.data } : {}),
      };
      return { ...state, edges: [...state.edges, edge] };
    }

    case 'update_edge': {
      return {
        ...state,
        edges: state.edges.map((e) =>
          e.id === command.id ? { ...e, data: { ...e.data, ...command.patch } } : e,
        ),
      };
    }

    case 'disconnect': {
      return { ...state, edges: state.edges.filter((e) => e.id !== command.id) };
    }

    case 'select':
    case 'clear': {
      // `select` is a transient UI concern handled by the store; `clear` is
      // handled where a fresh canvas is needed. Neither mutates persisted graph
      // data here.
      if (command.op === 'clear') {
        return { ...state, nodes: [], edges: [], groups: [] };
      }
      return state;
    }

    case 'add_group': {
      if (state.groups.some((g) => g.id === command.id)) return state;
      const group: CanvasGroup = {
        id: command.id,
        label: command.label,
        position: command.position,
        width: command.width,
        height: command.height,
        memberIds: command.memberIds,
        ...(command.color !== undefined ? { color: command.color } : {}),
      };
      return { ...state, groups: [...state.groups, group] };
    }

    case 'update_group': {
      return {
        ...state,
        groups: state.groups.map((g) =>
          g.id === command.id ? { ...g, ...command.patch } : g,
        ),
      };
    }

    case 'remove_group': {
      return { ...state, groups: state.groups.filter((g) => g.id !== command.id) };
    }

    case 'batch': {
      return command.commands.reduce(applyCommand, state);
    }

    default: {
      // Exhaustiveness guard — a new command op without a case fails the build.
      const _exhaustive: never = command;
      return _exhaustive;
    }
  }
}
