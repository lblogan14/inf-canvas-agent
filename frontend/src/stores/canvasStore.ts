import { computed, ref, shallowRef } from 'vue';
import { defineStore } from 'pinia';
import {
  applyCommand,
  emptyCanvas,
  getEquipmentMeta,
  type CanvasCommand,
  type CanvasState,
  type CommandMessage,
  type CommandSource,
  type EquipmentType,
  type Position,
} from '@/schema';
import type { Edge as FlowEdge, Node as FlowNode } from '@vue-flow/core';

/** Data attached to each Vue Flow node, consumed by EquipmentNode.vue. */
export interface EquipmentNodeData {
  type: EquipmentType;
  label: string | undefined;
  rotation: number;
  meta: ReturnType<typeof getEquipmentMeta>;
}

function uid(prefix: string): string {
  return `${prefix}_${crypto.randomUUID().slice(0, 8)}`;
}

export const useCanvasStore = defineStore('canvas', () => {
  const state = ref<CanvasState>(emptyCanvas(uid('cv'), 'Untitled'));
  const selectedIds = ref<string[]>([]);

  /**
   * Set by the realtime layer (realtime/ws.ts). Local user commands are pushed
   * here so the backend stays in sync; null when offline.
   */
  const outbound = shallowRef<((msg: CommandMessage) => void) | null>(null);

  const flowNodes = computed<FlowNode<EquipmentNodeData>[]>(() =>
    state.value.nodes.map((n) => ({
      id: n.id,
      type: 'equipment',
      position: n.position,
      selected: selectedIds.value.includes(n.id),
      data: {
        type: n.type,
        label: n.label,
        rotation: n.rotation ?? 0,
        meta: getEquipmentMeta(n.type),
      },
    })),
  );

  const flowEdges = computed<FlowEdge[]>(() =>
    state.value.edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      sourceHandle: e.sourcePort,
      targetHandle: e.targetPort,
      type: 'pipe',
      data: e.data,
      animated: e.data?.animated ?? false,
    })),
  );

  /** Core entry point. `emit` controls whether the command is sent to backend. */
  function dispatch(command: CanvasCommand, source: CommandSource = 'user', emit = true): void {
    if (command.op === 'select') {
      // Selection is a client-local concern; never sent over the wire.
      selectedIds.value = command.ids;
      return;
    }
    state.value = applyCommand(state.value, command);
    state.value.meta.updatedAt = new Date().toISOString();
    if (emit && outbound.value) {
      outbound.value({ type: 'command', source, command });
    }
  }

  /** Apply a command received from the backend (no echo back). */
  function applyRemote(message: CommandMessage): void {
    dispatch(message.command, message.source, false);
  }

  // --- Convenience actions used by the UI --------------------------------

  function addEquipment(equipment: EquipmentType, position: Position, label?: string): string {
    const id = uid('n');
    dispatch({ op: 'add_node', id, equipment, position, ...(label ? { label } : {}) });
    return id;
  }

  function connect(params: {
    source: string;
    target: string;
    sourceHandle?: string | null;
    targetHandle?: string | null;
  }): void {
    if (!params.sourceHandle || !params.targetHandle) return;
    dispatch({
      op: 'connect',
      id: uid('e'),
      source: params.source,
      sourcePort: params.sourceHandle,
      target: params.target,
      targetPort: params.targetHandle,
      data: { lineType: 'process' },
    });
  }

  function moveNode(id: string, position: Position): void {
    dispatch({ op: 'move_node', id, position });
  }

  function updateNode(id: string, patch: { label?: string; rotation?: number }): void {
    dispatch({ op: 'update_node', id, patch });
  }

  function removeNode(id: string): void {
    dispatch({ op: 'remove_node', id });
  }

  function removeSelected(): void {
    const ids = [...selectedIds.value];
    selectedIds.value = [];
    for (const id of ids) {
      if (state.value.nodes.some((n) => n.id === id)) dispatch({ op: 'remove_node', id });
      else dispatch({ op: 'disconnect', id });
    }
  }

  function setSelection(ids: string[]): void {
    selectedIds.value = ids;
  }

  function loadState(next: CanvasState): void {
    state.value = next;
    selectedIds.value = [];
  }

  function newCanvas(name = 'Untitled'): void {
    loadState(emptyCanvas(uid('cv'), name));
  }

  const selectedNode = computed(() =>
    selectedIds.value.length === 1
      ? (state.value.nodes.find((n) => n.id === selectedIds.value[0]) ?? null)
      : null,
  );

  return {
    state,
    selectedIds,
    selectedNode,
    outbound,
    flowNodes,
    flowEdges,
    dispatch,
    applyRemote,
    addEquipment,
    connect,
    moveNode,
    updateNode,
    removeNode,
    removeSelected,
    setSelection,
    loadState,
    newCanvas,
  };
});
