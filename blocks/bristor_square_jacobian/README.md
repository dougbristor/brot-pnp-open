# bristor_square_jacobian

Squaring in Bristorian 3-space and its Jacobian, as a two-sign family. The shipped signs are
(sIJ, sJI) = (−1, +1), which gives the B in the repo README.

```
nx = wx² − wy² − wz²
ny = wy·(2·wx + sIJ·wz)
nz = wz·(2·wx + sJI·wy)
```

```
⎡ 2wx        −2wy          −2wz        ⎤
⎢ 2wy    2wx + sIJ·wz    sIJ·wy        ⎥
⎣ 2wz      sJI·wz      2wx + sJI·wy    ⎦
```

The Jacobian is returned as nine scalars, row-major, the argument order `cramer3_solve` takes: the two
blocks are the two halves of one Newton step.

**Conformance.** `node conform.mjs` (JS) and `python3 conform.py` (Python), against `vectors.json`.
