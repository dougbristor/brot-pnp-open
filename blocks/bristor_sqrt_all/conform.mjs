#!/usr/bin/env node
// codetree:bristor_sqrt_all/v1 — conformance runner
//
//   node conform.mjs              check v1.js against vectors.json
//   node conform.mjs --selftest   plants: each must make the check FAIL (a check that cannot fail is not a check)
//
// Expectations are from oracle_elim.py (exact elimination, two orders) gated by a 400-start Newton search,
// never from v1.js. The contract checked: on a regular target, status 'complete' and the exact root set
// (every expected root matched to 1e-8·√|t|, no extras); 'edge' is accepted for a correct 2 next to the cap. On the caustic itself (caveat cases) there is no
// regular count. Documented behaviour (CAVEAT): v1 never claims 'complete' with 4, but at a fold point it
// drops the double root (J is singular there, so Newton cannot land on it) and returns the 2 simple roots as
// 'complete'. These targets are measure zero. If v1 starts returning the double root, that is STALE CAVEAT
// (good news, but the prose in block.md and v1.js is then out of date).
// CAVEAT 2 (caveat-tongue, 10-31): three 6-targets in a cusp tongue of the cap thinner than a table pixel (lon ≈ −179.6°, lat ≈ −31.7°,
// found by a root-completeness check that placed targets on the caustic on purpose). v1 returns 2 roots as 'complete' there: a false
// 'complete', pinned as documented wrongness. If v1 returns all 6, that is STALE CAVEAT (the fix landed; update README.md).
// Scale arm (T-196, caro 2h4k): B is homogeneous, so every regular case rerun at t·k must give roots·√k, matched relative to
// √|t·k| and with residual |B(w) − t|/|t| < 1e-9. An absolute tolerance passes tiny targets unpolished; plant P5 is that path.
import fs from 'node:fs';
import * as M from './v1.js';
import { bristorSquare, SHIPPED } from '../bristor_square_jacobian/v1.js';
const V = JSON.parse(fs.readFileSync(new URL('./vectors.json', import.meta.url)));
const tab = await M.loadTable();
const near = (a, b, e) => Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]) < e;
const SCALES = [1e-16, 1e-6, 1e6, 1e16];
const relRes = (w, t) => { const f = bristorSquare(...w, SHIPPED); return Math.hypot(f[0] - t[0], f[1] - t[1], f[2] - t[2]) / Math.hypot(...t); };
const scaled = V.cases.filter(c => !c.kind.startsWith('caveat') && c.kind !== 'zero' && c.roots)
  .flatMap(c => SCALES.map(k => ({ kind: `scale×${k}`, t: c.t.map(v => v * k), roots: c.roots.map(w => w.map(v => v * Math.sqrt(k))) })));
function run(opts = {}, label = 'v1') {
  const fails = [], stale = [], kinds = {}; let falseComplete = 0;
  for (const c of [...V.cases, ...scaled]) {
    const r = M.sqrtAll(...c.t, opts), s = Math.sqrt(Math.hypot(...c.t)) || 1, e = 1e-8 * s;
    kinds[c.kind] = kinds[c.kind] || [0, 0]; kinds[c.kind][1]++;
    let ok;
    if (c.kind.startsWith('caveat')) {
      ok = true;
      if (r.status === 'complete' && r.roots.length === 4) ok = false;                     // a 4 must never be called complete
      if (r.status === 'complete' && c.kind === 'caveat-fold') stale.push(`${c.kind}: fold returned as 'complete', documented 'edge'`);
      if (c.kind === 'caveat-tongue' && r.roots.length === 6) stale.push(`${c.kind} ${JSON.stringify(c.t.map(v => +v.toPrecision(4)))}: all 6 roots returned now (${r.status})`);
      if (c.kind === 'caveat-fold' && r.roots.some(w => near(w, c.double, 1e-5 * s))) stale.push(`${c.kind} ${JSON.stringify(c.t)}: the double root IS returned now (${r.status}, ${r.roots.length})`);
    } else if (c.roots === null) ok = r.status === 'complete' && r.roots.length === c.count;
    else if (c.kind === 'zero') ok = r.status === 'zero' && r.roots.length === 1;
    else ok = (r.status === 'complete' || (r.status === 'edge' && c.roots.length === 2)) && r.roots.length === c.roots.length && c.roots.every(w => r.roots.some(x => near(x, w, e)))
      && r.roots.every(w => relRes(w, c.t) < 1e-9);
    if (r.status === 'edge') kinds[c.kind][2] = (kinds[c.kind][2] || 0) + 1;
    if (!ok && r.status === 'complete') falseComplete++;
    if (ok) kinds[c.kind][0]++; else fails.push(`${c.kind} t=${JSON.stringify(c.t.map(v => +v.toPrecision(3)))}: got ${r.roots.length} (${r.status}${r.escalated ? ', escalated' : ''}), want ${c.roots ? c.roots.length : c.count ?? c.distinct}${r.roots.length && c.t.some(v => v) ? `, max rel residual ${Math.max(...r.roots.map(w => relRes(w, c.t))).toExponential(1)}` : ''}`);
  }
  return { fails, stale, kinds, label, falseComplete };
}
function report(R) {
  console.log(`${R.label}: ` + Object.entries(R.kinds).map(([k, [a, b, ed]]) => `${k} ${a}/${b}${ed ? ` (${ed} edge)` : ''}`).join(' · '));
  for (const f of R.fails.slice(0, 8)) console.log('  FAIL ' + f); if (R.fails.length > 8) console.log(`  … ${R.fails.length - 8} more`);
  for (const s of R.stale) console.log('  STALE CAVEAT ' + s);
  return R.fails.length === 0;
}
const clean = report(run());
if (!process.argv.includes('--selftest')) process.exit(clean ? 0 : 1);
// plants. Each must fire (produce fails).
const plants = [];
const swap = (name, mut, opts = {}) => { const t = { r: tab.r.slice(), c: tab.c.slice() }; mut(t); M.setTable(t); const R = run(opts, name); M.setTable(tab); plants.push([name, R.fails.length, R.falseComplete]); };
// 1 no neighbour rule: near-caustic 6-targets whose pixel reads 2 must be missed
swap('P1 neighbour off', () => {}, { neighbour: false });
// 2 table claims 2 everywhere (cap erased): the 2-or-6 rule cannot see it; fails = the residual risk made real
swap('P2 cap erased', t => { for (let k = 0; k < t.c.length; k++) if (t.c[k] === 6) t.c[k] = 2; });
// 3 table rotated 180° in longitude (wrong direction convention)
swap('P3 lon shifted', t => { const W = M.TW, H = M.TH, r = t.r.slice(), c = t.c.slice(); for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) { const a = j * W + i, b = j * W + (i + W / 2) % W; t.c[a] = c[b]; t.r.set(r.subarray(b * 18, b * 18 + 18), a * 18); } });
// 4 one pair's coordinates lost at every 6-pixel (count byte kept): the rule sees every 4, so no FALSE 'complete' may appear; the fallback's
//   16 starts cannot always separate near-caustic roots, so those come back 'unresolved' (honest), not wrong
swap('P4 pair lost (rule rescues)', t => { for (let k = 0; k < t.c.length; k++) if (t.c[k] === 6) for (const [d, src] of [[4, 0], [5, 1]]) t.r.set(t.r.subarray((k * 6 + src) * 3, (k * 6 + src) * 3 + 3), (k * 6 + d) * 3); });
// 5 the absolute tolerance (pre-T-196 path): tiny targets come back 'complete' with unpolished table seeds
{ const R = run({ unit: false }, 'P5 absolute tol'); plants.push(['P5 absolute tol', R.fails.length, R.falseComplete]); }
let good = clean;
for (const [n, f, fc] of plants) { const want = n.startsWith('P4') ? fc === 0 : f > 0; good &&= want; console.log(`${want ? 'ok ' : 'BAD'} ${n}: ${f} fails, ${fc} falsely 'complete'${n.startsWith('P4') ? ' (false complete must be 0)' : ' (fails must be > 0)'}`); }
process.exit(good ? 0 : 1);
