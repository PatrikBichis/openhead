# Face engine

TypeScript + Canvas 2D face engine, built with Vite. It runs in the iOS app's WKWebView, in the desktop simulator and in Playwright tests, and knows nothing about the network.

```bash
cd face
npm ci
npm run dev        # http://localhost:5173/?theme=halloween&emotion=happy  (gallery.html shows every combination)
npm run build      # generates theme types from protocol/schema, typechecks, writes dist/
npm test           # Playwright: golden images (3 themes × 10 emotions + extras + iPad landscape) and API tests
npm run gallery    # test-results/gallery.png with every theme × expression
```

After an intentional visual change, review `npm run gallery`, then `npm run test:update` and commit the new files in `tests/golden/`.

## API

`window.openhead` is a `FaceEngine` (`src/engine.ts`):

| Method | Notes |
| --- | --- |
| `setTheme(name, transitionMs = 300)` | Rejects unknown names. Cross-fades. |
| `setEmotion(name, intensity = 1, blend = "replace", durationMs?)` | Unknown names fall back to `neutral` with a warning. |
| `setGaze(x, y)` | Screen frame, [-1, 1], +y up. |
| `setEnvelope(level)` | 0–1 at 20–30 Hz while speaking; decays after 200 ms without updates. |
| `blink()`, `setIdle(on)` | Idle motion: blinks, saccades, breathing, jitter. |
| `tick(dtMs)`, `render()`, `start()`, `stop()` | Hosts drive time; `start()` uses `requestAnimationFrame`. |
| `state()`, `params()`, `listThemes()` | Current theme, emotion, parameters; installed themes for `face.list`. |

Query parameters: `theme`, `emotion`, `test` (no idle motion, no animation loop), `seed`.

## Themes

Each folder in `themes/` holds `theme.json`, `expressions.json` and optional `assets/`; both JSON files are validated against `protocol/schema` by `tools/protocol.py check`. Themes are bundled at build time, so the engine works offline and from `file://`. See [docs/themes.md](../docs/themes.md).
