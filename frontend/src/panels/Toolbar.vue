<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { EQUIPMENT_METADATA, EQUIPMENT_TYPES, type EquipmentType } from '@/schema';
import { useCanvasStore } from '@/stores/canvasStore';
import { api, type ProjectSummary } from '@/api/client';

const store = useCanvasStore();
const projects = ref<ProjectSummary[]>([]);
const saving = ref(false);
let cascade = 0;

const groups = EQUIPMENT_TYPES.reduce<Record<string, EquipmentType[]>>((acc, type) => {
  const cat = EQUIPMENT_METADATA[type].category;
  (acc[cat] ??= []).push(type);
  return acc;
}, {});

function add(type: EquipmentType): void {
  cascade = (cascade + 1) % 8;
  store.addEquipment(type, { x: 240 + cascade * 28, y: 160 + cascade * 28 });
}

async function refreshProjects(): Promise<void> {
  projects.value = await api.listProjects().catch(() => []);
}

async function save(): Promise<void> {
  saving.value = true;
  try {
    await api.saveProject(store.state);
    await refreshProjects();
  } finally {
    saving.value = false;
  }
}

async function load(event: Event): Promise<void> {
  const id = (event.target as HTMLSelectElement).value;
  if (!id) return;
  store.loadState(await api.getProject(id));
}

onMounted(refreshProjects);
</script>

<template>
  <aside class="toolbar">
    <div class="brand">⬡ Inf-Canvas</div>

    <div class="section-title">Equipment</div>
    <div v-for="(types, cat) in groups" :key="cat" class="group">
      <div class="group-label">{{ cat }}</div>
      <button v-for="t in types" :key="t" class="eq-btn" @click="add(t)">
        {{ EQUIPMENT_METADATA[t].label }}
      </button>
    </div>

    <div class="spacer" />

    <div class="section-title">Project</div>
    <select class="select" @change="load">
      <option value="">Load project…</option>
      <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }} ({{ p.id }})</option>
    </select>
    <input v-model="store.state.meta.name" class="input" placeholder="Canvas name" />
    <div class="row">
      <button class="action" :disabled="saving" @click="save">
        {{ saving ? 'Saving…' : 'Save' }}
      </button>
      <button class="action" @click="store.newCanvas()">New</button>
    </div>
    <button
      class="action danger"
      :disabled="!store.selectedIds.length"
      @click="store.removeSelected()"
    >
      Delete selected
    </button>
  </aside>
</template>

<style scoped>
.toolbar {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 220px;
  padding: 12px;
  background: #111827;
  border-right: 1px solid #1f2937;
  overflow-y: auto;
  color: #e5e7eb;
}
.brand {
  font-weight: 700;
  font-size: 15px;
  margin-bottom: 8px;
  color: #38bdf8;
}
.section-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin-top: 8px;
}
.group-label {
  font-size: 10px;
  color: #475569;
  margin: 6px 0 2px;
  text-transform: capitalize;
}
.eq-btn {
  display: block;
  width: 100%;
  text-align: left;
  font-size: 12px;
  padding: 5px 8px;
  border-radius: 6px;
  border: 1px solid #1f2937;
  background: #0b1220;
  color: #cbd5e1;
  cursor: pointer;
}
.eq-btn:hover {
  border-color: #38bdf8;
  color: #38bdf8;
}
.spacer {
  flex: 1;
}
.select,
.input {
  width: 100%;
  font-size: 12px;
  padding: 5px 8px;
  border-radius: 6px;
  border: 1px solid #1f2937;
  background: #0b1220;
  color: #cbd5e1;
}
.row {
  display: flex;
  gap: 6px;
}
.action {
  flex: 1;
  font-size: 12px;
  padding: 6px;
  border-radius: 6px;
  border: 1px solid #1f2937;
  background: #1e293b;
  color: #e5e7eb;
  cursor: pointer;
}
.action:hover:not(:disabled) {
  border-color: #38bdf8;
}
.action:disabled {
  opacity: 0.5;
  cursor: default;
}
.action.danger:hover:not(:disabled) {
  border-color: #ef4444;
  color: #ef4444;
}
</style>
