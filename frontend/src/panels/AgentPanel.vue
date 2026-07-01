<script setup lang="ts">
import { nextTick, reactive, ref, watch } from 'vue';
import { useCanvasStore } from '@/stores/canvasStore';
import { useSpeech } from '@/composables/useSpeech';
import { api, type ExtractOptions } from '@/api/client';

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

// --- P&ID extraction: upload opens a setup card before running ----------
const pending = ref<File | null>(null);
const opts = reactive<Required<ExtractOptions>>({
  hint: '',
  effort: 1,
  useTiling: false,
  tileCols: 2,
  tileRows: 2,
  useLegend: false,
  useVerify: true,
  useLineHybrid: true,
});

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

// Uploading only stages the file — the user tunes options, then extracts.
function onUpload(event: Event): void {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  pending.value = file;
}

function cancelExtract(): void {
  pending.value = null;
  if (fileEl.value) fileEl.value.value = '';
}

function optsSummary(): string {
  const bits: string[] = [];
  if (opts.effort > 1) bits.push(`${opts.effort} passes`);
  if (opts.useTiling) bits.push(`tiled ${opts.tileCols}×${opts.tileRows}`);
  if (opts.useLegend) bits.push('legend');
  if (opts.useVerify) bits.push('verify');
  if (opts.useLineHybrid) bits.push('line-hybrid');
  return bits.length ? ` · ${bits.join(', ')}` : '';
}

async function runExtract(): Promise<void> {
  const file = pending.value;
  if (!file || busy.value) return;
  pending.value = null;
  const hint = opts.hint.trim();
  await push({
    role: 'user',
    text: `📷 Extract ${file.name}${optsSummary()}${hint ? `\n"${hint}"` : ''}`,
  });
  steps.value = [];
  busy.value = true;
  try {
    const res = await api.extractPID(store.state.meta.id, file, { ...opts }, (s) =>
      onStep(s.label),
    );
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

    <div v-if="pending" class="extract-setup">
      <div class="es-head">
        <span class="es-title">Extract P&ID</span>
        <span class="es-file" :title="pending.name">{{ pending.name }}</span>
      </div>
      <textarea
        v-model="opts.hint"
        class="es-hint"
        rows="2"
        placeholder="Guidance (optional): e.g. ~40 symbols, focus on the reactor loop, ignore the title block"
      />
      <div class="es-row">
        <label class="es-field">
          <span>Passes</span>
          <select v-model.number="opts.effort">
            <option :value="1">1 · fast</option>
            <option :value="2">2</option>
            <option :value="3">3 · thorough</option>
            <option :value="4">4 · max</option>
          </select>
        </label>
        <label class="es-check">
          <input v-model="opts.useTiling" type="checkbox" />
          <span>Tiling <em>(dense sheets)</em></span>
        </label>
        <template v-if="opts.useTiling">
          <label class="es-field">
            <span>Cols</span>
            <select v-model.number="opts.tileCols">
              <option :value="2">2</option>
              <option :value="3">3</option>
              <option :value="4">4</option>
            </select>
          </label>
          <label class="es-field">
            <span>Rows</span>
            <select v-model.number="opts.tileRows">
              <option :value="2">2</option>
              <option :value="3">3</option>
              <option :value="4">4</option>
            </select>
          </label>
        </template>
      </div>
      <div class="es-row">
        <label class="es-check">
          <input v-model="opts.useLegend" type="checkbox" />
          <span>Legend few-shot</span>
        </label>
        <label class="es-check">
          <input v-model="opts.useVerify" type="checkbox" />
          <span>Verify (Set-of-Mark)</span>
        </label>
        <label class="es-check">
          <input v-model="opts.useLineHybrid" type="checkbox" />
          <span>Line hybrid</span>
        </label>
      </div>
      <p class="es-note">
        More passes / tiling improve accuracy on dense drawings but take longer.
      </p>
      <div class="es-actions">
        <button class="es-cancel" @click="cancelExtract">Cancel</button>
        <button class="es-go" :disabled="busy" @click="runExtract">Extract</button>
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

/* --- P&ID extraction setup card --------------------------------------- */
.extract-setup {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 12px;
  border-top: 1px solid var(--border);
  background: var(--surface-3);
}
.es-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.es-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text);
}
.es-file {
  font-size: 11px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.es-hint {
  font-size: 12px;
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  resize: vertical;
  font-family: inherit;
}
.es-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}
.es-field {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--text-muted);
}
.es-field select {
  font-size: 11px;
  padding: 2px 4px;
  border-radius: 5px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
}
.es-check {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--text);
  cursor: pointer;
}
.es-check em {
  color: var(--text-faint);
  font-style: normal;
}
.es-note {
  font-size: 10px;
  color: var(--text-faint);
  margin: 0;
}
.es-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.es-cancel {
  padding: 5px 12px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
}
.es-go {
  padding: 5px 16px;
  border-radius: 6px;
  border: none;
  background: var(--accent);
  color: var(--accent-contrast);
  font-weight: 600;
  cursor: pointer;
}
.es-go:disabled {
  opacity: 0.5;
  cursor: default;
}
</style>
