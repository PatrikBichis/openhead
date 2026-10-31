import { expect, test, type Page } from "@playwright/test";
import { openFace, settle } from "./face";

// Two people: one close (locked, the largest), one further away.
const FACES = [
  { id: 3, bearing: 12, elevation: -4, size: 0.2, confidence: 0.94, box: { x: 0.26, y: 0.2, w: 0.16, h: 0.34 } },
  { id: 7, bearing: -20, elevation: 3, size: 0.1, confidence: 0.81, box: { x: 0.68, y: 0.28, w: 0.09, h: 0.19 } },
];

// What the host reports a few times a second.
const DEVICE = { battery: 76, charging: false, thermal: "nominal", heading: 47, pitch: 4.5, roll: -6,
  x: 0.12, y: 0.01, z: -0.35, tracking: "normal", mode: "capture", clients: 1 };

async function camera(page: Page, hud: string, opts: object = {}) {
  await openFace(page, "cartoon");
  await page.evaluate(() => document.fonts.load('600 24px "Inter Variable"'));
  await page.evaluate(([h, o]) => window.openhead.show("camera", "", { hud: h as string, ...(o as object) }), [hud, opts] as const);
  await page.evaluate((f) => window.openhead.setFaces(f), FACES);
  await page.evaluate((d) => window.openhead.setHudValues(d), DEVICE);
}

const tick = (page: Page, ms: number) =>
  page.evaluate((ms) => {
    for (let t = 0; t < ms; t += 20) window.openhead.tick(20);
    window.openhead.render();
  }, ms);

test("lists the HUD themes", async ({ page }) => {
  await openFace(page, "cartoon");
  const huds = await page.evaluate(() => window.openhead.listHuds());
  expect(huds.map((h) => h.name)).toEqual(["boot", "camcorder", "flight", "hunter"]);
});

for (const hud of ["hunter", "camcorder", "boot", "flight"]) {
  test(`${hud} HUD over the synthetic camera`, async ({ page }) => {
    await camera(page, hud);
    await tick(page, 2400); // past the boot text
    expect(await page.evaluate(() => window.openhead.screen())).toMatchObject({ view: "camera", hud, faces: 2 });
    await expect(page).toHaveScreenshot(`hud-${hud}.png`);
  });
}

test("the host's own values, blocks and widgets (display.hud)", async ({ page }) => {
  await camera(page, "camcorder");
  await page.evaluate(() =>
    window.openhead.hudExtras({
      values: { speed: 0.4, task: "DELIVER CUP" },
      blocks: [{ at: "top-left", lines: ["", "", "TASK {task}", "SPEED {speed} M/S", "HDG {heading}"], size: 0.8 }],
      widgets: [{ type: "compass", at: "top" }],
    }),
  );
  await tick(page, 600);
  await expect(page).toHaveScreenshot("hud-camcorder-extras.png");
  // clear removes the host's additions but keeps the device readings
  await page.evaluate(() => window.openhead.hudExtras({ clear: true }));
  await page.evaluate(() => window.openhead.hudExtras({ blocks: [{ at: "top-left", lines: ["", "", "{task} {battery}"] }] }));
  await tick(page, 600);
  await expect(page).toHaveScreenshot("hud-camcorder-extras-cleared.png");
});

test("the horizon follows pitch and roll", async ({ page }) => {
  await camera(page, "flight");
  await page.evaluate(() => window.openhead.setFaces([]));
  await page.evaluate(() => window.openhead.setHudValues({ pitch: -12, roll: 20, heading: 300 }));
  await tick(page, 300);
  await expect(page).toHaveScreenshot("hud-flight-tilted.png");
});

test("no faces: searching, no lock", async ({ page }) => {
  await camera(page, "hunter");
  await page.evaluate(() => window.openhead.setFaces([]));
  await tick(page, 600);
  await expect(page).toHaveScreenshot("hud-hunter-empty.png");
});

test("camera with the face in the corner", async ({ page }) => {
  await camera(page, "camcorder", { overlay: "face-corner" });
  await tick(page, 600);
  await settle(page);
  await expect(page).toHaveScreenshot("hud-camcorder-face-corner.png");
});

test("bare camera without HUD", async ({ page }) => {
  await camera(page, "none");
  await tick(page, 100);
  expect((await page.evaluate(() => window.openhead.screen())).hud).toBe("none");
  await expect(page).toHaveScreenshot("hud-none.png");
});

test("boot HUD types its lines one by one", async ({ page }) => {
  await camera(page, "boot");
  await tick(page, 400);
  await expect(page).toHaveScreenshot("hud-boot-400ms.png");
});

test("an unknown HUD is rejected and the face stays", async ({ page }) => {
  await openFace(page, "cartoon");
  const error = await page.evaluate(() => window.openhead.show("camera", "", { hud: "nope" }).then(() => "", (e) => String(e)));
  expect(error).toContain("unknown hud: nope");
  expect((await page.evaluate(() => window.openhead.screen())).view).toBe("face");
});

test("native camera on iOS: the page is transparent under the HUD", async ({ page }) => {
  await camera(page, "hunter", { nativeCamera: true });
  await tick(page, 100);
  expect(await page.locator("canvas.synthetic-camera").count()).toBe(0);
  expect(await page.evaluate(() => getComputedStyle(document.body).backgroundColor)).toBe("rgba(0, 0, 0, 0)");
});

test("the eyes follow the locked face, then another, then stop", async ({ page }) => {
  await camera(page, "hunter", { overlay: "face-corner" });
  const gaze = () =>
    page.evaluate(() => {
      for (let i = 0; i < 40; i++) window.openhead.tick(20);
      return window.openhead.params().gaze_x;
    });
  await page.evaluate(() => window.openhead.followFace(null));
  const toLocked = await gaze(); // face 3, bearing +12: the viewer's right
  await page.evaluate(() => window.openhead.followFace(7));
  const toSeven = await gaze(); // bearing -20: the viewer's left
  await page.evaluate(() => window.openhead.followFace(undefined));
  const rest = await gaze();
  expect(toLocked).toBeGreaterThan(0.15);
  expect(toSeven).toBeLessThan(-0.25);
  expect(Math.abs(rest)).toBeLessThan(0.1);
});

test("clear hides the HUD", async ({ page }) => {
  await camera(page, "hunter");
  await page.evaluate(() => window.openhead.clear());
  await expect(page.locator("#hud")).toBeHidden();
  expect((await page.evaluate(() => window.openhead.screen())).hud).toBe("none");
});
