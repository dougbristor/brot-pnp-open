# vectors.json for conform.mjs. Expectations come from the exact elimination (oracle_elim.py), NOT from v1.js,
# and every regular case is gated at generation by an independent 400-start Newton search agreeing on the count.
#   python make_vectors.py
import numpy as np, json, os
from oracle_elim import exact, B, J, dirOf, detJ
rng = np.random.default_rng(1019)
def newton_count(t, n=400):
    s = np.sqrt(np.linalg.norm(t)); out = []
    for _ in range(n):
        w = rng.normal(size=3) * s
        for _ in range(60):
            try: w = w - np.linalg.solve(J(w), B(w) - t)
            except np.linalg.LinAlgError: break
        if np.linalg.norm(B(w) - t) < 1e-10 * max(1, np.linalg.norm(t)) and not any(np.linalg.norm(w - o) < 1e-6 * s for o in out): out.append(w)
    return len(out)
def cone_lat(lo):
    f = lambda la: detJ(dirOf(lo, la)); a, b = -90.0, 90.0; fa = f(a)
    for _ in range(80):
        m = (a + b) / 2; fm = f(m)
        if fa * fm <= 0: b = m
        else: a, fa = m, fm
    return (a + b) / 2
cases = []; dropped = 0
def regular(kind, t):
    global dropped
    r = exact(t)
    if len(r) not in (2, 6) or newton_count(t) != len(r): dropped += 1; return
    cases.append(dict(kind=kind, t=[float(v) for v in t], roots=[[float(v) for v in w] for w in r]))
for _ in range(300):
    d = rng.normal(size=3); regular('random', d / np.linalg.norm(d) * np.exp(rng.uniform(np.log(0.05), np.log(20))))
got = 0
while got < 40:  # inside the 6-cap (around −1)
    d = rng.normal(size=3) * 0.6 + np.array([-1.0, 0, 0]); d /= np.linalg.norm(d)
    if len(exact(d)) == 6: n0 = len(cases); regular('cap', d * np.exp(rng.uniform(np.log(0.05), np.log(20)))); got += len(cases) > n0
cus = [11.779, 78.221, 135.0]
for lo in rng.uniform(0, 360, 30):
    if min(abs(((lo - c + 180) % 360) - 180) for c in cus) < 3: continue
    d = dirOf(lo, cone_lat(lo)); m = np.linalg.svd(J(d))[0][:, -1]
    for eps in (3e-3, 3e-2):
        for sg in (1, -1): regular('near-caustic', B(d) + sg * eps * m)
# axis targets: one nudge off each axis (the elimination's blind spot is the exact axis), and the axes themselves
for t in ([1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]):
    regular('axis-nudge', np.array(t, float) + 1e-4 * rng.normal(size=3))
for t in ([1, 0, 0], [-1, 0, 0], [4, 0, 0], [-0.25, 0, 0]):  # exact() closed forms; −1: ±i, ±j, ±(1,−2,2)/√7
    cases.append(dict(kind='axis', t=t, roots=[[float(v) for v in w] for w in exact(t)]))
cases.append(dict(kind='zero', t=[0, 0, 0], roots=[[0, 0, 0]]))
# caveat: exactly on the caustic there is no regular count (fold: 4 distinct, one double; cusp: 2, a triple)
for lo in (30.0, 100.0, 200.0, 250.0):
    d = dirOf(lo, cone_lat(lo)); cases.append(dict(kind='caveat-fold', t=[float(v) for v in B(d)], distinct=4, double=[float(v) for v in d]))
for lo in cus:
    d = dirOf(lo, cone_lat(lo)); cases.append(dict(kind='caveat-cusp', t=[float(v) for v in B(d)], distinct=2, double=[float(v) for v in d]))
json.dump(dict(note='expectations from oracle_elim.py (two eliminations) gated by 400-start Newton; not from v1.js', dropped=dropped, cases=cases),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vectors.json'), 'w'), indent=0)
from collections import Counter
print('cases', Counter(c['kind'] for c in cases), 'dropped', dropped, 'six', sum(1 for c in cases if c.get('roots') and len(c['roots']) == 6))
