# 🐤 /canary — try a few first, then do the rest

```
/canary 3 "draft replies to all of these"
```

The AI does 3 items and **stops**. You approve or fix them. Your fixes become the rules. It finishes the rest in growing waves — and **holds back anything that doesn't look like what you approved.**

```
🐤 canary done — 9 done · 2 held · 3 sampled
held:
  07_principal_openhouse.txt — formal note from your principal; your samples were casual, didn't want to guess.
  11_riley_receipt.txt       — asks about reimbursement; your samples never touched money.
Run /canary resume to review held items.
```

## The problem

Ask AI to do one task to many things — reply to 50 emails, fix 40 files, rename 300 photos — and you have two bad options: check all of them yourself (defeats the point), or trust it blindly (every item wrong the same way). Everyone already works around this by hand: *"do 3, show me, then do the rest."* /canary gives that habit a name and a handle.

## How it works

1. **Sample** — picks N *varied* items (not the first N) and does them reversibly: drafts, not sent emails.
2. **Approve or edit** — you fix the samples.
3. **Learn** — your edits become explicit rules in `.canary/rules.md`.
4. **Roll out in waves** — remaining items in growing batches, each output judged against your approved samples.
5. **Hold the odd ones** — anything unlike your examples is skipped with a one-line reason.
6. **Report** — done / held / why. `/canary resume` reviews the held items.

## Why it's not just few-shot prompting

Few-shot gives examples. /canary **stops for approval**, turns your *edits* into diff-able rules, ships in waves — and **quarantines outliers** with reasons instead of guessing. The hold-back is the feature: it's what makes the other 40 items safe to automate.

## Install

It's one folder — `skills/canary/` — in the open Agent Skills format. No dependencies beyond Python 3.

| Agent | Setup |
|---|---|
| Claude Code | `claude plugin add` this repo, or copy `skills/canary/` into `~/.claude/skills/` |
| Devin | copy `skills/canary/` into `.devin/skills/` in your project |
| Codex / other agents | copy `skills/canary/` into your skills dir, or paste `SKILL.md` as an instruction file |
| No skill support | paste `SKILL.md` into the chat, then run `python3 skills/canary/scripts/canary.py init` in your working dir |

## 60-second demo

```bash
cd canary                       # this repo
# open your agent here, then:

/canary 3 "draft replies to everything in demo/inbox — keep them short and casual, sign off – Ricardo"
```

1. It drafts 3 varied emails into `.canary/outbox/` and stops.
2. Edit one draft — e.g. fix the sign-off. Say "go."
3. It drafts the rest in your style, then reports: **9 done · 2 held** — the principal's formal request and a reimbursement question, each with a one-line reason.
4. `/canary resume` to review the held ones.

## Architecture

```
canary/
├── .claude-plugin/plugin.json   # Claude Code plugin manifest
├── commands/canary.md           # /canary slash command
├── skills/canary/
│   ├── SKILL.md                 # the protocol — the whole idea lives here
│   └── scripts/canary.py        # bookkeeping: ledger, waves, holds (stdlib only)
└── demo/inbox/                  # 12 club emails, 2 engineered to be held
```

State lives in `.canary/` next to your work: `golden/` (approved samples), `rules.md` (learned rules), `held/` (quarantine + reasons), `outbox/` (drafts), `ledger.jsonl` (every decision). The script keeps score; the agent does all judgment — so the skill ports to any agent that can read a markdown file.

## Roadmap

Git-worktree sampling for code edits, Gmail drafts adapter, wave-size tuning, confidence thresholds for the judge pass.

Built at EvoHacks 2026 — theme: *AI for Automation*. /canary automates the part of automation nobody trusts.
