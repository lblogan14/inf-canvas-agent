"""Server-Sent Events helper that streams a LangGraph run node-by-node.

The graph runs in a worker thread (the model SDKs are sync); each completed node
is pushed to an asyncio queue and emitted as an SSE `step` event, so the UI can
show live progress instead of a spinner. When the run finishes, `on_done`
applies side effects (canvas commands) and the merged final state produces the
`done` event.
"""

import asyncio
import json
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

DoneHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


def _sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event)}\n\n"


async def stream_graph_events(
    graph: Any,
    inputs: dict[str, Any],
    node_labels: dict[str, str],
    on_done: DoneHandler,
) -> AsyncIterator[str]:
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    merged: dict[str, Any] = {}

    def worker() -> None:
        try:
            for update in graph.stream(inputs, stream_mode="updates"):
                for node, delta in update.items():
                    if isinstance(delta, dict):
                        merged.update(delta)
                    loop.call_soon_threadsafe(
                        queue.put_nowait,
                        {"type": "step", "node": node, "label": node_labels.get(node, node)},
                    )
            loop.call_soon_threadsafe(queue.put_nowait, {"type": "_final"})
        except Exception as err:
            loop.call_soon_threadsafe(queue.put_nowait, {"type": "error", "message": str(err)})

    loop.run_in_executor(None, worker)

    while True:
        event = await queue.get()
        etype = event.get("type")
        if etype == "_final":
            try:
                result = await on_done(merged)
            except Exception as err:
                yield _sse({"type": "error", "message": str(err)})
                return
            yield _sse({"type": "done", **result})
            return
        yield _sse(event)
        if etype == "error":
            return
