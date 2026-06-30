<script setup lang="ts">
import { computed, markRaw, ref, watch } from 'vue';
import {
  VueFlow,
  useVueFlow,
  type Connection,
  type EdgeMouseEvent,
  type NodeDragEvent,
  type NodeMouseEvent,
} from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { Controls } from '@vue-flow/controls';
import { MiniMap } from '@vue-flow/minimap';
import { isEquipmentType, type EquipmentType } from '@/schema';
import { useCanvasStore } from '@/stores/canvasStore';
import { useUiStore } from '@/stores/uiStore';
import { useTheme } from '@/composables/useTheme';
import EquipmentNode from './nodes/EquipmentNode.vue';
import PipeEdge from './edges/PipeEdge.vue';
import ContextMenu, { type MenuItem } from './ContextMenu.vue';
import SpotlightSearch from './SpotlightSearch.vue';

const store = useCanvasStore();
const ui = useUiStore();
const { theme } = useTheme();

const nodeTypes = { equipment: markRaw(EquipmentNode) };
const edgeTypes = { pipe: markRaw(PipeEdge) };

const gridColor = computed(() => (theme.value === 'dark' ? '#334155' : '#cbd5e1'));
const miniMask = computed(() =>
  theme.value === 'dark' ? 'rgba(15, 23, 42, 0.6)' : 'rgba(226, 232, 240, 0.6)',
);
const miniNodeColor = computed(() => (theme.value === 'dark' ? '#475569' : '#94a3b8'));

const {
  onConnect,
  onNodeDragStop,
  onPaneClick,
  setNodes,
  setEdges,
  fitView,
  screenToFlowCoordinate,
} = useVueFlow('main');

let prevNodeCount = 0;
watch(
  () => store.flowNodes,
  (nodes) => {
    setNodes(nodes);
    // Auto-frame when a batch of content first appears (extraction/import/paste),
    // not for single manual adds. maxZoom keeps it from zooming in too far.
    if (prevNodeCount === 0 && nodes.length > 2) {
      setTimeout(() => fitView({ padding: 0.2, maxZoom: 1.2 }), 200);
    }
    prevNodeCount = nodes.length;
  },
  { immediate: true, deep: false },
);
watch(
  () => store.flowEdges,
  (edges) => setEdges(edges),
  { immediate: true, deep: false },
);
watch(
  () => store.fitSignal,
  () => setTimeout(() => fitView({ padding: 0.2, maxZoom: 1.5 }), 60),
);

onConnect((params: Connection) => store.connect(params));

onNodeDragStop((e: NodeDragEvent) => {
  const moves = e.nodes.map((n) => ({ op: 'move_node' as const, id: n.id, position: n.position }));
  if (moves.length === 1) store.moveNode(moves[0]!.id, moves[0]!.position);
  else if (moves.length > 1) store.dispatch({ op: 'batch', commands: moves });
});

onPaneClick(() => store.setSelection([]));

function onNodeClick(e: NodeMouseEvent) {
  const additive = e.event.shiftKey || e.event.ctrlKey || e.event.metaKey;
  if (additive) {
    const ids = new Set(store.selectedIds);
    if (ids.has(e.node.id)) ids.delete(e.node.id);
    else ids.add(e.node.id);
    store.setSelection([...ids]);
  } else {
    store.setSelection([e.node.id]);
  }
}

function onEdgeClick(e: EdgeMouseEvent) {
  store.setSelection([e.edge.id]);
}

function onDrop(event: DragEvent) {
  const type = event.dataTransfer?.getData('application/inf-equipment');
  if (!type || !isEquipmentType(type)) return;
  store.addEquipment(type, screenToFlowCoordinate({ x: event.clientX, y: event.clientY }));
}

// --- spotlight (double-click to add) -----------------------------------
const spotlight = ref<{ x: number; y: number; pos: { x: number; y: number } } | null>(null);

function onDblClick(e: MouseEvent) {
  const el = e.target as HTMLElement;
  if (!el.classList.contains('vue-flow__pane')) return;
  spotlight.value = {
    x: e.clientX,
    y: e.clientY,
    pos: screenToFlowCoordinate({ x: e.clientX, y: e.clientY }),
  };
}

function onSpotlightSelect(type: EquipmentType) {
  if (spotlight.value) store.addEquipment(type, spotlight.value.pos);
  spotlight.value = null;
}

// --- context menus ------------------------------------------------------
const ctx = ref<{ x: number; y: number; items: MenuItem[] } | null>(null);

function rotate(id: string) {
  const n = store.state.nodes.find((x) => x.id === id);
  if (n) store.updateNode(id, { rotation: ((n.rotation ?? 0) + 90) % 360 });
}

function onPaneContextMenu(e: MouseEvent) {
  e.preventDefault();
  const pos = screenToFlowCoordinate({ x: e.clientX, y: e.clientY });
  ctx.value = {
    x: e.clientX,
    y: e.clientY,
    items: [
      {
        label: 'Add equipment…',
        action: () => (spotlight.value = { x: e.clientX, y: e.clientY, pos }),
      },
      { label: 'Paste', action: () => store.pasteAt(), disabled: !store.hasClipboard },
      { separator: true },
      { label: 'Select all', action: () => store.selectAll() },
      { label: 'Fit view', action: () => store.requestFit() },
      {
        label: 'Auto-layout',
        action: () => store.autoLayout(),
        disabled: !store.state.nodes.length,
      },
    ],
  };
}

function onNodeContextMenu(payload: NodeMouseEvent) {
  const ev = payload.event as MouseEvent;
  ev.preventDefault();
  if (!store.selectedIds.includes(payload.node.id)) store.setSelection([payload.node.id]);
  ctx.value = {
    x: ev.clientX,
    y: ev.clientY,
    items: [
      { label: 'Duplicate', action: () => store.duplicate() },
      { label: 'Copy', action: () => store.copy() },
      { label: 'Rotate 90°', action: () => rotate(payload.node.id) },
      { separator: true },
      { label: 'Delete', action: () => store.removeSelected(), danger: true },
    ],
  };
}

function onEdgeContextMenu(payload: EdgeMouseEvent) {
  const ev = payload.event as MouseEvent;
  ev.preventDefault();
  ctx.value = {
    x: ev.clientX,
    y: ev.clientY,
    items: [
      {
        label: 'Delete pipe',
        action: () => store.dispatch({ op: 'disconnect', id: payload.edge.id }),
        danger: true,
      },
    ],
  };
}
</script>

<template>
  <div class="canvas-host" @dblclick="onDblClick">
    <VueFlow
      id="main"
      :node-types="nodeTypes"
      :edge-types="edgeTypes"
      :delete-key-code="null"
      :min-zoom="0.1"
      :max-zoom="4"
      :snap-to-grid="ui.snapToGrid"
      :snap-grid="[20, 20]"
      :zoom-on-double-click="false"
      class="canvas"
      @node-click="onNodeClick"
      @edge-click="onEdgeClick"
      @drop="onDrop"
      @dragover.prevent
      @pane-context-menu="onPaneContextMenu"
      @node-context-menu="onNodeContextMenu"
      @edge-context-menu="onEdgeContextMenu"
    >
      <Background :gap="20" :pattern-color="gridColor" />
      <Controls />
      <MiniMap pannable zoomable :mask-color="miniMask" :node-color="miniNodeColor" />
    </VueFlow>

    <SpotlightSearch
      v-if="spotlight"
      :x="spotlight.x"
      :y="spotlight.y"
      @select="onSpotlightSelect"
      @close="spotlight = null"
    />
    <ContextMenu v-if="ctx" :x="ctx.x" :y="ctx.y" :items="ctx.items" @close="ctx = null" />
  </div>
</template>

<style scoped>
.canvas-host {
  width: 100%;
  height: 100%;
  position: relative;
}
.canvas {
  width: 100%;
  height: 100%;
  background: var(--bg);
}
:deep(.vue-flow__minimap) {
  background: var(--surface-3);
}
:deep(.vue-flow__controls-button) {
  background: var(--surface-3);
  border-bottom: 1px solid var(--border);
  fill: var(--text);
}
:deep(.vue-flow__controls-button:hover) {
  background: var(--surface);
}
:deep(.vue-flow__controls-button svg) {
  fill: var(--text);
}
</style>
