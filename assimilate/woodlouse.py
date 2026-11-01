#!/usr/bin/env python3
"""woodlouse: the brot's assimilating compute.

A brotette (a fork) sends a claim as a new folder claims/<id>/ holding exactly two files:
  claim.json  the atoms: machine-readable statements, each carrying its own certificate
  claim.md    the contributor's prose. It is kept and shown to the reviewer, but it is never
              admitted and never quoted in the ledger.

The woodlouse chops a claim into atoms, checks each atom with its own exact arithmetic
(never with code the claim brings), and feeds only verified atoms to the ledger, as text
it writes itself. A persuasive paragraph therefore has no route into the store: only what
a certificate carries does. See ASSIMILATION.md.

Commands:
  woodlouse.py verify <claim_dir>                  one claim -> JSON verdict
  woodlouse.py route <base> <head> --repo DIR      which route a PR is on: intake (claims/) or core
  woodlouse.py intake <base> <head> --repo DIR [--files DIR] [--claims-only]
                                                   PR intake: guard, then verify each new claim;
                                                   --claims-only fails a core PR instead of passing it
  woodlouse.py admit <claim_dir>                   append a ledger row (core, after merge)
  woodlouse.py selftest                            plants must be caught, valid cases must pass

Standard library only. Exit status 0 = pass, 1 = fail.
"""
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LEDGER = ROOT / "ledger" / "ledger.jsonl"

CLAIM_FILES = {"claim.json", "claim.md"}
CLAIM_ID = re.compile(r"^[0-9]{4}-[a-z0-9-]{1,48}$")
MAX_FILE = 64 * 1024        # same cap as the hollow
MAX_NUM_CHARS = 200         # a rational longer than this is refused, not parsed
MAX_LEVEL = 64
RATIONAL = re.compile(r"-?[0-9]+(/[0-9]+|\.[0-9]+)?\Z")   # \Z: '$' would let "1/2\n" through
KIND_ID = re.compile(r"[a-z][a-z0-9-]{0,31}\Z")              # a kind is a name, never a sentence
MEMBER_KEYS = {"kind", "c", "A", "n", "chain", "cell"}
CELL_KEYS = {"eps", "index"}
DEFINITIONS = ("README.md", "QUESTION.md", "claims/README.md")  # what a statement's words mean

# Prose words that often mark a claim reaching past its certificate. A flag is a prompt for
# the reviewer, never a verdict: the prose is not admitted either way.
OVERREACH = re.compile(
    r"\b(all|every|always|never|any|proves?|proven|proof|guarantee[sd]?|"
    r"exponential|NP|P vs NP|NP-hard|lower bound)\b", re.IGNORECASE)


class Bad(Exception):
    pass


# ── exact arithmetic ──────────────────────────────────────────────────────────

def q(s, where):
    """A rational from a JSON string. JSON numbers are refused: 0.1 as a float is not 1/10."""
    if not isinstance(s, str):
        raise Bad(f"{where}: numbers must be strings, got {type(s).__name__} {s!r}")
    if len(s) > MAX_NUM_CHARS or not RATIONAL.match(s):
        raise Bad(f"{where}: not an exact rational: {s[:40]!r}")
    if re.search(r"/0+\Z", s):
        raise Bad(f"{where}: zero denominator: {s!r}")
    return Fraction(s)


def vec(v, where):
    if not isinstance(v, list) or len(v) != 3:
        raise Bad(f"{where}: expected a list of 3 rationals")
    return tuple(q(s, f"{where}[{i}]") for i, s in enumerate(v))


def F(w, c):
    """F_c(x,y,z) = (x² − y² − z², y(2x − z), z(2x + y)) + c, as in README.md."""
    x, y, z = w
    return (x * x - y * y - z * z + c[0], y * (2 * x - z) + c[1], z * (2 * x + y) + c[2])


def in_ball(w):
    return w[0] * w[0] + w[1] * w[1] + w[2] * w[2] <= 4


def show(w):
    return "(" + ", ".join(str(t) for t in w) + ")"


# ── atom checkers ─────────────────────────────────────────────────────────────

def check_member(a, where):
    """Atom 'member': chain = [w_n, ..., w_1], each in the closed ball |w| ≤ 2,
    F_c(w_k) = w_{k−1} exactly, with w_0 = A. Optional cell = {eps, index}: w_n lies in the
    half-open ε-cell index, i.e. index = ⌊w_n / ε⌋ componentwise."""
    extra = set(a) - MEMBER_KEYS
    if extra:
        # an ignored field could say more than the statement does ("question", "closed")
        raise Bad(f"{where}: unknown fields {sorted(extra)}")
    c = vec(a.get("c"), f"{where}.c")
    A = vec(a.get("A"), f"{where}.A")
    n = a.get("n")
    if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= MAX_LEVEL:
        raise Bad(f"{where}.n: an integer 1..{MAX_LEVEL}")
    chain = a.get("chain")
    if not isinstance(chain, list) or len(chain) != n:
        raise Bad(f"{where}.chain: must hold exactly n = {n} points, holds "
                  f"{len(chain) if isinstance(chain, list) else 'none'}")
    pts = [vec(p, f"{where}.chain[{i}]") for i, p in enumerate(chain)]
    for i, p in enumerate(pts):
        if not in_ball(p):
            raise Bad(f"{where}.chain[{i}] = {show(p)} is outside |w| ≤ 2")
        target = pts[i + 1] if i + 1 < n else A
        if F(p, c) != target:
            raise Bad(f"{where}.chain[{i}]: F_c(w) = {show(F(p, c))} ≠ {show(target)}")
    text = (f"Under F_c with c = {show(c)}, the point {show(pts[0])} is a level-{n} point "
            f"of the backward tree from A = {show(A)} (exact; |w_k| ≤ 2 for k = 1..{n}, "
            f"A itself unconstrained)")
    cell = a.get("cell")
    if cell is not None:
        if not isinstance(cell, dict) or set(cell) != CELL_KEYS:
            raise Bad(f"{where}.cell: exactly {sorted(CELL_KEYS)}")
        eps = q(cell.get("eps"), f"{where}.cell.eps")
        if eps <= 0:
            raise Bad(f"{where}.cell.eps must be > 0")
        idx = cell.get("index")
        if not (isinstance(idx, list) and len(idx) == 3
                and all(isinstance(i, int) and not isinstance(i, bool) for i in idx)):
            raise Bad(f"{where}.cell.index: a list of 3 integers")
        true_idx = [math.floor(t / eps) for t in pts[0]]
        if true_idx != idx:
            raise Bad(f"{where}.cell: w_n lies in cell {true_idx}, not {idx} (cells are half-open)")
        text += f", so level {n} meets the half-open ε = {eps} cell {tuple(idx)}"
    return text + "."


CHECKERS = {"member": check_member}


# ── claims ────────────────────────────────────────────────────────────────────

def claim_hash(d):
    h = hashlib.sha256()
    for name in sorted(CLAIM_FILES):
        h.update(name.encode() + b"\0" + (d / name).read_bytes() + b"\0")
    return h.hexdigest()


def verify(d):
    """Verdict on one claim folder:
      rejected    a file or an atom failed: nothing from it is admitted
      reproduced  every atom verified
      partial     some atoms verified, the rest have no checker (they are not admitted)
      held        no atom could be verified"""
    d = Path(d)
    out = {"claim": d.name, "verdict": "rejected", "statements": [], "unbacked": [],
           "errors": [], "prose_flags": []}
    try:
        if not CLAIM_ID.match(d.name):
            raise Bad(f"claim id {d.name!r} must look like 0001-short-name")
        names = {p.name for p in d.iterdir()}
        if names != CLAIM_FILES:
            raise Bad(f"a claim folder holds exactly {sorted(CLAIM_FILES)}; found {sorted(names)}")
        for name in CLAIM_FILES:
            p = d / name
            if p.is_symlink() or not p.is_file():
                raise Bad(f"{name} must be a plain file")
            if p.stat().st_size > MAX_FILE:
                raise Bad(f"{name} is over {MAX_FILE} bytes")
        prose = (d / "claim.md").read_text(encoding="utf-8")
        out["prose_flags"] = sorted({m.group(0).lower() for m in OVERREACH.finditer(prose)})
        try:
            doc = json.loads((d / "claim.json").read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise Bad(f"claim.json: {e}")
        atoms = doc.get("atoms") if isinstance(doc, dict) else None
        if not isinstance(atoms, list) or not atoms:
            raise Bad("claim.json needs a non-empty list 'atoms'")
        for i, a in enumerate(atoms):
            if not isinstance(a, dict):
                raise Bad(f"atoms[{i}] must be an object")
            kind = a.get("kind")
            if not isinstance(kind, str):
                raise Bad(f"atoms[{i}].kind must be a string")
            check = CHECKERS.get(kind)
            if check is None:
                # the ledger keeps a name, never contributor text
                shown = repr(kind) if KIND_ID.match(kind) else \
                    f"<not a kind name; sha256 {hashlib.sha256(kind.encode()).hexdigest()[:16]}>"
                out["unbacked"].append(f"atoms[{i}]: no checker for kind {shown}")
                continue
            out["statements"].append(check(a, f"atoms[{i}]"))
        out["sha256"] = claim_hash(d)
        if out["statements"] and not out["unbacked"]:
            out["verdict"] = "reproduced"
        elif out["statements"]:
            out["verdict"] = "partial"
        else:
            out["verdict"] = "held"
    except Bad as e:
        out["errors"].append(str(e))
        out["statements"] = []
    except (UnicodeDecodeError, RecursionError, ValueError, OSError) as e:
        # hostile input must end in a verdict, not a crash
        out["errors"].append(f"unreadable claim: {type(e).__name__}: {str(e)[:120]}")
        out["statements"] = []
    return out


# ── PR intake ─────────────────────────────────────────────────────────────────

def guard(changes):
    """changes = [(status, path)] from git diff --name-status base...head.
    An intake PR may only ADD files inside new claims/<id>/ folders. A PR touching nothing
    under claims/ is a core PR: the guard steps aside and the owner's review governs it.
    A PR mixing the two is refused: a claim must not arrive with edits to its own judge."""
    touches_claims = any(p.startswith("claims/") for _, p in changes)
    if not touches_claims:
        return {"route": "core", "ok": True, "claims": [], "errors": [],
                "note": "no claims/ change: a core PR, governed by owner review, not by intake"}
    errors, claims = [], set()
    for status, p in changes:
        parts = p.split("/")
        if not p.startswith("claims/"):
            errors.append(f"{status} {p}: an intake PR may not touch anything outside claims/")
        elif status != "A":
            errors.append(f"{status} {p}: admitted claims are immutable; only additions are taken")
        elif len(parts) != 3 or parts[2] not in CLAIM_FILES:
            errors.append(f"A {p}: a claim is claims/<id>/claim.json + claim.md, nothing else")
        elif not CLAIM_ID.match(parts[1]):
            errors.append(f"A {p}: claim id must look like 0001-short-name")
        else:
            claims.add(parts[1])
    return {"route": "intake", "ok": not errors, "claims": sorted(claims), "errors": errors}


def git_changes(base, head, repo):
    # -z: raw NUL-separated paths. Without it git quotes non-ASCII paths ("claims/0500-\321\205/..."),
    # the quote hides the claims/ prefix, and the PR was routed as a core PR with nothing checked.
    r = subprocess.run(["git", "-C", str(repo), "diff", "--no-renames", "--name-status", "-z",
                        f"{base}...{head}"], capture_output=True, check=True)
    f = r.stdout.decode("utf-8", "surrogateescape").split("\0")
    return [(f[i], f[i + 1]) for i in range(0, len(f) - 1, 2)]


def intake(base, head, repo, files=None):
    # repo: where git diffs base...head. files: where the head's claims/ tree sits on disk (CI unpacks
    # only that tree, so a fork's other files never reach the runner). Default: the same folder.
    g = guard(git_changes(base, head, repo))
    report = {"guard": g, "claims": []}
    ok = g["ok"]
    if ok and g["route"] == "intake":
        for cid in g["claims"]:
            v = verify(Path(files or repo) / "claims" / cid)
            report["claims"].append(v)
            ok = ok and v["verdict"] in ("reproduced", "partial")
    return ok, report


def route(base, head, repo):
    """The route alone, for CI. A core PR is reported as core, never as a pass: the required
    check must be able to tell "intake verified" from "not an intake PR" (Brief 8, M1)."""
    g = guard(git_changes(base, head, repo))
    out, summary = os.environ.get("GITHUB_OUTPUT"), os.environ.get("GITHUB_STEP_SUMMARY")
    if out:
        with open(out, "a") as f:
            f.write(f"route={g['route']}\n")
    if summary:
        with open(summary, "a") as f:
            f.write(f"route: **{g['route']}**. " + (
                "Not checked by intake: owner review (CODEOWNERS) governs this PR.\n"
                if g["route"] == "core" else "The intake job verifies each new claim.\n"))
    return g


def admit(d):
    d = Path(d).resolve()
    if d.parent != (ROOT / "claims").resolve():
        raise SystemExit(f"not admitted: {d} is not a claims/<id> folder of this core ({ROOT})")
    v = verify(d)
    if v["verdict"] not in ("reproduced", "partial"):
        raise SystemExit(f"not admitted: {v['verdict']}: {v['errors'] or v['unbacked']}")
    rows = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()] if LEDGER.exists() else []
    if any(r["id"] == v["claim"] for r in rows):
        raise SystemExit(f"{v['claim']} is already in the ledger")
    defs = hashlib.sha256()
    for name in DEFINITIONS:
        defs.update(name.encode() + b"\0" + (ROOT / name).read_bytes() + b"\0")
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True)
    row = {"id": v["claim"], "sha256": v["sha256"], "level": "reproduced", "verdict": v["verdict"],
           "files_sha256": {n: hashlib.sha256((d / n).read_bytes()).hexdigest() for n in sorted(CLAIM_FILES)},
           "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "definitions_sha256": defs.hexdigest(),
           "core_commit": commit.stdout.strip() if commit.returncode == 0 else None,
           "python": sys.version.split()[0],
           "statements": v["statements"], "not_admitted": v["unbacked"],
           "prose_flags": v["prose_flags"],
           "admitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    if row["sha256"] != claim_hash(d):
        raise SystemExit("not admitted: the claim's bytes changed while it was being checked")
    LEDGER.parent.mkdir(exist_ok=True)
    with LEDGER.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


# ── selftest: plants must fire, valid cases must pass ─────────────────────────

PLANTS = HERE / "plants"
# folder -> (expected verdict, substring the reason must contain)
EXPECT = {
    "0001-valid-chain": ("reproduced", None),
    "0002-valid-sphere": ("reproduced", None),
    "0003-valid-face": ("reproduced", None),
    "0101-broken-link": ("rejected", "≠"),
    "0102-leaves-ball": ("rejected", "outside |w| ≤ 2"),
    "0103-wrong-level": ("rejected", "exactly n = 3"),
    "0104-face-cell": ("rejected", "half-open"),
    "0105-float-number": ("rejected", "must be strings"),
    "0106-unbacked-only": ("held", None),
    "0107-extra-file": ("rejected", "holds exactly"),
    "0108-zero-denominator": ("rejected", "zero denominator"),
    "0109-bad-utf8": ("rejected", "unreadable claim"),
}
GUARD_CASES = [
    ("clean add", [("A", "claims/0200-x/claim.json"), ("A", "claims/0200-x/claim.md")], "intake", True),
    ("core PR", [("M", "assimilate/woodlouse.py")], "core", True),
    ("claim + edit to judge", [("A", "claims/0200-x/claim.json"), ("A", "claims/0200-x/claim.md"),
                               ("M", "assimilate/woodlouse.py")], "intake", False),
    ("claim + new file outside", [("A", "claims/0200-x/claim.json"), ("A", "claims/0200-x/claim.md"),
                                  ("A", "assimilate/helper.py")], "intake", False),
    ("claim smuggled into ledger/", [("A", "claims/0200-x/claim.json"),
                                     ("A", "ledger/0200-x/claim.json")], "intake", False),
    ("claim + workflow edit", [("A", "claims/0200-x/claim.json"),
                               ("M", ".github/workflows/assimilate.yml")], "intake", False),
    ("edit an admitted claim", [("M", "claims/0001-valid-chain/claim.json")], "intake", False),
    ("delete a claim", [("D", "claims/0001-valid-chain/claim.md")], "intake", False),
    ("script in a claim", [("A", "claims/0200-x/run.py")], "intake", False),
    ("bad id", [("A", "claims/Evil/claim.json")], "intake", False),
]


def selftest():
    fails = 0
    for name, (want, reason) in EXPECT.items():
        v = verify(PLANTS / name)
        why = " ".join(v["errors"])
        ok = v["verdict"] == want and (reason is None or reason in why)
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name:22s} {v['verdict']:10s} {why[:90]}")
    # the prose of 0001 overreaches on purpose: it must be flagged and must not reach the ledger text
    v = verify(PLANTS / "0001-valid-chain")
    prose = (PLANTS / "0001-valid-chain" / "claim.md").read_text()
    leaked = any(s in " ".join(v["statements"]) for s in ("every", "proves", "NP"))
    ok = bool(v["prose_flags"]) and not leaked and "every n" in prose
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} prose overreach        flagged {v['prose_flags']}, ledger text clean: {not leaked}")
    for label, changes, route, want_ok in GUARD_CASES:
        g = guard(changes)
        ok = g["route"] == route and g["ok"] == want_ok
        fails += not ok
        print(f"{'ok  ' if ok else 'FAIL'} guard: {label:24s} route={g['route']} ok={g['ok']}")
    print(f"selftest: {'PASS' if not fails else f'{fails} FAILED'}")
    return fails == 0


def _flags(argv, valued, bare):
    """The options after the two shas. An unknown one is an error, never skipped: a workflow newer than this
    judge (PR #1, 2026-11-01: --files ignored, claim read from the wrong folder) must fail loudly."""
    out, i = {}, 4
    while i < len(argv):
        a = argv[i]
        if a in valued and i + 1 < len(argv):
            out[a] = argv[i + 1]; i += 2
        elif a in bare:
            out[a] = True; i += 1
        else:
            raise SystemExit(f"woodlouse {argv[1]}: unknown or incomplete option {a!r} (knows {sorted(valued | bare)})")
    return out


def main(argv):
    if len(argv) >= 2 and argv[1] == "verify" and len(argv) == 3:
        v = verify(argv[2])
        print(json.dumps(v, indent=2, ensure_ascii=False))
        return 0 if v["verdict"] in ("reproduced", "partial") else 1
    if len(argv) >= 4 and argv[1] == "route":
        o = _flags(argv, {"--repo"}, set())
        print(json.dumps(route(argv[2], argv[3], o.get("--repo", ".")), indent=2, ensure_ascii=False))
        return 0
    if len(argv) >= 4 and argv[1] == "intake":
        o = _flags(argv, {"--repo", "--files"}, {"--claims-only"})
        ok, report = intake(argv[2], argv[3], o.get("--repo", "."), o.get("--files"))
        if o.get("--claims-only") and report["guard"]["route"] != "intake":
            report["guard"]["errors"].append("--claims-only: a core PR has no claim to verify")
            ok = False
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if ok else 1
    if len(argv) == 3 and argv[1] == "admit":
        print(json.dumps(admit(argv[2]), indent=2, ensure_ascii=False))
        return 0
    if len(argv) == 2 and argv[1] == "selftest":
        return 0 if selftest() else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
