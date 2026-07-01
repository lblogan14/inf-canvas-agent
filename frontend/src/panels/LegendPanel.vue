<script setup lang="ts">
import type { LineType } from '@/schema';
import { LINE_STYLES } from '@/canvas/edges/lineStyles';

const order: LineType[] = ['process', 'signal', 'electrical', 'pneumatic'];
const entries = order.map((key) => ({ key, ...LINE_STYLES[key] }));
</script>

<template>
  <div class="legend">
    <div class="scroll">
      <p class="intro">
        Connections between equipment are drawn as pipes and signal lines. The
        <strong>line style</strong> encodes the connection type, following ISA-5.1 conventions.
      </p>

      <section class="block">
        <div class="block-head">Line types</div>
        <div v-for="e in entries" :key="e.key" class="row">
          <svg class="sample" viewBox="0 0 64 16" preserveAspectRatio="none" aria-hidden="true">
            <line x1="2" y1="8" x2="62" y2="8" :stroke-width="e.width" :stroke-dasharray="e.dash" />
          </svg>
          <div class="text">
            <div class="row-label">{{ e.label }}</div>
            <div class="row-desc">{{ e.description }}</div>
          </div>
        </div>
      </section>

      <section class="block">
        <div class="block-head">Reading a connection</div>
        <ul class="notes">
          <li><strong>Solid, heavy</strong> lines are process piping (material flow).</li>
          <li>
            <strong>Dashed / dotted</strong> lines are instrument, electrical, or pneumatic signals.
          </li>
          <li>
            The <strong>arrowhead</strong> points from upstream to downstream (flow direction).
          </li>
          <li>Line weight also helps: process piping is drawn thicker than signal lines.</li>
        </ul>
      </section>

      <section class="block">
        <div class="block-head">Editing connections</div>
        <ul class="notes">
          <li>Drag from a node's port handle to another port to create a connection.</li>
          <li>
            Select a pipe, then use the <strong>Inspector</strong> to change its type or add a line
            number.
          </li>
          <li>
            With a pipe selected, drag the round handles to <strong>reroute</strong> it;
            double-click a handle to remove that bend.
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<style scoped>
.legend {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.scroll {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}
.intro {
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-muted);
  margin: 0 0 14px;
}
.block {
  margin-bottom: 16px;
}
.block-head {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-faint);
  margin-bottom: 8px;
}
.row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.sample {
  flex: 0 0 64px;
  width: 64px;
  height: 16px;
}
.sample line {
  stroke: var(--edge);
}
.text {
  min-width: 0;
}
.row-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
}
.row-desc {
  font-size: 11px;
  line-height: 1.4;
  color: var(--text-muted);
}
.notes {
  margin: 0;
  padding-left: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.notes li {
  font-size: 11px;
  line-height: 1.45;
  color: var(--text-muted);
}
.notes strong {
  color: var(--text);
}
</style>
