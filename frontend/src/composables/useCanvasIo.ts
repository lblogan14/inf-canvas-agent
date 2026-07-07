import { toPng } from 'html-to-image';
import { useVueFlow } from '@vue-flow/core';
import { useCanvasStore } from '@/stores/canvasStore';
import { api } from '@/api/client';
import type { CanvasState } from '@/schema';

function triggerDownload(url: string, filename: string): void {
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
}

function freshId(): string {
  return `cv_${crypto.randomUUID().slice(0, 8)}`;
}

export function useCanvasIo() {
  const store = useCanvasStore();
  const { vueFlowRef } = useVueFlow('main');

  function exportJson(): void {
    const blob = new Blob([JSON.stringify(store.state, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    triggerDownload(url, `${store.state.meta.name || 'canvas'}.json`);
    URL.revokeObjectURL(url);
  }

  async function importJsonFile(file: File): Promise<void> {
    const data = JSON.parse(await file.text()) as Partial<CanvasState>;
    if (!data || !data.meta || !Array.isArray(data.nodes) || !Array.isArray(data.edges)) {
      throw new Error('Not a valid canvas .json file');
    }
    // Import as a NEW canvas, then persist before the WS reconnects to its id
    // (otherwise the snapshot for an unknown id would wipe the import).
    const fresh: CanvasState = {
      meta: {
        ...data.meta,
        id: freshId(),
        name: data.meta.name || file.name.replace(/\.json$/, ''),
      },
      nodes: data.nodes,
      edges: data.edges,
      groups: data.groups ?? [],
    };
    await api.saveProject(fresh);
    store.loadState(fresh);
    store.requestFit();
  }

  async function exportPng(): Promise<void> {
    const el = vueFlowRef.value;
    if (!el) return;
    const bg =
      getComputedStyle(document.documentElement).getPropertyValue('--bg').trim() || '#0f172a';
    const dataUrl = await toPng(el, {
      backgroundColor: bg,
      filter: (node) => {
        const cl = (node as HTMLElement).classList;
        if (!cl) return true;
        return !cl.contains('vue-flow__minimap') && !cl.contains('vue-flow__controls');
      },
    });
    triggerDownload(dataUrl, `${store.state.meta.name || 'canvas'}.png`);
  }

  return { exportJson, importJsonFile, exportPng };
}
