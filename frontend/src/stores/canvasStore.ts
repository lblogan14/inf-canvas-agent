import { computed, ref, shallowRef, watch } from 'vue';
import { defineStore } from 'pinia';
import {
  applyCommand,
  emptyCanvas,
  getEquipmentMeta,
  type CanvasCommand,
  type CanvasEdge,
  type CanvasNode,
  type CanvasState,
  type CommandMessage,
  type CommandSource,
  type EquipmentType,
  type Position,
} from '@/schema';
import type { Edge as FlowEdge, Node as FlowNode } from '@vue-flow/core';
import { computeAutoLayout } from '@/canvas/layout';
import { api } from '@/api/client';

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

const ACTIVE_KEY = 'inf-canvas-active';

function initialCanvasId(): string {
  return localStorage.getItem(ACTIVE_KEY) ?? uid('cv');
}

export const useCanvasStore = defineStore('canvas', () => {
  const state = ref<CanvasState>(emptyCanvas(initialCanvasId(), 'Untitled'));
  const selectedIds = ref<string[]>([]);
  /** Bumped to ask the canvas to re-frame (fitView). */
  const fitSignal = ref(0);

  // Remember the active canvas so a reload reopens it (backend sends the saved
  // snapshot when the WS connects to this id).
  watch(
    () => state.value.meta.id,
    (id) => localStorage.setItem(ACTIVE_KEY, id),
    { immediate: true },
  );

  // --- undo/redo history --------------------------------------------------
  const undoStack = ref<CanvasState[]>([]);
  const redoStack = ref<CanvasState[]>([]);
  const canUndo = computed(() => undoStack.value.length > 0);
  const canRedo = computed(() => redoStack.value.length > 0);

  function clone(s: CanvasState): CanvasState {
    return JSON.parse(JSON.stringify(s)) as CanvasState;
  }

  function pushHistory(): void {
    undoStack.value.push(clone(state.value));
    if (undoStack.value.length > 100) undoStack.value.shift();
    redoStack.value = [];
  }

  // --- clipboard ----------------------------------------------------------
  const clipboard = ref<{ nodes: CanvasNode[]; edges: CanvasEdge[] } | null>(null);

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
    pushHistory();
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
    if (!ids.length) return;
    selectedIds.value = [];
    const commands: CanvasCommand[] = ids.map((id) =>
      state.value.nodes.some((n) => n.id === id)
        ? { op: 'remove_node', id }
        : { op: 'disconnect', id },
    );
    dispatch({ op: 'batch', commands });
  }

  function setSelection(ids: string[]): void {
    selectedIds.value = ids;
  }

  function requestFit(): void {
    fitSignal.value += 1;
  }

  /** Re-arrange the whole graph with a left-to-right dagre layout. */
  function autoLayout(): void {
    const moves = computeAutoLayout(state.value.nodes, state.value.edges);
    if (!moves.length) return;
    dispatch({
      op: 'batch',
      commands: moves.map((m) => ({ op: 'move_node', id: m.id, position: { x: m.x, y: m.y } })),
    });
    requestFit();
  }

  // --- history actions ----------------------------------------------------
  // Undo/redo restore a full snapshot locally, then PUT it so the backend
  // (authoritative state + persistence) stays in sync.
  function persistFull(): void {
    void api.saveProject(state.value).catch(() => {});
  }

  function undo(): void {
    if (!undoStack.value.length) return;
    redoStack.value.push(clone(state.value));
    state.value = undoStack.value.pop()!;
    selectedIds.value = [];
    persistFull();
  }

  function redo(): void {
    if (!redoStack.value.length) return;
    undoStack.value.push(clone(state.value));
    state.value = redoStack.value.pop()!;
    selectedIds.value = [];
    persistFull();
  }

  // --- clipboard actions --------------------------------------------------
  function copy(): void {
    const ids = new Set(selectedIds.value);
    const nodes = state.value.nodes.filter((n) => ids.has(n.id));
    if (!nodes.length) return;
    const nodeIds = new Set(nodes.map((n) => n.id));
    const edges = state.value.edges.filter((e) => nodeIds.has(e.source) && nodeIds.has(e.target));
    clipboard.value = {
      nodes: JSON.parse(JSON.stringify(nodes)) as CanvasNode[],
      edges: JSON.parse(JSON.stringify(edges)) as CanvasEdge[],
    };
  }

  function pasteAt(offset: Position = { x: 40, y: 40 }): void {
    const clip = clipboard.value;
    if (!clip || !clip.nodes.length) return;
    const idMap = new Map<string, string>();
    const commands: CanvasCommand[] = [];
    for (const n of clip.nodes) {
      const newId = uid('n');
      idMap.set(n.id, newId);
      commands.push({
        op: 'add_node',
        id: newId,
        equipment: n.type,
        position: { x: n.position.x + offset.x, y: n.position.y + offset.y },
        ...(n.label ? { label: n.label } : {}),
        ...(n.rotation !== undefined ? { rotation: n.rotation } : {}),
        ...(n.data ? { data: n.data } : {}),
      });
    }
    for (const e of clip.edges) {
      const src = idMap.get(e.source);
      const tgt = idMap.get(e.target);
      if (!src || !tgt) continue;
      commands.push({
        op: 'connect',
        id: uid('e'),
        source: src,
        sourcePort: e.sourcePort,
        target: tgt,
        targetPort: e.targetPort,
        ...(e.data ? { data: e.data } : {}),
      });
    }
    dispatch({ op: 'batch', commands });
    selectedIds.value = [...idMap.values()];
  }

  function duplicate(): void {
    copy();
    pasteAt({ x: 40, y: 40 });
  }

  function selectAll(): void {
    selectedIds.value = state.value.nodes.map((n) => n.id);
  }

  const hasClipboard = computed(() => !!clipboard.value?.nodes.length);

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
    fitSignal,
    flowNodes,
    flowEdges,
    canUndo,
    canRedo,
    hasClipboard,
    dispatch,
    applyRemote,
    addEquipment,
    connect,
    moveNode,
    updateNode,
    removeNode,
    removeSelected,
    setSelection,
    requestFit,
    autoLayout,
    undo,
    redo,
    copy,
    pasteAt,
    duplicate,
    selectAll,
    loadState,
    newCanvas,
  };
});
