import type { CanvasState } from '@/schema';

const BASE = '/api';

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export interface ProjectSummary {
  id: string;
  name: string;
  updatedAt?: string;
}

export interface AgentResult {
  /** Natural-language reply from the agent. */
  message: string;
  /** How many canvas commands were applied as a side effect. */
  commandsApplied: number;
}

export const api = {
  listProjects: (): Promise<ProjectSummary[]> =>
    fetch(`${BASE}/projects`).then((r) => json<ProjectSummary[]>(r)),

  getProject: (id: string): Promise<CanvasState> =>
    fetch(`${BASE}/projects/${id}`).then((r) => json<CanvasState>(r)),

  saveProject: (state: CanvasState): Promise<CanvasState> =>
    fetch(`${BASE}/projects/${state.meta.id}`, {
      method: 'PUT',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(state),
    }).then((r) => json<CanvasState>(r)),

  /** Optimus orchestrator: routes the message to the right sub-agent. */
  runOptimus: (canvasId: string, message: string): Promise<AgentResult> =>
    fetch(`${BASE}/agents/optimus`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ canvasId, message }),
    }).then((r) => json<AgentResult>(r)),

  /** Canvas Commander: NL instruction -> canvas commands. */
  runCommander: (canvasId: string, instruction: string): Promise<AgentResult> =>
    fetch(`${BASE}/agents/commander`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ canvasId, instruction }),
    }).then((r) => json<AgentResult>(r)),

  /** P&ID Extractor: upload an image, extract equipment + connections. */
  extractPID: (canvasId: string, file: File): Promise<AgentResult> => {
    const form = new FormData();
    form.append('canvas_id', canvasId);
    form.append('image', file);
    return fetch(`${BASE}/agents/pid/extract`, { method: 'POST', body: form }).then((r) =>
      json<AgentResult>(r),
    );
  },
};
