#!/usr/bin/env node
// codetree:bristor_square_jacobian/v1 — conformance runner
//
//   node conform.mjs                                     check this block's generator, all 4 pairs
//   node conform.mjs <module.js> [exportName]            check a site's own hand-written version
//                                                        against the SHIPPED pair (it is the only
//                                                        one a fixed implementation can have)
//
// The expectations in vectors.json come from central finite differences of the squaring map over
// exact rationals — not from this block's closed form. Squaring is quadratic, so the central
// difference is exact, which makes agreement evidence instead of a tautology.
//
// A site's implementation is expected to return NINE SCALARS ROW-MAJOR, the order cramer3 takes.
// A 3x3 nested array is accepted and flattened: that is a shape difference, not a disagreement,
// and saying so is half of what this table is for.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const here = path.dirname(fileURLToPath(import.meta.url));
const doc = JSON.parse(fs.readFileSync(path.join(here, 'vectors.json'), 'utf8'));
const [modArg, exportName = 'jacobian3x3'] = process.argv.slice(2);

const flat = v => (Array.isArray(v[0]) ? v.flat() : Array.from(v));
let fn, label, cases;

if (modArg) {
  const mod = await import(path.resolve(modArg));
  if (!mod[exportName]) {
    console.error(`no export '${exportName}' in ${modArg} — exports: ${Object.keys(mod).join(', ')}`);
    process.exit(2);
  }
  fn = (w) => flat(mod[exportName](...w));
  label = `${path.relative(process.cwd(), path.resolve(modArg))} :: ${exportName}`;
  cases = doc.cases.filter(c => c.signs.sIJ === -1 && c.signs.sJI === 1);   // shipped only
} else {
  const mod = await import(path.join(here, 'v1.js'));
  fn = (w, s) => flat(mod.bristorSquareJacobian(...w, s));
  label = 'v1.js :: bristorSquareJacobian (all four sign pairs)';
  cases = doc.cases;
}

let fail = 0;
console.log(`bristor_square_jacobian — ${cases.length} vectors against ${label}`);
console.log(`expectations from: ${doc.expectations_from.split('—')[0].trim()}\n`);
for (const c of cases) {
  const got = fn(c.w, c.signs);
  const err = got.length !== 9 ? Infinity
            : Math.max(...got.map((v, i) => Math.abs(v - c.jacobian[i])));
  const ok = err <= doc.tol;
  if (!ok) fail++;
  console.log(`  ${(ok ? 'ok' : 'FAIL').padEnd(6)} ${c.name.padEnd(20)} ` +
              `(sIJ,sJI)=(${c.signs.sIJ},${c.signs.sJI})  max abs err ${err.toExponential(2)}`);
}
console.log();
console.log(fail ? `${fail} FAILURE(S) — this is not the Jacobian of the squaring map it claims.`
                 : `conforms — every entry matches a derivative taken independently of the formula.`);
if (!modArg) console.log(`naming: ${doc.naming_is_open}`);
process.exit(fail ? 1 : 0);
