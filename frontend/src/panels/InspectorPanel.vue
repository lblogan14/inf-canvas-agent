<script setup lang="ts">
import { computed } from 'vue';
import { getEquipmentMeta, type LineType } from '@/schema';
import { useCanvasStore } from '@/stores/canvasStore';
import { useUiStore } from '@/stores/uiStore';
import { LINE_STYLES } from '@/canvas/edges/lineStyles';

const store = useCanvasStore();
const ui = useUiStore();
const node = computed(() => store.selectedNode);
const meta = computed(() => (node.value ? getEquipmentMeta(node.value.type) : null));

const edge = computed(() => store.selectedEdge);
const lineTypes = Object.entries(LINE_STYLES).map(([key, s]) => ({
  key: key as LineType,
  label: s.label,
}));

function rotate(): void {
  if (!node.value) return;
  store.updateNode(node.value.id, { rotation: ((node.value.rotation ?? 0) + 90) % 360 });
}
</script>

<template>
  <aside class="inspector">
    <div class="section-head">
      <span class="section-title">Inspector</span>
      <button class="collapse" title="Hide inspector" @click="ui.rightOpen = false">›</button>
    </div>
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

    <template v-else-if="edge">
      <div class="field">
        <label>Connection</label>
        <div class="value">Pipe / signal line</div>
      </div>
      <div class="field">
        <label>Line type</label>
        <select
          class="input"
          :value="edge.data?.lineType ?? 'process'"
          @change="
            store.updateEdgeData(edge.id, {
              lineType: ($event.target as HTMLSelectElement).value as LineType,
            })
          "
        >
          <option v-for="lt in lineTypes" :key="lt.key" :value="lt.key">{{ lt.label }}</option>
        </select>
      </div>
      <div class="field">
        <label>Line number / label</label>
        <input
          class="input"
          :value="edge.data?.label ?? ''"
          placeholder='e.g. 6"-P-1001-CS'
          @change="
            store.updateEdgeData(edge.id, { label: ($event.target as HTMLInputElement).value })
          "
        />
      </div>
      <p class="hint">Drag the handles on the selected pipe to reroute it.</p>
    </template>

    <div v-else class="empty">Select a node or connection to edit its properties.</div>
  </aside>
</template>

<style scoped>
.inspector {
  width: 240px;
  padding: 12px;
  background: var(--surface);
  border-left: 1px solid var(--border);
  color: var(--text);
  overflow-y: auto;
}
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.section-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-faint);
}
.collapse {
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text-muted);
  border-radius: 6px;
  cursor: pointer;
  padding: 2px 8px;
}
.collapse:hover {
  color: var(--accent);
  border-color: var(--accent);
}
.field {
  margin-bottom: 10px;
}
.field label {
  display: block;
  font-size: 10px;
  color: var(--text-faint);
  margin-bottom: 3px;
}
.value {
  font-size: 13px;
  color: var(--text-muted);
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
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
}
.action {
  width: 100%;
  font-size: 12px;
  padding: 6px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-3);
  color: var(--text);
  cursor: pointer;
}
.action:hover {
  border-color: var(--accent);
}
.hint {
  font-size: 11px;
  color: var(--text-faint);
  line-height: 1.4;
  margin: 8px 0 0;
}
.empty {
  font-size: 12px;
  color: var(--text-faint);
}
</style>
