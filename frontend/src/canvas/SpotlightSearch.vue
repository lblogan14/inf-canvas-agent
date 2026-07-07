<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { EQUIPMENT_METADATA, EQUIPMENT_TYPES, type EquipmentType } from '@/schema';

defineProps<{ x: number; y: number }>();
const emit = defineEmits<{ select: [type: EquipmentType]; close: [] }>();

const query = ref('');
const active = ref(0);
const inputEl = ref<HTMLInputElement | null>(null);

const results = computed<EquipmentType[]>(() => {
  const q = query.value.trim().toLowerCase();
  return EQUIPMENT_TYPES.filter((t) => {
    if (!q) return true;
    return EQUIPMENT_METADATA[t].label.toLowerCase().includes(q) || t.includes(q);
  }).slice(0, 8);
});

function choose(type: EquipmentType): void {
  emit('select', type);
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
    const pick = results.value[active.value];
    if (pick) choose(pick);
  } else if (e.key === 'Escape') {
    emit('close');
  }
}

onMounted(() => inputEl.value?.focus());
</script>

<template>
  <div class="sp-backdrop" @click="emit('close')" @contextmenu.prevent="emit('close')" />
  <div class="spotlight" :style="{ left: `${x}px`, top: `${y}px` }">
    <input
      ref="inputEl"
      v-model="query"
      class="sp-input"
      placeholder="Add equipment…"
      @keydown="onKey"
      @input="active = 0"
    />
    <div class="sp-list">
      <button
        v-for="(t, i) in results"
        :key="t"
        class="sp-item"
        :class="{ active: i === active }"
        @click="choose(t)"
        @mouseenter="active = i"
      >
        {{ EQUIPMENT_METADATA[t].label }}
      </button>
      <div v-if="!results.length" class="sp-empty">No matches</div>
    </div>
  </div>
</template>

<style scoped>
.sp-backdrop {
  position: fixed;
  inset: 0;
  z-index: 60;
}
.spotlight {
  position: fixed;
  z-index: 61;
  width: 240px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}
.sp-input {
  width: 100%;
  font-size: 13px;
  padding: 7px 9px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
  margin-bottom: 4px;
}
.sp-list {
  max-height: 240px;
  overflow-y: auto;
}
.sp-item {
  display: block;
  width: 100%;
  text-align: left;
  font-size: 13px;
  padding: 6px 9px;
  border-radius: 6px;
  background: none;
  border: none;
  color: var(--text);
  cursor: pointer;
}
.sp-item.active,
.sp-item:hover {
  background: var(--surface-3);
}
.sp-empty {
  font-size: 12px;
  color: var(--text-faint);
  padding: 6px 9px;
}
</style>
