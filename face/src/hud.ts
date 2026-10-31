import type { Block, Hud, Widget } from "./generated/hud";
import { mulberry32 } from "./rng";

/** A face from the `faces` topic, as the host passes it to the page. */
export interface SeenFace {
  id: number;
  bearing: number;
  elevation: number;
  size: number;
  confidence: number;
  /** Normalised 0-1 in the camera view as shown, origin top-left. */
  box?: { x: number; y: number; w: number; h: number };
  locked?: boolean;
}

/** Values for HUD templates: device readings from the host and the host's own (`display.hud`). */
export type HudValues = Record<string, string | number | boolean | null>;

/** What `display.hud` adds on top of the theme. */
export interface HudExtras {
  values?: HudValues;
  blocks?: Block[];
  widgets?: Widget[];
  clear?: boolean;
}

const HEADINGS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];

export interface HudInfo {
  name: string;
  title: string;
  version: string;
}

// Bundled at build time, like the face themes.
const huds = import.meta.glob<Hud>("../huds/*/hud.json", { eager: true, import: "default" });

export function hudNames(): string[] {
  return Object.keys(huds)
    .map((key) => key.split("/")[2])
    .sort();
}

export function hudInfo(name: string): HudInfo {
  const hud = huds[`../huds/${name}/hud.json`];
  if (!hud) throw new Error(`unknown hud: ${name}`);
  return { name, title: hud.title, version: hud.version };
}

export function getHud(name: string): Hud {
  const hud = huds[`../huds/${name}/hud.json`];
  if (!hud) throw new Error(`unknown hud: ${name}`);
  return hud;
}

const MONO = 'ui-monospace, "SF Mono", Menlo, Consolas, "Courier New", monospace';
const SANS = '"Inter Variable", system-ui, sans-serif';

/**
 * Draws a HUD theme over the camera view: tint, vignette, scanlines, boxes around faces, the
 * locked face, text blocks and boot text. Time comes from `tick`, so tests are deterministic.
 */
export class HudRenderer {
  private hud?: Hud;
  private faces: SeenFace[] = [];
  private followId?: number;
  private clock = 0;
  private frame = 0;
  private ctx: CanvasRenderingContext2D;
  /** Random digits for {rand:N}: one sequence per render, new every half second. */
  private rand = mulberry32(7);
  /** Device readings (battery, heading, pitch, ...) and the host's own values. */
  private values: Record<string, string | number | boolean> = {};
  private extraBlocks: Block[] = [];
  private extraWidgets: Widget[] = [];

  constructor(private canvas: HTMLCanvasElement) {
    this.ctx = canvas.getContext("2d")!;
  }

  /** Start a HUD theme (or none), with its clock at zero. */
  set(name: string | undefined) {
    this.hud = name && name !== "none" ? getHud(name) : undefined;
    this.clock = 0;
    this.frame = 0;
  }

  get name(): string {
    return this.hud?.name ?? "none";
  }

  /** Merge values for templates; `null` removes one. */
  setValues(values: HudValues) {
    for (const [key, value] of Object.entries(values)) {
      if (value === null) delete this.values[key];
      else this.values[key] = value;
    }
  }

  /** `display.hud`: the host's values, blocks and widgets on top of the theme. */
  setExtras(extras: HudExtras) {
    if (extras.clear) {
      this.extraBlocks = [];
      this.extraWidgets = [];
      for (const key of Object.keys(this.values)) if (!DEVICE_KEYS.has(key)) delete this.values[key];
    }
    if (extras.values) this.setValues(extras.values);
    if (extras.blocks) this.extraBlocks = extras.blocks;
    if (extras.widgets) this.extraWidgets = extras.widgets;
  }

  setFaces(faces: SeenFace[]) {
    this.faces = faces;
  }

  get faceCount(): number {
    return this.faces.length;
  }

  /** Follow `id` (a face id) or the default (locked by the host, else the largest). */
  follow(id: number | undefined) {
    this.followId = id;
  }

  locked(): SeenFace | undefined {
    if (!this.faces.length) return undefined;
    return (
      (this.followId !== undefined ? this.faces.find((f) => f.id === this.followId) : undefined) ??
      this.faces.find((f) => f.locked) ??
      [...this.faces].sort((a, b) => b.size - a.size)[0]
    );
  }

  tick(dt: number) {
    this.clock += dt;
    this.frame += 1;
  }

  render() {
    const { canvas, ctx } = this;
    const dpr = window.devicePixelRatio || 1;
    const w = Math.max(1, Math.round(canvas.clientWidth * dpr));
    const h = Math.max(1, Math.round(canvas.clientHeight * dpr));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const hud = this.hud;
    if (!hud) return;
    ctx.scale(dpr, dpr);
    const W = w / dpr;
    const H = h / dpr;

    if (hud.tint) {
      ctx.globalAlpha = hud.tint.opacity;
      ctx.fillStyle = hud.tint.color;
      ctx.fillRect(0, 0, W, H);
      ctx.globalAlpha = 1;
    }
    if (hud.vignette) {
      const g = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.35, W / 2, H / 2, Math.hypot(W, H) / 2);
      g.addColorStop(0, "rgba(0,0,0,0)");
      g.addColorStop(1, `rgba(0,0,0,${hud.vignette})`);
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);
    }
    if (hud.scanlines) {
      ctx.fillStyle = `rgba(0,0,0,${hud.scanlines.opacity})`;
      const step = hud.scanlines.spacing ?? 3;
      for (let y = 0; y < H; y += step) ctx.fillRect(0, y, W, 1);
    }

    const unit = H * 0.045; // text size 1
    const font = (size: number, weight = 600) =>
      `${weight} ${Math.round(unit * size)}px ${hud.font === "sans" ? SANS : MONO}`;
    ctx.shadowColor = hud.shadow ?? "transparent";
    ctx.shadowBlur = hud.shadow ? 6 : 0;
    const locked = this.locked();
    const vars = this.vars(locked);
    this.rand = mulberry32(Math.floor(this.clock / 500) + 7);

    // faces
    for (const face of this.faces) {
      if (!face.box) continue;
      const x = face.box.x * W;
      const y = face.box.y * H;
      const bw = face.box.w * W;
      const bh = face.box.h * H;
      const isLocked = face === locked;
      ctx.strokeStyle = isLocked ? (hud.accent ?? hud.color) : hud.color;
      ctx.lineWidth = hud.boxes?.width ?? 2;
      const lockShown = isLocked && hud.lock?.style !== "none" && this.visible(hud.lock?.blink_ms);
      if (!lockShown) this.box(hud.boxes?.style ?? "corners", x, y, bw, bh);
      if (lockShown) {
        ctx.lineWidth = (hud.boxes?.width ?? 2) * 1.6;
        this.lock(hud.lock!.style, x, y, bw, bh);
      }
      const label = hud.boxes?.label;
      if (label) {
        ctx.font = font(0.6);
        ctx.fillStyle = isLocked ? (hud.accent ?? hud.color) : hud.color;
        ctx.textBaseline = "bottom";
        ctx.textAlign = "left";
        ctx.fillText(this.fill(label, this.vars(face)), x, y - 4);
      }
    }

    // big lock label
    if (locked && hud.lock?.label && this.visible(hud.lock.blink_ms)) {
      ctx.font = font(1.9, 700);
      ctx.fillStyle = hud.accent ?? hud.color;
      ctx.textAlign = "center";
      ctx.textBaseline = "bottom";
      ctx.fillText(hud.lock.label, W / 2, H - unit * 1.2);
    }

    // instruments
    const margin = Math.max(16, H * 0.05);
    for (const widget of [...(hud.widgets ?? []), ...this.extraWidgets]) {
      this.widget(widget, W, H, unit, margin, font, hud);
    }

    // text blocks
    for (const block of [...(hud.blocks ?? []), ...this.extraBlocks]) {
      if (!this.visible(block.blink_ms)) continue;
      const size = block.size ?? 1;
      ctx.font = font(size);
      ctx.fillStyle = block.color ?? hud.color;
      const lh = unit * size * 1.25;
      const right = block.at.endsWith("right");
      const bottom = block.at.startsWith("bottom");
      ctx.textAlign = right ? "right" : "left";
      ctx.textBaseline = "top";
      const x = right ? W - margin * 1.4 : margin * 1.4;
      const lines = block.lines.map((l) => this.fill(l, vars));
      let y = bottom ? H - margin - lh * lines.length : block.at === "left" ? H * 0.3 : margin;
      for (const line of lines) {
        ctx.fillText(line, x, y);
        y += lh;
      }
    }

    // boot text, typed line by line, then kept
    if (hud.boot) {
      const per = hud.boot.ms_per_line ?? 150;
      const shown = Math.min(hud.boot.lines.length, Math.floor(this.clock / per) + 1);
      ctx.font = font(0.85);
      ctx.fillStyle = hud.color;
      ctx.textAlign = "left";
      ctx.textBaseline = "top";
      const lh = unit * 0.85 * 1.3;
      for (let i = 0; i < shown; i++) ctx.fillText(hud.boot.lines[i], margin * 1.4, margin + i * lh);
    }
    ctx.shadowBlur = 0;
  }

  private widget(w: Widget, W: number, H: number, unit: number, margin: number,
                 font: (size: number, weight?: number) => string, hud: Hud) {
    const { ctx } = this;
    const size = w.size ?? 1;
    const num = (key: string) => (typeof this.values[key] === "number" ? (this.values[key] as number) : undefined);
    ctx.strokeStyle = hud.color;
    ctx.fillStyle = hud.color;
    ctx.lineWidth = 1.5;
    if (w.type === "compass") {
      const heading = num("heading");
      const width = W * 0.4 * size;
      const height = unit * 1.5 * size;
      const [x, y] = place(w.at ?? "top", width, height, W, H, margin);
      const cx = x + width / 2;
      const span = 70; // degrees across the tape
      ctx.font = font(0.55 * size);
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.beginPath();
      ctx.moveTo(x, y + height * 0.55);
      ctx.lineTo(x + width, y + height * 0.55);
      if (heading !== undefined) {
        const first = Math.ceil((heading - span / 2) / 5) * 5;
        for (let deg = first; deg <= heading + span / 2; deg += 5) {
          const tx = cx + ((deg - heading) / span) * width;
          const long = deg % 15 === 0;
          ctx.moveTo(tx, y + height * 0.55);
          ctx.lineTo(tx, y + height * (long ? 0.2 : 0.38));
          const d = ((deg % 360) + 360) % 360;
          if (d % 45 === 0) ctx.fillText(HEADINGS[d / 45], tx, y + height * 0.62);
        }
      }
      ctx.stroke();
      // the heading itself, in a box above the centre mark
      const label = heading === undefined ? "---" : String(Math.round(((heading % 360) + 360) % 360)).padStart(3, "0");
      ctx.font = font(0.7 * size, 700);
      ctx.textBaseline = "bottom";
      const bw = ctx.measureText("000").width + 10;
      ctx.strokeRect(cx - bw / 2, y - unit * 0.85 * size, bw, unit * 0.85 * size);
      ctx.fillText(label, cx, y - 2);
      ctx.beginPath();
      ctx.moveTo(cx - 5, y);
      ctx.lineTo(cx + 5, y);
      ctx.lineTo(cx, y + 7);
      ctx.closePath();
      ctx.fill();
    } else if (w.type === "horizon") {
      const pitch = num("pitch") ?? 0;
      const roll = num("roll") ?? 0;
      const r = H * 0.26 * size;
      const [x, y] = place(w.at ?? "center", r * 2, r * 2, W, H, margin);
      const cx = x + r;
      const cy = y + r;
      const perDeg = r / 30;
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate((-roll * Math.PI) / 180);
      ctx.translate(0, pitch * perDeg);
      ctx.font = font(0.5 * size);
      ctx.textBaseline = "middle";
      ctx.beginPath();
      ctx.moveTo(-r * 1.1, 0);
      ctx.lineTo(-r * 0.25, 0);
      ctx.moveTo(r * 0.25, 0);
      ctx.lineTo(r * 1.1, 0);
      for (const step of [-20, -10, 10, 20]) {
        const ly = -step * perDeg;
        ctx.moveTo(-r * 0.45, ly);
        ctx.lineTo(-r * 0.2, ly);
        ctx.moveTo(r * 0.2, ly);
        ctx.lineTo(r * 0.45, ly);
      }
      ctx.stroke();
      ctx.textAlign = "left";
      for (const step of [-20, -10, 10, 20]) ctx.fillText(String(Math.abs(step)), r * 0.5, -step * perDeg);
      ctx.restore();
      // fixed reticle: the head
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(cx - r * 0.18, cy);
      ctx.lineTo(cx - r * 0.07, cy);
      ctx.lineTo(cx, cy + r * 0.06);
      ctx.lineTo(cx + r * 0.07, cy);
      ctx.lineTo(cx + r * 0.18, cy);
      ctx.stroke();
    } else if (w.type === "battery") {
      const level = num("battery");
      const bw = unit * 2 * size;
      const bh = unit * 0.95 * size;
      ctx.font = font(0.7 * size, 700);
      const text = level === undefined ? "--%" : `${Math.round(level)}%${this.values.charging === true ? " +" : ""}`;
      const tw = ctx.measureText("100% +").width;
      const [x, y] = place(w.at ?? "top-right", bw + 8 + tw, bh, W, H, margin);
      ctx.strokeRect(x, y, bw, bh);
      ctx.fillRect(x + bw, y + bh * 0.3, bw * 0.07, bh * 0.4);
      if (level !== undefined) {
        ctx.fillStyle = level < 20 ? "#ff4040" : hud.color;
        ctx.fillRect(x + 3, y + 3, Math.max(0, (bw - 6) * Math.min(1, level / 100)), bh - 6);
        ctx.fillStyle = hud.color;
      }
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillText(text, x + bw * 1.07 + 6, y + bh / 2);
    }
  }

  private box(style: string, x: number, y: number, w: number, h: number) {
    const { ctx } = this;
    const l = Math.min(w, h) * 0.22;
    ctx.beginPath();
    if (style === "rect") {
      ctx.rect(x, y, w, h);
    } else if (style === "bracket") {
      ctx.moveTo(x + l * 0.6, y);
      ctx.lineTo(x, y);
      ctx.lineTo(x, y + h);
      ctx.lineTo(x + l * 0.6, y + h);
      ctx.moveTo(x + w - l * 0.6, y);
      ctx.lineTo(x + w, y);
      ctx.lineTo(x + w, y + h);
      ctx.lineTo(x + w - l * 0.6, y + h);
    } else if (style === "corners") {
      for (const [cx, cy, dx, dy] of [
        [x, y, 1, 1],
        [x + w, y, -1, 1],
        [x, y + h, 1, -1],
        [x + w, y + h, -1, -1],
      ]) {
        ctx.moveTo(cx + dx * l, cy);
        ctx.lineTo(cx, cy);
        ctx.lineTo(cx, cy + dy * l);
      }
    }
    ctx.stroke();
  }

  private lock(style: string, x: number, y: number, w: number, h: number) {
    const { ctx } = this;
    if (style === "crosshair") {
      const cx = x + w / 2;
      const cy = y + h / 2;
      const r = Math.max(w, h) * 0.55;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.moveTo(cx - r * 1.35, cy);
      ctx.lineTo(cx - r * 0.55, cy);
      ctx.moveTo(cx + r * 0.55, cy);
      ctx.lineTo(cx + r * 1.35, cy);
      ctx.moveTo(cx, cy - r * 1.35);
      ctx.lineTo(cx, cy - r * 0.55);
      ctx.moveTo(cx, cy + r * 0.55);
      ctx.lineTo(cx, cy + r * 1.35);
      ctx.stroke();
    } else if (style === "corners") {
      const pad = Math.min(w, h) * 0.12;
      this.box("corners", x - pad, y - pad, w + pad * 2, h + pad * 2);
    } else if (style === "rect") {
      ctx.strokeRect(x, y, w, h);
    }
  }

  private visible(blinkMs?: number): boolean {
    return !blinkMs || Math.floor(this.clock / blinkMs) % 2 === 0;
  }

  private vars(face: SeenFace | undefined): Record<string, string> {
    const s = Math.floor(this.clock / 1000);
    const pad = (n: number) => String(n).padStart(2, "0");
    const v = this.values;
    const n = (key: string, digits: number, sign = false) => {
      const value = v[key];
      if (typeof value !== "number") return value === undefined ? "-" : String(value);
      return `${sign && value >= 0 ? "+" : ""}${value.toFixed(digits)}`;
    };
    const heading = typeof v.heading === "number" ? ((v.heading % 360) + 360) % 360 : undefined;
    const custom: Record<string, string> = {};
    for (const [key, value] of Object.entries(v)) custom[key] = typeof value === "boolean" ? (value ? "YES" : "NO") : String(value);
    return {
      ...custom,
      battery: n("battery", 0),
      thermal: typeof v.thermal === "string" ? v.thermal.toUpperCase() : "-",
      heading: heading === undefined ? "-" : String(Math.round(heading)).padStart(3, "0"),
      heading_name: heading === undefined ? "-" : HEADINGS[Math.round(heading / 45) % 8],
      pitch: n("pitch", 1, true),
      roll: n("roll", 1, true),
      x: n("x", 2, true),
      y: n("y", 2, true),
      z: n("z", 2, true),
      tracking: typeof v.tracking === "string" ? v.tracking.toUpperCase() : "-",
      mode: typeof v.mode === "string" ? v.mode.toUpperCase() : "-",
      faces: String(this.faces.length),
      target: face ? String(face.id) : "NONE",
      status: face ? "LOCKED" : "SEARCHING",
      id: face ? String(face.id) : "-",
      conf: face ? face.confidence.toFixed(2) : "0.00",
      bearing: face ? `${face.bearing >= 0 ? "+" : ""}${face.bearing.toFixed(1)}` : "-",
      elevation: face ? `${face.elevation >= 0 ? "+" : ""}${face.elevation.toFixed(1)}` : "-",
      size: face ? face.size.toFixed(2) : "-",
      frame: String(40000 + this.frame),
      time: `${pad(Math.floor(s / 3600))}:${pad(Math.floor(s / 60) % 60)}:${pad(s % 60)}:${pad(Math.floor((this.clock % 1000) / 40))}`,
    };
  }

  private fill(template: string, vars: Record<string, string>): string {
    const rand = this.rand;
    return template.replace(/\{(\w+)(?::(\d+))?\}/g, (_, key: string, n?: string) => {
      if (key === "rand") {
        let out = "";
        for (let i = 0; i < Number(n ?? 4); i++) out += Math.floor(rand() * 10);
        return out;
      }
      return vars[key] ?? "-";
    });
  }
}

/** Keys the device fills in; `display.hud {clear}` keeps them. */
const DEVICE_KEYS = new Set(["battery", "charging", "thermal", "heading", "pitch", "roll", "x", "y", "z",
  "tracking", "mode", "clients"]);

/** Top-left corner for something `w` x `h` at a named place. */
function place(at: string, w: number, h: number, W: number, H: number, margin: number): [number, number] {
  const x = at.endsWith("left") ? margin * 1.4 : at.endsWith("right") ? W - margin * 1.4 - w : (W - w) / 2;
  const y = at.startsWith("top") ? margin * 1.4 : at.startsWith("bottom") ? H - margin - h : (H - h) / 2;
  return [x, y];
}

/**
 * The simulator's stand-in for the front camera: a room with a person drawn at every face
 * box, so the HUD can be seen and tested without a camera.
 */
export function drawSyntheticCamera(canvas: HTMLCanvasElement, faces: SeenFace[]) {
  const dpr = window.devicePixelRatio || 1;
  const w = Math.max(1, Math.round(canvas.clientWidth * dpr));
  const h = Math.max(1, Math.round(canvas.clientHeight * dpr));
  if (canvas.width !== w || canvas.height !== h) {
    canvas.width = w;
    canvas.height = h;
  }
  const ctx = canvas.getContext("2d")!;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const W = w / dpr;
  const H = h / dpr;
  // room: wall, window, floor
  const wall = ctx.createLinearGradient(0, 0, 0, H);
  wall.addColorStop(0, "#8d8478");
  wall.addColorStop(1, "#5d564e");
  ctx.fillStyle = wall;
  ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = "#c9d6de";
  ctx.fillRect(W * 0.08, H * 0.12, W * 0.22, H * 0.42);
  ctx.strokeStyle = "#4b443d";
  ctx.lineWidth = 6;
  ctx.strokeRect(W * 0.08, H * 0.12, W * 0.22, H * 0.42);
  ctx.beginPath();
  ctx.moveTo(W * 0.19, H * 0.12);
  ctx.lineTo(W * 0.19, H * 0.54);
  ctx.stroke();
  ctx.fillStyle = "#3d3832";
  ctx.fillRect(0, H * 0.82, W, H * 0.18);
  // people, far ones first
  const skins = ["#e0b08c", "#a8714f", "#f1c9a5", "#7b4a32"];
  const shirts = ["#2a4d6e", "#7a2e2e", "#3f6b3a", "#5b4a7a"];
  for (const f of [...faces].sort((a, b) => a.size - b.size)) {
    if (!f.box) continue;
    const x = f.box.x * W;
    const y = f.box.y * H;
    const bw = f.box.w * W;
    const bh = f.box.h * H;
    const cx = x + bw / 2;
    ctx.fillStyle = shirts[f.id % shirts.length];
    ctx.beginPath();
    ctx.ellipse(cx, y + bh * 2.05, bw * 1.25, bh * 1.05, 0, Math.PI, 0);
    ctx.fill();
    ctx.fillRect(cx - bw * 1.25, y + bh * 2.05, bw * 2.5, H);
    ctx.fillStyle = skins[f.id % skins.length];
    ctx.fillRect(cx - bw * 0.18, y + bh * 0.85, bw * 0.36, bh * 0.4);
    ctx.beginPath();
    ctx.ellipse(cx, y + bh / 2, bw * 0.5, bh * 0.5, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#2b211b";
    ctx.beginPath();
    ctx.ellipse(cx, y + bh * 0.18, bw * 0.52, bh * 0.25, 0, Math.PI, 0);
    ctx.fill();
    ctx.fillStyle = "#1d1714";
    for (const dx of [-0.18, 0.18]) {
      ctx.beginPath();
      ctx.arc(cx + dx * bw, y + bh * 0.47, Math.max(1.5, bw * 0.045), 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.strokeStyle = "#6b3b2e";
    ctx.lineWidth = Math.max(1.5, bw * 0.03);
    ctx.beginPath();
    ctx.arc(cx, y + bh * 0.62, bw * 0.14, 0.15 * Math.PI, 0.85 * Math.PI);
    ctx.stroke();
  }
}
