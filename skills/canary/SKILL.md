---
name: canary
description: Do one task across many items safely. Sample a few, learn from the user's edits, finish the rest in batches, and hold back items that don't match.
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

# /canary

`/canary N "task"`: do the task on N items and stop. Let the user approve or fix them, save their fixes as rules, finish the remaining items in growing batches, and hold back any item that doesn't fit what they approved.

## Invocation

- `/canary [N] "task over <collection>"`. N defaults to 3. The collection is a folder, a list, or any set of items the user names.
- `/canary resume` reviews held items after a run.

## State

Everything goes in `.canary/` in the user's working folder:

- `ledger.jsonl`: one line per decision, `{item, status, wave, reason}`
- `golden/`: final versions of the approved samples
- `rules.md`: one rule per line, each noting which edit it came from
- `held/`: one `<item>.reason.md` per held item
- `outbox/`: drafts for anything that isn't code

`scripts/canary.py` (next to this file, standard library only) does the bookkeeping. Run it with the user's working folder as the current directory. It only records what happened; you make every judgment call.

| Command | Use |
|---|---|
| `canary.py init` | create `.canary/` |
| `canary.py list <dir> [-r]` | list the collection; `-r` includes subfolders and skips `.git`, `node_modules`, etc. |
| `canary.py record <item> <sampled\|done\|approved\|held\|rejected> [--wave K] [--reason "..."]` | log a decision |
| `canary.py status [--total T] [--waves W]` | print progress |
| `canary.py held` | list held items and reasons |

## Keep it undoable

Don't do anything permanent until the user has approved the result.

- Text, documents, messages: write to `.canary/outbox/`. Don't send anything or overwrite originals.
- Code in a git repo: create a branch (`git switch -c canary/<short-task>`), edit files there, and show samples as diffs. Don't commit to the user's current branch and don't push.
- Renames and moves: write the plan (`old → new`) to `.canary/outbox/plan.txt` and apply it only after the user approves the final report.

## Steps

### 1. Sample

- Run `canary.py init`, then `canary.py list <collection>` (with `-r` for code).
- Pick N items that differ from each other in sender, length, file type, or pattern. Don't take the first N.
- Do the task on those N items only.
- Run `canary.py record <item> sampled` for each.

### 2. Stop

Show the N results briefly and ask: "Fix any of these or say 'go'."
Don't start on the other items until the user answers.

### 3. Learn

For each correction, write a one-line rule to `rules.md` in the user's words and note which edit it came from, for example `- use logError(), never console.error  (your edit to users.js)`. Apply the correction to the sample, copy every final sample into `golden/`, and run `record <item> approved`. From here on, the golden samples and rules take priority over the original instruction.

If the user says "go" without editing anything, approve the samples as they are. `rules.md` can stay empty.

### 4. Run in batches

Do the remaining items in batches of about 2N, then 4N, then the rest, with at most about 25 per batch. After each item, run `record <item> done --wave K`. After each batch, show progress with `canary.py status --total <collection size> --waves <planned batches>`.

### 5. Decide what to hold

Before doing an item, compare it to the golden samples and rules. Hold it instead if any of these are true:

- It's a different kind of item from every approved sample: a different type of recipient, level of formality, or level of stakes.
- Doing it well needs facts or decisions the samples never covered, such as money, dates, commitments, or approvals.
- It would break a rule in `rules.md`, or clearly needs an exception to one.

Leave a held item unchanged (for code, don't edit the file). Write `held/<item>.reason.md` with one line: "I held this because ___. Approve, edit, or discard with /canary resume." Then run `record <item> held --reason "..."`. If you're unsure, hold it; the user can approve it in seconds, but a wrong result can slip through unnoticed.

### 6. Report

```
🐤 canary done: 37 done · 2 held · 3 sampled
held:
  07_principal.txt  formal note from your principal; your samples were casual, didn't want to guess.
  11_receipt.txt    asks about reimbursement; your samples never touched money.
Run /canary resume to review held items.
```

## /canary resume

Run `canary.py held` and show each item with its reason. For each one the user can:

- approve your best attempt: do it, then `record <item> done`
- give guidance: add a rule to `rules.md`, do the item, then `record <item> done`
- skip it: `record <item> rejected`

Ask about each item separately. Don't approve them in bulk.
