# ledger/

`ledger.jsonl`: one row per admitted claim, appended by the core with `woodlouse.py admit` after a merge. Contributors never edit it.

Each row holds the claim id and the sha256 of its two files, its level, the sha256 of the verifier that checked it, the **statements the woodlouse wrote** from the verified atoms, the atoms it did not admit, the prose flags, and the time. The contributor's prose is never copied here.

Levels: `reproduced` (the core's own verifier passed every admitted atom) → `audited` (a fresh session re-derived it under a brief) → `cited` (another claim builds on it). A row records a level and the instruments behind it, never "true".
