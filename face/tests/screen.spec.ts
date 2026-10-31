import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { openFace, settle } from "./face";

// Media shared with the YAML scenarios (scenarios/assets, see make_assets.py), served under /media/.
const ASSETS = fileURLToPath(new URL("../../scenarios/assets/", import.meta.url));
const TYPES: Record<string, string> = {
  png: "image/png", svg: "image/svg+xml", gif: "image/gif", mp4: "video/mp4", html: "text/html",
};

async function open(page: Page, theme = "cartoon") {
  await page.route("**/media/**", async (route) => {
    const name = new URL(route.request().url()).pathname.split("/").pop()!;
    if (name === "page.html") {
      return route.fulfill({ contentType: "text/html", body: "<body style='background:#2a9d8f;font:40px sans-serif'>web page</body>" });
    }
    let body: Buffer;
    try {
      body = readFileSync(ASSETS + name);
    } catch {
      return route.fulfill({ status: 404, body: "not found" });
    }
    const contentType = TYPES[name.split(".").pop()!];
    // Video seeks with range requests, as from any web server.
    const range = /bytes=(\d+)-(\d*)/.exec(route.request().headers()["range"] ?? "");
    if (!range) return route.fulfill({ body, contentType, headers: { "accept-ranges": "bytes" } });
    const start = Number(range[1]);
    const end = range[2] ? Math.min(Number(range[2]), body.length - 1) : body.length - 1;
    await route.fulfill({
      status: 206,
      body: body.subarray(start, end + 1),
      contentType,
      headers: { "accept-ranges": "bytes", "content-range": `bytes ${start}-${end}/${body.length}` },
    });
  });
  await openFace(page, theme);
  // The subtitle font loads on first use; load it now so it cannot swap mid-screenshot.
  await page.evaluate(() => document.fonts.load('600 24px "Inter Variable"'));
}

const show = (page: Page, content: string, source: string, opts: object = {}) =>
  page.evaluate(([c, s, o]) => window.openhead.show(c as never, s as string, o as object), [content, source, opts] as const);
const subtitle = (page: Page, text: string, opts: object = {}) =>
  page.evaluate(([t, o]) => window.openhead.subtitle(t, o), [text, opts] as const);
const screenState = (page: Page) => page.evaluate(() => window.openhead.screen());
const tick = (page: Page, ms: number) =>
  page.evaluate((ms) => {
    for (let t = 0; t < ms; t += 20) window.openhead.tick(20);
    window.openhead.render();
  }, ms);

test.describe("image", () => {
  test("PNG fills the screen and hides the face", async ({ page }) => {
    await open(page);
    await show(page, "image", "/media/test-card.png");
    expect(await screenState(page)).toEqual({ view: "image", overlay: "none", subtitle: "" });
    await expect(page).toHaveScreenshot("screen-image-png.png");
  });

  test("SVG stays sharp at full size", async ({ page }) => {
    await open(page);
    await show(page, "image", "/media/test-card.svg");
    await expect(page).toHaveScreenshot("screen-image-svg.png");
  });

  test("SVG as a data URI", async ({ page }) => {
    await open(page);
    const svg = readFileSync(ASSETS + "test-card.svg").toString("base64");
    await show(page, "image", `data:image/svg+xml;base64,${svg}`);
    await expect(page).toHaveScreenshot("screen-image-svg.png");
  });

  test("animated GIF loads and plays", async ({ page }) => {
    await open(page);
    await show(page, "image", "/media/spinner.gif");
    const size = await page.evaluate(() => {
      const img = document.querySelector<HTMLImageElement>("#display img")!;
      return [img.naturalWidth, img.naturalHeight];
    });
    expect(size).toEqual([120, 120]);
    expect((await screenState(page)).view).toBe("image");
  });

  test("face keeps running in the corner", async ({ page }) => {
    await open(page);
    await page.evaluate(() => window.openhead.setEmotion("happy", 1));
    await show(page, "image", "/media/test-card.svg", { overlay: "face-corner" });
    await settle(page);
    expect((await screenState(page)).overlay).toBe("face-corner");
    await expect(page).toHaveScreenshot("screen-image-face-corner.png");
  });

  test("a bad source is rejected and the screen stays as it was", async ({ page }) => {
    await open(page);
    await show(page, "image", "/media/test-card.png");
    const error = await page.evaluate(() =>
      window.openhead.show("image", "/media/missing.png").then(() => "", (e) => String(e)));
    expect(error).toContain("could not load image /media/missing.png");
    expect(await page.locator("#display img").getAttribute("src")).toBe("/media/test-card.png");
  });

  test("clear brings the face back", async ({ page }) => {
    await open(page);
    await show(page, "image", "/media/test-card.png", { overlay: "face-corner" });
    await page.evaluate(() => window.openhead.clear());
    await settle(page);
    expect(await screenState(page)).toEqual({ view: "face", overlay: "none", subtitle: "" });
    await expect(page.locator("#display")).toBeHidden();
    await expect(page).toHaveScreenshot("screen-face-after-clear.png");
  });
});

test.describe("video", () => {
  /** Pause at `seconds` and wait for the frame, so the screenshot is deterministic. */
  async function seek(page: Page, seconds: number) {
    await page.evaluate(async (s) => {
      const v = document.querySelector("video")!;
      v.pause();
      const seeked = new Promise((ok) => v.addEventListener("seeked", ok, { once: true }));
      v.currentTime = s;
      await seeked;
      await new Promise((ok) => requestAnimationFrame(() => requestAnimationFrame(ok)));
    }, seconds);
  }

  test("plays H.264, frame at 0.5 s and 2.5 s", async ({ page }) => {
    await open(page);
    await show(page, "video", "/media/clip.mp4", { muted: true });
    expect((await screenState(page)).view).toBe("video");
    expect(await page.evaluate(() => document.querySelector("video")!.duration)).toBeCloseTo(3, 1);
    await seek(page, 0.5);
    await expect(page).toHaveScreenshot("screen-video-0.5s.png", { maxDiffPixelRatio: 0.02 });
    await seek(page, 2.5);
    await expect(page).toHaveScreenshot("screen-video-2.5s.png", { maxDiffPixelRatio: 0.02 });
  });

  test("with the face in the corner", async ({ page }) => {
    await open(page);
    await show(page, "video", "/media/clip.mp4", { muted: true, overlay: "face-corner" });
    await seek(page, 1.5);
    await settle(page);
    await expect(page).toHaveScreenshot("screen-video-face-corner.png", { maxDiffPixelRatio: 0.02 });
  });

  test("returns to the face when it ends and tells the host", async ({ page }) => {
    await open(page);
    const events: string[] = [];
    page.on("console", (m) => m.text().startsWith("[face-event]") && events.push(m.text()));
    await show(page, "video", "/media/clip.mp4", { muted: true });
    await page.evaluate(() => {
      const v = document.querySelector("video")!;
      v.currentTime = 2.8;
      return v.play();
    });
    await expect.poll(() => screenState(page).then((s) => s.view), { timeout: 5000 }).toBe("face");
    expect(events.join("\n")).toContain('"reason":"video ended"');
  });

  test("freezeVideo shows the current frame as a still (for iOS snapshots)", async ({ page }) => {
    await open(page);
    await show(page, "video", "/media/clip.mp4", { muted: true });
    await seek(page, 2.5);
    await page.evaluate(() => window.openhead.freezeVideo(true));
    await page.evaluate(() => document.querySelector("video")!.style.visibility = "hidden");
    await expect(page).toHaveScreenshot("screen-video-2.5s.png", { maxDiffPixelRatio: 0.02 });
    await page.evaluate(() => window.openhead.freezeVideo(false));
    expect(await page.locator("canvas.frame").count()).toBe(0);
  });

  test("loops when asked", async ({ page }) => {
    await open(page);
    await show(page, "video", "/media/clip.mp4", { muted: true, loop: true });
    expect(await page.evaluate(() => document.querySelector("video")!.loop)).toBe(true);
  });

  test("showing something else stops the video", async ({ page }) => {
    await open(page);
    await show(page, "video", "/media/clip.mp4", { muted: true });
    await show(page, "image", "/media/test-card.png");
    expect(await page.locator("video").count()).toBe(0);
  });
});

test.describe("web", () => {
  test("in an iframe (simulator)", async ({ page }) => {
    await open(page);
    await show(page, "web", "/media/page.html", { overlay: "face-corner" });
    await expect(page.frameLocator("#display iframe").locator("body")).toHaveText("web page");
    expect((await screenState(page)).view).toBe("web");
  });

  test("native on iOS: the page turns transparent, the face stays in the corner", async ({ page }) => {
    await open(page);
    await show(page, "web", "https://example.com", { overlay: "face-corner", nativeWeb: true });
    await settle(page);
    expect(await page.locator("#display iframe").count()).toBe(0);
    expect(await page.evaluate(() => getComputedStyle(document.body).backgroundColor)).toBe("rgba(0, 0, 0, 0)");
    await expect(page).toHaveScreenshot("screen-web-native-corner.png", { omitBackground: true });
  });
});

test.describe("subtitles", () => {
  test("a line at the bottom over the face", async ({ page }) => {
    await open(page);
    await subtitle(page, "Hello! I can't speak, so I write.");
    expect((await screenState(page)).subtitle).toBe("Hello! I can't speak, so I write.");
    await expect(page).toHaveScreenshot("screen-subtitle-bottom.png");
  });

  test("at the top, over an image", async ({ page }) => {
    await open(page);
    await show(page, "image", "/media/test-card.svg");
    await subtitle(page, "Map of the kitchen", { position: "top" });
    await expect(page).toHaveScreenshot("screen-subtitle-top-image.png");
  });

  test("append streams an answer; only the newest three lines show", async ({ page }) => {
    await open(page, "minimal");
    const words = ("The robot answers in pieces as the language model produces them, and the head " +
      "keeps the newest lines on screen so the end of the answer is always visible to the person " +
      "in front of it, even when the whole answer is far too long to fit.").split(" ");
    for (const [i, w] of words.entries()) await subtitle(page, (i ? " " : "") + w, { mode: "append" });
    expect((await screenState(page)).subtitle).toBe(words.join(" "));
    const box = await page.locator("#subtitles").boundingBox();
    expect(box!.height).toBeLessThan(390 * 0.4);
    await expect(page).toHaveScreenshot("screen-subtitle-append-clamped.png");
  });

  test("line breaks are kept", async ({ page }) => {
    await open(page, "halloween");
    await subtitle(page, "Trick\nor treat?");
    await expect(page).toHaveScreenshot("screen-subtitle-lines.png");
  });

  test("clear and duration", async ({ page }) => {
    await open(page);
    await subtitle(page, "gone soon", { durationMs: 1000 });
    await tick(page, 900);
    await expect(page.locator("#subtitles")).toBeVisible();
    await tick(page, 200);
    await expect(page.locator("#subtitles")).toBeHidden();
    expect((await screenState(page)).subtitle).toBe("");
    await subtitle(page, "held");
    await subtitle(page, "", { mode: "clear" });
    await expect(page.locator("#subtitles")).toBeHidden();
  });

  test("appending restarts the duration", async ({ page }) => {
    await open(page);
    await subtitle(page, "one", { durationMs: 1000 });
    await tick(page, 800);
    await subtitle(page, " two", { mode: "append", durationMs: 1000 });
    await tick(page, 800);
    expect((await screenState(page)).subtitle).toBe("one two");
  });

  test("mouth moves with the text, then closes", async ({ page }) => {
    await open(page);
    await subtitle(page, "Hello there, how are you?", { mouth: true });
    const opens = await page.evaluate(() => {
      const values: number[] = [];
      for (let i = 0; i < 100; i++) {
        window.openhead.tick(20);
        values.push(window.openhead.state().envelope);
      }
      for (let i = 0; i < 50; i++) window.openhead.tick(20);
      return { max: Math.max(...values), min: Math.min(...values.slice(10)), end: window.openhead.state().envelope };
    });
    expect(opens.max).toBeGreaterThan(0.5);
    expect(opens.min).toBeLessThan(0.2); // closes between words
    expect(opens.end).toBeLessThan(0.05);
  });

  test("a streamed envelope from the host wins over the text mouth", async ({ page }) => {
    await open(page);
    await subtitle(page, "aaaaaaaaaaaaaaaaaaaa", { mouth: true });
    const level = await page.evaluate(() => {
      for (let i = 0; i < 20; i++) {
        window.openhead.setEnvelope(0.1);
        window.openhead.tick(20);
      }
      return window.openhead.state().envelope;
    });
    expect(level).toBeLessThan(0.2);
  });
});

test.describe("animation at fixed times", () => {
  test("emotion transition halfway", async ({ page }) => {
    await open(page);
    await page.evaluate(() => window.openhead.setEmotion("surprised", 1));
    await tick(page, 120);
    await expect(page.locator("#face")).toHaveScreenshot("anim-neutral-to-surprised-120ms.png");
  });

  test("theme cross-fade halfway", async ({ page }) => {
    await open(page);
    await page.evaluate(() => window.openhead.setTheme("halloween", 400));
    await tick(page, 200);
    await expect(page.locator("#face")).toHaveScreenshot("anim-cartoon-to-halloween-200ms.png");
  });

  test("blink closes the eyes, then opens them", async ({ page }) => {
    await open(page);
    const open_ = await page.evaluate(() => {
      const f = window.openhead;
      f.blink();
      const seen: number[] = [];
      for (let i = 0; i < 30; i++) {
        f.tick(10);
        seen.push(f.params().open_l);
      }
      for (let i = 0; i < 50; i++) f.tick(20);
      return { min: Math.min(...seen), after: f.params().open_l };
    });
    expect(open_.min).toBeLessThan(0.15);
    expect(open_.after).toBeGreaterThan(0.6);
  });

  test("look_at moves the pupils over time", async ({ page }) => {
    await open(page);
    const xs = await page.evaluate(() => {
      const f = window.openhead;
      f.setGaze(1, 0);
      const out: number[] = [];
      for (const ms of [0, 40, 80, 400]) {
        if (ms) f.tick(ms - (out.length ? [0, 40, 80, 400][out.length - 1] : 0));
        out.push(f.params().gaze_x);
      }
      return out;
    });
    expect(xs[0]).toBeLessThan(xs[1]);
    expect(xs[1]).toBeLessThan(xs[2]);
    expect(xs[3]).toBeGreaterThan(0.9);
  });
});
