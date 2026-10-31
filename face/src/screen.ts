import type { FaceEngine, LogLevel } from "./engine";

export type View = "face" | "image" | "video" | "web";
export type Overlay = "none" | "face-corner";

export interface ShowOptions {
  overlay?: Overlay;
  /** `video`: start again at the end. */
  loop?: boolean;
  /** `video`: no sound. */
  muted?: boolean;
  /**
   * `web`: the host draws the page itself (iOS, native web view below this one); the page
   * turns transparent so the corner face and subtitles stay on top. Otherwise an iframe.
   */
  nativeWeb?: boolean;
}

export interface SubtitleOptions {
  mode?: "replace" | "append" | "clear";
  position?: "bottom" | "top";
  /** Clear this long after the last update. */
  durationMs?: number;
  /** Move the mouth with the text at reading pace. */
  mouth?: boolean;
}

export interface ScreenState {
  view: View;
  overlay: Overlay;
  subtitle: string;
}

/** Something the host should know about without asking: the page changed view on its own. */
export interface ScreenEvent {
  type: "view";
  view: View;
  reason: string;
}

const MS_PER_CHAR = 65; // reading pace for the text-driven mouth (~15 characters/s)
const LOAD_TIMEOUT_MS = 20000;

/**
 * Everything on screen besides the face itself: an image (PNG, JPEG, GIF, WebP, SVG), a video,
 * a web page, the face in a corner, and subtitles on top. Time comes from the engine's tick,
 * so subtitles and the text-driven mouth are deterministic in tests.
 */
export class Screen {
  private view: View = "face";
  private overlay: Overlay = "none";
  private display: HTMLElement;
  private subtitles: HTMLElement;
  private text = "";
  private subtitleAge = 0;
  private subtitleLife = Infinity;
  private mouth?: { text: string; ms: number };

  constructor(
    private engine: FaceEngine,
    private log: (level: LogLevel, message: string) => void,
    private emit: (event: ScreenEvent) => void,
  ) {
    this.display = document.getElementById("display")!;
    this.subtitles = document.getElementById("subtitles")!;
  }

  async show(content: View, source = "", opts: ShowOptions = {}): Promise<void> {
    if (content === "face") return this.clear();
    const overlay = opts.overlay ?? "none";
    let element: HTMLElement | undefined;
    let loaded: Promise<void> = Promise.resolve();
    if (content === "image") {
      const img = document.createElement("img");
      loaded = settle(img, "load", "error", `could not load image ${short(source)}`);
      img.src = source;
      element = img;
    } else if (content === "video") {
      const video = document.createElement("video");
      video.playsInline = true;
      video.autoplay = true;
      video.loop = opts.loop ?? false;
      video.muted = opts.muted ?? false;
      loaded = settle(video, "loadeddata", "error", `could not load video ${short(source)}`);
      video.onended = () => {
        if (this.display.firstElementChild !== video) return;
        this.log("info", "video ended; showing the face");
        this.clear();
        this.emit({ type: "view", view: "face", reason: "video ended" });
      };
      video.src = source;
      element = video;
    } else if (content === "web" && !opts.nativeWeb) {
      const frame = document.createElement("iframe");
      frame.src = source;
      element = frame;
    } else if (content !== "web") {
      throw new Error(`unknown content: ${content}`);
    }

    // Swap only once the new content has loaded, so a bad source leaves the screen as it was.
    const parked = document.createElement("div");
    parked.hidden = true;
    if (element) parked.append(element);
    document.body.append(parked);
    try {
      await withTimeout(loaded, LOAD_TIMEOUT_MS, `${content} did not load within ${LOAD_TIMEOUT_MS / 1000} s`);
    } catch (error) {
      parked.remove();
      throw error;
    }
    this.stopVideo();
    this.display.replaceChildren(...(element ? [element] : []));
    parked.remove();
    if (element instanceof HTMLVideoElement) {
      element.play().catch((e) => this.log("warning", `video did not start: ${e}`));
    }
    this.view = content;
    this.overlay = overlay;
    this.apply();
    this.log("info", `view=${content} overlay=${overlay}`);
  }

  clear() {
    this.stopVideo();
    this.display.replaceChildren();
    this.view = "face";
    this.overlay = "none";
    this.apply();
  }

  subtitle(text = "", opts: SubtitleOptions = {}) {
    const mode = opts.mode ?? "replace";
    if (mode === "clear") {
      this.setText("");
      this.mouth = undefined;
      return;
    }
    this.setText(mode === "append" ? this.text + text : text);
    this.subtitles.dataset.position = opts.position ?? this.subtitles.dataset.position ?? "bottom";
    this.subtitleAge = 0;
    this.subtitleLife = opts.durationMs ?? Infinity;
    if (opts.mouth) {
      // Appended text extends the speech; replaced text starts it over.
      const rest = mode === "append" && this.mouth ? this.mouth.text.slice(Math.floor(this.mouth.ms / MS_PER_CHAR)) : "";
      this.mouth = { text: rest + text, ms: 0 };
    } else if (mode === "replace") {
      this.mouth = undefined;
    }
  }

  /** Called by the engine every tick. */
  tick(dt: number) {
    if (this.text) {
      this.subtitleAge += dt;
      if (this.subtitleAge >= this.subtitleLife) this.setText("");
    }
    if (this.mouth) {
      this.mouth.ms += dt;
      const i = Math.floor(this.mouth.ms / MS_PER_CHAR);
      if (i >= this.mouth.text.length) this.mouth = undefined;
      else this.engine.setEnvelope(levelFor(this.mouth.text[i]), "text");
    }
  }

  /**
   * WebKit snapshots (iOS screenshots) leave video black: while `on`, the current frame is
   * drawn into a canvas over the video. Drawing a cross-origin frame is allowed; only reading
   * the pixels back from script would not be.
   */
  freezeVideo(on: boolean) {
    this.display.querySelector("canvas.frame")?.remove();
    const video = this.display.querySelector("video");
    if (!on || !video || !video.videoWidth) return;
    const frame = document.createElement("canvas");
    frame.className = "frame";
    frame.width = video.videoWidth;
    frame.height = video.videoHeight;
    frame.getContext("2d")!.drawImage(video, 0, 0);
    this.display.append(frame);
  }

  state(): ScreenState {
    return { view: this.view, overlay: this.overlay, subtitle: this.text };
  }

  private setText(text: string) {
    this.text = text;
    // The box is three lines high and bottom-aligned, so the newest lines stay visible.
    const p = this.subtitles.querySelector("p")!;
    p.textContent = text;
    this.subtitles.hidden = !text;
  }

  private apply() {
    const body = document.body.classList;
    body.toggle("showing", this.view !== "face");
    body.toggle("face-corner", this.view !== "face" && this.overlay === "face-corner");
    body.toggle("native-web", this.view === "web" && !this.display.firstElementChild);
    this.display.hidden = this.view === "face";
  }

  private stopVideo() {
    this.display.querySelector("canvas.frame")?.remove();
    const old = this.display.querySelector("video");
    if (old) {
      old.onended = null;
      old.pause();
      old.removeAttribute("src");
      old.load();
    }
  }
}

/** Mouth opening per character: vowels wide, consonants a little, spaces and punctuation shut. */
function levelFor(ch: string): number {
  if (/[aeiouyåäöáéíóúàèìòùâêîôûæø]/i.test(ch)) return 0.85;
  if (/[\p{L}\p{N}]/u.test(ch)) return 0.35;
  return 0;
}

function settle(el: HTMLElement, ok: string, fail: string, message: string): Promise<void> {
  return new Promise((resolve, reject) => {
    el.addEventListener(ok, () => resolve(), { once: true });
    el.addEventListener(fail, () => reject(new Error(message)), { once: true });
  });
}

function withTimeout<T>(p: Promise<T>, ms: number, message: string): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(message)), ms);
    p.then(
      (v) => (clearTimeout(timer), resolve(v)),
      (e) => (clearTimeout(timer), reject(e)),
    );
  });
}

function short(source: string): string {
  return source.startsWith("data:") ? source.slice(0, source.indexOf(",")) : source;
}
