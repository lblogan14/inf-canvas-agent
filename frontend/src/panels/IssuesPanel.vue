<script setup lang="ts">
import { computed } from 'vue';
import { useCanvasStore } from '@/stores/canvasStore';
import { validateCanvas } from '@/canvas/validation';

const store = useCanvasStore();

const issues = computed(() => validateCanvas(store.state));
const errorCount = computed(() => issues.value.filter((i) => i.severity === 'error').length);
const warnCount = computed(() => issues.value.filter((i) => i.severity === 'warning').length);
</script>

<template>
  <div class="issues">
    <div class="summary">
      <span class="chip err" :class="{ zero: !errorCount }">{{ errorCount }} errors</span>
      <span class="chip warn" :class="{ zero: !warnCount }">{{ warnCount }} warnings</span>
    </div>

    <div class="scroll">
      <div v-if="!issues.length" class="clean">
        <div class="clean-icon">✓</div>
        <div>No issues found.</div>
        <div class="clean-sub">Connections, tags, and ports all check out.</div>
      </div>

      <button
        v-for="issue in issues"
        :key="issue.id"
        class="issue"
        :class="issue.severity"
        @click="store.focusOn(issue.targetIds)"
      >
        <span class="ic">{{ issue.severity === 'error' ? '⛔' : '⚠️' }}</span>
        <span class="body">
          <span class="title">{{ issue.title }}</span>
          <span v-if="issue.detail" class="detail">{{ issue.detail }}</span>
        </span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.issues {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.summary {
  display: flex;
  gap: 6px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
}
.chip {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid var(--border);
}
.chip.err {
  color: var(--danger, #ef4444);
  border-color: color-mix(in srgb, var(--danger, #ef4444) 40%, transparent);
}
.chip.warn {
  color: #d97706;
  border-color: color-mix(in srgb, #d97706 40%, transparent);
}
.chip.zero {
  color: var(--text-faint);
  border-color: var(--border);
}
.scroll {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.clean {
  text-align: center;
  color: var(--text-muted);
  font-size: 12px;
  padding: 32px 12px;
}
.clean-icon {
  font-size: 28px;
  color: var(--accent);
  margin-bottom: 8px;
}
.clean-sub {
  font-size: 11px;
  color: var(--text-faint);
  margin-top: 4px;
}
.issue {
  display: flex;
  gap: 8px;
  width: 100%;
  text-align: left;
  padding: 8px;
  margin-bottom: 4px;
  border-radius: 7px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
  cursor: pointer;
}
.issue:hover {
  border-color: var(--accent);
}
.issue.error {
  border-left: 3px solid var(--danger, #ef4444);
}
.issue.warning {
  border-left: 3px solid #d97706;
}
.ic {
  flex: 0 0 auto;
  font-size: 13px;
}
.body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.title {
  font-size: 12px;
  line-height: 1.35;
}
.detail {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.35;
}
</style>
