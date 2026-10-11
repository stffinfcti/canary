---
name: canary
description: Apply one task to many items safely — sample a few, learn the user's edits, roll out in waves, hold the odd ones.
argument-hint: "[N] \"task\" | resume"
allowed-tools:
  - read
  - edit
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
- `outbox/` — draft outputs for non-code tasks

Use the bundled `scripts/canary.py` (in `scripts/` next to this SKILL.md; stdlib only, run it with the user's working root as cwd) for bookkeeping. The script keeps score; you do all judgment.

| Command | Use |
|---|---|
| `canary.py init` | create `.canary/` |
| `canary.py list <dir> [-r]` | list the collection; `-r` for nested folders (code), skips `.git`, `node_modules`, etc. |
| `canary.py record <item> <sampled\|done\|approved\|held\|rejected> [--wave K] [--reason "..."]` | log a decision |
| `canary.py status [--total T] [--waves W]` | progress ticker |
| `canary.py held` | held items with reasons |

## Stay reversible

Nothing irreversible until the user approves the result.

- **Text / documents / messages:** write outputs to `.canary/outbox/`, never send or overwrite originals.
- **Code in a git repo:** work on a branch (`git switch -c canary/<short-task>`), edit files in place there, and show samples as diffs. Never commit to the user's current branch or push.
- **Renames / moves:** write the plan (`old → new`) to `.canary/outbox/plan.txt` and apply it only after the final report is approved.

## Protocol

### 1. Sample

- Run `canary.py init`, then `canary.py list <collection>` (add `-r` for code).
- Pick N items that are *varied* — different senders, lengths, file types, or patterns — never the first N.
- Do the task on exactly those N, reversibly (see above).
- `canary.py record <item> sampled` for each.

### 2. Stop and show

Present the N outputs compactly. Say: **"Fix any of these or say 'go'."**
Do not touch the remaining items until the user responds. This stop is the entire point.

### 3. Learn

For each user correction, extract a rule — one line, in the user's voice — and append it to `rules.md` citing the edit it came from, e.g. `- use logError(), never console.error  (your edit to users.js)`. Apply the correction to the sample itself, copy the final version of every sample into `golden/`, and `record <item> approved`. Golden samples + rules are now the spec; the original instruction is subordinate to them.

If the user says "go" with no edits, approve the samples as-is — `rules.md` stays empty, and that's fine.

### 4. Roll out in waves

Process the remaining items in waves of roughly 2N, then 4N, then the rest (cap ~25 per wave). After finishing each item, `record <item> done --wave K`. After every wave print the ticker with `canary.py status --total <collection size> --waves <planned waves>`: `🐤 8 done of 40 · 1 held · 3 sampled · 0 rejected · wave 2/3`.

### 5. Judge pass

Before writing output for an item, compare it against the golden samples and rules. **Hold the item instead of producing output** if any of these apply:

- The item is a different *kind* than every approved sample — different recipient type, formality level, or stakes.
- Doing it well needs facts or judgment the samples never established — money, dates, commitments, approvals.
- A rule in `rules.md` would be violated, or the item clearly needs an exception to one.

Leave the item untouched (for code: don't edit the file) and write `held/<item>.reason.md` — one line: *"I held this because ___. Approve, edit, or discard with /canary resume."* — and `record <item> held --reason "..."`. When unsure, hold: a hold is a question, a bad output is a broken promise.

### 6. Report

```
🐤 canary done — 37 done · 2 held · 3 sampled
held:
  07_principal.txt — formal note from your principal; your samples were casual, didn't want to guess.
  11_receipt.txt   — asks about reimbursement; your samples never touched money.
Run /canary resume to review held items.
```

## /canary resume

Run `canary.py held` and list the items with their reasons. For each, the user can approve your best attempt (`record <item> done`), give guidance (extract a new rule into `rules.md`, redo the item, then `record <item> done`), or discard it (`record <item> rejected`). Ask about each held item; don't batch-approve silently.

## What this is not

Not few-shot prompting: examples alone don't quarantine outliers, don't turn edits into explicit reusable rules, and don't stop for approval. The hold-back is the feature — it is what makes the other 40 items safe to automate.
