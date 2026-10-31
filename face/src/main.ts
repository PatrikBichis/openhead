import { FaceEngine, type LogLevel } from "./engine";

/**
 * Entry point of the face page. Query parameters:
 *   theme=<name>      initial theme (default cartoon)
 *   emotion=<name>    initial emotion
 *   test              deterministic mode: no idle motion, no animation loop
 *   idle=0            animate, but without idle motion (headless simulator)
 *   seed=<n>          idle randomness seed
 */
declare global {
  interface Window {
    openhead: FaceEngine;
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
window.openhead = engine;

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
