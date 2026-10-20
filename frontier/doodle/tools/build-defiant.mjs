// Every frontier piece in one module for defiant.to: <ani-doodle piece="frontier-car-t">.
//   node tools/build-defiant.mjs     -> ../../assets/doodles/defiant.mjs
// A piece is src/canvas-core/frontier<Name>.ts exporting `frontier<Name>` (a Piece); its tag name
// is the kebab of that export: frontierCarT -> frontier-car-t.
import { build } from "esbuild";
import { mkdirSync, readdirSync, writeFileSync } from "node:fs";
import { gzipSync } from "node:zlib";
const names = readdirSync("src/canvas-core").filter((f) => /^frontier[A-Z]\w*\.ts$/.test(f) && !f.endsWith("Film.ts")).map((f) => f.slice(0, -3));
const kebab = (n) => n.replace(/([a-z0-9])([A-Z])/g, "$1-$2").replace(/([A-Z])([A-Z][a-z])/g, "$1-$2").toLowerCase();
const src = `import { define } from "./src/hosts/interactive";\n${names.map((n) => `import { ${n} } from "./src/canvas-core/${n}";`).join("\n")}\ndefine({ ${names.map((n) => `"${kebab(n)}": ${n}`).join(", ")} });`;
const js = (await build({ stdin: { contents: src, resolveDir: process.cwd(), loader: "ts" }, bundle: true, format: "esm", target: "es2020", minify: true, write: false, legalComments: "none" })).outputFiles[0].text;
mkdirSync("../../assets/doodles", { recursive: true });
writeFileSync("../../assets/doodles/defiant.mjs", js);
console.log(`defiant.mjs ${(js.length / 1024).toFixed(1)} KB (${(gzipSync(js).length / 1024).toFixed(1)} KB gzip): ${names.map(kebab).join(", ")}`);
