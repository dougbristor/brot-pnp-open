# Assimilation: forks that feed the core

*Design note, October 2026. The intake below is in pilot: it has been audited once and is now being tested against real forks.*

## The aim

The brot is a concept and a construction at once, and other explorers will want to explore it their own way. We want them to **fork and evolve independently**, and we want what they find to **feed a central core** that stays the lead authority. Every new fork should start from the current core, so each one is more evolved than the last.

The danger is in the feeding. **A persuasive argument can be a deceptive overreach.** If the core takes in arguments, it takes in whatever argues best. So the core needs an immune system as well as a mouth.

## The shape, in git

| part | what it is | in git |
|---|---|---|
| **brot-core** | the definitions (README, QUESTION.md), the verifier, and the ledger of admitted results | the upstream repo; its owner merges |
| **brotette** | any fork, exploring as it likes | an ordinary fork; `git fetch upstream && git rebase` keeps it on the current core |
| **claim** | a result sent back | a PR that adds one folder, `claims/<id>/` (format in `claims/README.md`) |
| **woodlice** | the assimilating compute: it chops a claim into atoms, checks each one, and feeds only the verified ones to the ledger | `assimilate/woodlouse.py`, run by CI from the core's copy |
| **fruit** | what the core holds and grows from | `ledger/ledger.jsonl` |

This intake takes in *constructions*, not words: **a submission is a body to test, never evidence.**

## The immune system

1. **The certificate defines the claim; the prose is a hypothesis.** A claim's atoms are machine-readable statements, each carrying a certificate. The woodlouse checks them in exact arithmetic and then **writes the ledger text itself**, from the atoms it verified. The contributor's prose is kept for the reviewer and flagged where it reaches past the atoms ("every", "proves", "P vs NP"), but it has no route into the ledger. A brilliant paragraph that the atoms do not carry is simply not admitted.
2. **The judge is the core's, never the claim's.** CI runs `pull_request_target`, which uses the workflow **and the woodlouse from the base branch**. The PR's files are read as data and nothing in them is executed. A claim PR that also edits anything else (the woodlouse, the workflow, the ledger, an earlier claim) is refused outright.
   The rule is never to **execute PR code** under `pull_request_target`, not to avoid it: with plain `pull_request`, a PR could edit its own judge. Only the default branch may judge, so a PR cannot choose a base branch that carries a different woodlouse.
3. **Converge the store, diverge the method.** Contributors share findings, not verifiers. The core checks with its own instrument, so a contributor's mistake and the core's are not the same mistake.
4. **Controls that can fire.** `woodlouse.py selftest` runs every CI job. It plants bad claims (a broken link, a point outside the ball, the wrong level, a half-open face misassigned, a float smuggled in for a rational, an unbacked statement, a script in the folder, a zero denominator, non-UTF-8 prose) and bad PR shapes (an edit to the judge, a workflow edit, an edit to an admitted claim, a claim smuggled into `ledger/`), and it fails unless every plant is caught and every valid case passes. The valid cases include a point exactly on |w| = 2 and one exactly on a cell face.
5. **Levels, not "true".** A ledger row says *reproduced* (the core's verifier passed it), later *audited* (a fresh session re-derived it under a brief), later *cited*. Each row also records the hash of the verifier that checked it, so a verifier bug found later says exactly which rows to re-check.
6. **Immutability.** An admitted claim never changes. A correction is a new claim that cites the old one.

## Who pays for what: P vs NP as economics

An earlier run of this project measured the asymmetry this rests on: **finding** a certificate is expensive and **checking** it is cheap (for YES certificates: a median 0.09 CPU-s to find and 0.013 s to check). So:

- **brotettes pay for search**, with their own cloud credits or hardware. That is where the cost is, and it is theirs to spend.
- **the core pays only for the woodlice**: CI checks take seconds, and GitHub Actions is free on public repos.

## Not built yet

- **One atom kind.** `member` is the exact YES certificate. The chain (YES) and cover (NO) formats used for cell questions are the next kinds.
- **NO claims** need covers, which can be large. How expensive they are to check is itself an open question.
- **A real fork from another account** has not yet been run through the intake. That test comes before contributions open.
- **Prose flags are a word list.** They prompt the reviewer; they are not a detector, and a careful overreach avoids the words. The real defence is rule 1: prose is never admitted.
