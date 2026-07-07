<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useVueFlow } from '@vue-flow/core';
import { EQUIPMENT_METADATA, EQUIPMENT_TYPES } from '@/schema';
import { useCanvasStore } from '@/stores/canvasStore';
import { useUiStore, type LeftTab } from '@/stores/uiStore';
import { useTheme } from '@/composables/useTheme';
import { useCanvasIo } from '@/composables/useCanvasIo';
import { REPORT_BUILDERS, toCsv } from '@/canvas/reports';
import { api } from '@/api/client';

const emit = defineEmits<{ close: [] }>();

const store = useCanvasStore();
const ui = useUiStore();
const { toggle: toggleTheme } = useTheme();
const { exportJson, exportPng } = useCanvasIo();
const { screenToFlowCoordinate } = useVueFlow('main');

interface Command {
  id: string;
  title: string;
  group: string;
  /** Show when the query is empty (curated set). */
  pinned?: boolean;
  run: () => void;
}

function viewportCenter(): { x: number; y: number } {
  return screenToFlowCoordinate({ x: window.innerWidth / 2, y: window.innerHeight / 2 });
}

function downloadReport(key: string): void {
  const b = REPORT_BUILDERS.find((r) => r.key === key);
  if (!b) return;
  const report = b.build(store.state);
  const blob = new Blob([toCsv(report)], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${store.state.meta.name || 'canvas'}-${report.slug}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function openTab(tab: LeftTab): void {
  ui.leftTab = tab;
  ui.leftOpen = true;
}

const commands = computed<Command[]>(() => {
  const list: Command[] = [
    {
      id: 'save',
      title: 'Save project',
      group: 'Project',
      pinned: true,
      run: () => void api.saveProject(store.state),
    },
    {
      id: 'new',
      title: 'New canvas',
      group: 'Project',
      pinned: true,
      run: () => store.newCanvas(),
    },
    { id: 'fit', title: 'Fit view', group: 'View', pinned: true, run: () => store.requestFit() },
    {
      id: 'layout',
      title: 'Auto-layout',
      group: 'View',
      pinned: true,
      run: () => void store.autoLayout(),
    },
    { id: 'undo', title: 'Undo', group: 'Edit', run: () => store.undo() },
    { id: 'redo', title: 'Redo', group: 'Edit', run: () => store.redo() },
    { id: 'theme', title: 'Toggle light / dark theme', group: 'View', run: () => toggleTheme() },
    {
      id: 'optimus',
      title: 'Open Optimus (AI assistant)',
      group: 'AI',
      pinned: true,
      run: () => {
        ui.optimusOpen = true;
        ui.optimusMinimized = false;
      },
    },
    {
      id: 'tab-project',
      title: 'Go to Project tab',
      group: 'Panels',
      run: () => openTab('project'),
    },
    {
      id: 'tab-equipment',
      title: 'Go to Equipment tab',
      group: 'Panels',
      run: () => openTab('equipment'),
    },
    { id: 'tab-legend', title: 'Go to Legend tab', group: 'Panels', run: () => openTab('legend') },
    { id: 'tab-issues', title: 'Go to Issues tab', group: 'Panels', run: () => openTab('issues') },
    {
      id: 'inspector',
      title: 'Toggle Inspector',
      group: 'Panels',
      run: () => (ui.rightOpen = !ui.rightOpen),
    },
    { id: 'export-json', title: 'Export JSON', group: 'Export', run: () => exportJson() },
    { id: 'export-png', title: 'Export PNG', group: 'Export', run: () => exportPng() },
  ];
  for (const r of REPORT_BUILDERS) {
    list.push({
      id: `report-${r.key}`,
      title: `Export ${r.label} (CSV)`,
      group: 'Export',
      run: () => downloadReport(r.key),
    });
  }
  for (const t of EQUIPMENT_TYPES) {
    list.push({
      id: `add-${t}`,
      title: `Add ${EQUIPMENT_METADATA[t].label}`,
      group: 'Add equipment',
      run: () => store.addEquipment(t, viewportCenter()),
    });
  }
  for (const n of store.state.nodes) {
    const label = (n.label ?? '').trim();
    if (label) {
      list.push({
        id: `goto-${n.id}`,
        title: `Go to ${label}`,
        group: 'Navigate',
        run: () => store.focusOn([n.id]),
      });
    }
  }
  return list;
});

const query = ref('');
const active = ref(0);
const inputEl = ref<HTMLInputElement | null>(null);

function score(title: string, q: string): number {
  const t = title.toLowerCase();
  const idx = t.indexOf(q);
  if (idx >= 0) return idx;
  // subsequence fallback
  let qi = 0;
  for (let i = 0; i < t.length && qi < q.length; i++) if (t[i] === q[qi]) qi++;
  return qi === q.length ? 500 + title.length : -1;
}

const results = computed<Command[]>(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return commands.value.filter((c) => c.pinned);
  return commands.value
    .map((c) => ({ c, s: score(c.title, q) }))
    .filter((x) => x.s >= 0)
    .sort((a, b) => a.s - b.s)
    .slice(0, 40)
    .map((x) => x.c);
});

function choose(cmd: Command | undefined): void {
  if (!cmd) return;
  cmd.run();
  emit('close');
}

function onKey(e: KeyboardEvent): void {
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    active.value = Math.min(active.value + 1, results.value.length - 1);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    active.value = Math.max(active.value - 1, 0);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    choose(results.value[active.value]);
  } else if (e.key === 'Escape') {
    e.preventDefault();
    emit('close');
  }
}

onMounted(() => inputEl.value?.focus());
</script>

<template>
  <div class="cp-backdrop" @click="emit('close')" @contextmenu.prevent="emit('close')" />
  <div class="cp">
    <input
      ref="inputEl"
      v-model="query"
      class="cp-input"
      placeholder="Type a command or search… (Esc to close)"
      @keydown="onKey"
      @input="active = 0"
    />
    <div class="cp-list">
      <button
        v-for="(c, i) in results"
        :key="c.id"
        class="cp-item"
        :class="{ active: i === active }"
        @click="choose(c)"
        @mouseenter="active = i"
      >
        <span class="cp-title">{{ c.title }}</span>
        <span class="cp-group">{{ c.group }}</span>
      </button>
      <div v-if="!results.length" class="cp-empty">No matching commands</div>
    </div>
  </div>
</template>

<style scoped>
.cp-backdrop {
  position: fixed;
  inset: 0;
  z-index: 80;
  background: rgba(0, 0, 0, 0.25);
}
.cp {
  position: fixed;
  z-index: 81;
  top: 14vh;
  left: 50%;
  transform: translateX(-50%);
  width: min(560px, 92vw);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}
.cp-input {
  width: 100%;
  font-size: 14px;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
  margin-bottom: 6px;
}
.cp-list {
  max-height: 50vh;
  overflow-y: auto;
}
.cp-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  width: 100%;
  text-align: left;
  font-size: 13px;
  padding: 8px 12px;
  border-radius: 8px;
  background: none;
  border: none;
  color: var(--text);
  cursor: pointer;
}
.cp-item.active {
  background: var(--surface-3);
}
.cp-group {
  flex: 0 0 auto;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-faint);
}
.cp-empty {
  font-size: 13px;
  color: var(--text-faint);
  padding: 10px 12px;
}
</style>
