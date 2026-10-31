import { expect, test } from "@playwright/test";
import { SHARED_EMOTIONS } from "../src/params";
import { openFace, settle } from "./face";

const THEMES = ["cartoon", "minimal", "halloween"];

for (const theme of THEMES) {
  for (const emotion of SHARED_EMOTIONS) {
    test(`${theme} × ${emotion}`, async ({ page }) => {
      await openFace(page, theme);
      await page.evaluate((e) => window.openhead.setEmotion(e, 1), emotion);
      await settle(page);
      await expect(page.locator("#face")).toHaveScreenshot(`${theme}-${emotion}.png`);
    });
  }
}

test("halloween × cackle (theme extra)", async ({ page }) => {
  await openFace(page, "halloween");
  await page.evaluate(() => window.openhead.setEmotion("cackle", 1));
  await settle(page);
  await expect(page.locator("#face")).toHaveScreenshot("halloween-cackle.png");
});

// The phone is normally mounted in landscape (default viewport); other shapes must still work.
for (const [shape, viewport] of [
  ["portrait", { width: 390, height: 844 }],
  ["ipad", { width: 1024, height: 768 }],
] as const) {
  test.describe(shape, () => {
    test.use({ viewport });
    for (const theme of THEMES) {
      test(`${theme} keeps proportions`, async ({ page }) => {
        await openFace(page, theme);
        await page.evaluate(() => window.openhead.setEmotion("happy", 1));
        await settle(page);
        await expect(page.locator("#face")).toHaveScreenshot(`${theme}-happy-${shape}.png`);
      });
    }
  });
}
