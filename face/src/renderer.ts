import type { Shape } from "./generated/theme";
import type { FaceParams } from "./params";
import type { ThemePack } from "./themes";

export interface Frame {
  params: FaceParams;
  /** Vertical breathing offset, -1 to 1. */
  breath: number;
}

const LAYOUT = { eye_spacing: 0.46, eye_size: 0.24, eye_y: 0.12, mouth_width: 0.36, mouth_y: -0.3 };

type Ctx = CanvasRenderingContext2D;

/**
 * Draws one frame. All sizes derive from S, the canvas's shortest side, so portrait
 * phones, landscape tablets and the simulator window get the same proportions.
 */
export class Renderer {
  private low = document.createElement("canvas");

  draw(ctx: Ctx, w: number, h: number, pack: ThemePack, frame: Frame) {
    const block = Math.round((pack.theme.render?.pixelate ?? 0) * (window.devicePixelRatio || 1));
    if (block > 1) {
      // Pixelate: draw small, scale up without smoothing.
      this.low.width = Math.max(1, Math.ceil(w / block));
      this.low.height = Math.max(1, Math.ceil(h / block));
      const lctx = this.low.getContext("2d")!;
      drawFace(lctx, this.low.width, this.low.height, pack, frame);
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(this.low, 0, 0, w, h);
      ctx.imageSmoothingEnabled = true;
    } else {
      drawFace(ctx, w, h, pack, frame);
    }
    if (pack.theme.render?.scanlines) {
      ctx.fillStyle = "rgba(0, 0, 0, 0.22)";
      const step = Math.max(3, Math.round(Math.min(w, h) / 160));
      for (let y = 0; y < h; y += step) ctx.fillRect(0, y, w, Math.max(1, step / 3));
    }
  }
}

function drawFace(ctx: Ctx, w: number, h: number, pack: ThemePack, { params: p, breath }: Frame) {
  const { theme } = pack;
  const L = { ...LAYOUT, ...theme.layout };
  const S = Math.min(w, h);

  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = theme.palette.bg;
  ctx.fillRect(0, 0, w, h);

  const bob = breath * (theme.idle.breath_amplitude ?? 0) * S * 0.1;
  ctx.translate(w / 2, h / 2 + bob);
  ctx.rotate(p.head_tilt * 0.26);

  const glow = theme.render?.glow ?? 0;
  if (glow > 0) {
    ctx.shadowColor = theme.palette.accent;
    ctx.shadowBlur = glow * S * 0.06;
  }

  const ex = (L.eye_spacing * S) / 2;
  const ey = (-L.eye_y * S) / 2;
  drawEye(ctx, S, -ex, ey, -1, p, pack, L.eye_size * S);
  drawEye(ctx, S, ex, ey, 1, p, pack, L.eye_size * S);
  drawMouth(ctx, S, 0, (-L.mouth_y * S) / 2, p, pack, L.mouth_width * S);
  ctx.restore();
}

// --- eyes -------------------------------------------------------------------

interface EyeGeom {
  path: Path2D;
  r: number;
  hh: number;
}

function eyeGeometry(shape: Shape, eyeW: number, pack: ThemePack): EyeGeom {
  const r = eyeW / 2;
  const path = new Path2D();
  if ("preset" in shape) {
    switch (shape.preset) {
      case "almond":
        path.moveTo(-r, 0);
        path.quadraticCurveTo(0, -r * 1.25, r, 0);
        path.quadraticCurveTo(0, r * 1.25, -r, 0);
        return { path, r, hh: r * 0.62 };
      case "slit":
        path.ellipse(0, 0, r, r * 0.38, 0, 0, Math.PI * 2);
        return { path, r, hh: r * 0.38 };
      case "pixel":
        path.rect(-r, -r * 0.9, 2 * r, 1.8 * r);
        return { path, r, hh: r * 0.9 };
      case "line":
      case "round":
      default:
        path.ellipse(0, 0, r, r, 0, 0, Math.PI * 2);
        return { path, r, hh: r };
    }
  }
  if ("path" in shape) {
    path.addPath(new Path2D(shape.path), new DOMMatrix().scale(r, r));
    return { path, r, hh: r };
  }
  const img = pack.images.get(shape.image)!;
  const iw = eyeW * (shape.scale ?? 1);
  const ih = (iw * img.naturalHeight) / img.naturalWidth;
  const [ax, ay] = shape.anchor ?? [0.5, 0.5];
  path.rect(-ax * iw, -ay * ih, iw, ih);
  return { path, r: iw / 2, hh: ih / 2 };
}

function drawEye(
  ctx: Ctx,
  S: number,
  x: number,
  y: number,
  side: -1 | 1,
  p: FaceParams,
  pack: ThemePack,
  eyeW: number,
) {
  const { theme } = pack;
  const shape = theme.shapes.eye;
  const pal = theme.palette;
  const open = side < 0 ? p.open_l : p.open_r;
  const tilt = side < 0 ? p.tilt_l : p.tilt_r;
  // Local frame is mirrored for the right eye so +x always points to the face centre.
  const gx = side < 0 ? p.gaze_x : -p.gaze_x;
  const gy = -p.gaze_y;

  ctx.save();
  ctx.translate(x, y);
  ctx.scale(side < 0 ? 1 : -1, 1);

  if ("preset" in shape && shape.preset === "line") {
    // Minimal theme: a glowing capsule whose height follows the lid opening.
    const r = eyeW / 2;
    const cw = r * 0.42;
    const ch = Math.max(cw, 2 * r * open * (1 - p.squint * 0.45));
    ctx.translate(gx * r * 0.5, gy * r * 0.4);
    ctx.rotate(-tilt * 0.35);
    ctx.fillStyle = pal.iris;
    ctx.beginPath();
    ctx.roundRect(-cw / 2, -ch / 2, cw, ch, cw / 2);
    ctx.fill();
    ctx.restore();
    return;
  }

  const { path, r, hh } = eyeGeometry(shape, eyeW, pack);
  const stroke = (theme.render?.stroke ?? 0) * S;

  // Lid lines: the upper lid comes down with (1 - open) and slopes with tilt
  // (positive tilt lowers the inner corner); squint raises the lower lid.
  const slope = Math.tan(tilt * 0.45);
  let upper = -hh + (1 - open) * 2 * hh;
  let lower = hh - p.squint * hh * 0.8;
  if (upper > lower) upper = lower = (upper + lower) / 2;
  const X = r * 2;
  // Squinting bows the lower lid upwards ("smiling eyes").
  // The curve spans ±2r, so the eye's own corners sit a quarter of `bow` below the centre.
  const bow = p.squint * hh * 4;
  const lowerLid = (path: Path2D | CanvasRenderingContext2D, from: number) => {
    path.moveTo(from, lower + bow);
    path.quadraticCurveTo(0, lower - bow, -from, lower + bow);
  };
  const band = new Path2D();
  band.moveTo(-X, upper - X * slope);
  band.lineTo(X, upper + X * slope);
  band.lineTo(X, lower + bow);
  band.quadraticCurveTo(0, lower - bow, -X, lower + bow);
  band.closePath();

  ctx.save();
  ctx.clip(path);
  ctx.shadowBlur = 0;
  // Visible lids only when they differ from the background; drawing them on top of
  // the sclera would leave an anti-aliased ghost of the eye outline.
  if (pal.lid.toLowerCase() !== theme.palette.bg.toLowerCase()) {
    ctx.fillStyle = pal.lid;
    ctx.fillRect(-X, -X * 2, 2 * X, X * 4);
  }
  ctx.clip(band);
  if ("image" in shape) {
    const img = pack.images.get(shape.image)!;
    const [ax, ay] = shape.anchor ?? [0.5, 0.5];
    ctx.drawImage(img, -ax * 2 * r, -ay * 2 * hh, 2 * r, 2 * hh);
    // A flame-like slit pupil that follows the gaze.
    ctx.fillStyle = pal.pupil;
    ctx.beginPath();
    ctx.ellipse(gx * r * 0.35, hh * 0.25 + gy * hh * 0.3, r * 0.07 * (0.6 + p.pupil), hh * 0.32, 0, 0, Math.PI * 2);
    ctx.fill();
  } else {
    ctx.fillStyle = pal.sclera;
    ctx.fillRect(-r, -hh, 2 * r, 2 * hh);
    const ir = Math.min(r, hh) * 0.5;
    const ix = gx * r * 0.42;
    const iy = gy * hh * 0.42;
    ctx.fillStyle = pal.iris;
    ctx.beginPath();
    ctx.arc(ix, iy, ir, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = pal.pupil;
    ctx.beginPath();
    ctx.arc(ix, iy, ir * (0.3 + 0.45 * p.pupil), 0, Math.PI * 2);
    ctx.fill();
    // Specular highlight keeps the eye alive.
    ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
    ctx.beginPath();
    ctx.arc(ix - ir * 0.35, iy - ir * 0.4, ir * 0.18, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();

  if (stroke > 0) {
    // Lid edges, inside the eye shape, so a closed eye reads as a single line.
    ctx.save();
    ctx.clip(path);
    ctx.strokeStyle = pal.pupil;
    ctx.lineWidth = stroke;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(-X, upper - X * slope);
    ctx.lineTo(X, upper + X * slope);
    if (lower < hh * 0.98) lowerLid(ctx, X);
    ctx.stroke();
    ctx.restore();

    // Outline only where the eye is open.
    ctx.save();
    ctx.clip(band);
    ctx.strokeStyle = pal.pupil;
    ctx.lineWidth = stroke;
    ctx.stroke(path);
    ctx.restore();
  }
  ctx.restore();
}

// --- mouth ------------------------------------------------------------------

function drawMouth(ctx: Ctx, S: number, x: number, y: number, p: FaceParams, pack: ThemePack, mw: number) {
  const { theme } = pack;
  const shape = theme.shapes.mouth;
  const pal = theme.palette;
  const half = (mw / 2) * (0.5 + 0.55 * p.width);
  const lift = p.curve * mw * 0.16;
  const tilt = p.asym * mw * 0.07;
  const openPx = p.open * mw * 0.42;

  ctx.save();
  ctx.translate(x, y);

  if ("image" in shape) {
    const img = pack.images.get(shape.image)!;
    const iw = 2 * half * (shape.scale ?? 1);
    const ih = ((iw * img.naturalHeight) / img.naturalWidth) * (0.35 + 0.9 * p.open);
    ctx.rotate(p.asym * 0.12);
    if (p.curve < -0.15) ctx.scale(1, -1);
    const [ax, ay] = shape.anchor ?? [0.5, 0.5];
    ctx.drawImage(img, -ax * iw, -ay * ih, iw, ih);
    ctx.restore();
    return;
  }

  // Corners rise with curve (smile); asym lifts one side.
  const lx = -half;
  const ly = -lift + tilt;
  const rx = half;
  const ry = -lift - tilt;
  const upperCtrl = lift * 0.7;
  const lowerCtrl = upperCtrl + openPx * 2;
  const lineW = S * 0.02;

  const outline = new Path2D();
  outline.moveTo(lx, ly);
  outline.quadraticCurveTo(0, upperCtrl, rx, ry);
  outline.quadraticCurveTo(0, lowerCtrl, lx, ly);

  const isLine = "preset" in shape && shape.preset === "line";
  if (openPx < S * 0.006 || isLine) {
    ctx.strokeStyle = pal.mouth;
    ctx.lineWidth = isLine ? S * 0.016 : lineW;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    if (openPx < S * 0.006) {
      ctx.beginPath();
      ctx.moveTo(lx, ly);
      ctx.quadraticCurveTo(0, upperCtrl, rx, ry);
      ctx.stroke();
    } else {
      ctx.stroke(outline);
    }
    ctx.restore();
    return;
  }

  let mouth = outline;
  if ("path" in shape) {
    mouth = new Path2D();
    mouth.addPath(new Path2D(shape.path), new DOMMatrix().translate(0, -lift).scale(half, Math.max(openPx, S * 0.01)));
  }
  ctx.fillStyle = pal.mouth;
  ctx.fill(mouth);

  if (p.teeth > 0.01) {
    ctx.save();
    ctx.clip(mouth);
    ctx.shadowBlur = 0;
    const th = openPx * 0.9 * p.teeth;
    ctx.fillStyle = pal.teeth;
    ctx.beginPath();
    ctx.moveTo(lx, ly);
    ctx.quadraticCurveTo(0, upperCtrl, rx, ry);
    ctx.lineTo(rx, ry + th);
    ctx.quadraticCurveTo(0, upperCtrl + th, lx, ly + th);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  const stroke = (theme.render?.stroke ?? 0) * S;
  if (stroke > 0) {
    ctx.strokeStyle = pal.pupil;
    ctx.lineWidth = stroke;
    ctx.lineJoin = "round";
    ctx.stroke(mouth);
  }
  ctx.restore();
}
