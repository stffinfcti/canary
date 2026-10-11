# AGENTS.md

- The skill is `skills/canary/SKILL.md`; `skills/canary/scripts/canary.py` is stdlib-only bookkeeping (Python 3.9+).
- Test: `python3 -m unittest discover -s tests`
- After changing the skill, sync the local Devin install: `cp -R skills/canary/. ~/.config/devin/skills/canary/`
- `.canary/` is runtime state and is gitignored.
