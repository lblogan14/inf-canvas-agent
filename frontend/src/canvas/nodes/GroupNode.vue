<script setup lang="ts">
import type { NodeProps } from '@vue-flow/core';

const props = defineProps<NodeProps<{ label: string; color?: string }>>();
</script>

<template>
  <div
    class="group-node"
    :class="{ selected: props.selected }"
    :style="props.data.color ? { borderColor: props.data.color } : undefined"
  >
    <div class="group-title">{{ props.data.label }}</div>
  </div>
</template>

<style scoped>
.group-node {
  width: 100%;
  height: 100%;
  border: 1.5px dashed var(--text-faint);
  border-radius: 10px;
  background: color-mix(in srgb, var(--accent) 7%, transparent);
}
.group-node.selected {
  border-color: var(--accent);
  border-style: solid;
}
.group-title {
  position: absolute;
  top: 0;
  left: 10px;
  transform: translateY(-50%);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--surface);
  padding: 1px 6px;
  border-radius: 4px;
}
</style>
