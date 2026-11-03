import "@fontsource-variable/inter/wght.css";
import { FaceEngine, type LogLevel } from "./engine";
import { hudInfo, hudNames, type HudExtras, type HudInfo, type HudValues, type SeenFace } from "./hud";
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
  /** Before/after a WebKit snapshot: show the current video frame as a still. */
  freezeVideo(on: boolean): void;
  /** Faces from the host's `faces` stream (camera view, HUD, gaze following). */
  setFaces(faces: SeenFace[]): void;
  /** `look_at {frame: face}`: a face id, `null` for the locked face, `undefined` to stop. */
  followFace(id: number | null | undefined): void;
  listHuds(): HudInfo[];
  /** Device readings for HUD templates and widgets (the host sends them a few times a second). */
  setHudValues(values: HudValues): void;
  /** `display.hud`: the host's own values, text blocks and widgets on the HUD. */
  hudExtras(extras: HudExtras): void;
  /** Clients watching the `camera` topic: a marker on screen while there are any. */
  setWatching(viewers: number): void;
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
  freezeVideo: (on: boolean) => screen.freezeVideo(on),
  setFaces: (faces: SeenFace[]) => screen.setFaces(faces),
  followFace: (id: number | null | undefined) => screen.followFace(id),
  listHuds: () => hudNames().map(hudInfo),
  setHudValues: (values: HudValues) => screen.setHudValues(values),
  hudExtras: (extras: HudExtras) => screen.hudExtras(extras),
  setWatching: (viewers: number) => {
    const el = document.querySelector<HTMLElement>("#watching")!;
    el.hidden = viewers <= 0;
    el.textContent = viewers > 1 ? `Camera shared · ${viewers}` : "Camera shared";
  },
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
