import dagre from '@dagrejs/dagre';
import { getEquipmentMeta, type CanvasEdge, type CanvasNode } from '@/schema';

export interface LayoutMove {
  id: string;
  x: number;
  y: number;
}

/**
 * Compute a clean left-to-right graph layout (dagre) for the given nodes/edges.
 * Returns new top-left positions. Unlike the extractor's overlap resolution,
 * this re-arranges the whole graph, so it's a deliberate user action.
 */
export function computeAutoLayout(nodes: CanvasNode[], edges: CanvasEdge[]): LayoutMove[] {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: 'LR', nodesep: 48, ranksep: 96, marginx: 40, marginy: 40 });
  g.setDefaultEdgeLabel(() => ({}));

  for (const n of nodes) {
    const { size } = getEquipmentMeta(n.type);
    g.setNode(n.id, { width: size.width, height: size.height });
  }
  for (const e of edges) {
    if (g.hasNode(e.source) && g.hasNode(e.target)) g.setEdge(e.source, e.target);
  }

  dagre.layout(g);

  return nodes.map((n) => {
    const pos = g.node(n.id);
    // dagre returns node centers; Vue Flow positions are top-left.
    return { id: n.id, x: pos.x - pos.width / 2, y: pos.y - pos.height / 2 };
  });
}
