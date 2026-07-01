<script setup lang="ts">
import { ref } from 'vue';
import { useVueFlow } from '@vue-flow/core';
import { useCanvasStore } from '@/stores/canvasStore';
import { useUiStore, type LinkStyle } from '@/stores/uiStore';
import { useTheme } from '@/composables/useTheme';
import { useCanvasIo } from '@/composables/useCanvasIo';
import { api, type ProjectSummary } from '@/api/client';

const store = useCanvasStore();
const ui = useUiStore();
const { theme, toggle: toggleTheme } = useTheme();
const { fitView } = useVueFlow('main');
const { exportJson, exportPng, importJsonFile } = useCanvasIo();

const openMenu = ref<'project' | 'edit' | 'view' | null>(null);
const projects = ref<ProjectSummary[]>([]);
const fileInput = ref<HTMLInputElement | null>(null);

function toggle(menu: 'project' | 'edit' | 'view'): void {
  openMenu.value = openMenu.value === menu ? null : menu;
  if (openMenu.value === 'project') void refreshProjects();
}
function close(): void {
  openMenu.value = null;
}

async function refreshProjects(): Promise<void> {
  projects.value = await api.listProjects().catch(() => []);
}

async function save(): Promise<void> {
  await api.saveProject(store.state);
  await refreshProjects();
}
async function open(id: string): Promise<void> {
  store.loadState(await api.getProject(id));
  store.requestFit();
  close();
}
function fit(): void {
  fitView({ padding: 0.2 });
}
function onImport(e: Event): void {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (file) void importJsonFile(file).catch((err) => alert(err.message));
  if (fileInput.value) fileInput.value.value = '';
}
function run(fn: () => void): void {
  fn();
  close();
}
const linkStyles: LinkStyle[] = ['smoothstep', 'straight', 'step'];
</script>

<template>
  <header class="topbar">
    <div class="brand"><img src="/favicon.svg" class="brand-icon" alt="" /> P&amp;ID Agent</div>

    <!-- Menus -->
    <nav class="menus">
      <div class="menu">
        <button
          class="menu-btn"
          :class="{ active: openMenu === 'project' }"
          @click="toggle('project')"
        >
          Project
        </button>
        <div v-if="openMenu === 'project'" class="dropdown">
          <button class="mi" @click="run(() => store.newCanvas())">New</button>
          <button class="mi" @click="run(save)">Save</button>
          <div class="sep" />
          <button class="mi" @click="run(() => fileInput?.click())">Import JSON…</button>
          <button class="mi" @click="run(exportJson)">Export JSON</button>
          <button class="mi" @click="run(exportPng)">Export PNG</button>
          <div class="sep" />
          <div class="mi-label">Open</div>
          <div class="open-list">
            <button v-for="p in projects" :key="p.id" class="mi small" @click="open(p.id)">
              {{ p.name }} <span class="dim">{{ p.id }}</span>
            </button>
            <div v-if="!projects.length" class="mi dim">No saved projects</div>
          </div>
        </div>
      </div>

      <div class="menu">
        <button class="menu-btn" :class="{ active: openMenu === 'edit' }" @click="toggle('edit')">
          Edit
        </button>
        <div v-if="openMenu === 'edit'" class="dropdown">
          <button class="mi" :disabled="!store.canUndo" @click="run(store.undo)">Undo</button>
          <button class="mi" :disabled="!store.canRedo" @click="run(store.redo)">Redo</button>
          <div class="sep" />
          <button class="mi" :disabled="!store.selectedIds.length" @click="run(store.copy)">
            Copy
          </button>
          <button class="mi" :disabled="!store.hasClipboard" @click="run(() => store.pasteAt())">
            Paste
          </button>
          <button class="mi" :disabled="!store.selectedIds.length" @click="run(store.duplicate)">
            Duplicate
          </button>
          <button
            class="mi"
            :disabled="!store.selectedIds.length"
            @click="run(store.removeSelected)"
          >
            Delete
          </button>
          <div class="sep" />
          <button class="mi" @click="run(store.selectAll)">Select all</button>
        </div>
      </div>

      <div class="menu">
        <button class="menu-btn" :class="{ active: openMenu === 'view' }" @click="toggle('view')">
          View
        </button>
        <div v-if="openMenu === 'view'" class="dropdown">
          <button class="mi" @click="run(fit)">Fit view</button>
          <button class="mi" :disabled="!store.state.nodes.length" @click="run(store.autoLayout)">
            Auto-layout
          </button>
          <div class="sep" />
          <button class="mi check" @click="ui.snapToGrid = !ui.snapToGrid">
            <span>Snap to grid</span><span>{{ ui.snapToGrid ? '✓' : '' }}</span>
          </button>
          <div class="mi-label">Link style</div>
          <button v-for="ls in linkStyles" :key="ls" class="mi check" @click="ui.linkStyle = ls">
            <span class="cap">{{ ls }}</span
            ><span>{{ ui.linkStyle === ls ? '✓' : '' }}</span>
          </button>
          <div class="sep" />
          <button class="mi check" @click="ui.leftOpen = !ui.leftOpen">
            <span>Left panel</span><span>{{ ui.leftOpen ? '✓' : '' }}</span>
          </button>
          <button class="mi check" @click="ui.rightOpen = !ui.rightOpen">
            <span>Inspector</span><span>{{ ui.rightOpen ? '✓' : '' }}</span>
          </button>
          <button class="mi check" @click="ui.optimusOpen = !ui.optimusOpen">
            <span>Optimus</span><span>{{ ui.optimusOpen ? '✓' : '' }}</span>
          </button>
        </div>
      </div>
    </nav>

    <input
      :value="store.state.meta.name"
      class="name"
      placeholder="Canvas name"
      @input="store.renameCanvas(($event.target as HTMLInputElement).value)"
    />

    <div class="spacer" />

    <!-- Quick actions -->
    <div class="quick">
      <button
        class="qa kbd"
        title="Command palette (Ctrl/⌘+K)"
        @click="ui.commandPaletteOpen = true"
      >
        ⌘K
      </button>
      <button class="qa" title="Undo (Ctrl+Z)" :disabled="!store.canUndo" @click="store.undo">
        ↶
      </button>
      <button class="qa" title="Redo (Ctrl+Y)" :disabled="!store.canRedo" @click="store.redo">
        ↷
      </button>
      <button class="qa" title="Fit view (F)" @click="fit">⤢</button>
      <button
        class="qa"
        title="Auto-layout"
        :disabled="!store.state.nodes.length"
        @click="store.autoLayout"
      >
        ⌗
      </button>
      <button
        class="qa"
        :title="`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`"
        @click="toggleTheme"
      >
        {{ theme === 'dark' ? '☀️' : '🌙' }}
      </button>
    </div>

    <input ref="fileInput" type="file" accept="application/json,.json" hidden @change="onImport" />
    <div v-if="openMenu" class="backdrop" @click="close" />
  </header>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  padding: 0 10px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  color: var(--text);
  position: relative;
  z-index: 40;
}
.brand {
  display: flex;
  align-items: center;
  gap: 9px;
  font-weight: 800;
  font-size: 22px;
  letter-spacing: -0.01em;
  color: var(--accent);
  margin-right: 14px;
}
.brand-icon {
  width: 30px;
  height: 30px;
  border-radius: 7px;
}
.menus {
  display: flex;
  gap: 2px;
}
.menu {
  position: relative;
}
.menu-btn {
  font-size: 13px;
  padding: 5px 10px;
  border-radius: 6px;
  background: none;
  border: none;
  color: var(--text);
  cursor: pointer;
}
.menu-btn:hover,
.menu-btn.active {
  background: var(--surface-3);
}
.dropdown {
  position: absolute;
  top: 34px;
  left: 0;
  min-width: 200px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  z-index: 50;
}
.mi {
  display: flex;
  justify-content: space-between;
  width: 100%;
  text-align: left;
  font-size: 13px;
  padding: 6px 10px;
  border-radius: 6px;
  background: none;
  border: none;
  color: var(--text);
  cursor: pointer;
}
.mi:hover:not(:disabled) {
  background: var(--surface-3);
}
.mi:disabled {
  opacity: 0.4;
  cursor: default;
}
.mi.small {
  font-size: 12px;
}
.mi-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-faint);
  padding: 6px 10px 2px;
}
.cap {
  text-transform: capitalize;
}
.dim {
  color: var(--text-faint);
  font-size: 11px;
}
.open-list {
  max-height: 200px;
  overflow-y: auto;
}
.sep {
  height: 1px;
  background: var(--border);
  margin: 4px 0;
}
.name {
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
  width: 180px;
}
.spacer {
  flex: 1;
}
.quick {
  display: flex;
  gap: 4px;
}
.qa {
  width: 30px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
  cursor: pointer;
  font-size: 14px;
}
.qa:hover:not(:disabled) {
  border-color: var(--accent);
}
.qa.kbd {
  width: auto;
  padding: 0 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
}
.qa:disabled {
  opacity: 0.4;
  cursor: default;
}
.backdrop {
  position: fixed;
  inset: 0;
  z-index: 30;
}
</style>
