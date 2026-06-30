<script setup lang="ts">
export interface MenuItem {
  label?: string;
  action?: () => void;
  disabled?: boolean;
  danger?: boolean;
  separator?: boolean;
}

defineProps<{ x: number; y: number; items: MenuItem[] }>();
const emit = defineEmits<{ close: [] }>();

function run(item: MenuItem): void {
  if (item.disabled || item.separator) return;
  item.action?.();
  emit('close');
}
</script>

<template>
  <div class="ctx-backdrop" @click="emit('close')" @contextmenu.prevent="emit('close')" />
  <div class="ctx-menu" :style="{ left: `${x}px`, top: `${y}px` }">
    <template v-for="(item, i) in items" :key="i">
      <div v-if="item.separator" class="ctx-sep" />
      <button
        v-else
        class="ctx-item"
        :class="{ danger: item.danger }"
        :disabled="item.disabled"
        @click="run(item)"
      >
        {{ item.label }}
      </button>
    </template>
  </div>
</template>

<style scoped>
.ctx-backdrop {
  position: fixed;
  inset: 0;
  z-index: 60;
}
.ctx-menu {
  position: fixed;
  z-index: 61;
  min-width: 180px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}
.ctx-item {
  display: block;
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
.ctx-item:hover:not(:disabled) {
  background: var(--surface-3);
}
.ctx-item:disabled {
  opacity: 0.4;
  cursor: default;
}
.ctx-item.danger:hover:not(:disabled) {
  color: var(--danger);
}
.ctx-sep {
  height: 1px;
  background: var(--border);
  margin: 4px 0;
}
</style>
