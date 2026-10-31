# Themes

A theme is a folder in `face/themes/<name>/`:

```
theme.json        # palette, shapes, layout, render effects, idle behaviour, envelope curve
expressions.json  # parameter preset per emotion, plus theme-specific extras
assets/           # optional SVG/PNG for image-based eyes and mouth
```

Schemas: [theme](../protocol/docs/theme.schema.md), [expressions](../protocol/docs/expressions.schema.md). `uv run --project python python tools/protocol.py check` validates every theme; the folder name must equal `name`.

## Shapes

`shapes.eye` and `shapes.mouth` are one of:

- `{"preset": "round" | "almond" | "slit" | "pixel" | "line"}`. `line` eyes are glowing capsules and a `line` mouth is only stroked (the `minimal` theme).
- `{"path": "<SVG path>"}` in a [-1, 1] box, used as the clip shape.
- `{"image": "assets/eye.svg", "anchor": [0.5, 0.5], "scale": 1}`. Lids still close over image eyes; image mouths stretch with `open` and flip for frowns (the `halloween` theme).

## Expressions

Parameters: eyes `open_l`, `open_r`, `tilt_l`, `tilt_r` (positive lowers the inner corner), `pupil`, `gaze_x`, `gaze_y`, `squint`; mouth `open`, `width`, `curve` (+ smile), `asym`, `teeth`; global `head_tilt`, `breath_rate`, `blink_rate`, `jitter`. `_l` is the eye on the left of the screen.

`neutral` must set every parameter; other presets only set what differs. Active emotions blend as weighted differences from `neutral` and tween over 250 ms. `resting_emotion` is shown whenever no other emotion is held.

Shared names every theme should define: `neutral`, `happy`, `curious`, `thinking`, `surprised`, `sad`, `angry`, `sleepy`, `scared`, `mischievous`. Extras go under `extra` and are reported by `face.list`.

## Adding a theme

1. Copy a theme folder and change `name`.
2. Run `npm run dev` in `face/` and open `/gallery.html` while editing.
3. `tools/protocol.py check`, then `npm run test:update` to add golden images (add the theme to `tests/golden.spec.ts`).
