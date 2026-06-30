# Frontend — Infinite Canvas Agent

Vue 3 + Vite + TypeScript app built on **Vue Flow**. Renders the infinite canvas,
ISA/ISO equipment symbols, and the Optimus agent panel. State is driven by the
shared Canvas Command protocol.

## Stack

- **Vue 3** (`<script setup>`) + **Vite 6** + **TypeScript** (strict)
- **Vue Flow** (`@vue-flow/core`) — node/edge/handle canvas
- **Pinia** — state store wrapping the command reducer
- **Tailwind CSS v4** — styling
- **Vitest** — unit tests · **ESLint + Prettier** — lint/format

## Layout

```
src/
  schema/            shared canvas contract (state, commands, reducer, equipment)
  canvas/
    CanvasView.vue   <VueFlow> host: pan/zoom, minimap, controls
    nodes/           EquipmentNode + ISA/ISO SVG symbols + registry
    edges/           PipeEdge (process/signal line styles)
  stores/
    canvasStore.ts   Pinia store: canonical state + applyCommand reducer
  realtime/ws.ts     WebSocket client → applies broadcast commands
  panels/            Toolbar, AgentPanel (Optimus), InspectorPanel
  api/client.ts      REST calls (projects, agents, P&ID upload)
```

`@/` is aliased to `src/` (see `vite.config.ts` / `tsconfig.json`). The shared
contract is imported as `@/schema`.

## Commands

```bash
pnpm install        # install deps
pnpm dev            # dev server on :5173 (proxies /api + /ws to :8000)
pnpm build          # type-check + production build
pnpm preview        # preview the production build
pnpm typecheck      # vue-tsc --noEmit
pnpm test           # vitest run
pnpm lint           # eslint (report only)
pnpm lint:fix       # eslint --fix
pnpm format         # prettier --write src
```

## Notes

- The backend must be running on :8000 for persistence and agents; the Vite dev
  server proxies `/api` and `/ws` to it.
- `pnpm-workspace.yaml` here exists only to approve native build scripts
  (esbuild, vue-demi) for pnpm — this is a single-project setup, not a monorepo.
