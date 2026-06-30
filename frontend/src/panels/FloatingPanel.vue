<script setup lang="ts">
const x = defineModel<number>('x', { required: true });
const y = defineModel<number>('y', { required: true });
const w = defineModel<number>('w', { required: true });
const h = defineModel<number>('h', { required: true });

defineProps<{ title: string }>();
const emit = defineEmits<{ close: [] }>();

let mode: 'drag' | 'resize' | null = null;
let startX = 0;
let startY = 0;
let originX = 0;
let originY = 0;
let originW = 0;
let originH = 0;

function onMove(e: PointerEvent): void {
  if (!mode) return;
  const dx = e.clientX - startX;
  const dy = e.clientY - startY;
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
  startX = e.clientX;
  startY = e.clientY;
  originX = x.value;
  originY = y.value;
  originW = w.value;
  originH = h.value;
  window.addEventListener('pointermove', onMove);
  window.addEventListener('pointerup', stop);
}
</script>

<template>
  <div
    class="floating"
    :style="{ left: `${x}px`, top: `${y}px`, width: `${w}px`, height: `${h}px` }"
  >
    <div class="fp-header" @pointerdown="start($event, 'drag')">
      <span class="fp-title">{{ title }}</span>
      <button class="fp-close" title="Close" @pointerdown.stop @click="emit('close')">✕</button>
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
.fp-close {
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 13px;
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
