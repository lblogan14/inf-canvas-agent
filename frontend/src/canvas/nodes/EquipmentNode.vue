<script setup lang="ts">
import { computed } from 'vue';
import { Handle, Position as FlowPosition, type NodeProps } from '@vue-flow/core';
import type { PortDef, PortSide } from '@/schema';
import { symbolRegistry } from './symbols/symbolRegistry';
import type { EquipmentNodeData } from '@/stores/canvasStore';

const props = defineProps<NodeProps<EquipmentNodeData>>();

const symbolSvg = computed(() => symbolRegistry[props.data.meta.symbol]);

const sideToPosition: Record<PortSide, FlowPosition> = {
  top: FlowPosition.Top,
  right: FlowPosition.Right,
  bottom: FlowPosition.Bottom,
  left: FlowPosition.Left,
};

/** Distribute multiple handles evenly along their shared side. */
function handleStyle(port: PortDef): Record<string, string> {
  const sameSide = props.data.meta.ports.filter((p) => p.side === port.side);
  const index = sameSide.indexOf(port);
  const pct = ((index + 1) / (sameSide.length + 1)) * 100;
  return port.side === 'top' || port.side === 'bottom' ? { left: `${pct}%` } : { top: `${pct}%` };
}

// The node box equals the SYMBOL box so Vue Flow anchors handles (and thus edge
// endpoints) on the symbol perimeter. The label is floated below and excluded
// from the box.
const rootStyle = computed(() => ({
  width: `${props.data.meta.size.width}px`,
  height: `${props.data.meta.size.height}px`,
}));
const symbolStyle = computed(() => ({
  transform: props.data.rotation ? `rotate(${props.data.rotation}deg)` : undefined,
}));
</script>

<template>
  <div class="equipment-node" :class="{ selected: props.selected }" :style="rootStyle">
    <!-- eslint-disable-next-line vue/no-v-html -- trusted first-party SVG assets -->
    <div class="symbol-wrap" :style="symbolStyle" :title="data.meta.label" v-html="symbolSvg" />

    <div v-if="data.label" class="node-label">{{ data.label }}</div>

    <!-- Each port exposes both a source and target handle so any port can be
         either end of a connection. -->
    <template v-for="port in data.meta.ports" :key="port.id">
      <Handle
        :id="port.id"
        type="source"
        :position="sideToPosition[port.side]"
        :style="handleStyle(port)"
        :title="port.label ?? port.id"
      />
      <Handle
        :id="port.id"
        type="target"
        :position="sideToPosition[port.side]"
        :style="handleStyle(port)"
      />
    </template>
  </div>
</template>

<style scoped>
.equipment-node {
  position: relative;
  color: var(--text);
}
.symbol-wrap {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: var(--node-stroke);
  transition: color 0.12s ease;
}
.symbol-wrap :deep(svg) {
  width: 100%;
  height: 100%;
  display: block;
}
.equipment-node.selected .symbol-wrap {
  color: var(--accent);
}
.node-label {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--node-label);
  white-space: nowrap;
  pointer-events: none;
}
.equipment-node.selected .node-label {
  color: var(--accent);
}
:deep(.vue-flow__handle) {
  width: 8px;
  height: 8px;
  background: var(--handle);
  border: 1px solid var(--handle-border);
}
:deep(.vue-flow__handle:hover) {
  background: var(--accent);
}
</style>
