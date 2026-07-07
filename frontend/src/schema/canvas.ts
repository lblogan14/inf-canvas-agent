/** Authoritative canvas data model. Persisted as JSON; shared by both sides. */

import type { EquipmentType } from './equipment';

export interface Position {
  x: number;
  y: number;
}

export interface CanvasNode {
  id: string;
  type: EquipmentType;
  position: Position;
  /** Tag / display label, e.g. "P-101". */
  label?: string;
  /** Rotation in degrees (0, 90, 180, 270). */
  rotation?: number;
  /** Free-form attributes (tag number, design specs, source bbox, ...). */
  data?: Record<string, unknown>;
}

export type LineType = 'process' | 'signal' | 'electrical' | 'pneumatic';

export interface PipeData {
  lineType?: LineType;
  /** Line number / pipe spec, e.g. '6"-P-1001-CS'. */
  label?: string;
  animated?: boolean;
  /** Manual routing points the pipe passes through (reroute). */
  waypoints?: Position[];
}

export interface CanvasEdge {
  id: string;
  source: string;
  sourcePort: string;
  target: string;
  targetPort: string;
  data?: PipeData;
}

/** A titled background region grouping equipment (e.g. by unit/system). */
export interface CanvasGroup {
  id: string;
  label: string;
  position: Position;
  width: number;
  height: number;
  color?: string;
  /** Node ids that move with the group. */
  memberIds: string[];
}

export interface CanvasMeta {
  id: string;
  name: string;
  /** ISO-8601 timestamps. */
  createdAt?: string;
  updatedAt?: string;
}

export interface CanvasState {
  meta: CanvasMeta;
  nodes: CanvasNode[];
  edges: CanvasEdge[];
  groups: CanvasGroup[];
}

export function emptyCanvas(id: string, name: string): CanvasState {
  return {
    meta: { id, name },
    nodes: [],
    edges: [],
    groups: [],
  };
}
