<script setup lang="ts">
import type { EquipmentType } from '@/schema';

const props = defineProps<{ width: number; height: number; type?: EquipmentType }>();

const isControl = props.type === 'control_valve';
const isCheck = props.type === 'check_valve';
</script>

<template>
  <!-- ISA valve: bowtie (two triangles). Control valve adds an actuator. -->
  <svg :width="width" :height="height" viewBox="0 0 100 70" class="symbol">
    <line x1="2" y1="45" x2="98" y2="45" class="lead" />
    <polygon points="20,25 20,65 50,45" />
    <polygon points="80,25 80,65 50,45" />
    <!-- control valve diaphragm actuator -->
    <template v-if="isControl">
      <line x1="50" y1="45" x2="50" y2="16" />
      <path d="M34 16 Q50 2 66 16 Z" />
    </template>
    <!-- check valve seat ball -->
    <circle v-if="isCheck" cx="50" cy="45" r="6" class="ball" />
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
.symbol .ball {
  fill: currentColor;
}
</style>
