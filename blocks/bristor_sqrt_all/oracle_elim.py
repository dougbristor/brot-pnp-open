# Oracle for bristor_sqrt_all: exact elimination (two orders, complementary blind spots). Copied from
# aicolab/tmp/rcm/inverse_count/elim.py (insights 2026-10-19). Builds the table and the conformance vectors.
# Two eliminations of B(w)=t with different blind spots (T-049 B2: B=(x²−y²−z², y(2x−z), z(2x+y))).
#  A: x from eq2 (divides by y) -> Res_z -> poly in y.   blind where a root has y=0 (t2=0)
#  B: x from eq3 (divides by z) -> Res_y -> poly in z.   blind where a root has z=0 (t3=0)
import numpy as np, sympy as sp
y,z,t1,t2,t3=sp.symbols('y z t1 t2 t3')
# A: 2x = t2/y + z ;  eq3: z(t2/y + z + y) = t3 -> PA ; eq1 -> QA
PA=sp.expand(t2*z + y*z**2 + y**2*z - t3*y)
QA=sp.expand((t2+y*z)**2 - 4*y**2*(y**2+z**2+t1))
RA=sp.Poly(sp.resultant(PA,QA,z),y)
# B: 2x = t3/z - y ;  eq2: y(t3/z - y - z) = t2 -> PB ; eq1 -> QB
PB=sp.expand(t3*y - y**2*z - y*z**2 - t2*z)
QB=sp.expand((t3-y*z)**2 - 4*z**2*(y**2+z**2+t1))
RB=sp.Poly(sp.resultant(PB,QB,y),z)
cA=sp.lambdify((t1,t2,t3),RA.all_coeffs(),'numpy'); cB=sp.lambdify((t1,t2,t3),RB.all_coeffs(),'numpy')
def B(w):
    x,a,b=w; return np.array([x*x-a*a-b*b, a*(2*x-b), b*(2*x+a)])
def J(w):
    x,a,b=w; return np.array([[2*x,-2*a,-2*b],[2*a,2*x-b,-a],[2*b,b,2*x+a]])
def polish(w,t,it=6):
    for _ in range(it):
        try: w=w-np.linalg.solve(J(w),B(w)-t)
        except np.linalg.LinAlgError: break
    return w
def _collect(t,cands,res_tol,dedup):
    out=[]
    for w in cands:
        w=polish(w,t)
        if np.linalg.norm(B(w)-t)<res_tol*max(1,np.linalg.norm(t)) and not any(np.linalg.norm(w-o)<dedup for o in out): out.append(w)
    return out
def roots_A(t,imag_tol=1e-7,res_tol=1e-9,dedup=1e-6):
    c=np.array(cA(*t),float); cands=[]
    for yy in np.roots(c):
        if abs(yy.imag)>imag_tol*max(1,abs(yy)) or abs(yy.real)<1e-12: continue
        yy=yy.real
        for zz in np.roots([yy, t[1]+yy*yy, -t[2]*yy]):
            if abs(zz.imag)>1e-6*max(1,abs(zz)): continue
            zz=zz.real; cands.append(np.array([(t[1]+yy*zz)/(2*yy),yy,zz]))
    return _collect(t,cands,res_tol,dedup)
def roots_B(t,imag_tol=1e-7,res_tol=1e-9,dedup=1e-6):
    c=np.array(cB(*t),float); cands=[]
    for zz in np.roots(c):
        if abs(zz.imag)>imag_tol*max(1,abs(zz)) or abs(zz.real)<1e-12: continue
        zz=zz.real
        # PB quadratic in y: -z y² + (t3 - z²) y - t2 z = 0
        for yy in np.roots([-zz, t[2]-zz*zz, -t[1]*zz]):
            if abs(yy.imag)>1e-6*max(1,abs(yy)): continue
            yy=yy.real; cands.append(np.array([(t[2]/zz-yy)/2,yy,zz]))
    return _collect(t,cands,res_tol,dedup)
def dirOf(lo,la):  # explorer convention (brotoid_weft dirOf): lat 90 = real axis
    lo,la=np.radians(lo),np.radians(la); return np.array([np.sin(la),np.cos(la)*np.cos(lo),np.cos(la)*np.sin(lo)])
def lonlat(v):
    v=v/np.linalg.norm(v); return np.degrees(np.arctan2(v[2],v[1])), np.degrees(np.arcsin(np.clip(v[0],-1,1)))
def detJ(w): return np.linalg.det(J(w))
# exact(t): the general-purpose entry (caro 10-19 sewr: the A∪B union is [] at (1,0,0), and loses roots within ~1e-12 of
# the positive real axis, because both eliminations divide by a coordinate that vanishes there).
# Contracts:  t=0 -> [0] (the only real zero; B is proper; det J(0)=0, singular).
#   t=(a,0,0), a>0 -> ±(√a,0,0)            (y(2x−z)=z(2x+y)=0 forces y=z=0)
#   t=(a,0,0), a<0 -> ±(0,s,0), ±(0,0,s), ±(1,−2,2)·s/√7, s=√−a   (−1: ±i, ±j, ±(1,−2,2)/√7)
#   else A∪B, plus Newton from ±(√t1, t2/2√t1, t3/2√t1) when t1>0 (first-order root off the positive axis).
# A count outside {2,6} means t is on the caustic (a fold has 4 distinct, a cusp 2): no regular count there.
def _union(a,b,tol):
    out=list(a)
    for w in b:
        if not any(np.linalg.norm(w-o)<tol for o in out): out.append(w)
    return out
def exact(t):
    t=np.asarray(t,float); n=np.linalg.norm(t)
    if n==0: return [np.zeros(3)]
    if t[1]==0 and t[2]==0:
        s=np.sqrt(abs(t[0]))
        if t[0]>0: return [np.array([s,0,0]),np.array([-s,0,0])]
        v=np.array([1.,-2,2])*s/np.sqrt(7)
        return [np.array([0,s,0]),np.array([0,-s,0]),np.array([0,0,s]),np.array([0,0,-s]),v,-v]
    tol=1e-6*np.sqrt(n); r=_union(roots_A(t),roots_B(t),tol)
    if len(r) not in (2,6) and t[0]>0:
        s=np.sqrt(t[0]); w0=np.array([s,t[1]/(2*s),t[2]/(2*s)])
        r=_union(r,_collect(t,[w0,-w0],1e-9,tol),tol)
    return r
