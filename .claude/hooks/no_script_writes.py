#!/usr/bin/env python3
"""PreToolUse hook (Bash): block file writes done via scripts.

Rationale: file modifications must go through the Edit or Write tools so
every change is a reviewable diff. Local models tend to fall back to
`python3 - <<EOF ... open(path, "w")` after an Edit mismatch, which hides
an 8 KB insertion behind a one-line summary. Read-only inspection
(printing lines, repr() for whitespace) stays allowed.

Exit codes: 0 = allow; 2 = deny and feed stderr back to the model.
"""
import json
import re
import shlex
import sys

try:
    payload = json.load(sys.stdin)
except Exception:  # malformed input → don't block
    sys.exit(0)

if payload.get("tool_name") not in (None, "Bash"):
    sys.exit(0)

cmd = (payload.get("tool_input") or {}).get("command", "") or ""

# Sanctioned repair tool: the ONLY script allowed to write files — it
# self-limits to ast-validated off-by-one dedents (scripts/fix_indent.py).
try:
    first = shlex.split(cmd.strip().split("&&")[0])
except ValueError:
    first = []
if first[:1] in (["python3"], ["python"]) and first[1:2] == ["scripts/fix_indent.py"]:
    sys.exit(0)
if first[:3] == ["uv", "run", "python"] and first[3:4] == ["scripts/fix_indent.py"]:
    sys.exit(0)


WRITE_PATTERNS = [
    (r"""open\([^)]*,\s*['"][wax]\+?['"]""", "open(..., 'w'/'a'/'x')"),
    (r"\.write_text\(|\.write_bytes\(|\.writelines\(|\.write\(", ".write*()"),
    (r"\bsed\s+(-[a-zA-Z]*i|--in-place)", "sed -i"),
    (r"\btee\s+(-a\s+)?['\"]?[\w./-]+", "tee"),
    (r"(?<![<>|])>{1,2}\s*['\"]?[\w./-]+\.(py|md|txt|toml|json|ya?ml|cfg|ini)\b", "> redirection"),
    (r"\b(cat|python3?|bash|sh)\b[^\n]*<<-?\s*['\"]?\w*EOF", "heredoc"),
    (r"\bshutil\.(copy|move)|\bos\.(rename|replace|remove|unlink)\b", "shutil/os file ops"),
]

for pattern, label in WRITE_PATTERNS:
    if re.search(pattern, cmd):
        print(
            f"Blocked ({label}): file writes must go through the Edit tool "
            "(exact old_string) or the Write tool (whole file) so the change "
            "is a reviewable diff. Read-only python inspection is fine. "
            "If Edit failed on whitespace, inspect with repr() and retry Edit "
            "with the exact string.",
            file=sys.stderr,
        )
        sys.exit(2)

sys.exit(0)
