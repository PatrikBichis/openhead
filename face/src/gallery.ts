import { FaceEngine } from "./engine";
import { themeInfo, themeNames } from "./themes";

// Every theme × expression side by side, for reviewing changes by eye.
const root = document.querySelector<HTMLDivElement>("#gallery")!;

for (const name of themeNames()) {
  const info = themeInfo(name);
  const heading = document.createElement("h2");
  heading.textContent = `${info.title} (${name} ${info.version})`;
  const row = document.createElement("div");
  row.className = "row";
  root.append(heading, row);

  for (const emotion of [...info.expressions, ...info.extras]) {
    const figure = document.createElement("figure");
    const canvas = document.createElement("canvas");
    const caption = document.createElement("figcaption");
    caption.textContent = emotion;
    figure.append(canvas, caption);
    row.append(figure);

    const engine = new FaceEngine(canvas, { idle: false });
    await engine.setTheme(name, 0);
    engine.setEmotion(emotion);
    engine.tick(1000);
    engine.render();
  }
}
document.documentElement.dataset.ready = "1";
