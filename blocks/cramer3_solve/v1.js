// cramer3_solve / v1
// codetree:cramer3_solve/v1 — see codetree/blocks/cramer3_solve/
//
// VERBATIM. Every line below is character-identical to the 28 copies already in the repo
// (28 of 28 agree once whitespace is normalised; the only divergence found anywhere was a
// trailing comma). Nothing was tidied, parameterised or renamed on the way in — the first
// three blocks in this tree were all refactored as they were planted, and the result is that
// no citing site contains the code its own citation header points at. See
// fable/RESULT_codetree_faults_20260920.md. The `export` is appended at the end so an ESM
// consumer can import it without a single line inside the function differing from the sites.
//
// Solves the 3x3 system A x = b by Cramer's rule, A given row-major as a00..a22.
// Returns [x0, x1, x2], or NULL when |det| < 1e-14 — see block.md for what null means.

function cramer3(a00,a01,a02, a10,a11,a12, a20,a21,a22, b0,b1,b2) {
  const c00=a11*a22-a12*a21, c01=a10*a22-a12*a20, c02=a10*a21-a11*a20;
  const det=a00*c00-a01*c01+a02*c02;
  if (Math.abs(det) < 1e-14) return null;
  const iv = 1/det;
  return [
    iv*(b0*c00  - a01*(b1*a22-a12*b2) + a02*(b1*a21-a11*b2)),
    iv*(a00*(b1*a22-a12*b2) - b0*c01  + a02*(a10*b2-b1*a20)),
    iv*(a00*(a11*b2-b1*a21) - a01*(a10*b2-b1*a20) + b0*c02),
  ];
}

export { cramer3 };
