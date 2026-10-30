#!/usr/bin/env python3
"""
conform.py — the same vectors against the Python site that hand-writes this matrix.

  python3 conform.py                      check julia_bristor's bristor_jacobian / bristor_square
  python3 conform.py --module M --fn F    check any module's 3x3 Jacobian function

julia_bristor/bristor_inverse_julia.py holds both halves of this block, written by hand in
numpy: the squaring map and its Jacobian, used for the Newton step of the inverse. No amount of
copying moves the JavaScript there, so the table is what says the two are the same thing.

Expectations come from central finite differences of the squaring map over exact rationals —
not from either implementation's closed form. Squaring is quadratic, so the central difference
is exact, and agreement is evidence rather than a tautology.

Only the SHIPPED (sIJ,sJI) = (-1,+1) cases are checked here: a hand-written implementation has
one convention baked in, and which one it is is precisely what this file exists to establish.
"""
import argparse, importlib.util, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOC = json.loads((HERE / 'vectors.json').read_text())


def load(path, name):
    spec = importlib.util.spec_from_file_location('site_under_test', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--module', default=str(ROOT / 'julia_bristor/bristor_inverse_julia.py'))
    ap.add_argument('--fn', default='bristor_jacobian')
    ap.add_argument('--square-fn', default='bristor_square')
    a = ap.parse_args()

    jac = load(a.module, a.fn)
    try:
        sq = load(a.module, a.square_fn)
    except AttributeError:
        sq = None

    cases = [c for c in DOC['cases'] if c['signs'] == {'sIJ': -1, 'sJI': 1}]
    rel = Path(a.module).relative_to(ROOT) if str(a.module).startswith(str(ROOT)) else a.module
    print(f"bristor_square_jacobian — {len(cases)} shipped-pair vectors against {rel} :: {a.fn}")
    print(f"expectations from: {DOC['expectations_from'].split('—')[0].strip()}\n")

    fail = 0
    for c in cases:
        got = np.asarray(jac(np.array(c['w'], float)), float).reshape(-1)
        err = float(np.max(np.abs(got - np.array(c['jacobian'], float))))
        ok = err <= DOC['tol']; fail += not ok
        note = f'max abs err {err:.2e}'
        if sq is not None:                       # the map the Jacobian must be the derivative OF
            se = float(np.max(np.abs(np.asarray(sq(np.array(c['w'], float)), float).reshape(-1)
                                     - np.array(c['square'], float))))
            note += f'   squaring map err {se:.2e}'
            if se > DOC['tol']:
                ok = False; fail += 1
                note += '  <- the map itself differs, so the Jacobian agreeing would be a coincidence'
        print(f"  {'ok' if ok else 'FAIL':<6} {c['name']:<20} {note}")

    print()
    if fail:
        print(f'{fail} FAILURE(S) — this site does not hold the shipped convention, or not this map.')
    else:
        print('conforms — this Python site and the JavaScript sites are the same matrix, shipped pair,')
        print('verified against a derivative taken independently of both.')
    print(f"naming: {DOC['naming_is_open']}")
    sys.exit(1 if fail else 0)


if __name__ == '__main__':
    main()
