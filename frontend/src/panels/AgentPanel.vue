<script setup lang="ts">
import { nextTick, ref } from 'vue';
import { useCanvasStore } from '@/stores/canvasStore';
import { api } from '@/api/client';

const store = useCanvasStore();

interface ChatEntry {
  role: 'user' | 'agent' | 'system';
  text: string;
}

const log = ref<ChatEntry[]>([
  { role: 'system', text: 'Optimus is ready. Ask me to build on the canvas or upload a P&ID.' },
]);
const input = ref('');
const busy = ref(false);
const logEl = ref<HTMLElement | null>(null);
const fileEl = ref<HTMLInputElement | null>(null);

async function push(entry: ChatEntry): Promise<void> {
  log.value.push(entry);
  await nextTick();
  logEl.value?.scrollTo({ top: logEl.value.scrollHeight });
}

async function send(): Promise<void> {
  const message = input.value.trim();
  if (!message || busy.value) return;
  input.value = '';
  await push({ role: 'user', text: message });
  busy.value = true;
  try {
    const res = await api.runOptimus(store.state.meta.id, message);
    await push({
      role: 'agent',
      text: `${res.message}${res.commandsApplied ? `\n(${res.commandsApplied} canvas actions)` : ''}`,
    });
  } catch (err) {
    await push({ role: 'system', text: `Error: ${(err as Error).message}` });
  } finally {
    busy.value = false;
  }
}

async function onUpload(event: Event): Promise<void> {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  await push({ role: 'user', text: `📷 Uploaded P&ID: ${file.name}` });
  busy.value = true;
  try {
    const res = await api.extractPID(store.state.meta.id, file);
    await push({ role: 'agent', text: `${res.message}\n(${res.commandsApplied} canvas actions)` });
  } catch (err) {
    await push({ role: 'system', text: `Error: ${(err as Error).message}` });
  } finally {
    busy.value = false;
    if (fileEl.value) fileEl.value.value = '';
  }
}
</script>

<template>
  <section class="agent-panel">
    <div class="header">
      <span class="title">🤖 Optimus</span>
      <span v-if="busy" class="busy">working…</span>
    </div>

    <div ref="logEl" class="log">
      <div v-for="(e, i) in log" :key="i" class="entry" :class="e.role">
        <div class="bubble">{{ e.text }}</div>
      </div>
    </div>

    <div class="composer">
      <input ref="fileEl" type="file" accept="image/png,image/jpeg" hidden @change="onUpload" />
      <button class="icon" title="Upload P&ID image" :disabled="busy" @click="fileEl?.click()">
        📷
      </button>
      <input
        v-model="input"
        class="text"
        placeholder="Tell Optimus what to do…"
        :disabled="busy"
        @keydown.enter="send"
      />
      <button class="send" :disabled="busy || !input.trim()" @click="send">Send</button>
    </div>
  </section>
</template>

<style scoped>
.agent-panel {
  display: flex;
  flex-direction: column;
  height: 280px;
  background: #0b1220;
  border-top: 1px solid #1f2937;
  color: #e5e7eb;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #1f2937;
}
.title {
  font-weight: 600;
  font-size: 13px;
}
.busy {
  font-size: 11px;
  color: #38bdf8;
}
.log {
  flex: 1;
  overflow-y: auto;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.entry {
  display: flex;
}
.entry.user {
  justify-content: flex-end;
}
.bubble {
  max-width: 80%;
  font-size: 12px;
  line-height: 1.4;
  padding: 6px 10px;
  border-radius: 8px;
  white-space: pre-wrap;
}
.entry.user .bubble {
  background: #1d4ed8;
  color: #fff;
}
.entry.agent .bubble {
  background: #1e293b;
  color: #e5e7eb;
}
.entry.system .bubble {
  background: transparent;
  color: #64748b;
  font-style: italic;
}
.composer {
  display: flex;
  gap: 6px;
  padding: 8px;
  border-top: 1px solid #1f2937;
}
.icon {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #1f2937;
  background: #1e293b;
  cursor: pointer;
}
.text {
  flex: 1;
  font-size: 13px;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #1f2937;
  background: #0f172a;
  color: #e5e7eb;
}
.send {
  padding: 6px 14px;
  border-radius: 6px;
  border: none;
  background: #38bdf8;
  color: #04243a;
  font-weight: 600;
  cursor: pointer;
}
.send:disabled,
.icon:disabled {
  opacity: 0.5;
  cursor: default;
}
</style>
