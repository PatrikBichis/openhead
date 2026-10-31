import type { Expressions, Params } from "./generated/expressions";
import type { Shape, Theme } from "./generated/theme";
import { SHARED_EMOTIONS, type SharedEmotion } from "./params";

export interface ThemePack {
  theme: Theme;
  expressions: Expressions;
  images: Map<string, HTMLImageElement>;
}

export interface ThemeInfo {
  name: string;
  version: string;
  title: string;
  expressions: string[];
  extras: string[];
}

// Themes are bundled at build time, so the engine works offline and from file://.
const themes = import.meta.glob<Theme>("../themes/*/theme.json", { eager: true, import: "default" });
const expressions = import.meta.glob<Expressions>("../themes/*/expressions.json", {
  eager: true,
  import: "default",
});
const assets = import.meta.glob<string>("../themes/*/assets/*", {
  eager: true,
  query: "?url",
  import: "default",
});

const themeKey = (name: string) => `../themes/${name}/theme.json`;

/** Preset for an emotion: a shared name at the top level, or a theme extra. */
export function presetFor(expr: Expressions, name: string): Params | undefined {
  const shared = (SHARED_EMOTIONS as readonly string[]).includes(name);
  return shared ? expr[name as SharedEmotion] : expr.extra?.[name];
}

export function themeNames(): string[] {
  return Object.keys(themes)
    .map((key) => key.split("/")[2])
    .sort();
}

export function themeInfo(name: string): ThemeInfo {
  const theme = themes[themeKey(name)];
  if (!theme) throw new Error(`unknown theme: ${name}`);
  const expr = expressions[`../themes/${name}/expressions.json`];
  return {
    name,
    version: theme.version,
    title: theme.title ?? name,
    expressions: Object.keys(expr).filter((k) => k !== "extra"),
    extras: Object.keys(expr.extra ?? {}),
  };
}

const cache = new Map<string, Promise<ThemePack>>();

export function loadTheme(name: string): Promise<ThemePack> {
  let pack = cache.get(name);
  if (!pack) {
    pack = load(name);
    cache.set(name, pack);
    pack.catch(() => cache.delete(name));
  }
  return pack;
}

async function load(name: string): Promise<ThemePack> {
  const theme = themes[themeKey(name)];
  if (!theme) throw new Error(`unknown theme: ${name}`);
  const images = new Map<string, HTMLImageElement>();
  const shapes: Shape[] = [theme.shapes.eye, theme.shapes.mouth];
  for (const shape of shapes) {
    if (!("image" in shape)) continue;
    const url = assets[`../themes/${name}/${shape.image}`];
    if (!url) throw new Error(`theme ${name}: missing ${shape.image}`);
    const img = new Image();
    img.src = url;
    await img.decode();
    images.set(shape.image, img);
  }
  return { theme, expressions: expressions[`../themes/${name}/expressions.json`], images };
}
