# Infinite Canvas Agent

An infinite engineering canvas (ComfyUI-2.0 style) where AI agents read and draw
**P&IDs** (Piping & Instrumentation Diagrams). Equipment are nodes, piping are
edges. Powered by **Gemini** via **LangGraph** agents.

- **Optimus** — orchestrator that routes a request to the right specialist.
- **P&ID Extractor** — extracts equipment + connections from an uploaded image
  and places them on the canvas, **preserving relative positions**.
- **Canvas Commander** — operates the canvas from natural language
  ("add two pumps feeding a tank and connect them").

## Stack (2026)

| Layer | Tech |
| --- | --- |
| Canvas / UI | Vue 3 + Vite + TypeScript, **Vue Flow**, Pinia, Tailwind v4 |
| Backend | FastAPI + Uvicorn, Pydantic v2, WebSockets |
| AI | **LangGraph** agents; **Gemini by default**, any provider via LangChain |
| Persistence | JSON files (behind a repository interface) |
| Tooling | `frontend/`: pnpm · `backend/`: uv + Ruff + mypy + pytest |

## Architecture — one command protocol

Everything mutates the canvas through a single **Canvas Command** protocol. The
TypeScript source of truth lives in [`frontend/src/schema`](frontend/src/schema)
and is mirrored as Pydantic on the backend:

```
toolbar / agents ──► CanvasCommand ──► command bus ──► reducer (authoritative state)
                                            │                       │
                                            └── broadcast (WS) ──────┴─► all browsers
```

The frontend store and backend bus each run the **same reducer** over this
union, so human edits and AI actions share one state model (and the door is open
for Yjs/CRDT multiplayer later).

## Repository layout

```
frontend/        Vue 3 + Vue Flow app (all TypeScript lives here)
  src/schema/    shared canvas contract: state, commands, reducer, equipment
backend/         FastAPI + LangGraph agents (all Python lives here)
  src/inf_canvas/
    api/         REST routes + /ws command channel
    canvas/      reducer, JSON repository, command bus
    schema/      Pydantic mirror of the canvas contract
    ai/models/   Gemini client + structured-output schemas + prompts
    ai/agents/   Optimus, P&ID Extractor, Canvas Commander (LangGraph)
.github/         CI workflow + PR template
```

Each sub-project has its own README:
[frontend/README.md](frontend/README.md) · [backend/README.md](backend/README.md)

## Quick start

Prerequisites: **Node ≥ 22 + pnpm**, and **uv** (`pip install uv`).

```bash
# 1. secrets
cp .env.example .env        # then put your GOOGLE_API_KEY in .env

# 2. install
cd frontend && pnpm install && cd ..
cd backend  && uv sync     && cd ..
```

Run both servers (two terminals):

```bash
# terminal 1 — backend on :8000
cd backend && uv run uvicorn inf_canvas.main:app --reload --port 8000

# terminal 2 — frontend on :5173 (proxies /api and /ws to :8000)
cd frontend && pnpm dev
```

Open http://localhost:5173. Add equipment from the left palette, wire ports
together, and use the **Optimus** panel (bottom) to chat or upload a P&ID image.

## Model providers

Gemini is the default, but the agents are provider-agnostic (they talk to a
small `ModelClient` interface, not an SDK). Configure via `.env`:

- **Gemini (default)** — `LLM_PROVIDER=gemini`, set `GOOGLE_API_KEY`. Uses the
  `google-genai` SDK directly.
- **Any other provider** (OpenAI, Anthropic, Groq, …) — install the extra and
  switch the provider:
  ```bash
  cd backend && uv sync --extra providers
  # .env:
  LLM_PROVIDER=openai
  MODEL_PRO=gpt-5        # or your provider's model ids
  MODEL_FLASH=gpt-5-mini
  MODEL_VISION=gpt-5
  OPENAI_API_KEY=...
  ```
  Non-Gemini providers route through LangChain's `init_chat_model`, so anything
  it supports works. Model ids are per role (`MODEL_PRO` / `MODEL_FLASH` /
  `MODEL_VISION`; the legacy `GEMINI_MODEL_*` names still work).

## Notes

- Without a valid provider key, the canvas and persistence work fully; the AI
  endpoints return HTTP 503 with a clear message.
- Agent runs **stream progress** (each step) to the Optimus panel via SSE.
