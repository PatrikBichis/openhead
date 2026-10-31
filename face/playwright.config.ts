import { defineConfig } from "@playwright/test";

const CI = !!process.env.CI;

export default defineConfig({
  testDir: "tests",
  // One golden per image, shared by all platforms; the tolerance absorbs anti-aliasing differences.
  snapshotPathTemplate: "{testDir}/golden/{arg}{ext}",
  fullyParallel: true,
  forbidOnly: CI,
  // A rare timing hiccup under load (pre-push runs everything at once) is retried once and
  // reported as "flaky" instead of blocking the push; a real regression fails both tries.
  retries: 1,
  reporter: CI ? [["list"], ["html", { open: "never" }]] : "list",
  expect: {
    toHaveScreenshot: { maxDiffPixelRatio: 0.01, threshold: 0.2, animations: "disabled" },
  },
  use: {
    baseURL: "http://localhost:4173",
    browserName: "chromium",
    // iPhone 12 in landscape (how the head is mounted), in points; scale 1 keeps goldens small.
    viewport: { width: 844, height: 390 },
    deviceScaleFactor: 1,
  },
  webServer: {
    command: "npm run preview",
    url: "http://localhost:4173",
    reuseExistingServer: !CI,
  },
});
