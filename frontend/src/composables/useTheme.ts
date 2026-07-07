import { ref, watchEffect } from 'vue';

export type Theme = 'light' | 'dark';

const STORAGE_KEY = 'inf-canvas-theme';

function initialTheme(): Theme {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved === 'light' || saved === 'dark') return saved;
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
}

// Module-level singleton so every component shares one reactive theme.
const theme = ref<Theme>(initialTheme());

watchEffect(() => {
  document.documentElement.setAttribute('data-theme', theme.value);
  localStorage.setItem(STORAGE_KEY, theme.value);
});

export function useTheme() {
  function toggle(): void {
    theme.value = theme.value === 'dark' ? 'light' : 'dark';
  }
  function set(next: Theme): void {
    theme.value = next;
  }
  return { theme, toggle, set };
}
