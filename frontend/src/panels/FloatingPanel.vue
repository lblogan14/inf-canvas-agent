<script setup lang="ts">
const x = defineModel<number>('x', { required: true });
const y = defineModel<number>('y', { required: true });
const w = defineModel<number>('w', { required: true });
const h = defineModel<number>('h', { required: true });
const minimized = defineModel<boolean>('minimized', { default: false });

defineProps<{ title: string; icon?: string }>();
const emit = defineEmits<{ close: [] }>();

let mode: 'drag' | 'resize' | null = null;
let startX = 0;
let startY = 0;
let originX = 0;
let originY = 0;
let originW = 0;
let originH = 0;
let moved = false;

function onMove(e: PointerEvent): void {
  if (!mode) return;
  const dx = e.clientX - startX;
  const dy = e.clientY - startY;
  if (Math.abs(dx) > 3 || Math.abs(dy) > 3) moved = true;
  if (mode === 'drag') {
    x.value = Math.max(0, originX + dx);
    y.value = Math.max(48, originY + dy);
  } else {
    w.value = Math.max(280, originW + dx);
    h.value = Math.max(200, originH + dy);
  }
}

function stop(): void {
  mode = null;
  window.removeEventListener('pointermove', onMove);
  window.removeEventListener('pointerup', stop);
}

function start(e: PointerEvent, m: 'drag' | 'resize'): void {
  mode = m;
  moved = false;
  startX = e.clientX;
  startY = e.clientY;
  originX = x.value;
  originY = y.value;
  originW = w.value;
  originH = h.value;
  window.addEventListener('pointermove', onMove);
  window.addEventListener('pointerup', stop);
}

function expand(): void {
  // Reposition so the full panel stays inside the viewport (a bubble parked at
  // an edge would otherwise open partly off-screen).
  const margin = 8;
  const maxX = Math.max(0, window.innerWidth - w.value - margin);
  const maxY = Math.max(48, window.innerHeight - h.value - margin);
  x.value = Math.min(Math.max(margin, x.value), maxX);
  y.value = Math.min(Math.max(48, y.value), maxY);
  minimized.value = false;
}

function onBubbleClick(): void {
  // Ignore the click that ends a drag; only a real tap expands.
  if (!moved) expand();
}
</script>

<template>
  <!-- Minimized: a small draggable round bubble -->
  <button
    v-if="minimized"
    class="fp-bubble"
    :style="{ left: `${x}px`, top: `${y}px` }"
    :title="`${title} — click to expand`"
    @pointerdown="start($event, 'drag')"
    @click="onBubbleClick"
  >
    {{ icon ?? '🗪' }}
  </button>

  <!-- Expanded: full floating panel -->
  <div
    v-else
    class="floating"
    :style="{ left: `${x}px`, top: `${y}px`, width: `${w}px`, height: `${h}px` }"
  >
    <div class="fp-header" @pointerdown="start($event, 'drag')" @dblclick="minimized = true">
      <span class="fp-title">{{ title }}</span>
      <div class="fp-actions">
        <button class="fp-btn" title="Minimize" @pointerdown.stop @click="minimized = true">
          –
        </button>
        <button class="fp-btn fp-close" title="Close" @pointerdown.stop @click="emit('close')">
          ✕
        </button>
      </div>
    </div>
    <div class="fp-body">
      <slot />
    </div>
    <div class="fp-resize" title="Resize" @pointerdown.stop="start($event, 'resize')" />
  </div>
</template>

<style scoped>
.floating {
  position: fixed;
  z-index: 35;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
  overflow: hidden;
}
.fp-bubble {
  position: fixed;
  z-index: 35;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--accent);
  color: var(--accent-contrast);
  font-size: 22px;
  line-height: 1;
  cursor: grab;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  display: grid;
  place-items: center;
  touch-action: none;
}
.fp-bubble:hover {
  filter: brightness(1.05);
}
.fp-bubble:active {
  cursor: grabbing;
}
.fp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  background: var(--surface-3);
  cursor: move;
  user-select: none;
}
.fp-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
}
.fp-actions {
  display: flex;
  gap: 2px;
}
.fp-btn {
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 13px;
  line-height: 1;
  padding: 2px 6px;
  border-radius: 4px;
}
.fp-btn:hover {
  background: var(--surface-2);
  color: var(--text);
}
.fp-close:hover {
  color: var(--danger);
}
.fp-body {
  flex: 1;
  min-height: 0;
  display: flex;
}
.fp-resize {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 14px;
  height: 14px;
  cursor: nwse-resize;
  background: linear-gradient(135deg, transparent 50%, var(--text-faint) 50%);
}
</style>
