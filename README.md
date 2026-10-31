# brot-pnp-open

**Finding is expensive. Checking is cheap.** This repo is a small, open experiment built on that asymmetry, on a real fractal.

> **Status: pilot. Contributions are not open yet.** The intake that checks submissions is being tested against real forks. This line will change when it opens.

## The idea

P vs NP asks whether what is easy to check is also easy to find. We use that as a **metaphor**, not as a claim: nothing here says anything about the real P vs NP problem.

The fractal is the Bristorbrot set, built from Bristorian squaring in 3-space. We ask finite questions of it, of the form "does this small cell contain a point that reaches A after exactly n backward steps?" Answering one can take a long search. Checking an answer takes seconds, if it comes with a **certificate**: an exact chain of points for YES, or a cover that rules out every point for NO.

So the work splits cleanly:
- **you search**, with your own compute or AI credits, in your own fork, any way you like;
- **the core checks**, with its own code, in exact arithmetic. Only what checks is admitted, and nothing you write in prose is admitted.

## The map

This is the Bristorian B2 square, not a quaternion. Coordinates are (x, y, z):

```
B(x, y, z)   = (x² − y² − z²,  y(2x − z),  z(2x + y))
F_c(w)       = B(w) + c
```

Every real target t has **2 or 6** real square roots under B, never 4 (generic case). `blocks/bristor_sqrt_all` finds them quickly from a lookup table, but it is not a proof: near the cusps of the 6-root region it can return 2 roots as `complete` where there are 6 (its README, Caveats). The exact definitions (ball, cells, backward tree) are in `QUESTION.md`.

## What is here

| path | what |
|---|---|
| `QUESTION.md` | the definitions, and the first question we asked of this map |
| `ASSIMILATION.md` | how forks send results back, and why the core can trust them without trusting the sender |
| `claims/` | where a submitted claim lands, one folder per claim (format in `claims/README.md`) |
| `assimilate/woodlouse.py` | the checker CI runs on every claim, always the core's own copy, never the PR's |
| `ledger/` | the admitted results, written by the checker, never by contributors |
| `blocks/` | small shared code with conformance tests: the square and its Jacobian, a 3×3 solve, and all square roots |
| `briefs/proposed/` | how to propose a piece of work for an AI agent to run |

## Check a claim yourself

```bash
python3 assimilate/woodlouse.py selftest          # every planted bad claim must be caught
python3 assimilate/woodlouse.py verify claims/<id>
```

Standard library only. `cd blocks/<name> && node conform.mjs` runs a block's conformance check.

License: MIT.
