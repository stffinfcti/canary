#!/usr/bin/env python3
"""canary — bookkeeping helper for the /canary skill.

Keeps score only. All judgment (sampling, drafting, learning rules,
judging holds) is done by the agent following SKILL.md.

Usage (from the working root containing .canary/):
    canary.py init
    canary.py list <dir>
    canary.py record <item> <status> [--wave N] [--reason "..."]
    canary.py status
    canary.py held
"""
import json
import sys
import time
from pathlib import Path
from typing import Optional

STATE = Path.cwd() / ".canary"
LEDGER = STATE / "ledger.jsonl"
STATUSES = {"sampled", "done", "held", "rejected", "approved"}


def init() -> None:
    for d in ("golden", "held", "outbox"):
        (STATE / d).mkdir(parents=True, exist_ok=True)
    (STATE / "rules.md").touch()
    LEDGER.touch()
    print("initialized .canary/")


def list_items(dirpath: str) -> None:
    p = Path(dirpath)
    if not p.is_dir():
        sys.exit(f"not a directory: {dirpath}")
    items = sorted(f for f in p.iterdir() if not f.name.startswith("."))
    for i, f in enumerate(items, 1):
        preview = "(dir)"
        if f.is_file():
            preview = "(binary)"
            try:
                text = f.read_bytes()[:4096].decode("utf-8")
            except (OSError, UnicodeDecodeError):
                text = ""
            for line in text.splitlines():
                if line.strip():
                    preview = line.strip()[:72]
                    break
        print(f"{i:>2}  {f.name}  ({f.stat().st_size}b)  {preview}")
    print(f"\n{len(items)} items — pick a varied sample, not the first N")


def record(item: str, status: str, wave: Optional[str], reason: Optional[str]) -> None:
    if status not in STATUSES:
        sys.exit(f"status must be one of {sorted(STATUSES)}")
    rec = {"ts": int(time.time()), "item": item, "status": status}
    if wave is not None:
        rec["wave"] = int(wave)
    if reason:
        rec["reason"] = reason
    with LEDGER.open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(f"recorded {item}: {status}")


def _latest() -> dict:
    """Last recorded status per item."""
    latest = {}
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                latest[rec["item"]] = rec
    return latest


def status() -> None:
    latest = _latest()
    counts = {s: 0 for s in STATUSES}
    for rec in latest.values():
        counts[rec["status"]] += 1
    held = [r["item"] for r in latest.values() if r["status"] == "held"]
    waves = {r.get("wave") for r in latest.values() if r.get("wave") is not None}
    wave_txt = f" · wave {max(waves)}" if waves else ""
    print(
        f"🐤 {counts['done'] + counts['approved']} done · "
        f"{counts['held']} held · {counts['sampled']} sampled · "
        f"{counts['rejected']} rejected{wave_txt}"
    )
    for item in held:
        print(f"   held: {item}")


def held() -> None:
    latest = _latest()
    rows = [r for r in latest.values() if r["status"] == "held"]
    if not rows:
        print("nothing held")
        return
    for r in rows:
        print(f"- {r['item']}: {r.get('reason', '(no reason)')}")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd, rest = args[0], args[1:]
    if cmd == "init":
        init()
    elif cmd == "list" and rest:
        list_items(rest[0])
    elif cmd == "record" and len(rest) >= 2:
        wave = reason = None
        if "--wave" in rest:
            i = rest.index("--wave")
            wave = rest[i + 1]
            del rest[i : i + 2]
        if "--reason" in rest:
            i = rest.index("--reason")
            reason = rest[i + 1]
            del rest[i : i + 2]
        record(rest[0], rest[1], wave, reason)
    elif cmd == "status":
        status()
    elif cmd == "held":
        held()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
