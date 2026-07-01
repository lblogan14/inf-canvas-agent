<script setup lang="ts">
import { computed, onBeforeUnmount } from 'vue';
import { useUiStore, type LeftTab } from '@/stores/uiStore';
import { useCanvasStore } from '@/stores/canvasStore';
import { validateCanvas } from '@/canvas/validation';
import ProjectPanel from './ProjectPanel.vue';
import NodeLibrary from './NodeLibrary.vue';
import LegendPanel from './LegendPanel.vue';
import IssuesPanel from './IssuesPanel.vue';

const ui = useUiStore();
const store = useCanvasStore();

const tabs: { key: LeftTab; label: string; icon: string }[] = [
  { key: 'project', label: 'Project', icon: '📁' },
  { key: 'equipment', label: 'Equipment', icon: '⚙️' },
  { key: 'legend', label: 'Legend', icon: '〰️' },
  { key: 'issues', label: 'Issues', icon: '✓' },
];

const issueCount = computed(() => validateCanvas(store.state).length);

// --- draggable width ----------------------------------------------------
let startX = 0;
let startW = 0;

function onMove(e: PointerEvent): void {
  ui.setLeftWidth(startW + (e.clientX - startX));
}
function endResize(): void {
  window.removeEventListener('pointermove', onMove);
  window.removeEventListener('pointerup', endResize);
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
}
function startResize(e: PointerEvent): void {
  e.preventDefault();
  startX = e.clientX;
  startW = ui.leftWidth;
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
  window.addEventListener('pointermove', onMove);
  window.addEventListener('pointerup', endResize);
}
onBeforeUnmount(endResize);
</script>

<template>
  <aside class="left-panel" :style="{ width: ui.leftWidth + 'px' }">
    <!-- Icon rail: collapsed to icons; expands to show labels on hover -->
    <nav class="rail">
      <button
        v-for="t in tabs"
        :key="t.key"
        class="rail-tab"
        :class="{ active: ui.leftTab === t.key }"
        :title="t.label"
        @click="ui.leftTab = t.key"
      >
        <span class="ri">
          {{ t.icon }}
          <span v-if="t.key === 'issues' && issueCount" class="badge">{{ issueCount }}</span>
        </span>
        <span class="rl">{{ t.label }}</span>
      </button>
      <div class="rail-spacer" />
      <button class="rail-tab" title="Hide panel" @click="ui.leftOpen = false">
        <span class="ri">‹</span>
        <span class="rl">Hide</span>
      </button>
    </nav>

    <div class="body">
      <ProjectPanel v-show="ui.leftTab === 'project'" />
      <NodeLibrary v-show="ui.leftTab === 'equipment'" />
      <LegendPanel v-show="ui.leftTab === 'legend'" />
      <IssuesPanel v-show="ui.leftTab === 'issues'" />
    </div>

    <div class="resizer" title="Drag to resize" @pointerdown="startResize" />
  </aside>
</template>

<style scoped>
.left-panel {
  position: relative;
  display: flex;
  height: 100%;
  background: var(--surface);
  border-right: 1px solid var(--border);
  overflow: visible;
}
.rail {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 46px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 6px 4px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  z-index: 6;
  overflow: hidden;
  transition: width 0.14s ease;
}
.rail:hover {
  width: 168px;
  box-shadow: 6px 0 18px rgba(0, 0, 0, 0.18);
}
.rail-tab {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px;
  border-radius: 7px;
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
}
.rail-tab:hover {
  background: var(--surface-3);
  color: var(--text);
}
.rail-tab.active {
  background: var(--surface-3);
  color: var(--accent);
}
.ri {
  position: relative;
  flex: 0 0 22px;
  text-align: center;
  font-size: 16px;
}
.badge {
  position: absolute;
  top: -6px;
  right: -8px;
  min-width: 15px;
  height: 15px;
  padding: 0 3px;
  border-radius: 999px;
  background: #d97706;
  color: #fff;
  font-size: 9px;
  font-weight: 700;
  line-height: 15px;
  text-align: center;
}
.rl {
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.14s ease;
}
.rail:hover .rl {
  opacity: 1;
}
.rail-spacer {
  flex: 1;
}
.body {
  display: flex;
  flex: 1;
  min-width: 0;
  margin-left: 46px;
  overflow: hidden;
}
.body > * {
  flex: 1;
  min-width: 0;
}
.resizer {
  position: absolute;
  top: 0;
  right: -3px;
  width: 6px;
  height: 100%;
  cursor: col-resize;
  z-index: 7;
}
.resizer:hover {
  background: color-mix(in srgb, var(--accent) 40%, transparent);
}
</style>
