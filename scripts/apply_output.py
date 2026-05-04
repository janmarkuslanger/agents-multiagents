#!/usr/bin/env python3
"""Write files from a coder output JSON to disk.

Usage:
    python apply_output.py coder-output.json [target-dir]
    cat coder-output.json | python apply_output.py - [target-dir]
"""
import json
import sys
from pathlib import Path


def apply(data: str, base_dir: Path = Path(".")) -> None:
    out = json.loads(data)
    entries = out.get("files", []) + out.get("tests", [])
    if not entries:
        print("no files in output", file=sys.stderr)
        return
    for entry in entries:
        dest = base_dir / entry["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(entry["content"])
        print(f"wrote {dest}")


if __name__ == "__main__":
    src_arg = sys.argv[1] if len(sys.argv) > 1 else "-"
    raw = sys.stdin.read() if src_arg == "-" else Path(src_arg).read_text()
    base = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    apply(raw, base)
