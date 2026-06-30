<script setup lang="ts">
import { computed } from 'vue';
import { Handle, Position as FlowPosition, type NodeProps } from '@vue-flow/core';
import type { PortDef, PortSide } from '@/schema';
import { symbolRegistry } from './symbols/symbolRegistry';
import type { EquipmentNodeData } from '@/stores/canvasStore';

const props = defineProps<NodeProps<EquipmentNodeData>>();

const SymbolComponent = computed(() => symbolRegistry[props.data.meta.symbol]);

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

const sizeStyle = computed(() => ({
  width: `${props.data.meta.size.width}px`,
  height: `${props.data.meta.size.height}px`,
  transform: props.data.rotation ? `rotate(${props.data.rotation}deg)` : undefined,
}));
</script>

<template>
  <div class="equipment-node" :class="{ selected: props.selected }">
    <div class="symbol-wrap" :style="sizeStyle" :title="data.meta.label">
      <component
        :is="SymbolComponent"
        :width="data.meta.size.width"
        :height="data.meta.size.height"
      />
    </div>

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
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #e5e7eb;
}
.symbol-wrap {
  display: grid;
  place-items: center;
  color: #cbd5e1;
  transition: color 0.12s ease;
}
.equipment-node.selected .symbol-wrap {
  color: #38bdf8;
}
.node-label {
  margin-top: 4px;
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
  white-space: nowrap;
}
.equipment-node.selected .node-label {
  color: #38bdf8;
}
:deep(.vue-flow__handle) {
  width: 8px;
  height: 8px;
  background: #475569;
  border: 1px solid #94a3b8;
}
:deep(.vue-flow__handle:hover) {
  background: #38bdf8;
}
</style>
