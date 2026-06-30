<script setup lang="ts">
defineProps<{ width: number; height: number }>();
</script>

<template>
  <!-- ISA centrifugal pump: circle (casing) with volute triangle. -->
  <svg :width="width" :height="height" viewBox="0 0 100 100" class="symbol">
    <circle cx="50" cy="55" r="34" />
    <polygon points="50,21 78,21 50,55" />
    <line x1="16" y1="55" x2="2" y2="55" />
    <line x1="50" y1="21" x2="50" y2="6" />
  </svg>
</template>

<style scoped>
.symbol {
  fill: none;
  stroke: currentColor;
  stroke-width: 3;
  stroke-linejoin: round;
}
.symbol polygon {
  fill: color-mix(in srgb, currentColor 12%, transparent);
}
</style>
