# Summary

<!-- What does this PR do and why? Link any related issue (Closes #123). -->

## Changes

<!-- Bullet the key changes. Note frontend vs backend if relevant. -->

-

## Area

- [ ] Frontend (`frontend/`)
- [ ] Backend (`backend/`)
- [ ] Canvas contract / command protocol (`frontend/src/schema` + `backend/.../schema`)
- [ ] AI agents (`backend/src/inf_canvas/ai/`)
- [ ] CI / tooling / docs

## Checklist

- [ ] If the canvas command protocol changed, the **TS schema and the Python
      mirror were updated together** (and both reducers stay in sync).
- [ ] Frontend: `pnpm typecheck && pnpm lint && pnpm test && pnpm build` pass.
- [ ] Backend: `uv run ruff check . && uv run mypy && uv run pytest` pass.
- [ ] No secrets committed (`.env` stays local).

## Verification

<!-- How did you test this? Steps, screenshots, or sample P&ID input/output. -->
