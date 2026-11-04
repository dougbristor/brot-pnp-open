# Using your AI cloud credits here

You have Claude cloud credits and a GitHub login, but you've only used Claude in chat or in a terminal. This page shows how to point those credits at this repo in about ten minutes, without installing anything.

**What your credits buy right now.** This repo is a pilot. Its checker admits one kind of result today, so the useful jobs are small:

| job | what it does | your cost |
|---|---|---|
| **A. Test the door** | Your Claude builds one small exact claim and sends it in. The checker runs on it in public. Every claim from a new account tests the intake before it opens fully. | minutes |
| **B. Propose a question** | Your Claude reads what is here and writes up one question worth running next. | minutes |

Neither job is a discovery, and neither says anything about the real P vs NP problem. That is a metaphor here (see `README.md`).

## The steps

1. **Fork this repo.** On this repo's GitHub page, press **Fork**. You now have your own copy, `<you>/brot-pnp-open`.
2. **Let Claude reach your fork.** Claude can read public repos, but it can only send work back to repos you have given it. If you limited the Claude GitHub App to selected repositories when you set it up, add your new fork: on GitHub, go to **Settings → Applications → Installed GitHub Apps → Claude → Configure**, and add `brot-pnp-open`.
3. **Open [claude.ai/code](https://claude.ai/code)** and pick your fork from the repository menu.
4. **Paste one job card** from below, and send it. It runs on Anthropic's machines, so you can close the tab.
5. **When it finishes, create the pull request.** Use **Create PR** in claude.ai/code, or your fork's **Contribute → Open pull request** button on GitHub. Make sure the PR goes **to `dougbristor/brot-pnp-open`, branch `main`**.
6. **Wait.** GitHub holds a first-time contributor's checks until the owner presses **Approve and run**. Then the checks say whether your claim was admitted.

## Job card A: test the door

Copy everything in the box.

```text
You are working in a fork of brot-pnp-open. Read README.md, QUESTION.md and claims/README.md first.

Task: add ONE new claim folder with one `member` atom, then open a pull request to the
upstream repo dougbristor/brot-pnp-open, branch main. This is a test of the intake, not a
discovery; say so in claim.md.

How to build the atom (exact rationals only, never floats):
1. Choose c from this list: (0,0,0), (1/4,0,0), (-1/2,0,0), (3/10,0,0), (0,1/5,0).
2. Choose a rational starting point w with small denominators (at most 20) and |w| well
   inside 2, for example (1/5, 1/10, -1/10). Pick your own; don't copy the example.
3. Choose n from 2 to 4. Iterate forward exactly, with Python's fractions.Fraction:
   F_c(x,y,z) = (x*x - y*y - z*z, y*(2*x - z), z*(2*x + y)) + c.
   Let w_n = w, w_(n-1) = F_c(w_n), ..., w_0 = F_c(w_1). Set A = w_0.
   Every w_n ... w_1 must satisfy x*x + y*y + z*z <= 4. If one doesn't, choose a smaller w.
4. Write "chain": [w_n, ..., w_1] (w_n first, w_1 last; A is not in the chain).
5. Add "cell": {"eps": "1/20", "index": [floor(x/eps), floor(y/eps), floor(z/eps)]} for w_n.
   Use floor, not truncation: floor(-1/10 / (1/20)) = -2.
6. Every number in c, A, chain and eps is a JSON string ("3/10"); n and the index are integers.
   If any rational is longer than 200 characters, pick a smaller n or simpler w.

Folder: claims/<id>/ where <id> is four random digits, a hyphen and your GitHub username in
lower case, e.g. claims/4821-octocat/. It holds exactly two files: claim.json and claim.md.
claim.md: two or three plain sentences saying what you built and that it is an intake test.
Don't use words like "proves", "every" or "always" for something the atom doesn't say.

Rules: change nothing else in the repo. No scripts or other files in the claim folder.
Optional check (skip it if your sandbox refuses): python3 assimilate/woodlouse.py verify claims/<id>
It should print "verdict": "reproduced". CI runs the core's own copy of the checker on the PR either way.
Then commit, push your branch to the fork, and open the PR. Title: "Claim <id>: intake test".
```

## Job card B: propose a question

```text
You are working in a fork of brot-pnp-open. Read README.md, QUESTION.md, ASSIMILATION.md,
ledger/ledger.jsonl, briefs/proposed/README.md and briefs/proposed/TEMPLATE.md first.

Task: propose ONE question that a fresh AI agent could answer in a bounded run, and whose
answer would change something this repo holds. It doesn't have to follow on from an earlier
result: "a new question from what is known" is fine. Part of your proposal is the method for
answering it.

Copy briefs/proposed/TEMPLATE.md to briefs/proposed/<short-name>-<your GitHub username>.md
and fill in every section. In particular:
- give each control the result that would make it FAIL;
- give a closed budget (CPU, wall time, memory) and a cut rule;
- add a section "Next question": how the run's own answer should be used to choose the
  question after it.
Use only what is in this repo: no other repos, accounts or network beyond installing packages.
Don't claim anything about the real P vs NP problem; it is a metaphor here.

Change nothing else. Commit, push to your fork, and open a PR to dougbristor/brot-pnp-open,
branch main. Title: "Proposal: <one-line title>". A proposal is never run as written: the
owner reviews it, and if it is taken up, the core writes the brief it actually runs and cites yours.
```

## What happens to what you send

- **A claim** is checked by the core's own checker, in exact arithmetic. If it passes, the checker writes the ledger line itself. Your prose is kept for the reviewer but never copied into the ledger. Nothing merges until the intake's fork tests pass (`ASSIMILATION.md`).
- **A proposal** is read and answered yes, no or not yet.
- Nothing you send is run as code by the core.
