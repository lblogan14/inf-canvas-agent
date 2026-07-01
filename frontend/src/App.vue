<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue';
import { useCanvasStore } from '@/stores/canvasStore';
import { useUiStore } from '@/stores/uiStore';
import { connectRealtime } from '@/realtime/ws';
import TopBar from '@/panels/TopBar.vue';
import LeftPanel from '@/panels/LeftPanel.vue';
import CanvasView from '@/canvas/CanvasView.vue';
import InspectorPanel from '@/panels/InspectorPanel.vue';
import FloatingPanel from '@/panels/FloatingPanel.vue';
import AgentPanel from '@/panels/AgentPanel.vue';

const store = useCanvasStore();
const ui = useUiStore();
let disconnect: (() => void) | null = null;

function reconnect(canvasId: string): void {
  disconnect?.();
  disconnect = connectRealtime(canvasId);
}

function isTyping(t: EventTarget | null): boolean {
  const el = t as HTMLElement | null;
  return (
    !!el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable === true)
  );
}

function onKeydown(e: KeyboardEvent): void {
  if (isTyping(e.target)) return;
  const mod = e.ctrlKey || e.metaKey;
  const key = e.key.toLowerCase();

  if (mod && key === 'z') {
    e.preventDefault();
    if (e.shiftKey) store.redo();
    else store.undo();
  } else if (mod && key === 'y') {
    e.preventDefault();
    store.redo();
  } else if (mod && key === 'c') {
    store.copy();
  } else if (mod && key === 'v') {
    store.pasteAt();
  } else if (mod && key === 'd') {
    e.preventDefault();
    store.duplicate();
  } else if (mod && key === 'a') {
    e.preventDefault();
    store.selectAll();
  } else if (mod && key === 'g') {
    e.preventDefault();
    store.createGroupFromSelection();
  } else if (key === 'delete' || key === 'backspace') {
    e.preventDefault();
    store.removeSelected();
  } else if (key === 'f') {
    store.requestFit();
  } else if (key === 'escape') {
    store.setSelection([]);
  }
}

onMounted(() => {
  reconnect(store.state.meta.id);
  window.addEventListener('keydown', onKeydown);
});
watch(
  () => store.state.meta.id,
  (id) => reconnect(id),
);
onUnmounted(() => {
  disconnect?.();
  window.removeEventListener('keydown', onKeydown);
});
</script>

<template>
  <div class="app">
    <TopBar />
    <div class="workspace">
      <LeftPanel v-if="ui.leftOpen" />
      <button v-else class="edge-toggle left" title="Show panel" @click="ui.leftOpen = true">
        ›
      </button>

      <div class="canvas-wrap">
        <CanvasView />
      </div>

      <InspectorPanel v-if="ui.rightOpen" />
      <button v-else class="edge-toggle right" title="Show inspector" @click="ui.rightOpen = true">
        ‹
      </button>
    </div>

    <FloatingPanel
      v-if="ui.optimusOpen"
      v-model:x="ui.optimus.x"
      v-model:y="ui.optimus.y"
      v-model:w="ui.optimus.w"
      v-model:h="ui.optimus.h"
      v-model:minimized="ui.optimusMinimized"
      title="🤖 Optimus"
      icon="🤖"
      @close="ui.optimusOpen = false"
    >
      <AgentPanel />
    </FloatingPanel>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}
.workspace {
  display: flex;
  flex: 1;
  min-height: 0;
}
.canvas-wrap {
  flex: 1;
  min-width: 0;
  position: relative;
}
.edge-toggle {
  width: 18px;
  background: var(--surface);
  border: none;
  border-right: 1px solid var(--border);
  border-left: 1px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
}
.edge-toggle:hover {
  color: var(--accent);
  background: var(--surface-3);
}
</style>
