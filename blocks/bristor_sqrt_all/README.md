# bristor_sqrt_all

Every real w with B(w) = t, for the B2 square in the README (shipped signs):
`sqrtAll(tx, ty, tz) → { roots, status, escalated }`. Call `await loadTable()` once first. In the browser
it fetches `table180.f32` and `table180.cnt` from next to `v1.js`; in node it reads them with fs.

**Why it can know it is done.** A regular target has **2 or 6** roots, never 4. B has no nonzero real
zero, so B/|B| factors through RP² → S². The number of root pairs mod 2 is then a degree, and it equals 1
because (1,0,0) has 2 roots. Bézout caps the count at 8. The 6-root targets fill one three-cusped cap
around −1 (4.9% of directions), bounded by the caustic. On the caustic there are 4 distinct roots; at
the cusps, 2.

**Method.** B is homogeneous, so roots(s²·t̂) = s·roots(t̂).
1. A 180×90 table stores the roots of each unit direction, built by `make_table.py` from exact
   elimination (`oracle_elim.py`, entry point `exact(t)`).
2. Look up t̂, polish with Newton on t̂ (at most 12 iterations), then scale the roots by √|t|.
3. If the pixel has 2 roots but a 6-root pixel is in its 3×3 neighbourhood, polish that pixel's roots
   too; if still 2, polish every neighbour's.
4. If the count still breaks 2-or-6, fall back to 4 → 8 → 16 fixed Newton starts.

| status | meaning |
|---|---|
| `complete` | 6 roots; or 2 roots with no 6-root pixel in the 3×3 neighbourhood. A table claim, not a proof: see Caveats |
| `edge` | 2 roots near the cap's edge. Usually right, but a hidden pair is not ruled out: treat as unresolved if you need certainty |
| `unresolved` | the count still breaks 2-or-6 after 16 starts |
| `zero` | t = 0, root 0 |

**Caveats.** On the caustic itself (measure zero) the double root is dropped and the 2 simple roots come
back as `edge`. The table is for the shipped signs only.

**A `complete` 2 can be wrong.** The 6-root cap has cusp tongues thinner than one table pixel (2°). Near lon −179.6°,
lat −31.7°, v1 returns 2 roots as `complete` on targets that have 6 (4 roots missed; the roots are not close to merging).
This was found by a completeness check that placed targets on the caustic on purpose; a random bench almost never lands
there. `conform.mjs` pins three such targets as `caveat-tongue` (documented wrongness; it reports STALE CAVEAT once fixed).
**If you need certainty in or near the cap, do not trust `complete`:** check the count against `oracle_elim.py`.

**Conformance.** `node conform.mjs [--selftest]`. The selftest plants five known faults and fails unless
each is caught.
