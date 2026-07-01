import { getEquipmentMeta, type CanvasEdge, type CanvasNode, type Position } from '@/schema';

interface ElkEngine {
  layout(graph: unknown): Promise<ElkResult>;
}

// Lazy-load ELK so its ~1.4 MB bundle stays out of the initial app load and is
// only fetched the first time auto-layout runs.
let elkInstance: ElkEngine | null = null;
async function getElk(): Promise<ElkEngine> {
  if (!elkInstance) {
    const mod = await import('elkjs/lib/elk.bundled.js');
    const ELK = mod.default as new () => ElkEngine;
    elkInstance = new ELK();
  }
  return elkInstance;
}

export interface NodeMove {
  id: string;
  x: number;
  y: number;
}

export interface EdgeRoute {
  id: string;
  waypoints: Position[];
}

export interface AutoLayoutResult {
  moves: NodeMove[];
  edges: EdgeRoute[];
}

interface ElkPoint {
  x: number;
  y: number;
}
interface ElkResult {
  children?: { id: string; x?: number; y?: number }[];
  edges?: { id: string; sections?: { bendPoints?: ElkPoint[] }[] }[];
}

/**
 * Compute a clean left-to-right layout with ELK: non-overlapping node placement
 * plus ORTHOGONAL edge routing. The edge bend points become pipe waypoints, so
 * pipes route around equipment instead of crossing through it.
 */
export async function computeAutoLayout(
  nodes: CanvasNode[],
  edges: CanvasEdge[],
): Promise<AutoLayoutResult> {
  if (!nodes.length) return { moves: [], edges: [] };

  const graph = {
    id: 'root',
    layoutOptions: {
      'elk.algorithm': 'layered',
      'elk.direction': 'RIGHT',
      'elk.edgeRouting': 'ORTHOGONAL',
      'elk.spacing.nodeNode': '60',
      'elk.layered.spacing.nodeNodeBetweenLayers': '110',
      'elk.spacing.edgeNode': '30',
      'elk.spacing.edgeEdge': '22',
      'elk.layered.spacing.edgeEdgeBetweenLayers': '22',
    },
    children: nodes.map((n) => {
      const { size } = getEquipmentMeta(n.type);
      return { id: n.id, width: size.width, height: size.height };
    }),
    edges: edges.map((e) => ({ id: e.id, sources: [e.source], targets: [e.target] })),
  };

  const elk = await getElk();
  const laidOut = await elk.layout(graph);

  const moves: NodeMove[] = (laidOut.children ?? []).map((c) => ({
    id: c.id,
    x: c.x ?? 0,
    y: c.y ?? 0,
  }));

  const routes: EdgeRoute[] = (laidOut.edges ?? []).map((e) => {
    const section = e.sections?.[0];
    const waypoints: Position[] = (section?.bendPoints ?? []).map((p) => ({ x: p.x, y: p.y }));
    return { id: e.id, waypoints };
  });

  return { moves, edges: routes };
}
