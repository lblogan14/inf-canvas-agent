/**
 * P&ID rule-checker. Pure functions over `CanvasState` → a list of issues,
 * so the same logic can back the Issues panel and (later) an agent self-check.
 * No side effects, no store access — give it a state, get back findings.
 */

import { EQUIPMENT_METADATA, type CanvasState, type CanvasNode } from '@/schema';

export type IssueSeverity = 'error' | 'warning';

export interface Issue {
  /** Stable-ish key for list rendering. */
  id: string;
  severity: IssueSeverity;
  title: string;
  detail?: string;
  /** Node/edge ids to select + focus when the issue is clicked. */
  targetIds: string[];
}

function nodeLabel(n: CanvasNode): string {
  return (n.label ?? '').trim() || EQUIPMENT_METADATA[n.type].label;
}

export function validateCanvas(state: CanvasState): Issue[] {
  const errors: Issue[] = [];
  const warnings: Issue[] = [];

  const nodesById = new Map(state.nodes.map((n) => [n.id, n]));
  const degree = new Map<string, number>();
  const portsUsed = new Map<string, Set<string>>();
  const use = (nodeId: string, port: string): void => {
    degree.set(nodeId, (degree.get(nodeId) ?? 0) + 1);
    (portsUsed.get(nodeId) ?? portsUsed.set(nodeId, new Set()).get(nodeId)!).add(port);
  };

  // --- edge-level checks + degree/port tallies ---------------------------
  for (const e of state.edges) {
    const s = nodesById.get(e.source);
    const t = nodesById.get(e.target);
    if (!s || !t) {
      errors.push({
        id: `dangling:${e.id}`,
        severity: 'error',
        title: 'Connection references a missing node',
        targetIds: [e.id],
      });
      continue;
    }
    if (e.source === e.target) {
      errors.push({
        id: `selfloop:${e.id}`,
        severity: 'error',
        title: `${nodeLabel(s)} is connected to itself`,
        targetIds: [e.id, e.source],
      });
      continue;
    }
    use(e.source, e.sourcePort);
    use(e.target, e.targetPort);

    const lineType = e.data?.lineType ?? 'process';
    const sInstr = EQUIPMENT_METADATA[s.type].category === 'instrument';
    const tInstr = EQUIPMENT_METADATA[t.type].category === 'instrument';
    if (lineType === 'signal' && !sInstr && !tInstr) {
      warnings.push({
        id: `signal-noinstr:${e.id}`,
        severity: 'warning',
        title: 'Signal line not connected to an instrument',
        detail: `${nodeLabel(s)} → ${nodeLabel(t)}`,
        targetIds: [e.id],
      });
    }
    if (lineType === 'process' && (sInstr || tInstr)) {
      warnings.push({
        id: `process-toinstr:${e.id}`,
        severity: 'warning',
        title: 'Process line connected to an instrument',
        detail: `Expected a signal line: ${nodeLabel(s)} → ${nodeLabel(t)}`,
        targetIds: [e.id],
      });
    }
  }

  // --- duplicate tags ----------------------------------------------------
  const byTag = new Map<string, string[]>();
  for (const n of state.nodes) {
    const tag = (n.label ?? '').trim();
    if (!tag) continue;
    (byTag.get(tag) ?? byTag.set(tag, []).get(tag)!).push(n.id);
  }
  for (const [tag, ids] of byTag) {
    if (ids.length > 1) {
      errors.push({
        id: `duptag:${tag}`,
        severity: 'error',
        title: `Duplicate tag "${tag}"`,
        detail: `${ids.length} equipment items share this tag`,
        targetIds: ids,
      });
    }
  }

  // --- node-level checks -------------------------------------------------
  for (const n of state.nodes) {
    const meta = EQUIPMENT_METADATA[n.type];
    const deg = degree.get(n.id) ?? 0;

    if (deg === 0) {
      warnings.push(
        meta.category === 'instrument'
          ? {
              id: `orphan-instr:${n.id}`,
              severity: 'warning',
              title: `Instrument ${nodeLabel(n)} has no signal connection`,
              targetIds: [n.id],
            }
          : {
              id: `isolated:${n.id}`,
              severity: 'warning',
              title: `${nodeLabel(n)} is not connected to anything`,
              targetIds: [n.id],
            },
      );
    } else if (meta.category === 'pump' || meta.category === 'compressor') {
      // A connected pump/compressor should have both a suction and a discharge.
      const used = portsUsed.get(n.id) ?? new Set<string>();
      const inlets = meta.ports.filter((p) => p.role === 'inlet').map((p) => p.id);
      const outlets = meta.ports.filter((p) => p.role === 'outlet').map((p) => p.id);
      if (inlets.length && !inlets.some((id) => used.has(id))) {
        warnings.push({
          id: `nosuction:${n.id}`,
          severity: 'warning',
          title: `${nodeLabel(n)} has no suction (inlet) connection`,
          targetIds: [n.id],
        });
      }
      if (outlets.length && !outlets.some((id) => used.has(id))) {
        warnings.push({
          id: `nodischarge:${n.id}`,
          severity: 'warning',
          title: `${nodeLabel(n)} has no discharge (outlet) connection`,
          targetIds: [n.id],
        });
      }
    }

    if (!(n.label ?? '').trim()) {
      warnings.push({
        id: `untagged:${n.id}`,
        severity: 'warning',
        title: `${meta.label} is untagged`,
        detail: 'Add a tag (e.g. P-101) in the Inspector',
        targetIds: [n.id],
      });
    }
  }

  return [...errors, ...warnings];
}
