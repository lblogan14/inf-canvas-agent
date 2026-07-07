import { reactive, ref, watch } from 'vue';
import { defineStore } from 'pinia';
import type { EquipmentType } from '@/schema';

export type LinkStyle = 'smoothstep' | 'straight' | 'step';
export type LeftTab = 'project' | 'equipment' | 'legend' | 'issues';

const STORAGE_KEY = 'inf-canvas-ui';

export const LEFT_MIN_WIDTH = 200;
export const LEFT_MAX_WIDTH = 560;

function clampWidth(w: number): number {
  return Math.min(LEFT_MAX_WIDTH, Math.max(LEFT_MIN_WIDTH, Math.round(w)));
}

interface PersistedUi {
  leftOpen: boolean;
  leftTab: LeftTab;
  leftWidth: number;
  rightOpen: boolean;
  optimusOpen: boolean;
  optimusMinimized: boolean;
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
  const leftTab = ref<LeftTab>(saved.leftTab ?? 'equipment');
  const leftWidth = ref(clampWidth(saved.leftWidth ?? 240));
  // Inspector is hidden by default; double-clicking a symbol opens it.
  const rightOpen = ref(saved.rightOpen ?? false);
  const optimusOpen = ref(saved.optimusOpen ?? true);
  const optimusMinimized = ref(saved.optimusMinimized ?? false);
  const snapToGrid = ref(saved.snapToGrid ?? false);
  const linkStyle = ref<LinkStyle>(saved.linkStyle ?? 'smoothstep');
  const favorites = ref<EquipmentType[]>(saved.favorites ?? []);
  const optimus = reactive(saved.optimus ?? { x: 260, y: 420, w: 380, h: 340 });
  // Transient (not persisted): command palette visibility.
  const commandPaletteOpen = ref(false);

  watch(
    [
      leftOpen,
      leftTab,
      leftWidth,
      rightOpen,
      optimusOpen,
      optimusMinimized,
      snapToGrid,
      linkStyle,
      favorites,
      () => ({ ...optimus }),
    ],
    () => {
      const data: PersistedUi = {
        leftOpen: leftOpen.value,
        leftTab: leftTab.value,
        leftWidth: leftWidth.value,
        rightOpen: rightOpen.value,
        optimusOpen: optimusOpen.value,
        optimusMinimized: optimusMinimized.value,
        snapToGrid: snapToGrid.value,
        linkStyle: linkStyle.value,
        favorites: favorites.value,
        optimus: { ...optimus },
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    },
    { deep: true },
  );

  function setLeftWidth(w: number): void {
    leftWidth.value = clampWidth(w);
  }

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
    leftTab,
    leftWidth,
    setLeftWidth,
    rightOpen,
    optimusOpen,
    optimusMinimized,
    snapToGrid,
    linkStyle,
    favorites,
    optimus,
    commandPaletteOpen,
    toggleFavorite,
    isFavorite,
  };
});
