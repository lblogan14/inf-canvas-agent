<script setup lang="ts">
import { computed } from 'vue';
import { BaseEdge, EdgeLabelRenderer, getSmoothStepPath, type EdgeProps } from '@vue-flow/core';
import type { PipeData } from '@/schema';

const props = defineProps<EdgeProps<PipeData>>();

const path = computed(() =>
  getSmoothStepPath({
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    sourcePosition: props.sourcePosition,
    targetX: props.targetX,
    targetY: props.targetY,
    targetPosition: props.targetPosition,
    borderRadius: 4,
  }),
);

const lineType = computed(() => props.data?.lineType ?? 'process');
const dash = computed(() =>
  lineType.value === 'signal' || lineType.value === 'pneumatic' ? '6 4' : undefined,
);
</script>

<template>
  <BaseEdge
    :id="id"
    :path="path[0]"
    :style="{
      stroke: '#94a3b8',
      strokeWidth: lineType === 'process' ? 2.5 : 1.5,
      strokeDasharray: dash,
    }"
    :marker-end="markerEnd"
  />
  <EdgeLabelRenderer v-if="data?.label">
    <div
      class="pipe-label"
      :style="{ transform: `translate(-50%, -50%) translate(${path[1]}px, ${path[2]}px)` }"
    >
      {{ data.label }}
    </div>
  </EdgeLabelRenderer>
</template>

<style scoped>
.pipe-label {
  position: absolute;
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 4px;
  background: #1e293b;
  color: #cbd5e1;
  pointer-events: all;
}
</style>
