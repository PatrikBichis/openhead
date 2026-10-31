// Generate TypeScript types for theme packs from protocol/schema.
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { compileFromFile } from "json-schema-to-typescript";

const here = dirname(fileURLToPath(import.meta.url));
const schemaDir = resolve(here, "../../protocol/schema");
const outDir = resolve(here, "../src/generated");
const banner = "// Generated from protocol/schema by face/scripts/gen-types.mjs. Do not edit.";

await mkdir(outDir, { recursive: true });
for (const [schema, out] of [
  ["theme.schema.json", "theme.ts"],
  ["expressions.schema.json", "expressions.ts"],
]) {
  const ts = await compileFromFile(resolve(schemaDir, schema), {
    bannerComment: banner,
    cwd: schemaDir,
    additionalProperties: false,
    style: { singleQuote: false },
  });
  await writeFile(resolve(outDir, out), ts);
}
