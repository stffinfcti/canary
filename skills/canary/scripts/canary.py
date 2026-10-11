#!/usr/bin/env python3
"""canary — bookkeeping helper for the /canary skill.

Keeps score only. All judgment (sampling, drafting, learning rules,
judging holds) is done by the agent following SKILL.md.

Run from the working root; state lives in ./.canary/
"""
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Optional

STATE = Path.cwd() / ".canary"
LEDGER = STATE / "ledger.jsonl"
STATUSES = ("sampled", "done", "approved", "held", "rejected")
SKIP_DIRS = {".git", ".canary", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}


def ensure_state() -> None:
    for d in ("golden", "held", "outbox"):
        (STATE / d).mkdir(parents=True, exist_ok=True)
    (STATE / "rules.md").touch()
    LEDGER.touch()


def cmd_init(_: argparse.Namespace) -> None:
    ensure_state()
    print("initialized .canary/")


def _preview(f: Path) -> str:
    if f.is_dir():
        return "(dir)"
    try:
        text = f.read_bytes()[:4096].decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return "(binary)"
    return next((ln.strip()[:72] for ln in text.splitlines() if ln.strip()), "(empty)")


def cmd_list(args: argparse.Namespace) -> None:
    root = Path(args.dir)
    if not root.is_dir():
        sys.exit(f"not a directory: {args.dir}")
    if args.recursive:
        items = sorted(
            f for f in root.rglob("*")
            if f.is_file() and not any(part in SKIP_DIRS or part.startswith(".") for part in f.relative_to(root).parts)
        )
    else:
        items = sorted(f for f in root.iterdir() if not f.name.startswith("."))
    for i, f in enumerate(items, 1):
        name = f.relative_to(root).as_posix() if args.recursive else f.name
        print(f"{i:>3}  {name}  ({f.stat().st_size}b)  {_preview(f)}")
    print(f"\n{len(items)} items — pick a varied sample, not the first N")


def cmd_record(args: argparse.Namespace) -> None:
    ensure_state()
    rec = {"ts": int(time.time()), "item": args.item, "status": args.status}
    if args.wave is not None:
        rec["wave"] = args.wave
    if args.reason:
        rec["reason"] = args.reason
    with LEDGER.open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(f"recorded {args.item}: {args.status}")


def _latest() -> Dict[str, dict]:
    """Last recorded status per item; malformed lines are skipped."""
    latest: Dict[str, dict] = {}
    if not LEDGER.exists():
        return latest
    for n, line in enumerate(LEDGER.read_text().splitlines(), 1):
        try:
            rec = json.loads(line)
            latest[rec["item"]] = rec
        except (json.JSONDecodeError, KeyError, TypeError):
            if line.strip():
                print(f"warning: skipping malformed ledger line {n}", file=sys.stderr)
    return latest


def cmd_status(args: argparse.Namespace) -> None:
    latest = _latest()
    counts = {s: 0 for s in STATUSES}
    for rec in latest.values():
        counts[rec.get("status")] = counts.get(rec.get("status"), 0) + 1
    waves = [r["wave"] for r in latest.values() if isinstance(r.get("wave"), int)]
    wave_txt = ""
    if waves:
        wave_txt = f" · wave {max(waves)}" + (f"/{args.waves}" if args.waves else "")
    total_txt = f" of {args.total}" if args.total else ""
    print(
        f"🐤 {counts['done'] + counts['approved']} done{total_txt} · {counts['held']} held · "
        f"{counts['sampled']} sampled · {counts['rejected']} rejected{wave_txt}"
    )
    for item, rec in latest.items():
        if rec.get("status") == "held":
            print(f"   held: {item}")


def cmd_held(_: argparse.Namespace) -> None:
    rows = [r for r in _latest().values() if r.get("status") == "held"]
    if not rows:
        print("nothing held")
    for r in rows:
        print(f"- {r['item']}: {r.get('reason', '(no reason)')}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="canary.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="create .canary/ state").set_defaults(fn=cmd_init)
    ls = sub.add_parser("list", help="list items in a collection")
    ls.add_argument("dir")
    ls.add_argument("-r", "--recursive", action="store_true", help="include files in subfolders (skips .git, node_modules, ...)")
    ls.set_defaults(fn=cmd_list)
    rc = sub.add_parser("record", help="append a status for an item to the ledger")
    rc.add_argument("item")
    rc.add_argument("status", choices=STATUSES)
    rc.add_argument("--wave", type=int)
    rc.add_argument("--reason")
    rc.set_defaults(fn=cmd_record)
    st = sub.add_parser("status", help="print the progress ticker")
    st.add_argument("--total", type=int, help="collection size, shown as 'N done of TOTAL'")
    st.add_argument("--waves", type=int, help="planned wave count, shown as 'wave K/WAVES'")
    st.set_defaults(fn=cmd_status)
    sub.add_parser("held", help="list held items with reasons").set_defaults(fn=cmd_held)
    return p


def main(argv: Optional[list] = None) -> None:
    args = build_parser().parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
