import "@fontsource-variable/inter/wght.css";
import { FaceEngine, type LogLevel } from "./engine";
import { Screen, type ScreenEvent, type ScreenState, type ShowOptions, type SubtitleOptions, type View } from "./screen";

/**
 * Entry point of the face page. Query parameters:
 *   theme=<name>      initial theme (default cartoon)
 *   emotion=<name>    initial emotion
 *   test              deterministic mode: no idle motion, no animation loop
 *   idle=0            animate, but without idle motion (headless simulator)
 *   seed=<n>          idle randomness seed
 */
/** The page's API: the face engine plus what else is on screen (`screen.ts`). */
export interface OpenHead extends FaceEngine {
  show(content: View, source?: string, opts?: ShowOptions): Promise<void>;
  clear(): void;
  subtitle(text?: string, opts?: SubtitleOptions): void;
  screen(): ScreenState;
}

declare global {
  interface Window {
    openhead: OpenHead;
    webkit?: { messageHandlers?: { openhead?: { postMessage(message: unknown): void } } };
  }
}

const query = new URLSearchParams(location.search);
const test = query.has("test");
const canvas = document.querySelector<HTMLCanvasElement>("#face")!;

function onLog(level: LogLevel, message: string) {
  // iOS shell receives logs through WKScriptMessageHandler; elsewhere they go to the console.
  window.webkit?.messageHandlers?.openhead?.postMessage({ type: "log", level, message });
  (level === "warning" || level === "error" ? console.warn : console.info)(`[face] ${message}`);
}

const idle = !test && query.get("idle") !== "0";
const engine = new FaceEngine(canvas, { idle, seed: Number(query.get("seed") ?? 1), onLog });

function emit(event: ScreenEvent) {
  // iOS gets events like logs; the simulator reads them from the console.
  window.webkit?.messageHandlers?.openhead?.postMessage({ type: "event", event });
  console.info(`[face-event] ${JSON.stringify(event)}`);
}

const screen = new Screen(engine, onLog, emit);
engine.onTick = (dt) => screen.tick(dt);
window.openhead = Object.assign(engine, {
  show: (content: View, source?: string, opts?: ShowOptions) => screen.show(content, source, opts),
  clear: () => screen.clear(),
  subtitle: (text?: string, opts?: SubtitleOptions) => screen.subtitle(text, opts),
  screen: () => screen.state(),
});

await engine.setTheme(query.get("theme") ?? "cartoon", 0);
const emotion = query.get("emotion");
if (emotion) engine.setEmotion(emotion);

if (test) {
  engine.tick(1000);
  engine.render();
} else {
  engine.start();
  new ResizeObserver(() => engine.render()).observe(canvas);
}
document.documentElement.dataset.ready = "1";
window.webkit?.messageHandlers?.openhead?.postMessage({ type: "ready" });
