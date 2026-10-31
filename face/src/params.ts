import type { Params } from "./generated/expressions";

/** Every face parameter, resolved. Eyes/mouth in [0, 1] or [-1, 1]; `_l` is the screen-left eye. */
export type FaceParams = Required<Params>;
export type ParamName = keyof FaceParams;

export const SHARED_EMOTIONS = [
  "neutral",
  "happy",
  "curious",
  "thinking",
  "surprised",
  "sad",
  "angry",
  "sleepy",
  "scared",
  "mischievous",
  "confused",
  "shocked",
  "excited",
  "bored",
  "skeptical",
  "worried",
  "disgusted",
  "embarrassed",
  "proud",
  "determined",
  "relieved",
  "annoyed",
  "suspicious",
  "laughing",
  "disappointed",
  "focused",
  "nervous",
  "smug",
] as const;
export type SharedEmotion = (typeof SHARED_EMOTIONS)[number];

export const DEFAULT_PARAMS: FaceParams = {
  open_l: 0.9,
  open_r: 0.9,
  tilt_l: 0,
  tilt_r: 0,
  pupil: 0.5,
  gaze_x: 0,
  gaze_y: 0,
  squint: 0,
  open: 0,
  width: 0.5,
  curve: 0.1,
  asym: 0,
  teeth: 0,
  head_tilt: 0,
  breath_rate: 0.3,
  blink_rate: 0.5,
  jitter: 0,
};

export const PARAM_NAMES = Object.keys(DEFAULT_PARAMS) as ParamName[];

const SIGNED = new Set<ParamName>(["tilt_l", "tilt_r", "gaze_x", "gaze_y", "curve", "asym", "head_tilt"]);

export const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

export function clampParam(name: ParamName, v: number): number {
  return SIGNED.has(name) ? clamp(v, -1, 1) : clamp(v, 0, 1);
}

/** `base` with the values `preset` sets. */
export function applyPreset(base: FaceParams, preset: Params | undefined): FaceParams {
  const out = { ...base };
  if (preset) for (const k of PARAM_NAMES) if (preset[k] !== undefined) out[k] = preset[k]!;
  return out;
}
