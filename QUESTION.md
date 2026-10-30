# The question contract

## Objects

- **Map:** F_c(w) = B(w) + c, with B as in README.md. w is in ℝ³.
- **Backward tree from A:** level 0 is {A}. Level n is every w in the box R with F_c(w) in level n−1. Each point has 2 or 6 real preimages, so the tree branches.
- **Box R:** the ball |w| ≤ 2. A branch that leaves R is cut and not continued.
- **Cells at resolution ε:** the grid cell of w is (⌊x/ε⌋, ⌊y/ε⌋, ⌊z/ε⌋).

## Quantities, per step n

1. **raw(n):** the number of surviving branches at level n, counted with multiplicity, as if the tree were never merged.
2. **cells(n, ε):** the number of distinct ε-cells that level n occupies. When two branches land in the same cell, keep one representative and add their multiplicities. That is the state a cell-by-cell search would carry.

## Fixed cases

- A = (0.3, 0.2, 0.1)
- c ∈ { (0,0,0), (−1,0,0), (0.3,0,0) }, plus **two c of your own choosing**, with a sentence on why you chose them.
- ε ∈ { 0.08, 0.04, 0.02, 0.01 }, and 0.005 if it fits.
- n from 1 to at least 30.

## What counts as an answer

For each (c, ε):

- whether cells(n, ε) **levels off** in n, and from which n;
- if it levels off, how the level scales with ε (fit cells ≈ K·ε^(−D) and report D with its spread);
- the growth rate of raw(n) per step.

Then a verdict in one paragraph: **is the backward search cost exponential in the number of steps, or in the bits of precision?** A null result or a mixed one is a full answer, as long as it is stated plainly.

## Controls you must include

- **A control that can fire.** Name the result that would show your cell count is wrong. Build a case where you know the answer, and show your code gets it. Use the case c = (0,0,0), A = (0.3, 0, 0). Every level n ≥ 1 then has **exactly 2** tree points on the real axis (y = z = 0), at x = ±0.3^(1/2ⁿ). The negative one's 6 preimages all leave the axis. Your code must find exactly these.
- **Root completeness.** If you use your own inverse, check its root counts (2 or 6) against `blocks/bristor_sqrt_all` on at least 1000 random targets. If you use the block, check it against `oracle_elim.py` on at least 200.
- **Merge sensitivity.** Shift the grid by ε/2 in each axis and report how much cells(n, ε) changes.

## Out of scope

Claims about P vs NP itself, NP-hardness, or any algorithm lower bound. A finite timing curve is evidence, not a proof.
