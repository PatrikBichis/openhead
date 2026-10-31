import type { ThemeIdle } from "./generated/theme";
import { mulberry32 } from "./rng";

/** Blinks, saccades, breathing and jitter. Disabled in tests for deterministic frames. */
export class Idle {
  enabled = true;
  /** Eye closure from blinking, 0 (open) to 1 (closed). */
  blink = 0;
  /** Gaze offset from saccades and jitter, in gaze units. */
  gazeX = 0;
  gazeY = 0;
  /** Breathing, -1 to 1. */
  breath = 0;

  private rng: () => number;
  private cfg!: ThemeIdle;
  private nextBlink = 0;
  private blinkT = -1;
  private nextSaccade = 0;
  private saccadeX = 0;
  private saccadeY = 0;
  private breathPhase = 0;

  constructor(seed: number) {
    this.rng = mulberry32(seed);
  }

  configure(cfg: ThemeIdle) {
    this.cfg = cfg;
    this.nextBlink = this.draw(cfg.blink_interval_ms);
    this.nextSaccade = cfg.saccade_interval_ms ? this.draw(cfg.saccade_interval_ms) : Infinity;
  }

  triggerBlink() {
    this.blinkT = 0;
  }

  tick(dt: number, blinkRate: number, breathRate: number, jitter: number) {
    const c = this.cfg;
    if (this.enabled) {
      this.nextBlink -= dt * 2 ** ((blinkRate - 0.5) * 2);
      if (this.nextBlink <= 0 && this.blinkT < 0) {
        this.blinkT = 0;
        this.nextBlink = this.draw(c.blink_interval_ms);
      }
      this.nextSaccade -= dt;
      if (this.nextSaccade <= 0 && c.saccade_interval_ms) {
        const a = c.saccade_amplitude ?? 0;
        this.saccadeX = (this.rng() * 2 - 1) * a;
        this.saccadeY = (this.rng() * 2 - 1) * a * 0.6;
        this.nextSaccade = this.draw(c.saccade_interval_ms);
      }
      const period = (c.breath_period_ms ?? 4000) / (0.5 + breathRate * 1.67);
      this.breathPhase = (this.breathPhase + (dt / period) * Math.PI * 2) % (Math.PI * 2);
      this.breath = Math.sin(this.breathPhase);
    } else {
      this.saccadeX = this.saccadeY = this.breath = 0;
    }

    // Saccades are fast; ease 90 % of the way in ~60 ms.
    const k = 1 - Math.exp(-dt / 25);
    const j = this.enabled ? jitter * 0.08 : 0;
    this.gazeX += (this.saccadeX + (this.rng() * 2 - 1) * j - this.gazeX) * k;
    this.gazeY += (this.saccadeY + (this.rng() * 2 - 1) * j - this.gazeY) * k;

    if (this.blinkT >= 0) {
      const d = c.blink_duration_ms;
      this.blinkT += dt;
      const half = d / 2;
      this.blink = this.blinkT < half ? this.blinkT / half : Math.max(0, 1 - (this.blinkT - half) / half);
      if (this.blinkT >= d) {
        this.blinkT = -1;
        this.blink = 0;
      }
    }
  }

  private draw([lo, hi]: [number, number]): number {
    return lo + this.rng() * (hi - lo);
  }
}
