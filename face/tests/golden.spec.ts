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

test.describe("iPad landscape", () => {
  test.use({ viewport: { width: 1024, height: 768 } });
  for (const theme of THEMES) {
    test(`${theme} keeps proportions`, async ({ page }) => {
      await openFace(page, theme);
      await page.evaluate(() => window.openhead.setEmotion("happy", 1));
      await settle(page);
      await expect(page.locator("#face")).toHaveScreenshot(`${theme}-happy-landscape.png`);
    });
  }
});
