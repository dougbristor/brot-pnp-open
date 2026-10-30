# cramer3_solve

Solves the 3×3 system `A x = b` by Cramer's rule. `A` is passed row-major as twelve scalars
(`a00 a01 a02, a10 a11 a12, a20 a21 a22, b0 b1 b2`), so nothing is allocated inside a Newton loop.
Returns `[x0, x1, x2]`, or **`null` when |det| < 1e-14**.

Its use here is the Newton step of the Bristorian inverse: the Jacobian of squaring and the negated
residual. A `null` then means the iterate is on or near a critical point of the squaring map, where no
branch of the inverse is locally defined. A caller that treats `null` as a number gets `NaN`s.

**Conformance.** `node conform.mjs` and `python3 conform.py`, against `vectors.json`.
