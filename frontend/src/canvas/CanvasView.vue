<script setup lang="ts">
import { markRaw } from 'vue';
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
import { useCanvasStore } from '@/stores/canvasStore';
import EquipmentNode from './nodes/EquipmentNode.vue';
import PipeEdge from './edges/PipeEdge.vue';

const store = useCanvasStore();

const nodeTypes = { equipment: markRaw(EquipmentNode) };
const edgeTypes = { pipe: markRaw(PipeEdge) };

const { onConnect, onNodeDragStop, onPaneClick } = useVueFlow();

onConnect((params: Connection) => store.connect(params));

onNodeDragStop((e: NodeDragEvent) => {
  for (const node of e.nodes) {
    store.moveNode(node.id, node.position);
  }
});

onPaneClick(() => store.setSelection([]));

function onNodeClick(e: NodeMouseEvent) {
  store.setSelection([e.node.id]);
}

function onEdgeClick(e: EdgeMouseEvent) {
  store.setSelection([e.edge.id]);
}
</script>

<template>
  <VueFlow
    :nodes="store.flowNodes"
    :edges="store.flowEdges"
    :node-types="nodeTypes"
    :edge-types="edgeTypes"
    :delete-key-code="null"
    :min-zoom="0.1"
    :max-zoom="4"
    fit-view-on-init
    class="canvas"
    @node-click="onNodeClick"
    @edge-click="onEdgeClick"
  >
    <Background :gap="20" pattern-color="#334155" />
    <Controls />
    <MiniMap pannable zoomable />
  </VueFlow>
</template>

<style scoped>
.canvas {
  width: 100%;
  height: 100%;
  background: #0f172a;
}
:deep(.vue-flow__minimap) {
  background: #1e293b;
}
</style>
