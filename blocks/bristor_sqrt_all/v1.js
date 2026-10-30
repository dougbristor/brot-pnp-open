// bristor_sqrt_all / v1
// codetree:bristor_sqrt_all/v1 — see codetree/blocks/bristor_sqrt_all/
//
// Every real square root of t under T-049 B2 squaring (shipped signs): all w with B(w) = t.
// A regular target has 2 or 6 roots, never 4 (insights 2026-10-19: B/|B| factors through RP² → S²,
// pair count mod 2 is a degree = 1; Bézout ≤ 8). The 6 live in one three-cusped cap around −1.
//
// Method: B is homogeneous, so roots(s²·t̂) = s·roots(t̂). A 180×90 table holds the roots of each unit
// direction (built by make_table.py from exact elimination). Look up t̂, polish with Newton on t̂, then
// scale by √|t| (so the tolerance is relative at every |t|). If the pixel holds 2 roots but a neighbour holds 6, polish the neighbour's roots too (the
// cap's edge, the caustic, crosses pixels). If the count still breaks 2-or-6, fall back to 4 → 8 → 16
// fixed Newton starts. Bench (JS, 20k off-grid targets): 2.35 µs/target, 0 missed; stepped Newton 11 µs.
//
// Returns { roots, status, escalated }:
//   status 'complete'    6 roots, or 2 roots with no 6-pixel in the 3×3 table neighbourhood
//          'edge'        2 roots next to the cap (a 6-pixel is in the neighbourhood) after every neighbour's
//                        roots were polished. Usually right (the target sits just outside the caustic), but a
//                        hidden pair is not ruled out; a caller that needs certainty treats it as unresolved
//          'unresolved'  the count breaks 2-or-6 even after 16 starts (near the caustic, where two
//                        roots merge; on the caustic itself a regular count does not exist)
//          'zero'        t = 0: the only root is 0
//   escalated            the fallback ran
// RESIDUAL RISK: '2, complete' is a table claim, not a proof: it needs the whole 3×3 neighbourhood to read 2, so a
// 6-target would have to sit more than a pixel (2°) inside the caustic. 0 of 20,000 in the bench.
// CAVEAT: exactly on the caustic (measure zero) the double root is dropped: J is singular there, so Newton
// cannot land on it. The 2 simple roots come back, as 'edge'.
import { bristorSquare, bristorSquareJacobian, SHIPPED } from '../bristor_square_jacobian/v1.js';
import { cramer3 } from '../cramer3_solve/v1.js';

export const TW = 180, TH = 90;
let TAB = null;

/** Load the table (browser: fetch next to this file; node: fs). Call once before sqrtAll. */
export async function loadTable(base = new URL('./', import.meta.url)) {
  const get = async name => { const u = new URL(name, base);
    if (u.protocol === 'file:') { const fs = await import('node:fs'), b = fs.readFileSync(u); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength); }
    const r = await fetch(u); if (!r.ok) throw new Error('bristor_sqrt_all: ' + u + ' ' + r.status); return r.arrayBuffer(); };
  const [r, c] = await Promise.all([get('table180.f32'), get('table180.cnt')]);
  TAB = { r: new Float32Array(r), c: new Uint8Array(c) };
  if (TAB.c.length !== TW * TH || TAB.r.length !== TW * TH * 18) throw new Error('bristor_sqrt_all: table size');
  return TAB;
}
/** Replace the table (tests and plants). */
export const setTable = t => { TAB = t; };

// fallback starts, fixed (numpy default_rng(11), as in the bench); scaled by √|t|
const SEEDS = [
  [0.034193, 1.359748, 1.224721],
  [-0.510307, -0.297970, -0.527384],
  [0.569726, -0.056064, 0.746886],
  [-1.847325, 1.566549, -0.096432],
  [0.680378, -0.136566, -0.379099],
  [0.463110, 0.824514, -0.202530],
  [-0.152786, 0.685699, -0.870341],
  [-1.514384, 0.394982, -0.670566],
  [-1.920341, -0.814054, -0.467598],
  [-1.193202, -1.492464, 0.036638],
  [0.897249, -0.233132, -0.743596],
  [0.384994, 0.717236, -0.300011],
  [0.544668, 1.042875, -0.206956],
  [-0.813516, 0.347651, 0.247546],
  [1.098813, -1.284581, -0.661613],
  [-0.838167, -1.734015, 0.126435]
];

function newton(w0, w1, w2, tx, ty, tz, tol, maxIt) {
  for (let i = 0; i < maxIt; i++) {
    const f = bristorSquare(w0, w1, w2, SHIPPED), r0 = f[0] - tx, r1 = f[1] - ty, r2 = f[2] - tz;
    if (Math.hypot(r0, r1, r2) < tol) return [w0, w1, w2];
    const d = cramer3(...bristorSquareJacobian(w0, w1, w2, SHIPPED), r0, r1, r2);
    if (!d) return null;
    w0 -= d[0]; w1 -= d[1]; w2 -= d[2];
  }
  return null;
}
function add(R, w, eps) {
  if (!w) return;
  for (const c of [w, [-w[0], -w[1], -w[2]]])
    if (!R.some(o => Math.abs(o[0] - c[0]) + Math.abs(o[1] - c[1]) + Math.abs(o[2] - c[2]) < eps)) R.push(c);
}
const regular = n => n === 2 || n === 6;

/** Pixel of direction t (explorer dirOf convention: lat 90 = real axis). */
export function pixelOf(tx, ty, tz) {
  const n = Math.hypot(tx, ty, tz), lo = Math.atan2(tz, ty) * 180 / Math.PI, la = Math.asin(Math.max(-1, Math.min(1, tx / n))) * 180 / Math.PI;
  return Math.min(TH - 1, Math.floor((90 - la) / 180 * TH)) * TW + Math.min(TW - 1, Math.floor((lo + 180) / 360 * TW));
}

/** All real w with B(w) = (tx, ty, tz). */
export function sqrtAll(tx, ty, tz, { neighbour = true, unit = true } = {}) {
  if (!TAB) throw new Error('bristor_sqrt_all: call loadTable() first');
  const n = Math.hypot(tx, ty, tz);
  if (n === 0) return { roots: [[0, 0, 0]], status: 'zero', escalated: false };
  // solve for the unit target, then scale the roots by √|t|: the tolerance is then relative at every scale. An absolute
  // 1e-11 passed tiny targets as 'complete' with unpolished table seeds (T-196, caro 2h4k). unit: false = that old path, kept as conform's plant P5
  const k = Math.sqrt(n), s = unit ? 1 : k, tol = unit ? 1e-11 : 1e-11 * Math.max(1, n), eps = 1e-6 * s, R = [];
  if (unit) { tx /= n; ty /= n; tz /= n; }
  const p = pixelOf(tx, ty, tz), j = Math.floor(p / TW), i = p % TW, nb = [];
  for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) {
    const jj = j + dj; if (jj >= 0 && jj < TH) nb.push(jj * TW + (i + di + TW) % TW);
  }
  const expect6 = neighbour && nb.some(q => TAB.c[q] === 6), used = new Set();
  const polish = q => { if (used.has(q)) return; used.add(q);
    for (let k = 0; k < TAB.c[q]; k++) { const o = (q * 6 + k) * 3; add(R, newton(TAB.r[o] * s, TAB.r[o + 1] * s, TAB.r[o + 2] * s, tx, ty, tz, tol, 12), eps); } };
  polish(p);
  if (expect6 && TAB.c[p] === 2) polish(nb.find(q => TAB.c[q] === 6));
  // a 6 nearby but only 2 found, or an irregular count: use every neighbour's roots before any blind start
  if (neighbour && (!regular(R.length) || (R.length === 2 && expect6))) nb.forEach(polish);
  let escalated = false;
  for (const [a, b] of [[0, 4], [4, 8], [8, 16]]) {
    if (regular(R.length)) break;
    escalated = true;
    for (let k = a; k < b; k++) add(R, newton(SEEDS[k][0] * s, SEEDS[k][1] * s, SEEDS[k][2] * s, tx, ty, tz, tol, 40), eps);
  }
  const status = !regular(R.length) ? 'unresolved' : R.length === 2 && expect6 ? 'edge' : 'complete';
  return { roots: unit ? R.map(w => [w[0] * k, w[1] * k, w[2] * k]) : R, status, escalated };
}
