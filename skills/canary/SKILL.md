---
name: canary
description: Apply one task to many items safely — sample a few, learn the user's edits, roll out in waves, hold the odd ones.
argument-hint: "[N] \"task\" | resume"
allowed-tools:
  - read
  - edit
  - write
  - exec
  - grep
  - glob
triggers:
  - user
  - model
---

# /canary — try a few first, then do the rest

`/canary N "task"` means: do N items and stop, let the user approve or fix them, turn their fixes into rules, finish the rest in growing waves, and hold back anything that doesn't look like what they approved.

## Invocation

`/canary [N] "task over <collection>"` — N defaults to 3. The collection is a folder, list, or set the user names.
`/canary resume` — review held items after a run.

## State

All state lives in a `.canary/` folder at the working root:

- `ledger.jsonl` — one record per item: `{item, status, wave, reason}`
- `golden/` — the user's approved sample outputs. This is the spec.
- `rules.md` — rules learned from user edits, one per line, each citing the edit it came from
- `held/` — skipped items, each with a matching `*.reason.md`
- `outbox/` — draft outputs. Everything stays reversible: drafts, not sent emails; files, not mutations

Use the bundled `scripts/canary.py` (in `scripts/` next to this SKILL.md; stdlib only, run it with the user's working root as cwd) for bookkeeping: `init`, `list`, `record`, `status`, `held`. The script keeps score; you do all judgment.

## Protocol

### 1. Sample

- Run `canary.py init`, then `canary.py list <collection>`.
- Pick N items that are *varied* — different senders, lengths, and kinds — never the first N.
- Do the task on exactly those N. Write each output to `.canary/outbox/`.
- `canary.py record <item> sampled` for each.

### 2. Stop and show

Present the N outputs compactly. Say: **"Fix any of these or say 'go'."**
Do not touch the remaining items until the user responds. This stop is the entire point.

### 3. Learn

For each user correction, extract a rule — one line, in the user's voice — and append it to `rules.md` citing the edit it came from. Copy the user's final version of every sample into `golden/`. Golden samples + rules are now the spec; the original instruction is subordinate to them.

### 4. Roll out in waves

Process the remaining items in waves of roughly 2N, then 4N, then the rest (cap ~25 per wave). Record each item's wave in the ledger. After every wave print the ticker from `canary.py status`: `🐤 8 done · 1 held · wave 2/3`.

### 5. Judge pass

Before writing output for an item, compare it against the golden samples and rules. **Hold the item instead of producing output** if any of these apply:

- The item is a different *kind* than every approved sample — different recipient type, formality level, or stakes.
- Doing it well needs facts or judgment the samples never established — money, dates, commitments, approvals.
- A rule in `rules.md` would be violated, or the item clearly needs an exception to one.

Write the item to `held/` plus `<item>.reason.md` — one line: *"I held this because ___. Approve, edit, or discard with /canary resume."* — and `record <item> held --reason "..."`. When unsure, hold: a hold is a question, a bad output is a broken promise.

### 6. Report

```
🐤 canary done — 37 done · 2 held · 3 sampled
held:
  07_principal.txt — formal note from your principal; your samples were casual, didn't want to guess.
  11_receipt.txt   — asks about reimbursement; your samples never touched money.
Run /canary resume to review held items.
```

## /canary resume

List held items with their reasons. For each, the user can approve the draft as-is (mark done), edit it (extract a new rule into `rules.md`, then regenerate), or discard it (mark rejected). Ask about each held item; don't batch-approve silently.

## What this is not

Not few-shot prompting: examples alone don't quarantine outliers, don't turn edits into explicit reusable rules, and don't stop for approval. The hold-back is the feature — it is what makes the other 40 items safe to automate.
