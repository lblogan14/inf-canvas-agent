<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { EQUIPMENT_METADATA, EQUIPMENT_TYPES, type EquipmentType } from '@/schema';
import { useCanvasStore } from '@/stores/canvasStore';
import { useUiStore } from '@/stores/uiStore';

const store = useCanvasStore();
const ui = useUiStore();
const search = ref('');
const collapsed = reactive<Record<string, boolean>>({});
let cascade = 0;

interface Group {
  category: string;
  types: EquipmentType[];
}

const groups = computed<Group[]>(() => {
  const q = search.value.trim().toLowerCase();
  const byCat: Record<string, EquipmentType[]> = {};
  for (const t of EQUIPMENT_TYPES) {
    const meta = EQUIPMENT_METADATA[t];
    if (q && !meta.label.toLowerCase().includes(q) && !t.includes(q)) continue;
    (byCat[meta.category] ??= []).push(t);
  }
  return Object.entries(byCat).map(([category, types]) => ({ category, types }));
});

const favorites = computed(() =>
  ui.favorites.filter((t) => {
    const q = search.value.trim().toLowerCase();
    return !q || EQUIPMENT_METADATA[t].label.toLowerCase().includes(q);
  }),
);

function add(type: EquipmentType): void {
  cascade = (cascade + 1) % 8;
  store.addEquipment(type, { x: 240 + cascade * 28, y: 160 + cascade * 28 });
}

function onDragStart(event: DragEvent, type: EquipmentType): void {
  event.dataTransfer?.setData('application/inf-equipment', type);
  if (event.dataTransfer) event.dataTransfer.effectAllowed = 'move';
}
</script>

<template>
  <aside class="library">
    <div class="search-row">
      <input v-model="search" class="search" placeholder="Search equipment…" />
      <button class="collapse" title="Hide library" @click="ui.leftOpen = false">‹</button>
    </div>

    <div class="scroll">
      <section v-if="favorites.length" class="group">
        <div class="group-head">★ Favorites</div>
        <button
          v-for="t in favorites"
          :key="`fav-${t}`"
          class="item"
          draggable="true"
          @click="add(t)"
          @dragstart="onDragStart($event, t)"
        >
          <span class="item-label">{{ EQUIPMENT_METADATA[t].label }}</span>
          <span class="star active" title="Unfavorite" @click.stop="ui.toggleFavorite(t)">★</span>
        </button>
      </section>

      <section v-for="g in groups" :key="g.category" class="group">
        <button
          class="group-head clickable"
          @click="collapsed[g.category] = !collapsed[g.category]"
        >
          <span class="chevron">{{ collapsed[g.category] ? '▸' : '▾' }}</span>
          {{ g.category }}
        </button>
        <template v-if="!collapsed[g.category]">
          <button
            v-for="t in g.types"
            :key="t"
            class="item"
            draggable="true"
            @click="add(t)"
            @dragstart="onDragStart($event, t)"
          >
            <span class="item-label">{{ EQUIPMENT_METADATA[t].label }}</span>
            <span
              class="star"
              :class="{ active: ui.isFavorite(t) }"
              :title="ui.isFavorite(t) ? 'Unfavorite' : 'Favorite'"
              @click.stop="ui.toggleFavorite(t)"
              >★</span
            >
          </button>
        </template>
      </section>

      <div v-if="!groups.length && !favorites.length" class="empty">No matches.</div>
    </div>
  </aside>
</template>

<style scoped>
.library {
  display: flex;
  flex-direction: column;
  width: 220px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  height: 100%;
  overflow: hidden;
}
.search-row {
  display: flex;
  gap: 6px;
  align-items: center;
  padding: 8px;
  border-bottom: 1px solid var(--border);
}
.collapse {
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text-muted);
  border-radius: 6px;
  cursor: pointer;
  padding: 4px 8px;
}
.collapse:hover {
  color: var(--accent);
  border-color: var(--accent);
}
.search {
  flex: 1;
  font-size: 12px;
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
}
.scroll {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.group {
  margin-bottom: 8px;
}
.group-head {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-faint);
  margin: 6px 0 4px;
  background: none;
  border: none;
  padding: 0;
  text-align: left;
}
.group-head.clickable {
  cursor: pointer;
}
.chevron {
  width: 10px;
}
.item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  text-align: left;
  font-size: 12px;
  padding: 5px 8px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
  cursor: grab;
  margin-bottom: 3px;
}
.item:hover {
  border-color: var(--accent);
  color: var(--accent);
}
.item:active {
  cursor: grabbing;
}
.star {
  color: var(--text-faint);
  opacity: 0.5;
  font-size: 12px;
}
.star:hover {
  opacity: 1;
}
.star.active {
  color: var(--accent);
  opacity: 1;
}
.empty {
  font-size: 12px;
  color: var(--text-faint);
  padding: 8px;
}
</style>
