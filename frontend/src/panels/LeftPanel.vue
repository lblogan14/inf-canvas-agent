<script setup lang="ts">
import { useUiStore, type LeftTab } from '@/stores/uiStore';
import ProjectPanel from './ProjectPanel.vue';
import NodeLibrary from './NodeLibrary.vue';
import LegendPanel from './LegendPanel.vue';

const ui = useUiStore();

const tabs: { key: LeftTab; label: string; icon: string; title: string }[] = [
  { key: 'project', label: 'Project', icon: '📁', title: 'Project' },
  { key: 'equipment', label: 'Equipment', icon: '⚙️', title: 'Equipment templates' },
  { key: 'legend', label: 'Legend', icon: '〰️', title: 'Connection legend' },
];
</script>

<template>
  <aside class="left-panel">
    <div class="tab-bar">
      <button
        v-for="t in tabs"
        :key="t.key"
        class="tab"
        :class="{ active: ui.leftTab === t.key }"
        :title="t.title"
        @click="ui.leftTab = t.key"
      >
        <span class="ti">{{ t.icon }}</span
        ><span class="tl">{{ t.label }}</span>
      </button>
      <button class="collapse" title="Hide panel" @click="ui.leftOpen = false">‹</button>
    </div>

    <ProjectPanel v-show="ui.leftTab === 'project'" />
    <NodeLibrary v-show="ui.leftTab === 'equipment'" />
    <LegendPanel v-show="ui.leftTab === 'legend'" />
  </aside>
</template>

<style scoped>
.left-panel {
  display: flex;
  flex-direction: column;
  width: 240px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  height: 100%;
  overflow: hidden;
}
.tab-bar {
  display: flex;
  align-items: stretch;
  border-bottom: 1px solid var(--border);
}
.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 8px 4px;
  font-size: 11px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-muted);
  cursor: pointer;
}
.tab:hover {
  color: var(--text);
  background: var(--surface-3);
}
.tab.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
.ti {
  font-size: 13px;
}
.collapse {
  flex: 0 0 auto;
  padding: 0 8px;
  background: none;
  border: none;
  border-left: 1px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
}
.collapse:hover {
  color: var(--accent);
}
@media (max-width: 1100px) {
  .tl {
    display: none;
  }
}
</style>
