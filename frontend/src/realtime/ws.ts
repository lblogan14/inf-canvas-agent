import type { ClientMessage, ServerMessage } from '@/schema';
import { useCanvasStore } from '@/stores/canvasStore';

/**
 * Connects to the backend command channel. Incoming commands are applied to the
 * store (without echo); local user commands are pushed back to the backend via
 * `store.outbound`. Auto-reconnects with backoff.
 */
export function connectRealtime(canvasId: string): () => void {
  const store = useCanvasStore();
  let socket: WebSocket | null = null;
  let closedByCaller = false;
  let backoff = 500;

  function connect(): void {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    socket = new WebSocket(`${proto}://${location.host}/ws?canvas=${encodeURIComponent(canvasId)}`);

    socket.onopen = () => {
      backoff = 500;
      store.outbound = (msg: ClientMessage) => socket?.send(JSON.stringify(msg));
    };

    socket.onmessage = (ev) => {
      const msg = JSON.parse(ev.data) as ServerMessage;
      if (msg.type === 'snapshot') {
        store.loadState(msg.state);
      } else if (msg.type === 'command') {
        store.applyRemote(msg);
      }
    };

    socket.onclose = () => {
      store.outbound = null;
      if (closedByCaller) return;
      setTimeout(connect, backoff);
      backoff = Math.min(backoff * 2, 8000);
    };
  }

  connect();

  return () => {
    closedByCaller = true;
    socket?.close();
  };
}
