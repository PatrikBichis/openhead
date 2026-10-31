import { defineConfig } from "vite";

export default defineConfig({
  // Relative URLs so the bundle also loads from file:// inside the iOS app's WKWebView.
  base: "./",
  input: { main: "index.html", gallery: "gallery.html" },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
