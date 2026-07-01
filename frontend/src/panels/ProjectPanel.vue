<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useCanvasStore } from '@/stores/canvasStore';
import { useCanvasIo } from '@/composables/useCanvasIo';
import { REPORT_BUILDERS, toCsv } from '@/canvas/reports';
import { api, type ProjectSummary } from '@/api/client';

const store = useCanvasStore();
const { exportJson, exportPng, importJsonFile } = useCanvasIo();

const projects = ref<ProjectSummary[]>([]);
const fileInput = ref<HTMLInputElement | null>(null);
const saving = ref(false);
const savedAt = ref<string | null>(null);

const stats = computed(() => ({
  nodes: store.state.nodes.length,
  edges: store.state.edges.length,
  groups: store.state.groups.length,
}));

const updated = computed(() => {
  const iso = store.state.meta.updatedAt;
  if (!iso) return '—';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '—' : d.toLocaleString();
});

async function refresh(): Promise<void> {
  projects.value = await api.listProjects().catch(() => []);
}

async function save(): Promise<void> {
  saving.value = true;
  try {
    await api.saveProject(store.state);
    savedAt.value = new Date().toLocaleTimeString();
    await refresh();
  } finally {
    saving.value = false;
  }
}

async function open(id: string): Promise<void> {
  if (id === store.state.meta.id) return;
  store.loadState(await api.getProject(id));
  store.requestFit();
}

async function remove(p: ProjectSummary): Promise<void> {
  if (!confirm(`Delete "${p.name || 'Untitled'}"? This cannot be undone.`)) return;
  await api.deleteProject(p.id).catch((err) => alert((err as Error).message));
  if (p.id === store.state.meta.id) store.newCanvas();
  await refresh();
}

function newCanvas(): void {
  store.newCanvas();
  savedAt.value = null;
}

function onImport(e: Event): void {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (file) void importJsonFile(file).catch((err) => alert(err.message));
  if (fileInput.value) fileInput.value.value = '';
}

function exportReport(key: string): void {
  const builder = REPORT_BUILDERS.find((b) => b.key === key);
  if (!builder) return;
  const report = builder.build(store.state);
  const blob = new Blob([toCsv(report)], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${store.state.meta.name || 'canvas'}-${report.slug}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

onMounted(refresh);
</script>

<template>
  <div class="project">
    <div class="scroll">
      <section class="block">
        <div class="block-head">Current project</div>
        <input
          :value="store.state.meta.name"
          class="name"
          placeholder="Untitled"
          @input="store.renameCanvas(($event.target as HTMLInputElement).value)"
        />
        <div class="meta-row">
          <span class="dim mono">{{ store.state.meta.id }}</span>
        </div>
        <div class="meta-row">
          <span class="dim">Updated</span><span>{{ updated }}</span>
        </div>

        <div class="stats">
          <div class="stat">
            <div class="stat-num">{{ stats.nodes }}</div>
            <div class="stat-lbl">Equipment</div>
          </div>
          <div class="stat">
            <div class="stat-num">{{ stats.edges }}</div>
            <div class="stat-lbl">Connections</div>
          </div>
          <div class="stat">
            <div class="stat-num">{{ stats.groups }}</div>
            <div class="stat-lbl">Groups</div>
          </div>
        </div>
      </section>

      <section class="block">
        <div class="block-head">Actions</div>
        <div class="btn-grid">
          <button class="btn" @click="newCanvas">New</button>
          <button class="btn primary" :disabled="saving" @click="save">
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
          <button class="btn" @click="fileInput?.click()">Import JSON…</button>
          <button class="btn" @click="exportJson">Export JSON</button>
          <button class="btn" @click="exportPng">Export PNG</button>
        </div>
        <div v-if="savedAt" class="saved-note">Saved at {{ savedAt }}</div>
      </section>

      <section class="block">
        <div class="block-head">Reports (CSV)</div>
        <div class="report-list">
          <button
            v-for="r in REPORT_BUILDERS"
            :key="r.key"
            class="btn report"
            @click="exportReport(r.key)"
          >
            <span>{{ r.label }}</span>
            <span class="dl">↓</span>
          </button>
        </div>
      </section>

      <section class="block">
        <div class="block-head">Saved projects</div>
        <div class="open-list">
          <div
            v-for="p in projects"
            :key="p.id"
            class="proj"
            :class="{ current: p.id === store.state.meta.id }"
          >
            <button class="proj-open" :title="`Open ${p.name || 'Untitled'}`" @click="open(p.id)">
              <span class="proj-name">{{ p.name || 'Untitled' }}</span>
              <span v-if="p.id === store.state.meta.id" class="badge">current</span>
            </button>
            <button class="proj-del" title="Delete project" @click="remove(p)">✕</button>
          </div>
          <div v-if="!projects.length" class="empty">No saved projects yet.</div>
        </div>
      </section>
    </div>

    <input ref="fileInput" type="file" accept="application/json,.json" hidden @change="onImport" />
  </div>
</template>

<style scoped>
.project {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.scroll {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}
.block {
  margin-bottom: 16px;
}
.block-head {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-faint);
  margin-bottom: 8px;
}
.name {
  width: 100%;
  font-size: 13px;
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
  margin-bottom: 6px;
}
.meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 3px;
}
.dim {
  color: var(--text-faint);
}
.mono {
  font-family: ui-monospace, monospace;
  font-size: 10px;
}
.stats {
  display: flex;
  gap: 6px;
  margin-top: 10px;
}
.stat {
  flex: 1;
  text-align: center;
  padding: 8px 4px;
  border-radius: 8px;
  background: var(--surface-2);
  border: 1px solid var(--border);
}
.stat-num {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
}
.stat-lbl {
  font-size: 10px;
  color: var(--text-faint);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.btn-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}
.btn {
  font-size: 12px;
  padding: 7px 8px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
  cursor: pointer;
}
.btn:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}
.btn:disabled {
  opacity: 0.5;
  cursor: default;
}
.btn.primary {
  background: var(--accent);
  color: var(--accent-contrast);
  border-color: var(--accent);
}
.btn.primary:hover:not(:disabled) {
  color: var(--accent-contrast);
  opacity: 0.9;
}
.saved-note {
  font-size: 10px;
  color: var(--text-faint);
  margin-top: 6px;
}
.report-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.report {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.report .dl {
  color: var(--text-faint);
}
.report:hover .dl {
  color: var(--accent);
}
.open-list {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.proj {
  display: flex;
  align-items: stretch;
  gap: 4px;
  width: 100%;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  overflow: hidden;
}
.proj:hover,
.proj.current {
  border-color: var(--accent);
}
.proj-open {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  text-align: left;
  font-size: 12px;
  padding: 7px 8px;
  border: none;
  background: none;
  color: var(--text);
  cursor: pointer;
}
.proj-del {
  flex: 0 0 auto;
  border: none;
  border-left: 1px solid var(--border);
  background: none;
  color: var(--text-faint);
  cursor: pointer;
  padding: 0 9px;
  font-size: 11px;
}
.proj-del:hover {
  color: #fff;
  background: var(--danger, #ef4444);
}
.proj-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.badge {
  flex: 0 0 auto;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--accent);
  border: 1px solid var(--accent);
  border-radius: 4px;
  padding: 1px 4px;
}
.empty {
  font-size: 12px;
  color: var(--text-faint);
  padding: 4px 0;
}
</style>
