import type { Page } from "@playwright/test";

/** Open the face page in deterministic test mode and wait until the theme is loaded. */
export async function openFace(page: Page, theme: string) {
  await page.goto(`/?test&theme=${theme}`);
  await page.waitForFunction(() => document.documentElement.dataset.ready === "1");
}

/** Advance the engine past all transitions and draw one frame. */
export async function settle(page: Page, ms = 1000) {
  await page.evaluate((ms) => {
    for (let t = 0; t < ms; t += 50) window.openhead.tick(50);
    window.openhead.render();
  }, ms);
}
