# 🐤 /canary — try a few first, then do the rest

```
/canary 3 "draft replies to all of these"
```

The AI does 3 items and **stops**. You approve or fix them. Your fixes become the rules. It finishes the rest in growing waves — and **holds back anything that doesn't look like what you approved.**

```
🐤 canary done — 7 done · 2 held · 3 sampled
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

## Not just email

```
/canary 3 "add error handling to every route in src/api"
```

It works on a git branch, shows 3 varied routes as diffs, and stops. You reply *"use logError(), not console.error. then go"* — that becomes a rule in `.canary/rules.md`, applied to the other 21 routes. `src/api/legacy/payments.js` is held: it uses callbacks, and none of your samples covered that.

Same verb, any batch: rename 300 photos (holds the screenshots), format 40 citations (holds sources with no author), normalize 500 spreadsheet rows (holds cells with two dates).

## Why it's not just few-shot prompting

Few-shot gives examples. /canary **stops for approval**, turns your *edits* into diff-able rules, ships in waves — and **quarantines outliers** with reasons instead of guessing. The hold-back is the feature: it's what makes the other 40 items safe to automate.

## Install

It's one folder — `skills/canary/` — in the open Agent Skills format. No dependencies beyond Python 3.

| Agent | Setup |
|---|---|
| Claude Code | `/plugin marketplace add stffinfcti/canary` then `/plugin install canary@canary` — or copy `skills/canary/` into `~/.claude/skills/` |
| Devin | copy `skills/canary/` into `.devin/skills/` (project) or `~/.config/devin/skills/` (global) |
| Codex / other agents | copy `skills/canary/` into your agent's skills dir (`.agents/skills/` works for many) |
| No skill support | paste `SKILL.md` into the chat; the agent runs `scripts/canary.py` for bookkeeping |

As a Claude Code plugin the command is namespaced (`/canary:canary`); installed as a plain skill it's `/canary`.

## 60-second demo

```bash
cd canary                       # this repo
# open your agent here, then:

/canary 3 "draft replies to everything in demo/inbox — keep them short and casual, sign off – Ricardo"
```

1. It drafts 3 varied emails into `.canary/outbox/` and stops.
2. Edit one draft — e.g. fix the sign-off. Say "go."
3. It drafts the rest in your style, then reports: **7 done · 2 held** — the principal's formal request and a reimbursement question, each with a one-line reason.
4. `/canary resume` to review the held ones.

## Architecture

```
canary/
├── .claude-plugin/
│   ├── plugin.json              # Claude Code plugin manifest
│   └── marketplace.json         # lets this repo be added as a marketplace
├── skills/canary/
│   ├── SKILL.md                 # the protocol — the whole idea lives here
│   └── scripts/canary.py        # bookkeeping: ledger, waves, holds (stdlib only)
├── demo/inbox/                  # 12 club emails, 2 engineered to be held
└── tests/                       # CLI tests
```

State lives in `.canary/` next to your work: `golden/` (approved samples), `rules.md` (learned rules), `held/` (reasons for each held item), `outbox/` (drafts), `ledger.jsonl` (every decision — an audit trail). The script keeps score; the agent does all judgment — so the skill ports to any agent that can read a markdown file.

```
canary.py init
canary.py list <dir> [-r]                      # -r for code: nested files, skips .git / node_modules
canary.py record <item> <sampled|done|approved|held|rejected> [--wave K] [--reason "..."]
canary.py status [--total T] [--waves W]       # 🐤 8 done of 40 · 1 held · 3 sampled · 0 rejected · wave 2/3
canary.py held
```

Run the tests with `python3 -m unittest discover -s tests` (Python 3.9+, no dependencies).

## Roadmap

Gmail drafts adapter, wave-size tuning, confidence thresholds for the judge pass, `/canary undo` for a whole run.

Built at EvoHacks 2026 — theme: *AI for Automation*. /canary automates the part of automation nobody trusts.
