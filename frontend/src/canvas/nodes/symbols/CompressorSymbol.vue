<script setup lang="ts">
defineProps<{ width: number; height: number }>();
</script>

<template>
  <!-- ISA centrifugal compressor: circle with trapezoidal rotor. -->
  <svg :width="width" :height="height" viewBox="0 0 100 90" class="symbol">
    <circle cx="50" cy="45" r="36" />
    <polygon points="30,28 70,20 70,70 30,62" />
    <line x1="14" y1="45" x2="2" y2="45" />
    <line x1="86" y1="45" x2="98" y2="45" />
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
