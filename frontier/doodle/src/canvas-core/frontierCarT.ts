// CAR-T, DEFIANT RISO. Header for the frontier article on cell therapy for cancer in Thailand.
// One idea: your own T cell, given a new receptor, finds the cancer cell and grips it.
// Focal subject: the T cell (cyan) wearing its engineered receptors in MAGENTA, the one colour
// it shares with its target, so the eye reads the gene that was added. Light: upper left.
// Reference: the standard CAR-T schematic (lymphocyte ~7-10 um, large round nucleus, little
// cytoplasm; Y-shaped CAR = scFv head on a hinge through the membrane) against a tumour cell
// with surface antigen knobs; here inside a vessel, red cells drifting past.
//   - loop 480 ticks: the T cell drifts in and out; on the near pass its receptors meet the
//     antigens and a ring of dots sparks; red cells ride the current left to right; the cancer
//     cell breathes; the drums breathe a pixel out of register;
//   - tap: the T cell lunges and docks, the cancer cell bursts into its own halftone dots, the
//     press jolts out of register and settles; the cell grows back in over two seconds.
import { letter } from "./drafting";
import { rng, type Env, type P } from "./core";
import { clip, reactionSeed, type InputState, type Piece } from "./input";
import { usePaper } from "./bake";
import { ANG, CYN, MAG, SHEETS, blob, dome, dotsLive, ease, line, marks, plate, press, pressT, register, sheet, solid, strokeLive, tint } from "./defiantRiso";

const W = 1200, H = 630, LOOP = 480, HIT = 150;
const CA: P = [845, 318], CR = 150;          // the cancer cell
const TC: P = [372, 330], TR = 92;           // the T cell at rest (sprite drawn here)
const cancer = blob(CA[0], CA[1], CR, 41, 0.16), tcell = blob(TC[0], TC[1], TR, 7, 0.07);
const nucleus = blob(TC[0] + 6, TC[1] + 4, TR * 0.68, 9, 0.08), cNuc = blob(CA[0] + 18, CA[1] + 10, CR * 0.46, 43, 0.22);
// antigen knobs on the cancer cell's membrane, on the side facing the T cell
const antigens: P[] = Array.from({ length: 9 }, (_, i) => { const a = Math.PI * (0.62 + (i / 8) * 0.76); return [CA[0] + Math.cos(a) * (CR + 4), CA[1] + Math.sin(a) * (CR * 0.98 + 4)]; });
// red cells: biconcave discs, drifting with the current
const RBC = Array.from({ length: 7 }, (_, i) => { const r = rng(300 + i); return { x: r() * 1400 - 100, y: 70 + r() * 490, s: 20 + r() * 16, tilt: r() * 6.283, sp: 1 + Math.floor(r() * 2) }; });

const vessel = (top: boolean): P[] => { const pts: P[] = []; for (let x = -20; x <= W + 20; x += 20) pts.push([x, (top ? 54 : H - 54) + (top ? -1 : 1) * 14 * Math.sin(x / 160 + (top ? 0.6 : 2.1))]); return top ? [[-20, -20], ...pts, [W + 20, -20]] : [[-20, H + 20], ...pts, [W + 20, H + 20]]; };

const bg = (env: Env) => ({
  cyn: plate(env, "cart:bg:cyn", (g) => {
    // the vessel wall, top and bottom: dense screen fading into the lumen
    [true, false].forEach((top) => { const s = vessel(top); tint(g, s, 9, ANG.cyn, (_x, y) => 0.25 + 0.5 * Math.min(1, (top ? 70 - y : y - (H - 70)) / 60 + 0.2), CYN); });
    // the lumen, a faint screen thickening toward the lower left
    tint(g, [[0, 40], [W, 40], [W, H - 40], [0, H - 40]], 11, ANG.cyn, (x, y) => 0.02 + 0.11 * Math.max(0, 1 - (x / W) * 1.1 - (1 - y / H) * 0.6), CYN);
    letter(g, "CAR-T", 64, 100, { cap: 60, color: CYN, seed: 3, w: 10, opacity: 1 });
    marks(g, W, H);
  }),
  mag: plate(env, "cart:bg:mag", (g) => {
    // a magenta sun behind the target, screened denser at its lower edge
    const sun = blob(CA[0] - 20, CA[1] + 10, 250, 2, 0.02);
    tint(g, sun, 8, ANG.mag, (_x, y) => 0.06 + 0.2 * Math.max(0, (y - 80) / 520), MAG);
    letter(g, "CAR-T", 64, 100, { cap: 60, color: MAG, seed: 3, w: 10, opacity: 0.85 });
  }),
});
const cancerPlates = (env: Env) => ({
  mag: plate(env, "cart:ca:mag", (g) => {
    tint(g, cancer, 6, ANG.mag, dome(CA[0], CA[1], CR, 0.2, 0.86), MAG);
    line(g, cancer, MAG, 4.2, 11, true);
    // blebs: small lumps on the membrane, the look of a cell that grows too fast
    [[0.2, 12], [1.3, 10], [2.4, 14], [3.9, 9], [5.1, 11]].forEach(([a, r], i) => { const p: P = [CA[0] + Math.cos(a) * (CR + 2), CA[1] + Math.sin(a) * (CR * 0.98 + 2)]; solid(g, blob(p[0], p[1], r, 60 + i, 0.2, 18), MAG, 0.9); });
  }),
  cyn: plate(env, "cart:ca:cyn", (g) => {
    tint(g, cancer, 7, ANG.cyn, (x, y) => 0.5 * dome(CA[0], CA[1], CR, 0, 0.9)(x, y) ** 1.6, CYN); // the shade side goes violet
    tint(g, cNuc, 5, ANG.cyn, dome(CA[0] + 18, CA[1] + 10, CR * 0.46, 0.45, 0.9), CYN);
    line(g, cNuc, CYN, 2.4, 13, true);
    antigens.forEach(([x, y], i) => { solid(g, blob(x, y, 7, 80 + i, 0.15, 14), CYN); line(g, [[x, y], [x + (x - CA[0]) * 0.06, y + (y - CA[1]) * 0.06]], CYN, 2.2, 90 + i); });
  }),
});
const tPlates = (env: Env) => ({
  cyn: plate(env, "cart:t:cyn", (g) => {
    tint(g, tcell, 6, ANG.cyn, dome(TC[0], TC[1], TR, 0.16, 0.7), CYN);
    line(g, tcell, CYN, 3.6, 21, true);
    // microvilli: short hairs round the back of the cell
    const r = rng(23); for (let i = 0; i < 26; i++) { const a = Math.PI * (0.55 + 0.9 * (i / 25)) + (r() - 0.5) * 0.08, L = 7 + r() * 7; line(g, [[TC[0] + Math.cos(a) * TR, TC[1] + Math.sin(a) * TR], [TC[0] + Math.cos(a) * (TR + L), TC[1] + Math.sin(a) * (TR + L)]], CYN, 1.8, 30 + i); }
  }),
  mag: plate(env, "cart:t:mag", (g) => {
    tint(g, nucleus, 6, ANG.mag, dome(TC[0] + 6, TC[1] + 4, TR * 0.68, 0.18, 0.62), MAG); // the big nucleus, violet where it overprints
    line(g, nucleus, MAG, 2, 25, true);
  }),
});
const rbcPlate = (env: Env, i: number) => plate(env, `cart:rbc:${i}`, (g) => {
  const { s } = RBC[i], o: P = [60, 60], ell = (rx: number, ry: number, n: number, sd: number): P[] => { const q = rng(sd); return Array.from({ length: n }, (_, j) => { const a = (j / n) * 6.283, w = 1 + (q() - 0.5) * 0.04; return [o[0] + Math.cos(a) * rx * w, o[1] + Math.sin(a) * ry * w] as P; }); };
  const disc = ell(s, s * 0.62, 40, 200 + i), dent = ell(s * 0.5, s * 0.26, 24, 210 + i);
  // a red cell seen at a slant: the rim dense, the dimple thin, so the turn reads as it tumbles
  tint(g, disc, 4.5, ANG.mag, (x, y) => { const d = Math.hypot((x - o[0]) / s, (y - o[1]) / (s * 0.62)); return d > 1 ? 0 : 0.14 + 0.62 * Math.max(0, d - 0.45) ** 0.8; }, MAG);
  line(g, disc, MAG, 2.2, 220 + i, true); line(g, dent, MAG, 1.3, 230 + i, true);
});

// the receptors: Y shapes on the side of the T cell facing the target, waving a little
const receptors = (cx: number, cy: number, t: number, reach: number): P[][] => {
  const out: P[][] = [];
  for (let i = 0; i < 9; i++) {
    const a = -0.95 + (i / 8) * 1.9 + 0.05 * Math.sin(t / 19 + i * 1.7), L = 20 + 6 * reach + 2 * Math.sin(t / 13 + i);
    const b: P = [cx + Math.cos(a) * TR, cy + Math.sin(a) * TR], m: P = [cx + Math.cos(a) * (TR + L), cy + Math.sin(a) * (TR + L)], f = 0.45 + 0.1 * Math.sin(t / 23 + i);
    out.push([b, m], [m, [m[0] + Math.cos(a - f) * 11, m[1] + Math.sin(a - f) * 11]], [m, [m[0] + Math.cos(a + f) * 11, m[1] + Math.sin(a + f) * 11]]);
  }
  return out;
};
// the cancer cell as loose dots, for the burst: sampled once from its own screen
const burstDots = (seed: number) => { const r = rng(seed), out: { x: number; y: number; vx: number; vy: number; r: number; m: boolean }[] = []; for (let i = 0; i < 340; i++) { const a = r() * 6.283, d = Math.sqrt(r()) * CR, x = CA[0] + Math.cos(a) * d, y = CA[1] + Math.sin(a) * d, sp = 2 + r() * 7; out.push({ x, y, vx: Math.cos(a) * sp + 1.5, vy: Math.sin(a) * sp, r: 1.5 + r() * 3.2, m: r() < 0.62 }); } return out; };

export const frontierCarT: Piece = {
  meta: { title: "CAR-T, risograph", W, H, loop: LOOP, alt: "Risograph doodle in magenta and cyan: a T cell wearing magenta receptors grips a cancer cell inside a blood vessel. Tap it and the cancer cell bursts into dots." },
  input: { springs: {} },
  bake: function* (env) { yield "paper"; usePaper(env, SHEETS); yield "bg"; bg(env); yield "cancer"; cancerPlates(env); yield "t"; tPlates(env); for (let i = 0; i < RBC.length; i++) { yield `rbc${i}`; rbcPlate(env, i); } },
  draw: (ctx, t, env, s: InputState) => {
    usePaper(env, SHEETS);
    const R = s.reduced, lt = R ? 0 : t % LOOP, hit = R ? null : clip(s, "click:self", HIT);
    const reg = R ? [0, 0] as P : register(lt, 240, hit ? 10 : 0, hit ? Math.max(0, hit.f - 16) : 0);
    sheet(ctx, env);
    const B = bg(env); press(ctx, env, B.cyn); press(ctx, env, B.mag, reg[0], reg[1]);
    // red cells, riding the current; whole loop = whole laps, so the loop closes on itself
    RBC.forEach((c, i) => { const span = 1400, x = ((c.x + (lt / LOOP) * span * c.sp) % span) - 100, y = c.y + 8 * Math.sin((6.283 * lt) / LOOP * c.sp + i); pressT(ctx, env, rbcPlate(env, i), [60, 60], (c.tilt * 57.3 + (lt / LOOP) * 360 * c.sp) % 360, x - 60 + reg[0], y - 60 + reg[1], 1); });
    // the T cell: drifts in on a slow swell, closest at the middle of the loop
    const drift = R ? 0 : 0.5 - 0.5 * Math.cos((6.283 * lt) / LOOP);
    let tx = -40 + 150 * drift, ty = 10 * Math.sin((6.283 * lt) / LOOP * 2);
    let bit = 0; // 0..1: how far the cancer cell has burst
    if (hit) { const f = hit.f, go = ease(f / 18), back = ease((f - 70) / 60); tx = tx + (205 - tx) * go * (1 - back); ty = ty * (1 - go); bit = f < 18 ? 0 : f < 100 ? 1 : 1 - ease((f - 100) / 50); }
    // the cancer cell: breathes; gone while burst, then grows back in
    const breath = 0.985 + 0.015 * Math.sin((6.283 * lt) / 120), grow = bit > 0 ? 0.62 + 0.38 * (1 - bit) : 1, ca = cancerPlates(env);
    if (bit < 1) { const k = breath * grow, a = 1 - bit; pressT(ctx, env, ca.cyn, CA, 0, 0, 0, k, a); pressT(ctx, env, ca.mag, CA, 0, reg[0], reg[1], k, a); }
    if (hit && hit.f >= 18 && hit.f < 100) {
      const f = hit.f - 18, ds = burstDots(reactionSeed(s, "click:self")), fade = 1 - ease((f - 40) / 42), pos = (d: (typeof ds)[number]): [number, number, number] => [d.x + d.vx * f * (1 - f / 200), d.y + d.vy * f * (1 - f / 200) + 0.03 * f * f, d.r * (1 - f / 140)];
      dotsLive(ctx, env, ds.filter((d) => d.m).map(pos).map(([x, y, r]) => [x + reg[0], y + reg[1], r]), MAG, fade);
      dotsLive(ctx, env, ds.filter((d) => !d.m).map(pos), CYN, fade);
    }
    // the T cell and its receptors
    const T = tPlates(env), reach = hit ? Math.min(1, hit.f / 18) * (hit.f < 90 ? 1 : 0) : Math.max(0, (drift - 0.8) * 5);
    press(ctx, env, T.cyn, tx, ty); press(ctx, env, T.mag, tx + reg[0], ty + reg[1]);
    strokeLive(ctx, env, receptors(TC[0] + tx + reg[0], TC[1] + ty + reg[1], t, reach), MAG, 3.4);
    // the near pass: receptors meet antigens, a ring of sparks
    const near = R || hit ? 0 : Math.max(0, (drift - 0.93) / 0.07);
    if (near > 0) { const r = rng(5), sp: [number, number, number][] = []; for (let i = 0; i < 18; i++) { const a = r() * 6.283, d = 18 + 30 * near + r() * 8; sp.push([600 + Math.cos(a) * d, 320 + Math.sin(a) * d * 1.3, 2 + 2 * near]); } dotsLive(ctx, env, sp, i2(lt) ? MAG : CYN, near); }
  },
};
const i2 = (t: number) => Math.floor(t / 8) % 2 === 0;
