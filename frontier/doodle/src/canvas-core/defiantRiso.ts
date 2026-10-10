// DEFIANT RISO. The kit every frontier header is drawn with: two soy-ink drums, Defiant's
// magenta and cyan, overprinted by multiply into violet where they cross. Tone is a halftone
// screen per drum (magenta at 75 degrees, cyan at 15, so they rosette instead of moire); flat
// spot shapes are drawn solid; a litho-crayon line sits on top. The drums are never quite in
// register and the pressman never quite fixes it: the offset breathes a pixel or two at rest.
//
// A piece bakes each subject as TWO sprites (one per drum) so the misregister can move between
// them live, and composites every frame by multiply onto a sheet of off-white paper.
import { Gfx, rng, sample, type Ctx, type Env, type P } from "./core";
import { bake, blit, blitT, paperFactor, type Sprite } from "./bake";
import { LITHO, drum, screen, bounds } from "./riso";

export const MAG = "#ff2a9d", CYN = "#00b9cc", PAPER = "#fbf8f1";
export const ANG = { mag: 75, cyn: 15 };
export const SHEETS: [string, number][] = [["paper", 0.2], ["coldpress", 0.14]];

const smooth = (u: number) => (u <= 0 ? 0 : u >= 1 ? 1 : u * u * (3 - 2 * u));
export const ease = smooth;

// a soft, lumpy cell outline: a circle whose radius wanders by a few low harmonics
export const blob = (cx: number, cy: number, r: number, seed: number, rough = 0.1, n = 72): P[] => {
  const q = rng(seed), h = [2, 3, 5, 7].map((k) => ({ k, a: (q() - 0.3) * rough / Math.sqrt(k), p: q() * 6.283 }));
  return Array.from({ length: n }, (_, i) => { const t = (i / n) * 6.283, rr = r * (1 + h.reduce((s, x) => s + x.a * Math.sin(x.k * t + x.p), 0)); return [cx + Math.cos(t) * rr, cy + Math.sin(t) * rr] as P; });
};
// lit-sphere tone: dark on the side away from the light, a bare-paper highlight toward it
export const dome = (cx: number, cy: number, r: number, lo = 0.12, hi = 0.82, light: P = [-0.55, -0.6]) => (x: number, y: number) => {
  const u = (x - cx) / r, v = (y - cy) / r, d2 = u * u + v * v; if (d2 > 1.05) return 0;
  const z = Math.sqrt(Math.max(0, 1 - d2)), lz = Math.sqrt(Math.max(0, 1 - light[0] ** 2 - light[1] ** 2)), lit = Math.max(0, u * light[0] + v * light[1] + z * lz);
  return lo + (hi - lo) * (1 - lit) * (0.75 + 0.25 * Math.sqrt(d2));
};

// one drum of one subject, baked: everything fn draws lands in `ink`, with the drum's specks
export const plate = (env: Env, id: string, fn: (g: Gfx, c: Ctx) => void): Sprite =>
  bake(env, id, (g) => drum(g, [0, 0], () => fn(g, g.cur)), { medium: LITHO });
// the screen helper with a polygon clip, in one ink
export const tint = (g: Gfx, shape: P[], pitch: number, ang: number, tone: (x: number, y: number) => number, ink: string) =>
  screen(g, bounds(shape), pitch, ang, tone, ink, shape);
export const solid = (g: Gfx, shape: P[], ink: string, alpha = 1) => g.fill(sample(shape, true, 6), ink, alpha);
export const line = (g: Gfx, pts: P[], ink: string, w = 3, seed = 1, closed = false) =>
  g.pen(pts, { w, color: ink, seed, closed, wobble: 0.6, boil: 0, taper: 0.8, opacity: 0.95, retrace: false });

// the sheet: off-white stock and its grain, under everything
export const sheet = (ctx: Ctx, env: Env) => {
  const DW = Math.round(env.W * env.scale), DH = Math.round(env.H * env.scale);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = "source-over";
  ctx.fillStyle = PAPER; ctx.fillRect(0, 0, DW, DH);
  const f = paperFactor(env, SHEETS); ctx.globalCompositeOperation = "multiply"; ctx.drawImage(f.c, f.x, f.y); ctx.globalCompositeOperation = "source-over";
};
// print a sprite onto the sheet: multiply, offset in logical px (rounded to device px)
export const press = (ctx: Ctx, env: Env, s: Sprite, dx = 0, dy = 0, alpha = 1) => {
  ctx.globalCompositeOperation = "multiply"; blit(ctx, s, dx * env.scale, dy * env.scale, alpha); ctx.globalCompositeOperation = "source-over";
};
export const pressT = (ctx: Ctx, env: Env, s: Sprite, pivot: P, deg: number, dx: number, dy: number, k = 1, alpha = 1) => {
  ctx.globalCompositeOperation = "multiply"; blitT(ctx, s, [pivot[0] * env.scale, pivot[1] * env.scale], deg, dx * env.scale, dy * env.scale, k, k, alpha); ctx.globalCompositeOperation = "source-over";
};
// where the magenta drum sits relative to cyan: a breath at rest, a jolt when something hits
export const register = (t: number, period: number, jolt = 0, joltF = 0): P => {
  const a = (6.283 * t) / period, j = jolt * Math.exp(-joltF / 12) * Math.sin(joltF * 0.9);
  return [1.6 * Math.sin(a) + j, 1.1 * Math.cos(a) - j * 0.6];
};
// live halftone dots, for marks that move too much to bake (a burst, a spark)
export const dotsLive = (ctx: Ctx, env: Env, pts: [number, number, number][], ink: string, alpha = 1) => {
  if (!pts.length || alpha <= 0) return; const k = env.scale;
  ctx.setTransform(k, 0, 0, k, 0, 0); ctx.globalCompositeOperation = "multiply"; ctx.globalAlpha = alpha; ctx.fillStyle = ink; ctx.beginPath();
  pts.forEach(([x, y, r]) => { if (r > 0.2) { ctx.moveTo(x + r, y); ctx.arc(x, y, r, 0, 6.283); } }); ctx.fill();
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = "source-over";
};
// a live litho line (round caps, flat ink): receptors and other small moving parts
export const strokeLive = (ctx: Ctx, env: Env, paths: P[][], ink: string, w: number) => {
  const k = env.scale; ctx.setTransform(k, 0, 0, k, 0, 0); ctx.globalCompositeOperation = "multiply"; ctx.strokeStyle = ink; ctx.lineWidth = w; ctx.lineCap = "round"; ctx.lineJoin = "round";
  ctx.beginPath(); paths.forEach((p) => p.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)))); ctx.stroke();
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalCompositeOperation = "source-over";
};
// registration crosses and the ink swatch a riso operator leaves in the margin
export const marks = (g: Gfx, W: number, H: number) => g.group("plain", () => {
  const c = g.cur; g.touch(0, 0, W, H); c.strokeStyle = "#2a2430"; c.lineWidth = 1;
  [[22, 22], [W - 22, 22], [22, H - 22], [W - 22, H - 22]].forEach(([x, y]) => { c.beginPath(); c.arc(x, y, 6, 0, 6.283); c.moveTo(x - 10, y); c.lineTo(x + 10, y); c.moveTo(x, y - 10); c.lineTo(x, y + 10); c.stroke(); });
}, { alpha: 0.7 });
