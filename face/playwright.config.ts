import { defineConfig } from "@playwright/test";

const CI = !!process.env.CI;

export default defineConfig({
  testDir: "tests",
  // One golden per image, shared by all platforms; the tolerance absorbs anti-aliasing differences.
  snapshotPathTemplate: "{testDir}/golden/{arg}{ext}",
  fullyParallel: true,
  forbidOnly: CI,
  reporter: CI ? [["list"], ["html", { open: "never" }]] : "list",
  expect: {
    toHaveScreenshot: { maxDiffPixelRatio: 0.01, threshold: 0.2, animations: "disabled" },
  },
  use: {
    baseURL: "http://localhost:4173",
    browserName: "chromium",
    // iPhone 12 in points; device scale 1 keeps goldens small.
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 1,
  },
  webServer: {
    command: "npm run preview",
    url: "http://localhost:4173",
    reuseExistingServer: !CI,
  },
});
