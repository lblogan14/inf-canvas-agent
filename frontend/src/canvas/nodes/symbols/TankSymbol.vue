<script setup lang="ts">
defineProps<{ width: number; height: number }>();
</script>

<template>
  <!-- ISA atmospheric storage tank: flat-top cylinder. -->
  <svg
    :width="width"
    :height="height"
    viewBox="0 0 140 120"
    preserveAspectRatio="none"
    class="symbol"
  >
    <rect x="10" y="14" width="120" height="96" rx="4" />
    <ellipse cx="70" cy="14" rx="60" ry="9" class="lid" />
  </svg>
</template>

<style scoped>
.symbol {
  fill: color-mix(in srgb, currentColor 8%, transparent);
  stroke: currentColor;
  stroke-width: 3;
  stroke-linejoin: round;
}
.symbol .lid {
  fill: color-mix(in srgb, currentColor 16%, transparent);
}
</style>
