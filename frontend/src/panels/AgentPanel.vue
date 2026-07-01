<script setup lang="ts">
import { nextTick, ref, watch } from 'vue';
import { useCanvasStore } from '@/stores/canvasStore';
import { useSpeech } from '@/composables/useSpeech';
import { api } from '@/api/client';

const store = useCanvasStore();
const { supported: voiceSupported, listening, start: startVoice, stop: stopVoice } = useSpeech();

interface ChatEntry {
  role: 'user' | 'agent' | 'system';
  text: string;
}

const log = ref<ChatEntry[]>([
  { role: 'system', text: 'Optimus is ready. Ask me to build on the canvas or upload a P&ID.' },
]);
const input = ref('');
const busy = ref(false);
const steps = ref<string[]>([]);
const logEl = ref<HTMLElement | null>(null);
const fileEl = ref<HTMLInputElement | null>(null);

function onStep(label: string): void {
  steps.value = [...steps.value, label];
  void scrollToBottom();
}

async function scrollToBottom(): Promise<void> {
  await nextTick();
  const el = logEl.value;
  if (el) el.scrollTop = el.scrollHeight;
}

async function push(entry: ChatEntry): Promise<void> {
  log.value.push(entry);
  await scrollToBottom();
}

// The "working…" indicator changes height too — keep pinned to the bottom.
watch(busy, scrollToBottom);

async function send(): Promise<void> {
  const message = input.value.trim();
  if (!message || busy.value) return;
  input.value = '';
  await push({ role: 'user', text: message });
  steps.value = [];
  busy.value = true;
  try {
    const res = await api.runOptimus(store.state.meta.id, message, (s) => onStep(s.label));
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

function toggleVoice(): void {
  if (listening.value) {
    stopVoice();
    return;
  }
  startVoice((text, isFinal) => {
    input.value = text;
    // Auto-send once the spoken phrase is finalized.
    if (isFinal && text) void send();
  });
}

async function onUpload(event: Event): Promise<void> {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  await push({ role: 'user', text: `📷 Uploaded P&ID: ${file.name}` });
  steps.value = [];
  busy.value = true;
  try {
    const res = await api.extractPID(store.state.meta.id, file, (s) => onStep(s.label));
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
    <div ref="logEl" class="log">
      <div v-for="(e, i) in log" :key="i" class="entry" :class="e.role">
        <div class="bubble">{{ e.text }}</div>
      </div>
      <div v-if="busy" class="entry system">
        <div class="bubble steps">
          <div v-for="(s, i) in steps" :key="i" class="step done">✓ {{ s }}</div>
          <div class="step active"><span class="spinner" /> working…</div>
        </div>
      </div>
    </div>

    <div class="composer">
      <input ref="fileEl" type="file" accept="image/png,image/jpeg" hidden @change="onUpload" />
      <button class="icon" title="Upload P&ID image" :disabled="busy" @click="fileEl?.click()">
        📷
      </button>
      <button
        v-if="voiceSupported"
        class="icon mic"
        :class="{ listening }"
        :title="listening ? 'Stop listening' : 'Speak your request'"
        :disabled="busy"
        @click="toggleVoice"
      >
        🎤
      </button>
      <input
        v-model="input"
        class="text"
        :placeholder="listening ? 'Listening…' : 'Tell Optimus what to do…'"
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
  height: 100%;
  width: 100%;
  background: var(--surface-2);
  color: var(--text);
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
}
.title {
  font-weight: 600;
  font-size: 13px;
}
.busy {
  font-size: 11px;
  color: var(--accent);
}
.log {
  flex: 1;
  min-height: 0; /* allow the flex child to scroll instead of growing */
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
  background: var(--user-bubble);
  color: var(--user-bubble-text);
}
.entry.agent .bubble {
  background: var(--surface-3);
  color: var(--text);
}
.entry.system .bubble {
  background: transparent;
  color: var(--text-faint);
  font-style: italic;
}
.bubble.steps {
  background: var(--surface-3);
  color: var(--text-muted);
  font-style: normal;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.step {
  display: flex;
  align-items: center;
  gap: 6px;
}
.step.done {
  color: var(--accent);
}
.step.active {
  color: var(--text-muted);
}
.spinner {
  width: 10px;
  height: 10px;
  border: 2px solid var(--text-faint);
  border-top-color: var(--accent);
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.7s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.composer {
  display: flex;
  gap: 6px;
  padding: 8px;
  border-top: 1px solid var(--border);
}
.icon {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-3);
  cursor: pointer;
}
.mic.listening {
  border-color: var(--danger);
  background: color-mix(in srgb, var(--danger) 18%, transparent);
  animation: mic-pulse 1.2s ease-in-out infinite;
}
@keyframes mic-pulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 color-mix(in srgb, var(--danger) 45%, transparent);
  }
  50% {
    box-shadow: 0 0 0 4px transparent;
  }
}
.text {
  flex: 1;
  font-size: 13px;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
}
.send {
  padding: 6px 14px;
  border-radius: 6px;
  border: none;
  background: var(--accent);
  color: var(--accent-contrast);
  font-weight: 600;
  cursor: pointer;
}
.send:disabled,
.icon:disabled {
  opacity: 0.5;
  cursor: default;
}
</style>
