import { describe, expect, it } from 'vitest';
import { applyCommand, emptyCanvas, type CanvasCommand } from '@/schema';

describe('applyCommand', () => {
  const base = emptyCanvas('cv_test', 'Test');

  it('adds a node', () => {
    const next = applyCommand(base, {
      op: 'add_node',
      id: 'n1',
      equipment: 'centrifugal_pump',
      position: { x: 10, y: 20 },
      label: 'P-101',
    });
    expect(next.nodes).toHaveLength(1);
    expect(next.nodes[0]).toMatchObject({ id: 'n1', type: 'centrifugal_pump', label: 'P-101' });
    expect(base.nodes).toHaveLength(0); // input not mutated
  });

  it('ignores duplicate node ids', () => {
    const cmd: CanvasCommand = {
      op: 'add_node',
      id: 'n1',
      equipment: 'gate_valve',
      position: { x: 0, y: 0 },
    };
    const once = applyCommand(base, cmd);
    const twice = applyCommand(once, cmd);
    expect(twice.nodes).toHaveLength(1);
  });

  it('removes a node and its connected edges', () => {
    const state = applyCommand(base, {
      op: 'batch',
      commands: [
        { op: 'add_node', id: 'a', equipment: 'vessel', position: { x: 0, y: 0 } },
        { op: 'add_node', id: 'b', equipment: 'storage_tank', position: { x: 200, y: 0 } },
        {
          op: 'connect',
          id: 'e1',
          source: 'a',
          sourcePort: 'bottom',
          target: 'b',
          targetPort: 'fill',
        },
      ],
    });
    expect(state.edges).toHaveLength(1);
    const after = applyCommand(state, { op: 'remove_node', id: 'a' });
    expect(after.nodes.map((n) => n.id)).toEqual(['b']);
    expect(after.edges).toHaveLength(0);
  });

  it('manages groups and prunes members when a node is removed', () => {
    let state = applyCommand(base, {
      op: 'batch',
      commands: [
        { op: 'add_node', id: 'a', equipment: 'vessel', position: { x: 0, y: 0 } },
        { op: 'add_node', id: 'b', equipment: 'storage_tank', position: { x: 200, y: 0 } },
        {
          op: 'add_group',
          id: 'g1',
          label: 'Unit 100',
          position: { x: -10, y: -10 },
          width: 300,
          height: 200,
          memberIds: ['a', 'b'],
        },
      ],
    });
    expect(state.groups).toHaveLength(1);
    state = applyCommand(state, { op: 'remove_node', id: 'a' });
    expect(state.groups[0]?.memberIds).toEqual(['b']);
    state = applyCommand(state, { op: 'remove_group', id: 'g1' });
    expect(state.groups).toHaveLength(0);
    expect(state.nodes.map((n) => n.id)).toEqual(['b']);
  });

  it('sets edge waypoints via update_edge', () => {
    let state = applyCommand(base, {
      op: 'batch',
      commands: [
        { op: 'add_node', id: 'a', equipment: 'vessel', position: { x: 0, y: 0 } },
        { op: 'add_node', id: 'b', equipment: 'storage_tank', position: { x: 200, y: 0 } },
        { op: 'connect', id: 'e1', source: 'a', sourcePort: 'bottom', target: 'b', targetPort: 'fill' },
      ],
    });
    state = applyCommand(state, {
      op: 'update_edge',
      id: 'e1',
      patch: { waypoints: [{ x: 50, y: 50 }] },
    });
    expect(state.edges[0]?.data?.waypoints).toEqual([{ x: 50, y: 50 }]);
  });

  it('applies a batch atomically in order', () => {
    const state = applyCommand(base, {
      op: 'batch',
      commands: [
        { op: 'add_node', id: 'a', equipment: 'centrifugal_pump', position: { x: 0, y: 0 } },
        { op: 'move_node', id: 'a', position: { x: 50, y: 60 } },
      ],
    });
    expect(state.nodes[0]?.position).toEqual({ x: 50, y: 60 });
  });
});
