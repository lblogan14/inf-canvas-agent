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

export interface AgentStep {
  node: string;
  label: string;
}

export interface AgentResult {
  /** Natural-language reply from the agent. */
  message: string;
  /** How many canvas commands were applied as a side effect. */
  commandsApplied: number;
}

/**
 * Consume a Server-Sent Events stream from an agent endpoint. `onStep` fires as
 * each LangGraph node completes; resolves with the final result.
 */
async function streamAgent(
  url: string,
  init: RequestInit,
  onStep?: (step: AgentStep) => void,
): Promise<AgentResult> {
  const res = await fetch(url, init);
  if (!res.ok || !res.body) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let result: AgentResult | null = null;

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let sep: number;
    while ((sep = buffer.indexOf('\n\n')) >= 0) {
      const frame = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      const dataLine = frame.split('\n').find((l) => l.startsWith('data:'));
      if (!dataLine) continue;
      const event = JSON.parse(dataLine.slice(5).trim()) as {
        type: string;
        node?: string;
        label?: string;
        message?: string;
        commandsApplied?: number;
      };
      if (event.type === 'step') {
        onStep?.({ node: event.node ?? '', label: event.label ?? '' });
      } else if (event.type === 'done') {
        result = { message: event.message ?? 'Done.', commandsApplied: event.commandsApplied ?? 0 };
      } else if (event.type === 'error') {
        throw new Error(event.message ?? 'Agent error');
      }
    }
  }
  if (!result) throw new Error('Agent stream ended without a result');
  return result;
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

  /** Optimus orchestrator: routes the message to the right sub-agent (streamed). */
  runOptimus: (canvasId: string, message: string, onStep?: (s: AgentStep) => void) =>
    streamAgent(
      `${BASE}/agents/optimus`,
      {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ canvasId, message }),
      },
      onStep,
    ),

  /** Canvas Commander: NL instruction -> canvas commands (streamed). */
  runCommander: (canvasId: string, instruction: string, onStep?: (s: AgentStep) => void) =>
    streamAgent(
      `${BASE}/agents/commander`,
      {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ canvasId, instruction }),
      },
      onStep,
    ),

  /** P&ID Extractor: upload an image, extract equipment + connections (streamed). */
  extractPID: (canvasId: string, file: File, onStep?: (s: AgentStep) => void) => {
    const form = new FormData();
    form.append('canvas_id', canvasId);
    form.append('image', file);
    return streamAgent(`${BASE}/agents/pid/extract`, { method: 'POST', body: form }, onStep);
  },
};
