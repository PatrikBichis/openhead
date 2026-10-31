import { Blender } from "./blender";
import { Idle } from "./idle";
import { applyPreset, clamp, clampParam, DEFAULT_PARAMS, PARAM_NAMES, type FaceParams } from "./params";
import { Renderer } from "./renderer";
import { loadTheme, presetFor, themeInfo, themeNames, type ThemeInfo, type ThemePack } from "./themes";

export type LogLevel = "debug" | "info" | "notice" | "warning" | "error";

export interface EngineOptions {
  /** Blinks, saccades, breathing and jitter. Off in tests. Default true. */
  idle?: boolean;
  /** Seed for idle randomness. Default 1. */
  seed?: number;
  onLog?: (level: LogLevel, message: string) => void;
}

export interface FaceState {
  theme: string;
  emotion: string;
  params: FaceParams;
  envelope: number;
}

/**
 * The face engine. Knows nothing about the network: hosts (iOS shell, simulator,
 * tests) call this API and drive time with `tick` or `start`.
 */
export class FaceEngine {
  private pack?: ThemePack;
  private ctx: CanvasRenderingContext2D;
  private renderer = new Renderer();
  private blender = new Blender();
  private idle: Idle;
  private gazeTarget = { x: 0, y: 0 };
  private gaze = { x: 0, y: 0 };
  private envTarget = 0;
  private envLevel = 0;
  private envAge = Infinity;
  private manualBlink = false;
  private fade?: { image: HTMLCanvasElement; alpha: number; ms: number };
  private raf = 0;
  private last = 0;
  private log: NonNullable<EngineOptions["onLog"]>;

  constructor(
    private canvas: HTMLCanvasElement,
    opts: EngineOptions = {},
  ) {
    this.ctx = canvas.getContext("2d")!;
    this.idle = new Idle(opts.seed ?? 1);
    this.idle.enabled = opts.idle ?? true;
    this.log = opts.onLog ?? (() => {});
  }

  listThemes(): ThemeInfo[] {
    return themeNames().map(themeInfo);
  }

  async setTheme(name: string, transitionMs = 300): Promise<void> {
    const pack = await loadTheme(name);
    if (this.pack && transitionMs > 0) {
      const image = document.createElement("canvas");
      image.width = this.canvas.width;
      image.height = this.canvas.height;
      image.getContext("2d")!.drawImage(this.canvas, 0, 0);
      this.fade = { image, alpha: 1, ms: transitionMs };
    }
    this.pack = pack;
    this.idle.configure(pack.theme.idle);
    this.blender.clear();
    this.restIfIdle(pack);
    this.log("info", `theme=${name}`);
  }

  setEmotion(name: string, intensity = 1, blend: "replace" | "add" = "replace", durationMs?: number) {
    const pack = this.requirePack();
    let preset = presetFor(pack.expressions, name);
    let used = name;
    if (!preset) {
      this.log("warning", `emotion ${name} not in theme ${pack.theme.name}; using neutral`);
      used = "neutral";
      preset = pack.expressions.neutral;
    }
    this.blender.set(used, preset, clamp(intensity, 0, 1), blend, durationMs);
    this.log("info", `emotion=${used} intensity=${clamp(intensity, 0, 1).toFixed(2)} blend=${blend}`);
  }

  /** Gaze in screen units: x, y in [-1, 1], +y up. */
  setGaze(x: number, y: number) {
    this.gazeTarget = { x: clamp(x, -1, 1), y: clamp(y, -1, 1) };
  }

  /** Speech envelope, 0-1. Decays to closed if not refreshed within 200 ms. */
  setEnvelope(level: number) {
    this.envTarget = clamp(level, 0, 1);
    this.envAge = 0;
  }

  blink() {
    this.idle.triggerBlink();
    this.manualBlink = true;
  }

  setIdle(enabled: boolean) {
    this.idle.enabled = enabled;
  }

  tick(dt: number) {
    const pack = this.requirePack();
    this.blender.tick(dt);
    this.restIfIdle(pack);
    const base = this.composeBase(pack);
    this.idle.tick(dt, base.blink_rate, base.breath_rate, base.jitter);
    if (this.manualBlink && this.idle.blink === 0) this.manualBlink = false;

    const kg = 1 - Math.exp(-dt / 80);
    this.gaze.x += (this.gazeTarget.x - this.gaze.x) * kg;
    this.gaze.y += (this.gazeTarget.y - this.gaze.y) * kg;

    this.envAge += dt;
    if (this.envAge > 200) this.envTarget = 0;
    const env = pack.theme.envelope ?? {};
    const tau = this.envTarget > this.envLevel ? (env.attack_ms ?? 30) : (env.release_ms ?? 90);
    this.envLevel += (this.envTarget - this.envLevel) * (1 - Math.exp(-dt / Math.max(tau, 1)));

    if (this.fade) {
      this.fade.alpha -= dt / this.fade.ms;
      if (this.fade.alpha <= 0) this.fade = undefined;
    }
  }

  /** Current face parameters after blending, idle motion, gaze and envelope. */
  params(): FaceParams {
    const pack = this.requirePack();
    const p = this.composeBase(pack);
    p.gaze_x += this.gaze.x + this.idle.gazeX;
    p.gaze_y += this.gaze.y + this.idle.gazeY;
    p.open_l *= 1 - this.idle.blink;
    p.open_r *= 1 - this.idle.blink;
    const env = pack.theme.envelope ?? {};
    p.open += (env.gain ?? 1) * Math.pow(this.envLevel, env.gamma ?? 1);
    for (const k of PARAM_NAMES) p[k] = clampParam(k, p[k]);
    return p;
  }

  render() {
    const pack = this.requirePack();
    const dpr = window.devicePixelRatio || 1;
    const w = Math.max(1, Math.round(this.canvas.clientWidth * dpr));
    const h = Math.max(1, Math.round(this.canvas.clientHeight * dpr));
    if (this.canvas.width !== w || this.canvas.height !== h) {
      this.canvas.width = w;
      this.canvas.height = h;
    }
    this.renderer.draw(this.ctx, w, h, pack, { params: this.params(), breath: this.idle.breath });
    if (this.fade) {
      this.ctx.globalAlpha = Math.max(0, this.fade.alpha);
      this.ctx.drawImage(this.fade.image, 0, 0, w, h);
      this.ctx.globalAlpha = 1;
    }
  }

  start() {
    const loop = (now: number) => {
      const dt = this.last ? Math.min(now - this.last, 100) : 16;
      this.last = now;
      this.tick(dt);
      this.render();
      this.raf = requestAnimationFrame(loop);
    };
    this.raf = requestAnimationFrame(loop);
  }

  stop() {
    cancelAnimationFrame(this.raf);
    this.last = 0;
  }

  state(): FaceState {
    const pack = this.requirePack();
    return {
      theme: pack.theme.name,
      emotion: this.blender.dominant() ?? pack.theme.resting_emotion ?? "neutral",
      params: this.params(),
      envelope: this.envLevel,
    };
  }

  /** Fade to the theme's resting emotion when no other emotion is held. */
  private restIfIdle(pack: ThemePack) {
    const resting = pack.theme.resting_emotion;
    if (!resting || resting === "neutral" || this.blender.dominant()) return;
    const preset = presetFor(pack.expressions, resting);
    if (preset) this.blender.set(resting, preset, 1, "replace");
  }

  private composeBase(pack: ThemePack): FaceParams {
    return this.blender.compose(applyPreset(DEFAULT_PARAMS, pack.expressions.neutral));
  }

  private requirePack(): ThemePack {
    if (!this.pack) throw new Error("no theme loaded; call setTheme first");
    return this.pack;
  }
}
