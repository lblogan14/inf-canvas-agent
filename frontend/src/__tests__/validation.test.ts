import { describe, expect, it } from 'vitest';
import { emptyCanvas, type CanvasEdge, type CanvasNode, type CanvasState } from '@/schema';
import { validateCanvas } from '@/canvas/validation';

function state(nodes: CanvasNode[], edges: CanvasEdge[] = []): CanvasState {
  return { ...emptyCanvas('cv_v', 'V'), nodes, edges };
}

const pump = (id: string, label?: string): CanvasNode => ({
  id,
  type: 'centrifugal_pump',
  position: { x: 0, y: 0 },
  label,
});

describe('validateCanvas', () => {
  it('flags an isolated node', () => {
    const issues = validateCanvas(state([pump('p1', 'P-101')]));
    expect(issues.some((i) => i.id === 'isolated:p1')).toBe(true);
  });

  it('flags duplicate tags as errors targeting both nodes', () => {
    const issues = validateCanvas(state([pump('p1', 'P-101'), pump('p2', 'P-101')]));
    const dup = issues.find((i) => i.id === 'duptag:P-101');
    expect(dup?.severity).toBe('error');
    expect(dup?.targetIds.sort()).toEqual(['p1', 'p2']);
  });

  it('flags untagged equipment', () => {
    const issues = validateCanvas(state([pump('p1')]));
    expect(issues.some((i) => i.id === 'untagged:p1')).toBe(true);
  });

  it('flags a connected pump missing its discharge', () => {
    // suction connected, discharge not.
    const src: CanvasNode = { id: 'v', type: 'vessel', position: { x: 0, y: 0 }, label: 'V-1' };
    const edge: CanvasEdge = {
      id: 'e1',
      source: 'v',
      sourcePort: 'side_out',
      target: 'p1',
      targetPort: 'suction',
    };
    const issues = validateCanvas(state([src, pump('p1', 'P-101')], [edge]));
    expect(issues.some((i) => i.id === 'nodischarge:p1')).toBe(true);
    expect(issues.some((i) => i.id === 'nosuction:p1')).toBe(false);
  });

  it('flags a dangling edge endpoint as an error', () => {
    const edge: CanvasEdge = {
      id: 'e1',
      source: 'p1',
      sourcePort: 'discharge',
      target: 'ghost',
      targetPort: 'in',
    };
    const issues = validateCanvas(state([pump('p1', 'P-101')], [edge]));
    expect(issues.some((i) => i.id === 'dangling:e1' && i.severity === 'error')).toBe(true);
  });

  it('flags a signal line not touching an instrument', () => {
    const a = pump('p1', 'P-101');
    const b: CanvasNode = { id: 'v', type: 'vessel', position: { x: 0, y: 0 }, label: 'V-1' };
    const edge: CanvasEdge = {
      id: 'e1',
      source: 'p1',
      sourcePort: 'discharge',
      target: 'v',
      targetPort: 'side_in',
      data: { lineType: 'signal' },
    };
    const issues = validateCanvas(state([a, b], [edge]));
    expect(issues.some((i) => i.id === 'signal-noinstr:e1')).toBe(true);
  });

  it('returns no issues for a tagged, well-connected pair', () => {
    const v: CanvasNode = { id: 'v', type: 'vessel', position: { x: 0, y: 0 }, label: 'V-1' };
    const p = pump('p1', 'P-101');
    const t: CanvasNode = { id: 't', type: 'storage_tank', position: { x: 0, y: 0 }, label: 'T-1' };
    const e1: CanvasEdge = {
      id: 'e1',
      source: 'v',
      sourcePort: 'side_out',
      target: 'p1',
      targetPort: 'suction',
    };
    const e2: CanvasEdge = {
      id: 'e2',
      source: 'p1',
      sourcePort: 'discharge',
      target: 't',
      targetPort: 'fill',
    };
    // v has an inlet unused (side_in) but vessels aren't pump/compressor so no port rule;
    // it is connected, tagged -> clean. tank connected + tagged. pump both ports used.
    const issues = validateCanvas(state([v, p, t], [e1, e2]));
    expect(issues).toEqual([]);
  });
});
