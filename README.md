# /canary

Try a few first, then do the rest.

```
/canary 3 "draft replies to all of these"
```

The agent does 3 items and stops. You approve them or fix them, and your fixes get saved as rules. Then it does the rest in batches, and it skips anything that doesn't look like the samples you approved, with a short note saying why.

```
🐤 canary done: 7 done · 2 held · 3 sampled
held:
  07_principal_openhouse.txt  formal note from your principal; your samples were casual, didn't want to guess.
  11_riley_receipt.txt        asks about reimbursement; your samples never touched money.
Run /canary resume to review held items.
```

## Why

When you ask an AI to do the same thing to a lot of items (reply to 50 emails, fix 40 files, rename 300 photos), you either check every result yourself or you trust it and hope it understood you. If it didn't, every item comes out wrong in the same way.

Most people already handle this by saying "do 3, show me, then do the rest." /canary turns that into a command, and adds the part people usually skip: it holds back the items your examples didn't cover instead of guessing.

## How it works

1. Sample: picks N items that differ from each other (not just the first N) and does them in a way you can undo, like drafts instead of sent emails.
2. Review: you approve or edit the samples.
3. Learn: each edit becomes a one-line rule in `.canary/rules.md`.
4. Batches: the remaining items run in growing batches, each checked against your approved samples and rules.
5. Hold: anything that doesn't match is left alone, with a one-line reason.
6. Report: what got done, what got held, and why. `/canary resume` walks through the held items.

## Code works too

```
/canary 3 "add error handling to every route in src/api"
```

The agent switches to a new git branch, shows 3 different routes as diffs, and stops. You reply "use logError(), not console.error. then go". That becomes a rule and gets applied to the other 21 routes. `src/api/legacy/payments.js` is held because it uses callbacks and none of your samples did.

Other things it's useful for: renaming 300 photos (holds the screenshots), formatting 40 citations (holds sources with no author), cleaning up 500 spreadsheet rows (holds cells with two dates in them).

## How this differs from giving examples

Showing an AI a few examples helps, but it still runs everything in one go and fills gaps with guesses. /canary stops for your review, writes your edits down as rules you can read and change, runs in batches, and holds the items it isn't sure about.

## Install

The skill is one folder, `skills/canary/`, in the Agent Skills format. It needs Python 3.9 or newer and nothing else.

| Agent | Setup |
|---|---|
| Claude Code | `/plugin marketplace add stffinfcti/canary`, then `/plugin install canary@canary`. Or copy `skills/canary/` into `~/.claude/skills/`. |
| Devin | Copy `skills/canary/` into `.devin/skills/` (one project) or `~/.config/devin/skills/` (all projects). |
| Codex and others | Copy `skills/canary/` into your agent's skills folder. `.agents/skills/` works for many. |
| No skill support | Paste `SKILL.md` into the chat. The agent can still run `scripts/canary.py`. |

Installed as a Claude Code plugin, the command is `/canary:canary`. Installed as a plain skill, it's `/canary`.

## Try it

Open your agent in this repo and run:

```
/canary 3 "draft replies to everything in demo/inbox, keep them short and casual, sign off – Ricardo"
```

1. It drafts 3 replies into `.canary/outbox/` and stops.
2. Edit one if you want (the sign-off, say), then reply "go".
3. It drafts the other 9 and reports 7 done and 2 held: the principal's formal invitation and a question about getting reimbursed.
4. Run `/canary resume` to deal with those two.

## Layout

```
.claude-plugin/
  plugin.json          Claude Code plugin manifest
  marketplace.json     lets Claude Code install from this repo
skills/canary/
  SKILL.md             instructions the agent follows
  scripts/canary.py    keeps the ledger (standard library only)
demo/inbox/            12 club emails for the demo; 2 of them should get held
tests/                 tests for canary.py
```

While it runs, state goes in `.canary/` in your working folder: `golden/` (approved samples), `rules.md` (rules from your edits), `held/` (a reason file per held item), `outbox/` (drafts), and `ledger.jsonl` (a log of every decision). The script only does bookkeeping. The agent makes every judgment call, which is why the skill works in any agent that can read a markdown file.

```
canary.py init
canary.py list <dir> [-r]                  # -r includes subfolders, skipping .git, node_modules, etc.
canary.py record <item> <sampled|done|approved|held|rejected> [--wave K] [--reason "..."]
canary.py status [--total T] [--waves W]   # 🐤 8 done of 40 · 1 held · 3 sampled · 0 rejected · wave 2/3
canary.py held
```

Tests: `python3 -m unittest discover -s tests`

## Next

A Gmail drafts adapter, smarter batch sizes, and a way to undo a whole run.

Built for EvoHacks 2026 (theme: AI for Automation).
