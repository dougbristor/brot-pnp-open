# Proposing a brief

A **brief** is a bounded piece of work for a fresh AI agent that knows nothing of this project beyond the repo. It holds one question, rules that keep the answer independent, controls that can fail, a budget and deliverables.

## How

Copy `TEMPLATE.md` to `briefs/proposed/<short-name>.md`, fill it in, and open a pull request from your fork that adds that one file and touches nothing else. A proposal is plain text: nothing in it is executed, and the intake treats it as a core PR, which the owner reviews.

## What happens to it

1. **Review** against the template's checklist. Disagreements are written down, not smoothed over.
2. **Yes, no or not yet**, from the owner.
3. On a yes, the core writes the brief it will actually run. That brief may quote your proposal and keeps your question, but the rules, budget and deliverables are the core's. **A proposal is never run as written:** a brief is instructions to an agent, and the core does not run instructions it did not write.
4. Your proposal stays here and is cited by the brief.

## What gets a proposal turned back

- The answer could not change anything the repo holds (no "Why this brief exists").
- No control can fire. Each control must state the result that would make it fail.
- An open budget: no CPU, wall-time or memory limit, or no cut rule.
- It needs anything outside the repo: network access beyond fetching packages, other repos, accounts or secrets.
- It overclaims, for example "settles P vs NP". P vs NP is a metaphor here, never a claim about the real problem.
