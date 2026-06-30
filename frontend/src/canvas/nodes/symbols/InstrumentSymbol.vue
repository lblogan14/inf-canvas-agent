<script setup lang="ts">
defineProps<{ width: number; height: number; tag?: string }>();
</script>

<template>
  <!-- ISA instrument bubble: circle with a dividing line; tag inside. -->
  <svg :width="width" :height="height" viewBox="0 0 56 56" class="symbol">
    <circle cx="28" cy="28" r="25" />
    <line x1="3" y1="28" x2="53" y2="28" class="divider" />
    <text v-if="tag" x="28" y="22" class="tag">{{ tag }}</text>
  </svg>
</template>

<style scoped>
.symbol {
  fill: none;
  stroke: currentColor;
  stroke-width: 2.5;
}
.symbol .divider {
  stroke-width: 1.5;
}
.symbol .tag {
  fill: currentColor;
  stroke: none;
  font-size: 11px;
  font-weight: 600;
  text-anchor: middle;
}
</style>
