#!/usr/bin/env python3
"""Repair the off-by-one indentation left by model insertions (Dev Flow tool).

Observed failure mode (two 27B local models via Claude Code → Ollama): a
block inserted with Edit arrives with every line shifted right by one space
(5/9/13-space indents in 4-space code), which breaks ``ast.parse`` and which
local models cannot repair line-by-line. This tool fixes exactly that shape
and nothing else. It is the one script write the no_script_writes hook
allows.

Usage:  python3 scripts/fix_indent.py <file.py> [more.py ...]
Exit codes: 0 = file(s) valid (already, or after repair); 2 = could not repair
(file restored untouched).
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


def repair(src: str) -> str:
    lines = src.split("\n")
    out = []
    for line in lines:
        n = len(line) - len(line.lstrip(" "))
        out.append(line[1:] if n and n % 4 == 1 else line)
    return "\n".join(out)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    rc = 0
    for name in argv:
        path = Path(name)
        src = path.read_text(encoding="utf-8")
        try:
            ast.parse(src)
            print(f"{name}: already valid — untouched")
            continue
        except SyntaxError as e:
            first_error = f"line {e.lineno}: {e.msg}"
        fixed = repair(src)
        try:
            ast.parse(fixed)
        except SyntaxError as e:
            print(f"{name}: NOT repairable by off-by-one dedent "
                  f"(before: {first_error}; after: line {e.lineno}: {e.msg}). "
                  "File untouched — needs human attention.")
            rc = 2
            continue
        changed = sum(1 for a, b in zip(src.split("\n"), fixed.split("\n")) if a != b)
        path.write_text(fixed, encoding="utf-8")
        print(f"{name}: repaired — dedented {changed} lines (was: {first_error}). "
              "Run your formatter next.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
