// Load a page that mounts a frontier piece, wait for it, tap it, screenshot rest + after the tap.
//   node tools/check-defiant.mjs <piece> [outprefix]
import { detect } from "./detect.mjs";
import { createServer } from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { join, extname } from "node:path";
const piece = process.argv[2] ?? "frontier-car-t", out = process.argv[3] ?? `out/check-${piece}`;
const ROOT = "out/site", MIME = { ".html": "text/html", ".mjs": "text/javascript", ".css": "text/css" };
const srv = createServer((q, r) => { const u = decodeURIComponent(q.url.split("?")[0]), p = join(ROOT, u === "/" ? "index.html" : u); if (!existsSync(p)) { r.writeHead(404); return r.end(); } r.writeHead(200, { "content-type": MIME[extname(p)] ?? "application/octet-stream" }); r.end(readFileSync(p)); }).listen(0);
const url = `http://127.0.0.1:${srv.address().port}/?piece=${piece}`;
const d = detect(); const b = await d.pw.lib.chromium.launch({ executablePath: d.browser.executablePath });
for (const [name, vp, dpr] of [["desktop", { width: 1100, height: 900 }, 2], ["phone", { width: 390, height: 844 }, 3]]) {
  const p = await b.newPage({ viewport: vp, deviceScaleFactor: dpr, hasTouch: vp.width < 600 }); const errs = [];
  p.on("pageerror", (e) => errs.push(e.message)); p.on("console", (m) => { if (m.type() === "error") errs.push(m.text()); });
  await p.goto(url, { waitUntil: "networkidle" }); const el = p.locator(`ani-doodle[piece=${piece}]`); await el.scrollIntoViewIfNeeded();
  const ms = await p.evaluate(async () => { const t = performance.now(); while (performance.now() - t < 15000) { const c = document.querySelector("ani-doodle canvas"); if (c && c.style.opacity === "1") return performance.now() - t; await new Promise((r) => setTimeout(r, 50)); } return -1; });
  await el.screenshot({ path: `${out}-${name}-rest.png` });
  await el.click({ position: { x: 20, y: 20 } });
  for (const [ms2, tag] of [[450, "burst"], [1200, "scatter"], [2600, "regrow"]]) { await p.waitForTimeout(tag === "burst" ? ms2 : ms2 - (tag === "scatter" ? 450 : 1200)); await el.screenshot({ path: `${out}-${name}-${tag}.png` }); }
  const box = await el.boundingBox();
  console.log(name, "ready", Math.round(ms), "ms", `${Math.round(box.width)}x${Math.round(box.height)}`, errs.length ? "ERRORS " + errs.join(" | ") : "no errors");
  await p.close();
}
await b.close(); srv.close();
