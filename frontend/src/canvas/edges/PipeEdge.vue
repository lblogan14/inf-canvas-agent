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
import { lineStyle } from './lineStyles';

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

/** Insert corner points so every segment is horizontal or vertical (Manhattan).
 *  The exit/entry direction follows the source/target port side. */
function orthogonalize(pts: Position[], srcSide: string, tgtSide: string): Position[] {
  const out: Position[] = [pts[0]!];
  for (let i = 1; i < pts.length; i++) {
    const prev = out[out.length - 1]!;
    const cur = pts[i]!;
    if (prev.x === cur.x || prev.y === cur.y) {
      out.push(cur);
      continue;
    }
    let horizFirst: boolean;
    if (i === 1) {
      horizFirst = srcSide === 'left' || srcSide === 'right';
    } else if (i === pts.length - 1) {
      // Approach the target from its port side: enter horizontally for
      // left/right ports (so the last segment is horizontal → turn vertically first).
      horizFirst = !(tgtSide === 'left' || tgtSide === 'right');
    } else {
      horizFirst = Math.abs(cur.x - prev.x) >= Math.abs(cur.y - prev.y);
    }
    out.push(horizFirst ? { x: cur.x, y: prev.y } : { x: prev.x, y: cur.y });
    out.push(cur);
  }
  // Drop consecutive duplicates.
  return out.filter((p, i) => i === 0 || p.x !== out[i - 1]!.x || p.y !== out[i - 1]!.y);
}

/** SVG path through points, with rounded corners of `radius` (0 = sharp). */
function polyPath(points: Position[], radius: number): string {
  if (points.length < 2) return '';
  if (radius <= 0) {
    return points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x},${p.y}`).join(' ');
  }
  let d = `M ${points[0]!.x},${points[0]!.y}`;
  for (let i = 1; i < points.length - 1; i++) {
    const p = points[i - 1]!;
    const c = points[i]!;
    const n = points[i + 1]!;
    const d1 = Math.min(radius, Math.hypot(c.x - p.x, c.y - p.y) / 2);
    const d2 = Math.min(radius, Math.hypot(n.x - c.x, n.y - c.y) / 2);
    const a = { x: c.x - Math.sign(c.x - p.x) * d1, y: c.y - Math.sign(c.y - p.y) * d1 };
    const b = { x: c.x + Math.sign(n.x - c.x) * d2, y: c.y + Math.sign(n.y - c.y) * d2 };
    d += ` L ${a.x},${a.y} Q ${c.x},${c.y} ${b.x},${b.y}`;
  }
  const last = points[points.length - 1]!;
  d += ` L ${last.x},${last.y}`;
  return d;
}

const path = computed<[string, number, number]>(() => {
  const wps = waypoints.value;
  if (wps.length) {
    const raw = [
      { x: props.sourceX, y: props.sourceY },
      ...wps,
      { x: props.targetX, y: props.targetY },
    ];
    // 'straight' keeps the direct polyline; smoothstep/step are strictly H/V.
    const pts =
      ui.linkStyle === 'straight'
        ? raw
        : orthogonalize(raw, String(props.sourcePosition), String(props.targetPosition));
    const radius = ui.linkStyle === 'smoothstep' ? 8 : 0;
    const d = ui.linkStyle === 'straight' ? polyPath(pts, 0) : polyPath(pts, radius);
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

const style = computed(() => lineStyle(props.data?.lineType));
</script>

<template>
  <BaseEdge
    :id="id"
    :path="path[0]"
    :style="{
      stroke: 'var(--edge)',
      strokeWidth: style.width,
      strokeDasharray: style.dash,
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
    <!-- Reroute waypoint handles (only when selected; drag to move,
         double-click to remove) -->
    <template v-if="selected">
      <div
        v-for="(wp, i) in waypoints"
        :key="i"
        class="waypoint selected"
        :style="{ transform: `translate(-50%, -50%) translate(${wp.x}px, ${wp.y}px)` }"
        @pointerdown="startDrag(i, $event)"
        @dblclick.stop="store.removeWaypoint(id, i)"
      />
    </template>
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
