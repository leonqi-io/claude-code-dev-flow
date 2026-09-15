---
name: m2-03_add-dry-run-flag
status: approved
created: 2026-09-06
depends_on: [m2-02_sync-command]
approved_by: owner
approved_at: 2026-09-06
scope_test_files: [tests/test_cli.py]
scope_impl_files: [app/cli.py]
test_command: "uv run pytest tests/ -v"
cloud_allowed: true
plan_record: dev_flow/tickets/m2-03_add-dry-run-flag/plan_2026-09-06.md
red_run_file: dev_flow/tickets/m2-03_add-dry-run-flag/tests_red.txt
gates:
  plan: auto                             # overnight mode: plan record written, no mid-run stop
  red_run: auto                          # overnight mode: red output saved, no mid-run stop
stage_entries:
  planner: local 27B
  test_writer: local 27B
  implementer: local 27B
  reviewer: owner
---
# m2-03_add-dry-run-flag: `sync --dry-run` reports what would change without writing

> **Synthetic example.** This ticket is invented to show the template filled in at the
> level of detail that has worked. The project, files and functions do not exist.

Status: see frontmatter. v1 2026-09-06 (Strategist draft) · Approver: owner

**Why this ticket exists.** `sync` (m2-02) writes to the SQLite store as it goes. Users
want to see the planned inserts/updates/deletes before committing to them. This is the
thinnest slice that gives them that: one flag, no new module, no change to the engine.

## Context (read first)

- `CLAUDE.md` §3 — "CLI parses arguments and prints; all logic lives in `app/engine/`".
- `app/cli.py` — `main(argv) -> int`; `_cmd_sync(args) -> int` builds a `SyncOptions`
  and calls `engine.sync(options) -> SyncReport`.
- `app/engine/sync.py` — `SyncOptions(dry_run: bool = False, ...)` already exists and is
  honoured by the engine; `SyncReport.counts() -> dict[str, int]` with keys
  `inserted`, `updated`, `deleted`, `unchanged`.
- `tests/test_cli.py` — existing pattern: `monkeypatch.setattr("app.cli.engine.sync",
  fake_sync)`, capture stdout with `capsys`. Reuse it.

## Scope

**In:** `app/cli.py` (add the flag, pass it through, prefix the report line).
**Out:** the engine (`dry_run` is already implemented there); any other command; help
text wording beyond the one new line.

## Locked decisions

- Flag name is `--dry-run`, boolean, default off (matches the engine option name).
- Dry-run output is the normal report with the first line `DRY RUN — nothing written`;
  no separate output format.
- Exit code is unchanged by the flag.
- `--dry-run` together with `--rebuild` reports what the rebuild would do; it is not
  an error (was OD1; ruled at Gate 1 so the night has no open decision).

## Open decisions (for the plan phase)

None — overnight ticket. OD1 was ruled at Gate 1 and moved into Locked decisions.

## Test requirements

- `sync --dry-run` calls `engine.sync` with `SyncOptions.dry_run is True`.
- Plain `sync` still calls it with `dry_run is False` (regression).
- Output begins with `DRY RUN — nothing written` when the flag is set, and does not
  contain that line otherwise.
- Exit code is 0 in both cases with a successful fake report.
- `--dry-run --rebuild` reports without error (the former OD1, now locked).
- Fixtures: none needed beyond the fake `SyncReport` already in `tests/test_cli.py`.

Expected red state: 22 existing pass / 5 new fail. No new test is expected to pass
before implementation.

## Definition of Done

- 5 new tests in `tests/test_cli.py`; suite goes from 22 (pre-run baseline, run by
  the owner on 2026-09-06 evening) to 27 green.
- `uv run ruff format --check app/cli.py tests/test_cli.py` and `uv run ruff check`
  clean.
- `sync --help` shows the flag.

## Forbidden

- No changes outside `app/cli.py` and `tests/test_cli.py`.
- No new dependencies. No git commit.
- Do not open `data/` (real user data).

## Pre-run checklist (owner, 2026-09-06 evening)

0. `/context` after launch: small footprint confirmed.
1. No owner-side edit needed for this ticket.
2. `uv run pytest tests/ -v` → 22 passed; `git diff --stat` empty.
3. `ollama stop` others; `caffeinate -is`; on power, lid open.
4. `ulimit -n 4096` in the launching shell.
5. Allowlist and hook present; `plan_record` date = 2026-09-06.
6. Clean tree on branch `m2-03`.
7. Launched with `--permission-mode acceptEdits`, effort low;
   `/start-developing m2-03_add-dry-run-flag`.

## Gate log

- Gate 1 — approved by owner, 2026-09-06. Overnight ticket, fully local: `/start-developing` on the local model, `plan: auto`, `red_run: auto`; OD1 ruled here and locked, so the planner has nothing to decide.
