<script setup lang="ts">
defineProps<{ width: number; height: number }>();
</script>

<template>
  <!-- ISA vessel / column: capsule (cylinder with rounded heads). -->
  <svg
    :width="width"
    :height="height"
    viewBox="0 0 100 160"
    preserveAspectRatio="none"
    class="symbol"
  >
    <path d="M14 30 Q14 6 50 6 Q86 6 86 30 L86 130 Q86 154 50 154 Q14 154 14 130 Z" />
  </svg>
</template>

<style scoped>
.symbol {
  fill: color-mix(in srgb, currentColor 8%, transparent);
  stroke: currentColor;
  stroke-width: 3;
  stroke-linejoin: round;
}
</style>
