import { expect, test } from "@playwright/test";
import { SHARED_EMOTIONS } from "../src/params";
import { openFace, settle } from "./face";

test("lists the three built-in themes with all shared expressions", async ({ page }) => {
  await openFace(page, "cartoon");
  const themes = await page.evaluate(() => window.openhead.listThemes());
  expect(themes.map((t) => t.name)).toEqual(["cartoon", "halloween", "minimal"]);
  for (const t of themes) expect(t.expressions.sort()).toEqual([...SHARED_EMOTIONS].sort());
  expect(themes.find((t) => t.name === "halloween")!.extras).toEqual(["cackle"]);
});

test("unknown emotion falls back to neutral with a warning", async ({ page }) => {
  await openFace(page, "cartoon");
  const warnings: string[] = [];
  page.on("console", (m) => m.type() === "warning" && warnings.push(m.text()));
  await page.evaluate(() => window.openhead.setEmotion("cackle", 1));
  await settle(page);
  expect(await page.evaluate(() => window.openhead.state().emotion)).toBe("neutral");
  expect(warnings.join("\n")).toContain("emotion cackle not in theme cartoon");
});

test("unknown theme is rejected and the current theme stays", async ({ page }) => {
  await openFace(page, "minimal");
  const error = await page.evaluate(() => window.openhead.setTheme("nope").then(() => "", (e) => String(e)));
  expect(error).toContain("unknown theme: nope");
  expect(await page.evaluate(() => window.openhead.state().theme)).toBe("minimal");
});

test("envelope opens the mouth and decays when updates stop", async ({ page }) => {
  await openFace(page, "cartoon");
  const open = await page.evaluate(() => {
    const f = window.openhead;
    for (let i = 0; i < 6; i++) {
      f.setEnvelope(0.8);
      f.tick(40);
    }
    const speaking = f.params().open;
    for (let i = 0; i < 20; i++) f.tick(40);
    return { speaking, silent: f.params().open };
  });
  expect(open.speaking).toBeGreaterThan(0.6);
  expect(open.silent).toBeLessThan(0.05);
});

test("timed emotion returns to resting", async ({ page }) => {
  await openFace(page, "cartoon");
  const emotions = await page.evaluate(() => {
    const f = window.openhead;
    f.setEmotion("surprised", 1, "replace", 500);
    f.tick(300);
    const during = f.state().emotion;
    for (let i = 0; i < 20; i++) f.tick(50);
    return { during, after: f.state().emotion, open: f.params().open };
  });
  expect(emotions).toMatchObject({ during: "surprised", after: "neutral" });
  expect(emotions.open).toBeLessThan(0.01);
});

test("blink closes and reopens the eyes", async ({ page }) => {
  await openFace(page, "cartoon");
  const lids = await page.evaluate(() => {
    const f = window.openhead;
    f.blink();
    f.tick(65);
    const closed = f.params().open_l;
    f.tick(200);
    return { closed, open: f.params().open_l };
  });
  expect(lids.closed).toBeLessThan(0.1);
  expect(lids.open).toBeGreaterThan(0.85);
});

test("gaze follows set_gaze", async ({ page }) => {
  await openFace(page, "cartoon");
  const gaze = await page.evaluate(() => {
    window.openhead.setGaze(1, -1);
    window.openhead.tick(1000);
    const p = window.openhead.params();
    return [p.gaze_x, p.gaze_y];
  });
  expect(gaze[0]).toBeGreaterThan(0.95);
  expect(gaze[1]).toBeLessThan(-0.95);
});

test("theme switch logs and renders without page errors", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await openFace(page, "cartoon");
  for (const theme of ["halloween", "minimal", "cartoon"]) {
    await page.evaluate((t) => window.openhead.setTheme(t, 300), theme);
    await settle(page, 400);
  }
  expect(errors).toEqual([]);
});
