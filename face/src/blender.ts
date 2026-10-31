import { applyPreset, PARAM_NAMES, type FaceParams } from "./params";
import type { Params } from "./generated/expressions";

interface Layer {
  name: string;
  preset: Params;
  weight: number;
  target: number;
  /** Time at which the layer starts fading out, for timed emotions. */
  until?: number;
}

/**
 * Weighted blend of expression presets. Each active emotion is a layer whose weight
 * tweens linearly towards its target; the face is base + Σ weight · (preset − base).
 */
export class Blender {
  private layers: Layer[] = [];
  private time = 0;

  constructor(public transitionMs = 250) {}

  set(name: string, preset: Params, intensity: number, blend: "replace" | "add", durationMs?: number) {
    if (blend === "replace") for (const l of this.layers) if (l.name !== name) l.target = 0;
    let layer = this.layers.find((l) => l.name === name);
    if (!layer) {
      layer = { name, preset, weight: 0, target: 0 };
      this.layers.push(layer);
    }
    layer.preset = preset;
    layer.target = intensity;
    layer.until = durationMs === undefined ? undefined : this.time + durationMs;
  }

  clear() {
    for (const l of this.layers) l.target = 0;
  }

  tick(dt: number) {
    this.time += dt;
    const step = this.transitionMs > 0 ? dt / this.transitionMs : 1;
    for (const l of this.layers) {
      if (l.until !== undefined && this.time >= l.until) {
        l.target = 0;
        l.until = undefined;
      }
      const d = l.target - l.weight;
      l.weight = Math.abs(d) <= step ? l.target : l.weight + Math.sign(d) * step;
    }
    this.layers = this.layers.filter((l) => l.weight > 0 || l.target > 0);
  }

  /** Name of the emotion currently aimed for, or undefined when all are fading out. */
  dominant(): string | undefined {
    let best: Layer | undefined;
    for (const l of this.layers) if (l.target > 0 && (!best || l.target > best.target)) best = l;
    return best?.name;
  }

  compose(base: FaceParams): FaceParams {
    const out = { ...base };
    for (const l of this.layers) {
      const full = applyPreset(base, l.preset);
      for (const k of PARAM_NAMES) out[k] += l.weight * (full[k] - base[k]);
    }
    return out;
  }
}
