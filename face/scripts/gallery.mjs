// Screenshot the gallery page (every theme × expression) for review.
// Usage: npm run build && npm run gallery [-- out.png]
import { spawn } from "node:child_process";
import { mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

const here = dirname(fileURLToPath(import.meta.url));
const out = resolve(process.argv[2] ?? resolve(here, "../test-results/gallery.png"));
const port = 4174;

const server = spawn("npx", ["vite", "preview", "--port", String(port), "--strictPort"], {
  cwd: resolve(here, ".."),
  shell: true,
  stdio: "ignore",
});
try {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1420, height: 900 } });
  for (let i = 0; ; i++) {
    try {
      await page.goto(`http://localhost:${port}/gallery.html`);
      break;
    } catch (err) {
      if (i > 50) throw err;
      await new Promise((r) => setTimeout(r, 200));
    }
  }
  await page.waitForFunction(() => document.documentElement.dataset.ready === "1");
  await mkdir(dirname(out), { recursive: true });
  await page.screenshot({ path: out, fullPage: true });
  await browser.close();
  console.log(out);
} finally {
  server.kill();
  if (process.platform === "win32") spawn("taskkill", ["/pid", String(server.pid), "/T", "/F"]);
}
