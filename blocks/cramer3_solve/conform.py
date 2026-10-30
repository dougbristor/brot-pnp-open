#!/usr/bin/env python3
"""
conform.py — the same vectors, in the language the code could not travel to.

  python3 conform.py            check the numpy solve used by julia_bristor's inverse iteration
  python3 conform.py --json     machine-readable

WHY THIS FILE IS THE POINT. `cramer3` is 28 identical copies of JavaScript, which needed no
translation — but the same job is done in Python by `julia_bristor/bristor_inverse_julia.py`
(`np.linalg.solve(bristor_jacobian(p), R)`, the Newton step of the Bristorian inverse), and
no amount of copying moves JavaScript there. A generated "proto" implementation would make
both agree by construction and destroy the independence that catches errors. `vectors.json`
does the opposite: it lets two genuinely different implementations be compared, and SAYS SO
WHEN THEY DISAGREE.

A DISAGREEMENT HERE IS NOT A FAILURE. The `solve` and `null` cases are the contract and must
pass. The `caveat` cases assert that the JS block keeps misbehaving in its documented way —
another implementation is entitled to behave better, and when it does, this prints DIVERGES.
That is the finding, not an error: it means the two sites are not the same thing at the
boundary, and any caller moving between them needs to know which one it is standing on.
"""
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
DOC = json.loads((HERE / 'vectors.json').read_text())


def solve_numpy(A, b):
    """The contract, as julia_bristor's inverse iteration implements it: numpy LU with
    partial pivoting, None when the matrix is singular. Note what is NOT here — no absolute
    1e-14 determinant floor. That floor is the JS block's own choice, not the contract's."""
    try:
        return [float(v) for v in np.linalg.solve(np.array(A, float), np.array(b, float))]
    except np.linalg.LinAlgError:
        return None


def rel(got, want):
    return max(abs(g - w) / max(1e-300, abs(w)) for g, w in zip(got, want))


def main():
    rows, fail, diverge = [], 0, 0
    for c in DOC['cases']:
        got = solve_numpy(c['A'], c['b'])
        if c['kind'] == 'null':
            ok, note = got is None, 'null as required' if got is None else f'returned {got}'
        elif c['kind'] == 'solve':
            if got is None:
                ok, note = False, 'returned None for a solvable system'
            else:
                e = rel(got, c['expect']); ok = e <= DOC['tol']; note = f'rel err {e:.2e}'
        else:
            if c['assert_'] == 'null':
                ok = got is None
                note = ('shares the caveat — rejects it too' if ok else
                        f'DIVERGES — solves it: {[round(v, 12) for v in got]}')
            else:
                e = None if got is None else rel(got, c['exact'])
                ok = got is not None and e > 1e-6
                note = ('None' if got is None else f'accepted, rel err {e:.2e}') + \
                       ('' if ok else ' — DIVERGES, this implementation is accurate here')
            if not ok: diverge += 1
        if not ok and c['kind'] != 'caveat': fail += 1
        tag = ('ok' if ok else 'FAIL') if c['kind'] != 'caveat' else ('shared' if ok else 'DIVERGES')
        rows.append((tag, c['name'], c['det'], note))

    if '--json' in sys.argv:
        print(json.dumps([dict(zip(('tag', 'name', 'det', 'note'), r)) for r in rows], indent=1)); return

    print(f"cramer3_solve — {len(DOC['cases'])} vectors against numpy (julia_bristor's solver)")
    print(f"expectations from: {DOC['expectations_from'].split('—')[0].strip()}\n")
    for tag, name, det, note in rows:
        print(f'  {tag:<10} {name:<30} det={str(det):<10} {note}')
    print()
    if fail:
        print(f'{fail} CONTRACT FAILURE(S) — this implementation does not solve what it claims to.')
    if diverge:
        print(f'{diverge} DIVERGENCE(S) from the JS block, at the documented caveats only.')
        print('The contract holds in both; the EDGE does not. A caller that moves between them')
        print('changes which systems get silently rejected. That is the thing worth knowing, and')
        print('it is invisible to any check that only runs one implementation.')
    if not fail and not diverge:
        print('conforms, caveats included — the two implementations are the same thing throughout.')
    sys.exit(1 if fail else 0)


if __name__ == '__main__':
    main()
