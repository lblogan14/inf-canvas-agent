<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import { useCanvasStore } from '@/stores/canvasStore';
import { connectRealtime } from '@/realtime/ws';
import CanvasView from '@/canvas/CanvasView.vue';
import Toolbar from '@/panels/Toolbar.vue';
import InspectorPanel from '@/panels/InspectorPanel.vue';
import AgentPanel from '@/panels/AgentPanel.vue';

const store = useCanvasStore();
let disconnect: (() => void) | null = null;

onMounted(() => {
  disconnect = connectRealtime(store.state.meta.id);
});

onUnmounted(() => disconnect?.());
</script>

<template>
  <div class="layout">
    <Toolbar />
    <main class="center">
      <CanvasView />
      <AgentPanel />
    </main>
    <InspectorPanel />
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100%;
  width: 100%;
}
.center {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}
.center > :first-child {
  flex: 1;
  min-height: 0;
}
</style>
