# Proposal: <one-line title>

*Proposed by <who: a person, an AI agent, or both>, <date>. Builds on <briefs or results it follows>, or nothing.*

## The question

One question that a finished run answers. If it has parts, number them.

## Why this brief exists

What we hold now, and how the answer could change it. Name the result, file or claim it tests.

## Starting state

- The commit or branch the run starts from, and the branch it pushes to.
- Branches it must **not** push to.

## Independence rule

- What the run may read and run.
- What it must **not** read until its verdict is committed, and why. Usually the code whose answer it checks, and the earlier answers.
- What it must build on its own, and freeze before it opens anything else.
- If the independence cannot be met (for example, only the author's model family is available), say so, and record the run's prior exposure.

## Steps

Numbered. Put any freeze (strategies, budgets, samples) **before** the principal run, and commit it.

## Controls that can fire

For each control, give the result that would make it **fail**. A control that cannot fail is not a control.

- Known answers it must reproduce, chosen without looking at them.
- Plants: a planted defect that must be caught.
- A valid case that must pass. A checker that rejects everything is not a pass.

## Not in this run (needs a separate go)

Legs the question needs but this run must not do, such as a remote test or an external fork. Name them here; never cut them silently.

## Deliverables

- `results/<dir>/REPORT.md`, with the verdict first, and ending with "What was not checked" and "What would make me distrust this".
- `results/<dir>/answers.csv`, with columns `key,answer`, so that a repeat run can be compared.
- One command, `bash results/<dir>/run_all.sh`, that reproduces the verdict.
- In REPORT.md, the hashes actually run, beside the frozen ones.

## Budget

CPU only, at most N workers, at most M minutes of wall time per command, within G GiB, and T CPU-hours in total. If something does not fit, cut it, record the cut, and do not lower the bar.

## Reviewer checklist (the reviewer fills this in)

- [ ] The question is answerable, and the answer could change what we hold.
- [ ] Every control states the result that would make it fire.
- [ ] Freezes come before the first principal run.
- [ ] The budget is closed, and there is a cut rule.
- [ ] It needs nothing outside the repo, or each outside leg is named under "Not in this run".
- [ ] Nothing in it overclaims (P vs NP is a metaphor here).
- [ ] The brief that runs is written by the core, not copied from the proposal.
