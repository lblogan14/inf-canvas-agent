<script setup lang="ts">
defineProps<{ width: number; height: number }>();
</script>

<template>
  <!-- ISA shell & tube heat exchanger: shell rectangle with U-tube bundle. -->
  <svg
    :width="width"
    :height="height"
    viewBox="0 0 120 80"
    preserveAspectRatio="none"
    class="symbol"
  >
    <rect x="6" y="14" width="108" height="52" rx="6" />
    <path d="M6 30 H92 Q104 30 104 40 Q104 50 92 50 H6" class="tube" />
  </svg>
</template>

<style scoped>
.symbol {
  fill: color-mix(in srgb, currentColor 8%, transparent);
  stroke: currentColor;
  stroke-width: 3;
  stroke-linejoin: round;
}
.symbol .tube {
  fill: none;
  stroke-width: 2.5;
}
</style>
