<script setup lang="ts">
import { computed, ref } from 'vue';
import {
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath,
  getStraightPath,
  useVueFlow,
  type EdgeProps,
} from '@vue-flow/core';
import type { PipeData, Position } from '@/schema';
import { useUiStore } from '@/stores/uiStore';
import { useCanvasStore } from '@/stores/canvasStore';

const props = defineProps<EdgeProps<PipeData>>();
const ui = useUiStore();
const store = useCanvasStore();
const { screenToFlowCoordinate } = useVueFlow('main');

// --- reroute waypoint dragging -----------------------------------------
const dragIndex = ref<number | null>(null);
const override = ref<Position | null>(null);

const waypoints = computed<Position[]>(() => {
  const wps = props.data?.waypoints ?? [];
  if (dragIndex.value === null || !override.value) return wps;
  return wps.map((w, i) => (i === dragIndex.value ? override.value! : w));
});

const path = computed<[string, number, number]>(() => {
  const wps = waypoints.value;
  if (wps.length) {
    const pts = [
      { x: props.sourceX, y: props.sourceY },
      ...wps,
      { x: props.targetX, y: props.targetY },
    ];
    const d = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x},${p.y}`).join(' ');
    const mid = pts[Math.floor(pts.length / 2)]!;
    return [d, mid.x, mid.y];
  }
  const common = {
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    sourcePosition: props.sourcePosition,
    targetX: props.targetX,
    targetY: props.targetY,
    targetPosition: props.targetPosition,
  };
  const result =
    ui.linkStyle === 'straight'
      ? getStraightPath(common)
      : getSmoothStepPath({ ...common, borderRadius: ui.linkStyle === 'step' ? 0 : 6 });
  return [result[0], result[1], result[2]];
});

function onMove(e: PointerEvent): void {
  if (dragIndex.value === null) return;
  override.value = screenToFlowCoordinate({ x: e.clientX, y: e.clientY });
}

function endDrag(): void {
  if (dragIndex.value !== null && override.value) {
    const wps = [...(props.data?.waypoints ?? [])];
    wps[dragIndex.value] = override.value;
    store.setWaypoints(props.id, wps);
  }
  dragIndex.value = null;
  override.value = null;
  window.removeEventListener('pointermove', onMove);
  window.removeEventListener('pointerup', endDrag);
}

function startDrag(index: number, e: PointerEvent): void {
  e.stopPropagation();
  dragIndex.value = index;
  override.value = null;
  window.addEventListener('pointermove', onMove);
  window.addEventListener('pointerup', endDrag);
}

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
      stroke: 'var(--edge)',
      strokeWidth: lineType === 'process' ? 2.5 : 1.5,
      strokeDasharray: dash,
    }"
    :marker-end="markerEnd"
  />
  <EdgeLabelRenderer>
    <div
      v-if="data?.label"
      class="pipe-label"
      :style="{ transform: `translate(-50%, -50%) translate(${path[1]}px, ${path[2]}px)` }"
    >
      {{ data.label }}
    </div>
    <!-- Reroute waypoint handles (drag to move, double-click to remove) -->
    <div
      v-for="(wp, i) in waypoints"
      :key="i"
      class="waypoint"
      :class="{ selected: selected }"
      :style="{ transform: `translate(-50%, -50%) translate(${wp.x}px, ${wp.y}px)` }"
      @pointerdown="startDrag(i, $event)"
      @dblclick.stop="store.removeWaypoint(id, i)"
    />
  </EdgeLabelRenderer>
</template>

<style scoped>
.pipe-label {
  position: absolute;
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 4px;
  background: var(--surface-3);
  color: var(--text);
  pointer-events: all;
}
.waypoint {
  position: absolute;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--surface);
  border: 1.5px solid var(--edge);
  pointer-events: all;
  cursor: grab;
}
.waypoint:hover,
.waypoint.selected {
  border-color: var(--accent);
}
.waypoint:active {
  cursor: grabbing;
}
</style>
