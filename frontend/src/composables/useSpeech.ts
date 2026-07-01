import { ref } from 'vue';

// Minimal typing for the Web Speech API (not in the standard DOM lib).
interface SpeechAlternative {
  transcript: string;
}
interface SpeechResult {
  readonly length: number;
  isFinal: boolean;
  [index: number]: SpeechAlternative;
}
interface SpeechEvent {
  results: ArrayLike<SpeechResult>;
}
interface Recognition {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  onresult: ((e: SpeechEvent) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
  start(): void;
  stop(): void;
}
type RecognitionCtor = new () => Recognition;

const win = window as unknown as {
  SpeechRecognition?: RecognitionCtor;
  webkitSpeechRecognition?: RecognitionCtor;
};
const RecognitionImpl = win.SpeechRecognition ?? win.webkitSpeechRecognition;

export type SpeechCallback = (text: string, isFinal: boolean) => void;

/**
 * Thin wrapper over the browser SpeechRecognition API for dictation.
 * `listening` is reactive; `start` streams interim + final transcripts.
 */
export function useSpeech() {
  const supported = !!RecognitionImpl;
  const listening = ref(false);
  let rec: Recognition | null = null;

  function start(onResult: SpeechCallback): void {
    if (!RecognitionImpl || listening.value) return;
    rec = new RecognitionImpl();
    rec.lang = 'en-US';
    rec.interimResults = true;
    rec.continuous = false;
    rec.onresult = (e) => {
      let text = '';
      let isFinal = false;
      for (let i = 0; i < e.results.length; i++) {
        const result = e.results[i]!;
        text += result[0]?.transcript ?? '';
        if (result.isFinal) isFinal = true;
      }
      onResult(text.trim(), isFinal);
    };
    rec.onend = () => {
      listening.value = false;
      rec = null;
    };
    rec.onerror = () => {
      listening.value = false;
      rec = null;
    };
    listening.value = true;
    rec.start();
  }

  function stop(): void {
    rec?.stop();
    listening.value = false;
  }

  return { supported, listening, start, stop };
}
