# claims/

Where brotettes (forks) send results back. See `ASSIMILATION.md`.

A claim is one new folder, `claims/<id>/`, with exactly two files:

- `claim.json`: `{"atoms": [ ... ]}`. Each atom is one statement plus its certificate. Every coordinate, `c`, `A` and `eps` is a **string** holding an exact rational (`"3/10"`, `"-0.25"`: ASCII digits, optional leading `-`, at most 200 characters); JSON numbers are refused there. `n` (1 to 64) and the three `cell.index` entries are JSON **integers**. Unknown fields are refused. A `kind` is a short lowercase name.
- `claim.md`: your prose. The reviewer reads it. It is **not** admitted and never quoted in the ledger.

`<id>` is four digits and a short name: `0042-level-5-cell`.

**Atom kinds the woodlouse can check today**

| kind | fields | statement admitted |
|---|---|---|
| `member` | `c`, `A`, `n`, `chain` = [w_n, …, w_1], optional `cell` = {`eps`, `index`} | w_n is a level-n point of the backward tree from A under F_c (each w_k in \|w\| ≤ 2, F_c(w_k) = w_{k−1} exactly, w_0 = A); with `cell`, level n meets that half-open ε-cell |

Any other kind is kept as **unbacked**: it is listed, not admitted, until the core has a checker for it.

**Rules the intake enforces**: only additions, only inside a new `claims/<id>/`, only those two files, each ≤ 64 KiB. A PR that adds a claim and also edits anything else is refused. Admitted claims are immutable: a correction is a new claim.

Check your own claim before opening the PR:

```bash
python3 assimilate/woodlouse.py verify claims/0042-level-5-cell
```
