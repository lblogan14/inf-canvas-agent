/**
 * Data-centric deliverables derived from `CanvasState`: the line list, valve
 * list, instrument index, and equipment schedule that engineering teams expect
 * out of a P&ID. Pure functions → tabular reports → CSV. No store/DOM access.
 */

import { EQUIPMENT_METADATA, type CanvasState, type CanvasNode } from '@/schema';

export interface Report {
  name: string;
  /** Suggested download filename (without extension). */
  slug: string;
  headers: string[];
  rows: string[][];
}

function tag(n: CanvasNode): string {
  return (n.label ?? '').trim();
}

export function equipmentSchedule(state: CanvasState): Report {
  const rows = state.nodes.map((n) => {
    const meta = EQUIPMENT_METADATA[n.type];
    return [
      tag(n),
      meta.label,
      meta.category,
      String(Math.round(n.position.x)),
      String(Math.round(n.position.y)),
    ];
  });
  return {
    name: 'Equipment schedule',
    slug: 'equipment-schedule',
    headers: ['Tag', 'Type', 'Category', 'X', 'Y'],
    rows,
  };
}

export function lineList(state: CanvasState): Report {
  const byId = new Map(state.nodes.map((n) => [n.id, n]));
  const rows = state.edges.map((e) => {
    const from = byId.get(e.source);
    const to = byId.get(e.target);
    return [
      e.data?.label ?? '',
      e.data?.lineType ?? 'process',
      from ? tag(from) || EQUIPMENT_METADATA[from.type].label : e.source,
      e.sourcePort,
      to ? tag(to) || EQUIPMENT_METADATA[to.type].label : e.target,
      e.targetPort,
    ];
  });
  return {
    name: 'Line list',
    slug: 'line-list',
    headers: ['Line no.', 'Service', 'From', 'From port', 'To', 'To port'],
    rows,
  };
}

function nodesByCategory(state: CanvasState, category: string): CanvasNode[] {
  return state.nodes.filter((n) => EQUIPMENT_METADATA[n.type].category === category);
}

export function valveList(state: CanvasState): Report {
  const rows = nodesByCategory(state, 'valve').map((n) => [
    tag(n),
    EQUIPMENT_METADATA[n.type].label,
  ]);
  return { name: 'Valve list', slug: 'valve-list', headers: ['Tag', 'Type'], rows };
}

export function instrumentIndex(state: CanvasState): Report {
  const byId = new Map(state.nodes.map((n) => [n.id, n]));
  const connected = (id: string): string => {
    const e = state.edges.find((x) => x.source === id || x.target === id);
    if (!e) return '';
    const other = e.source === id ? e.target : e.source;
    const n = byId.get(other);
    return n ? tag(n) || EQUIPMENT_METADATA[n.type].label : '';
  };
  const rows = nodesByCategory(state, 'instrument').map((n) => [
    tag(n),
    EQUIPMENT_METADATA[n.type].label,
    connected(n.id),
  ]);
  return {
    name: 'Instrument index',
    slug: 'instrument-index',
    headers: ['Tag', 'Type', 'Connected to'],
    rows,
  };
}

export const REPORT_BUILDERS: { key: string; label: string; build: (s: CanvasState) => Report }[] =
  [
    { key: 'equipment', label: 'Equipment schedule', build: equipmentSchedule },
    { key: 'lines', label: 'Line list', build: lineList },
    { key: 'valves', label: 'Valve list', build: valveList },
    { key: 'instruments', label: 'Instrument index', build: instrumentIndex },
  ];

function csvCell(value: string): string {
  return /[",\r\n]/.test(value) ? `"${value.replace(/"/g, '""')}"` : value;
}

export function toCsv(report: Report): string {
  const lines = [report.headers, ...report.rows].map((row) => row.map(csvCell).join(','));
  return lines.join('\r\n');
}
