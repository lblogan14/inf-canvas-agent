# Backend — Infinite Canvas Agent

FastAPI backend: the canvas command bus, WebSocket sync, JSON persistence, and
the Gemini-powered **LangGraph** agents.

## Stack

- **FastAPI** + **Uvicorn**, **Pydantic v2**
- **google-genai** (Gemini Pro/Flash) for the models
- **LangGraph** for all three agents
- **uv** (deps + runner) · **Ruff** (lint/format) · **mypy --strict** · **pytest**

## Layout

```
src/inf_canvas/
  main.py            FastAPI app factory (CORS, routers)
  config.py          settings from repo-root .env (GOOGLE_API_KEY, model ids)
  api/
    routes_canvas.py REST: list/get/save projects
    routes_agents.py REST: /agents/optimus, /agents/commander, /agents/pid/extract
    ws.py            /ws command channel (snapshot + apply + broadcast)
  schema/            Pydantic mirror of the canvas contract + command union
  canvas/
    reducer.py       pure apply_command (mirrors the TS reducer)
    store.py         CanvasRepository protocol + JsonFileRepository
    command_bus.py   authoritative state, persistence, WS broadcast
  ai/
    models/          Gemini client, structured-output schemas, prompts
    agents/          orchestrator (Optimus), pid_extractor, canvas_commander
tests/               reducer, store, command bus, tool routing
storage/             persisted projects (JSON) + uploads
```

All three agents are LangGraph graphs; Optimus delegates to the Commander graph
(a graph invoking another graph).

## Commands

```bash
uv sync                                              # create venv + install
uv run uvicorn inf_canvas.main:app --reload --port 8000
uv run pytest                                        # tests
uv run ruff check .                                  # lint
uv run ruff format .                                 # format
uv run mypy                                          # strict type-check
```

> On Windows where `uv` was installed via pip into the system Python, invoke it
> from PowerShell as `python -m uv ...` if `uv` is not on PATH.

## Configuration

Reads the **repo-root `.env`** (`backend/.env` also supported):

| Var | Default | Purpose |
| --- | --- | --- |
| `LLM_PROVIDER` | `gemini` | `gemini` (google-genai) or any LangChain provider |
| `MODEL_PRO` | `gemini-2.5-pro` | Optimus routing (role: pro) |
| `MODEL_FLASH` | `gemini-2.5-flash` | Commander / answers (role: flash) |
| `MODEL_VISION` | `gemini-3.1-pro-preview` | P&ID extraction (role: vision) |
| `GOOGLE_API_KEY` | _(empty)_ | Gemini key (other providers use their own env var) |
| `STORAGE_DIR` | `storage` | where projects/uploads live |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | CORS origin |
| `EXTRACTOR_VERIFY` | `true` | Set-of-Mark verifier pass |
| `EXTRACTOR_LINE_HYBRID` | `true` | OpenCV line-connection proposals |

`MODEL_*` are provider-agnostic (legacy `GEMINI_MODEL_*` aliases still work).

### Model providers

The agents use a small `ModelClient` interface (`ai/models/`), so the provider
is a config choice:

- **Gemini (default)** — served by `GeminiClient` (google-genai).
- **Everything else** — `LangChainClient` via `init_chat_model`; install the
  extra: `uv sync --extra providers`, then set `LLM_PROVIDER`, the `MODEL_*`
  ids, and that provider's API key.

Agent endpoints stream progress as Server-Sent Events (one event per LangGraph
node). Without a usable provider key, canvas + persistence still work; agent
endpoints return HTTP 503.
