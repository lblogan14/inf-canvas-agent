<script setup lang="ts">
import { computed } from 'vue';
import { getEquipmentMeta } from '@/schema';
import { useCanvasStore } from '@/stores/canvasStore';

const store = useCanvasStore();
const node = computed(() => store.selectedNode);
const meta = computed(() => (node.value ? getEquipmentMeta(node.value.type) : null));

function rotate(): void {
  if (!node.value) return;
  store.updateNode(node.value.id, { rotation: ((node.value.rotation ?? 0) + 90) % 360 });
}
</script>

<template>
  <aside class="inspector">
    <div class="section-title">Inspector</div>
    <template v-if="node && meta">
      <div class="field">
        <label>Type</label>
        <div class="value">{{ meta.label }}</div>
      </div>
      <div class="field">
        <label>ID</label>
        <div class="value mono">{{ node.id }}</div>
      </div>
      <div class="field">
        <label>Tag / Label</label>
        <input
          class="input"
          :value="node.label ?? ''"
          placeholder="e.g. P-101"
          @change="store.updateNode(node.id, { label: ($event.target as HTMLInputElement).value })"
        />
      </div>
      <div class="field">
        <label>Position</label>
        <div class="value mono">
          {{ Math.round(node.position.x) }}, {{ Math.round(node.position.y) }}
        </div>
      </div>
      <button class="action" @click="rotate">Rotate 90°</button>
    </template>
    <div v-else class="empty">Select a node to edit its properties.</div>
  </aside>
</template>

<style scoped>
.inspector {
  width: 240px;
  padding: 12px;
  background: #111827;
  border-left: 1px solid #1f2937;
  color: #e5e7eb;
  overflow-y: auto;
}
.section-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin-bottom: 10px;
}
.field {
  margin-bottom: 10px;
}
.field label {
  display: block;
  font-size: 10px;
  color: #64748b;
  margin-bottom: 3px;
}
.value {
  font-size: 13px;
  color: #cbd5e1;
}
.mono {
  font-family: ui-monospace, monospace;
  font-size: 12px;
}
.input {
  width: 100%;
  font-size: 13px;
  padding: 5px 8px;
  border-radius: 6px;
  border: 1px solid #1f2937;
  background: #0b1220;
  color: #cbd5e1;
}
.action {
  width: 100%;
  font-size: 12px;
  padding: 6px;
  border-radius: 6px;
  border: 1px solid #1f2937;
  background: #1e293b;
  color: #e5e7eb;
  cursor: pointer;
}
.action:hover {
  border-color: #38bdf8;
}
.empty {
  font-size: 12px;
  color: #475569;
}
</style>
