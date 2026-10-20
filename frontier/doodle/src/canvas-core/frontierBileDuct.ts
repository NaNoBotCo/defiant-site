// BILE DUCT, DEFIANT RISO. Header for the frontier article on rilvegostomig for bile duct cancer.
// One idea: one antibody with two hands takes both brakes off a T cell at once, and the T cell
// goes for the tumour in the duct wall.
// Focal subject: the T cell (cyan), its two kinds of brake receptor drawn as stalks (PD-1 with a
// round head, TIGIT with a square one), and the drug in MAGENTA: a Y-shaped bispecific antibody
// whose left hand is a cup (fits PD-1) and right hand a bracket (fits TIGIT). Light: upper left.
// Reference: the standard IgG schematic (Y, ~10 nm: Fc stem, two Fab arms; a bispecific has two
// different arms) and the PD-1/TIGIT checkpoint diagram; the bile duct in cross-section as in a
// histology slide of an intrahepatic duct: one ring of cuboidal cholangiocytes round a lumen,
// here thickened on the side facing the T cell where a cholangiocarcinoma piles up (magenta).
//   - loop 480 ticks: antibodies tumble in; through the middle of the loop each docks on its pair
//     of receptors, the T cell bristles and leans toward the duct, sparks at the near pass; bile
//     specks circle in the lumen; the duct breathes; the drums breathe out of register;
//   - tap: every antibody snaps on, the T cell lunges, the tumour bursts into its own halftone
//     dots, the press jolts and settles; the tumour grows back over two seconds.
import { letter } from "./drafting";
import { rng, type Env, type P } from "./core";
import { clip, reactionSeed, type InputState, type Piece } from "./input";
import { usePaper } from "./bake";
import { ANG, CYN, MAG, SHEETS, blob, dome, dotsLive, ease, line, marks, plate, press, pressT, register, sheet, solid, strokeLive, tint } from "./defiantRiso";

const W = 1200, H = 630, LOOP = 480, HIT = 150, TAU = 6.283;
const D: P = [905, 328], RI = 88, RO = 160;  // the duct: centre, lumen radius, outer wall radius
const TC: P = [318, 330], TR = 90;           // the T cell at rest (sprite drawn here)
const TUM0 = Math.PI - 0.78, TUM1 = Math.PI + 0.78; // the arc of wall the tumour holds, facing the T cell
const tcell = blob(TC[0], TC[1], TR, 17, 0.07), nucleus = blob(TC[0] - 8, TC[1] + 2, TR * 0.66, 19, 0.08);
const u = (a: number): P => [Math.cos(a), Math.sin(a)];
const add = (a: P, b: P, k = 1): P => [a[0] + b[0] * k, a[1] + b[1] * k];

// one cholangiocyte: a wedge of the ring between two angles, its edges nudged so no two match
const wedge = (a0: number, a1: number, r0: number, r1: number, seed: number): P[] => {
  const q = rng(seed), pts: P[] = [], n = 6, j = () => 1 + (q() - 0.5) * 0.05, g = 0.012;
  for (let i = 0; i <= n; i++) { const a = a0 + g + (a1 - a0 - 2 * g) * (i / n); pts.push(add(D, u(a), r0 * j())); }
  for (let i = n; i >= 0; i--) { const a = a0 + g + (a1 - a0 - 2 * g) * (i / n); pts.push(add(D, u(a), r1 * j())); }
  return pts;
};
const NC = 24, cells = Array.from({ length: NC }, (_, i) => { const a0 = (i / NC) * TAU, a1 = ((i + 1) / NC) * TAU, m = (a0 + a1) / 2; return { a0, a1, m, tum: m > TUM0 && m < TUM1 }; });
// how far the tumour bulges out of the wall at angle a: most at the middle of its arc
const bulge = (a: number) => { const x = (a - Math.PI) / 0.78; return Math.max(0, 1 - x * x); };
const TUMC: P = add(D, u(Math.PI), RO + 18); // the tumour's centre, for growing back
// piled cancer cells outside the wall, lumpy and crowded
const pile = Array.from({ length: 9 }, (_, i) => { const r = rng(500 + i), a = Math.PI + (r() - 0.5) * 1.15, d = RO + 10 + r() * 46 * bulge(a) + 6; return { c: add(D, u(a), d), r: 17 + r() * 13, s: 510 + i }; });

const bg = (env: Env) => ({
  cyn: plate(env, "bd:bg:cyn", (g) => {
    // liver tissue: a faint screen, thicker toward the lower left, under everything
    tint(g, [[0, 0], [W, 0], [W, H], [0, H]], 11, ANG.cyn, (x, y) => 0.03 + 0.12 * Math.max(0, 1 - (x / W) * 1.2 - (1 - y / H) * 0.5), CYN);
    letter(g, "PD-1 + TIGIT", 60, 64, { cap: 40, color: CYN, seed: 5, w: 7, opacity: 1 });
    marks(g, W, H);
  }),
  mag: plate(env, "bd:bg:mag", (g) => {
    // a magenta sun behind the duct
    tint(g, blob(D[0] - 10, D[1] + 8, 255, 4, 0.02), 8, ANG.mag, (_x, y) => 0.05 + 0.2 * Math.max(0, (y - 80) / 520), MAG);
    letter(g, "PD-1 + TIGIT", 60, 64, { cap: 40, color: MAG, seed: 5, w: 7, opacity: 0.85 });
  }),
});
const ductPlates = (env: Env) => ({
  cyn: plate(env, "bd:duct:cyn", (g) => {
    // the lumen: bile, a pale screen lit from the upper left
    tint(g, blob(D[0], D[1], RI - 2, 31, 0.03), 7, ANG.cyn, dome(D[0], D[1], RI, 0.08, 0.32), CYN);
    cells.filter((c) => !c.tum).forEach((c, i) => { const s = wedge(c.a0, c.a1, RI, RO, 40 + i); tint(g, s, 5.5, ANG.cyn, dome(D[0], D[1], RO * 1.1, 0.22, 0.7), CYN); line(g, s, CYN, 2.2, 60 + i, true); });
    // the basement membrane, a ring round the outside of the healthy wall
    const ring: P[] = []; for (let a = TUM1; a <= TUM0 + TAU; a += 0.05) ring.push(add(D, u(a), RO + 7)); line(g, ring, CYN, 3, 33);
  }),
  mag: plate(env, "bd:duct:mag", (g) => {
    // a nucleus in the base of each healthy cell, violet where it overprints the cyan
    cells.filter((c) => !c.tum).forEach((c, i) => { const p = add(D, u(c.m), RI + (RO - RI) * 0.62); solid(g, blob(p[0], p[1], 10, 80 + i, 0.15, 18), MAG, 0.8); });
  }),
});
const tumourPlates = (env: Env) => ({
  mag: plate(env, "bd:tum:mag", (g) => {
    cells.filter((c) => c.tum).forEach((c, i) => { const s = wedge(c.a0, c.a1, RI - 6 * bulge(c.m), RO + 34 * bulge(c.m), 140 + i); tint(g, s, 5, ANG.mag, dome(TUMC[0], TUMC[1], 110, 0.3, 0.9), MAG); line(g, s, MAG, 3, 150 + i, true); });
    pile.forEach((p) => { const s = blob(p.c[0], p.c[1], p.r, p.s, 0.22); tint(g, s, 5, ANG.mag, dome(p.c[0], p.c[1], p.r, 0.3, 0.92), MAG); line(g, s, MAG, 2.6, p.s + 50, true); });
  }),
  cyn: plate(env, "bd:tum:cyn", (g) => {
    // big, crowded nuclei: the look of cells dividing too fast
    cells.filter((c) => c.tum).forEach((c, i) => { const r = rng(170 + i), p = add(D, u(c.m + (r() - 0.5) * 0.08), RI + (RO - RI) * (0.45 + r() * 0.4) + 10 * bulge(c.m)); const s = blob(p[0], p[1], 13 + r() * 5, 180 + i, 0.25, 20); tint(g, s, 4.5, ANG.cyn, () => 0.75, CYN); line(g, s, CYN, 1.8, 190 + i, true); });
    pile.forEach((p) => { const s = blob(p.c[0] + 3, p.c[1] + 2, p.r * 0.5, p.s + 9, 0.25, 20); tint(g, s, 4.5, ANG.cyn, () => 0.7, CYN); });
  }),
});
const tPlates = (env: Env) => ({
  cyn: plate(env, "bd:t:cyn", (g) => { tint(g, tcell, 6, ANG.cyn, dome(TC[0], TC[1], TR, 0.16, 0.7), CYN); line(g, tcell, CYN, 3.6, 21, true); }),
  mag: plate(env, "bd:t:mag", (g) => { tint(g, nucleus, 6, ANG.mag, dome(TC[0] - 8, TC[1] + 2, TR * 0.66, 0.18, 0.62), MAG); line(g, nucleus, MAG, 2, 25, true); }),
});

// receptor pairs on the T cell, facing the duct: TIGIT (square) then PD-1 (round) going clockwise, 0.118 rad apart (one antibody's span at YK)
const NP = 6, SPREAD = 0.118, STALK = 22, YK = 1.55;
const pairA = (k: number) => -1.02 + (k / (NP - 1)) * 2.04;
const receptorTip = (c: P, a: number, t: number, k: number): P => add(c, u(a + 0.015 * Math.sin(t / 17 + k)), TR + STALK);
// the receptors as live strokes: stalks, a round head for PD-1, a square head for TIGIT
const receptors = (c: P, t: number): P[][] => {
  const out: P[][] = [];
  for (let k = 0; k < NP; k++) {
    [-1, 1].forEach((side) => {
      const a = pairA(k) + side * SPREAD, base = add(c, u(a), TR - 1), tip = receptorTip(c, a, t, k * 2 + side), n = u(a), tg: P = [-n[1], n[0]];
      out.push([base, tip]);
      if (side > 0) out.push(Array.from({ length: 13 }, (_, i) => add(tip, u((i / 12) * TAU), 6)));
      else { const h = 5.5; out.push([add(add(tip, tg, -h), n, 0), add(add(tip, tg, -h), n, 2 * h), add(add(tip, tg, h), n, 2 * h), add(add(tip, tg, h), n, 0), add(add(tip, tg, -h), n, 0)]); }
    });
  }
  return out;
};
// the antibody, a Y in its own frame: fork at the origin, hands up (-y), stem down (+y)
const Y_HANDS: [P, P] = [[-9, -15], [9, -15]], Y_STEM: P = [0, 24];
const yShape = (o: P, ang: number, k = YK): P[][] => {
  const R = (p: P): P => [o[0] + (p[0] * Math.cos(ang) - p[1] * Math.sin(ang)) * k, o[1] + (p[0] * Math.sin(ang) + p[1] * Math.cos(ang)) * k];
  const cup = Array.from({ length: 9 }, (_, i) => { const a = Math.PI * (i / 8); return R([Y_HANDS[0][0] + Math.cos(a) * 5, Y_HANDS[0][1] - 5 + Math.sin(a) * 5]); }); // a bowl, open away from the fork
  const br: P[] = [[Y_HANDS[1][0] - 5, Y_HANDS[1][1] - 9], [Y_HANDS[1][0] - 5, Y_HANDS[1][1] - 1], [Y_HANDS[1][0] + 5, Y_HANDS[1][1] - 1], [Y_HANDS[1][0] + 5, Y_HANDS[1][1] - 9]];
  return [[R([0, 0]), R(Y_STEM)], [R([0, 0]), R(Y_HANDS[0])], [R([0, 0]), R(Y_HANDS[1])], cup, br.map(R)];
};
// where antibody j sits once docked on pair j: hands on the two heads, stem pointing out
const docked = (c: P, j: number, t: number): { o: P; ang: number } => {
  const a = pairA(j), p1 = receptorTip(c, a - SPREAD, t, j * 2 - 1), p2 = receptorTip(c, a + SPREAD, t, j * 2 + 1), m: P = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2];
  return { o: add(m, u(a), 20 * YK), ang: a - Math.PI / 2 };
};
// antibody j adrift: a slow loop of its own, tumbling a whole number of turns per loop
const ABS = Array.from({ length: NP }, (_, j) => { const r = rng(700 + j); return { x: 470 + r() * 120, y: 90 + (j / (NP - 1)) * 450 + (r() - 0.5) * 40, ax: 24 + r() * 20, ay: 18 + r() * 16, ph: r() * TAU, spin: (j % 2 ? 1 : -1) * (1 + (j % 3 === 0 ? 1 : 0)), a0: r() * TAU, lag: [3, 0, 4, 1, 5, 2][j] }; });
const adrift = (j: number, lt: number): { o: P; ang: number } => { const b = ABS[j], f = (TAU * lt) / LOOP; return { o: [b.x + b.ax * Math.sin(f + b.ph), b.y + b.ay * Math.sin(2 * f + b.ph * 1.3)], ang: b.a0 + b.spin * f }; };
const lerpAng = (a: number, b: number, k: number) => { let d = (b - a) % TAU; if (d > Math.PI) d -= TAU; if (d < -Math.PI) d += TAU; return a + d * k; };
// microvilli: short hairs round the back of the cell, longer when the cell wakes
const villi = (c: P, wake: number, t: number): P[][] => { const r = rng(23), out: P[][] = []; for (let i = 0; i < 26; i++) { const a = Math.PI * (0.58 + 0.84 * (i / 25)) + (r() - 0.5) * 0.08, L = 6 + r() * 6 + 9 * wake * (0.7 + 0.3 * Math.sin(t / 9 + i)); out.push([add(c, u(a), TR), add(c, u(a), TR + L)]); } return out; };
// bile specks circling the lumen
const SPECK = Array.from({ length: 16 }, (_, i) => { const r = rng(900 + i); return { r: 18 + r() * 58, a: r() * TAU, s: 1 + (i % 2), z: 1.6 + r() * 1.6 }; });
// the tumour as loose dots, for the burst
const burstDots = (seed: number) => { const r = rng(seed), out: { x: number; y: number; vx: number; vy: number; r: number; m: boolean }[] = []; for (let i = 0; i < 300; i++) { const a = Math.PI + (r() - 0.5) * 1.5, d = RI + r() * (RO - RI + 50 * bulge(a)), x = D[0] + Math.cos(a) * d, y = D[1] + Math.sin(a) * d, sp = 2 + r() * 7, b = Math.atan2(y - TUMC[1], x - TUMC[0]) + (r() - 0.5) * 0.9; out.push({ x, y, vx: Math.cos(b) * sp - 1, vy: Math.sin(b) * sp, r: 1.5 + r() * 3, m: r() < 0.66 }); } return out; };

export const frontierBileDuct: Piece = {
  meta: { title: "Bile duct, risograph", W, H, loop: LOOP, alt: "Risograph doodle in magenta and cyan: Y-shaped magenta antibodies lock onto two kinds of receptor on a T cell, which leans toward a tumour in the wall of a bile duct. Tap it and the tumour bursts into dots." },
  input: { springs: {} },
  bake: function* (env) { yield "paper"; usePaper(env, SHEETS); yield "bg"; bg(env); yield "duct"; ductPlates(env); yield "tumour"; tumourPlates(env); yield "t"; tPlates(env); },
  draw: (ctx, t, env, s: InputState) => {
    usePaper(env, SHEETS);
    const R = s.reduced, lt = R ? 240 : t % LOOP, tt = R ? 240 : t, hit = R ? null : clip(s, "click:self", HIT);
    const reg = R ? [0, 0] as P : register(lt, 240, hit ? 10 : 0, hit ? Math.max(0, hit.f - 16) : 0);
    sheet(ctx, env);
    const B = bg(env); press(ctx, env, B.cyn); press(ctx, env, B.mag, reg[0], reg[1]);
    // the duct: breathes a little; bile specks circle the lumen, whole laps per loop
    const breath = 0.99 + 0.01 * Math.sin((TAU * lt) / 160), dp = ductPlates(env);
    pressT(ctx, env, dp.cyn, D, 0, 0, 0, breath); pressT(ctx, env, dp.mag, D, 0, reg[0], reg[1], breath);
    dotsLive(ctx, env, SPECK.map((p) => { const a = p.a + (TAU * lt * p.s) / LOOP; return [D[0] + Math.cos(a) * p.r * breath, D[1] + Math.sin(a) * p.r * 0.92 * breath, p.z] as [number, number, number]; }), CYN, 0.8);
    // docking through the middle of the loop: each antibody in turn, then each lets go
    const swell = 0.5 - 0.5 * Math.cos((TAU * lt) / LOOP);
    const dock = ABS.map((b) => { const go = ease((swell - 0.45 - b.lag * 0.05) / 0.16); return hit ? Math.max(go, ease((hit.f - b.lag * 2) / 12) * (hit.f < 110 ? 1 : 1 - ease((hit.f - 110) / 40))) : go; });
    const wake = dock.reduce((a, b) => a + b, 0) / NP;
    // the T cell leans toward the duct as its brakes come off; on a tap it lunges
    let tx = 120 * wake, ty = 10 * Math.sin((TAU * lt) / LOOP * 2) * (1 - wake);
    let bit = 0;
    if (hit) { const f = hit.f, go = ease((f - 8) / 16), back = ease((f - 80) / 60); tx = tx + (175 - tx) * go * (1 - back); bit = f < 22 ? 0 : f < 100 ? 1 : 1 - ease((f - 100) / 50); }
    // the tumour: gone while burst, then grows back in from its middle
    const tp = tumourPlates(env), grow = bit > 0 ? 0.55 + 0.45 * (1 - bit) : 1;
    if (bit < 1) { const k = breath * grow, a = 1 - bit; pressT(ctx, env, tp.mag, TUMC, 0, reg[0], reg[1], k, a); pressT(ctx, env, tp.cyn, TUMC, 0, 0, 0, k, a); }
    if (hit && hit.f >= 22 && hit.f < 100) {
      const f = hit.f - 22, ds = burstDots(reactionSeed(s, "click:self")), fade = 1 - ease((f - 40) / 38), pos = (d: (typeof ds)[number]): [number, number, number] => [d.x + d.vx * f * (1 - f / 200), d.y + d.vy * f * (1 - f / 200) + 0.03 * f * f, d.r * (1 - f / 140)];
      dotsLive(ctx, env, ds.filter((d) => d.m).map(pos).map(([x, y, r]) => [x + reg[0], y + reg[1], r]), MAG, fade);
      dotsLive(ctx, env, ds.filter((d) => !d.m).map(pos), CYN, fade);
    }
    // the T cell, its hairs and its receptors
    const c: P = [TC[0] + tx, TC[1] + ty], T = tPlates(env);
    press(ctx, env, T.cyn, tx, ty); press(ctx, env, T.mag, tx + reg[0], ty + reg[1]);
    strokeLive(ctx, env, villi(c, wake, tt), CYN, 1.8);
    strokeLive(ctx, env, receptors(c, tt), CYN, 3);
    // the antibodies, adrift or docked, in magenta and printed off register with the magenta drum
    const cm: P = add(c, reg);
    const ys = ABS.flatMap((_, j) => { const a = adrift(j, lt), d = docked(cm, j, tt), k = dock[j]; return yShape([a.o[0] + reg[0] + (d.o[0] - a.o[0] - reg[0]) * k, a.o[1] + reg[1] + (d.o[1] - a.o[1] - reg[1]) * k], lerpAng(a.ang, d.ang, k)); });
    strokeLive(ctx, env, ys, MAG, 4.4);
    // the near pass: the T cell's front meets the tumour, a ring of sparks
    const near = R || hit ? 0 : Math.max(0, (wake - 0.9) / 0.1);
    if (near > 0) { const r = rng(5), sp: [number, number, number][] = []; for (let i = 0; i < 18; i++) { const a = r() * TAU, d = 16 + 26 * near + r() * 8; sp.push([TC[0] + 120 + TR + 92 + Math.cos(a) * d, TC[1] + Math.sin(a) * d * 1.4, 2 + 2 * near]); } dotsLive(ctx, env, sp, Math.floor(lt / 8) % 2 ? MAG : CYN, near); }
  },
};
