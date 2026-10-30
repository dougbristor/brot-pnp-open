# Build table180.f32 (180x90 directions x 6 roots x xyz, float32, unit targets) and table180.cnt (uint8 root count).
# Pixel (i, j) is the direction dirOf(lon, lat) with lon = -180 + (i+0.5)*2, lat = 90 - (j+0.5)*2  (explorer convention,
# lat 90 = real axis). Roots of B(w)=s²·t̂ are s·roots(t̂): B is homogeneous of degree 2.
#   python make_table.py      (needs numpy + sympy; ~10 s on 16 cores)
import numpy as np, os
from multiprocessing import Pool
from oracle_elim import roots_A, roots_B, dirOf
W, H = 180, 90
def union(a, b):
    out = list(a)
    for w in b:
        if not any(np.linalg.norm(w - o) < 1e-6 for o in out): out.append(w)
    return out
def row(j):
    R = np.zeros((W, 6, 3), np.float32); C = np.zeros(W, np.uint8)
    for i in range(W):
        t = dirOf(-180 + (i + .5) * 360 / W, 90 - (j + .5) * 180 / H); u = union(roots_A(t), roots_B(t))
        assert len(u) in (2, 6), (i, j, len(u)); C[i] = len(u)
        for k, w in enumerate(u): R[i, k] = w
    return j, R, C
if __name__ == '__main__':
    R = np.zeros((H, W, 6, 3), np.float32); C = np.zeros((H, W), np.uint8)
    with Pool() as p:
        for j, r, c in p.imap_unordered(row, range(H)): R[j] = r; C[j] = c
    d = os.path.dirname(os.path.abspath(__file__))
    R.astype('<f4').tofile(os.path.join(d, 'table180.f32')); C.tofile(os.path.join(d, 'table180.cnt'))
    print('table180:', {int(k): int(v) for k, v in zip(*np.unique(C, return_counts=True))})
