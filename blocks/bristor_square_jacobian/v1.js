// bristor_square_jacobian / v1
// codetree:bristor_square_jacobian/v1 — see codetree/blocks/bristor_square_jacobian/
//
// THIS BLOCK IS GENERATED, AND THAT IS A DELIBERATE EXCEPTION. Every other block in this tree
// is planted verbatim, because a tidied reference points at code no site runs
// (fable/RESULT_codetree_faults_20260920.md). The exception is for DATA-shaped atoms: where the
// thing is a table rather than an algorithm, there is no idiom to lose, translation is total,
// and generating it costs none of the independence that catches errors — there is nothing to
// re-derive, only a sign convention to state once.
//
// It is stated once here because stating it separately is how it went wrong: the same matrix is
// hand-written in JavaScript and in GLSL across five agents, and two file headers ended up
// describing the same formulas with different multiplication rules (T-098, brotdocs).
//
// THE FAMILY. Squaring in Bristorian 3-space, with two independent sign choices:
//
//     nx = wx² − wy² − wz²
//     ny = wy·(2·wx + sIJ·wz)
//     nz = wz·(2·wx + sJI·wy)
//
// and its Jacobian, which is what the Newton step of the inverse actually needs:
//
//     ⎡ 2wx        −2wy          −2wz       ⎤
//     ⎢ 2wy    2wx + sIJ·wz    sIJ·wy       ⎥
//     ⎣ 2wz      sJI·wz      2wx + sJI·wy   ⎦
//
// FOUR COMBINATIONS ARE LIVE IN THE REPO, counted per file and per line (never from a
// deduplicated grep — that mistake is F-15):
//   (-1, +1)  SHIPPED — 26 sites in 25 files across caro, cloud, codon, fable, sonic
//   (-1, -1)  codon/web/inv_jbrot_cloud_experimental_gxt.js:56, ...toothpaste...:111
//   (+1, +1)  codon/web/inv_jbrot_cloud_experimental_gxt.js:57, ...toothpaste...:112
//   (+1, -1)  written literally NOWHERE — reachable only through the parameterised call in
//             codon/web/generator_signflip_variants.html:173
//
// WHAT THIS BLOCK DOES NOT SAY. It does not name the algebras. Which multiplication rule each
// sign pair corresponds to is open as T-098 (OBJ-004) and its done-when requires the Cayley
// table, not a file header. Everything here is stated as FORMULAS, which are checkable, and
// the naming is left where it belongs.

/** The shipped convention — what 26 of the 30 live sites use. */
export const SHIPPED = { sIJ: -1, sJI: 1 };

/** The four combinations live in the repo, for a caller that wants to sweep them. */
export const FAMILY = [
  { sIJ: -1, sJI:  1, id: 'shipped' },
  { sIJ: -1, sJI: -1, id: 'both_negative' },
  { sIJ:  1, sJI:  1, id: 'both_positive' },
  { sIJ:  1, sJI: -1, id: 'mixed' },
];

/** Squaring: w ↦ w², in the (sIJ, sJI) convention. Returns [nx, ny, nz]. */
export function bristorSquare(wx, wy, wz, { sIJ, sJI } = SHIPPED) {
  return [
    wx * wx - wy * wy - wz * wz,
    wy * (2 * wx + sIJ * wz),
    wz * (2 * wx + sJI * wy),
  ];
}

/**
 * The Jacobian of the above at (wx, wy, wz), ROW-MAJOR as nine scalars — the order
 * `cramer3` takes them in, since that is where every caller sends it.
 * See codetree/blocks/cramer3_solve/ for the solve itself.
 */
export function bristorSquareJacobian(wx, wy, wz, { sIJ, sJI } = SHIPPED) {
  return [
    2 * wx,      -2 * wy,             -2 * wz,
    2 * wy,  2 * wx + sIJ * wz,   sIJ * wy,
    2 * wz,   sJI * wz,           2 * wx + sJI * wy,
  ];
}

/** The residual F(w) − t, negated, which is the right-hand side of the Newton step. */
export function bristorResidual(wx, wy, wz, tx, ty, tz, signs = SHIPPED) {
  const [nx, ny, nz] = bristorSquare(wx, wy, wz, signs);
  return [-(nx - tx), -(ny - ty), -(nz - tz)];
}
