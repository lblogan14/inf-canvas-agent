import { reactive, ref, watch } from 'vue';
import { defineStore } from 'pinia';
import type { EquipmentType } from '@/schema';

export type LinkStyle = 'smoothstep' | 'straight' | 'step';

const STORAGE_KEY = 'inf-canvas-ui';

interface PersistedUi {
  leftOpen: boolean;
  rightOpen: boolean;
  optimusOpen: boolean;
  snapToGrid: boolean;
  linkStyle: LinkStyle;
  favorites: EquipmentType[];
  optimus: { x: number; y: number; w: number; h: number };
}

function load(): Partial<PersistedUi> {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '{}') as Partial<PersistedUi>;
  } catch {
    return {};
  }
}

/** UI/view preferences (separate from canvas data). Persisted to localStorage. */
export const useUiStore = defineStore('ui', () => {
  const saved = load();

  const leftOpen = ref(saved.leftOpen ?? true);
  const rightOpen = ref(saved.rightOpen ?? true);
  const optimusOpen = ref(saved.optimusOpen ?? true);
  const snapToGrid = ref(saved.snapToGrid ?? false);
  const linkStyle = ref<LinkStyle>(saved.linkStyle ?? 'smoothstep');
  const favorites = ref<EquipmentType[]>(saved.favorites ?? []);
  const optimus = reactive(saved.optimus ?? { x: 260, y: 420, w: 380, h: 340 });

  watch(
    [leftOpen, rightOpen, optimusOpen, snapToGrid, linkStyle, favorites, () => ({ ...optimus })],
    () => {
      const data: PersistedUi = {
        leftOpen: leftOpen.value,
        rightOpen: rightOpen.value,
        optimusOpen: optimusOpen.value,
        snapToGrid: snapToGrid.value,
        linkStyle: linkStyle.value,
        favorites: favorites.value,
        optimus: { ...optimus },
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    },
    { deep: true },
  );

  function toggleFavorite(type: EquipmentType): void {
    const i = favorites.value.indexOf(type);
    if (i >= 0) favorites.value.splice(i, 1);
    else favorites.value.push(type);
  }

  function isFavorite(type: EquipmentType): boolean {
    return favorites.value.includes(type);
  }

  return {
    leftOpen,
    rightOpen,
    optimusOpen,
    snapToGrid,
    linkStyle,
    favorites,
    optimus,
    toggleFavorite,
    isFavorite,
  };
});
