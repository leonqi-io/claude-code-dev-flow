---
name: <milestone>-<seq>_<slug>          # e.g. m2-03_add-dry-run-flag; lives at dev_flow/tickets/<name>/ticket.md
status: draft                           # draft → approved (owner, Gate 1) → in-progress (session, Gate 2) → done (owner, Gate 4)
created: YYYY-MM-DD
depends_on: []                          # ticket names; the owner enforces by hand, nothing reads this
approved_by:
approved_at:
scope_test_files: []                    # the ONLY files the implementer may write tests into
scope_impl_files: []                    # the ONLY files the implementer may change (disjoint from tests)
test_command: "uv run pytest tests/ -v" # whatever your project uses
cloud_allowed: true                     # false = local model only: set it when the files or fixtures this ticket touches must not leave the machine
plan_record: dev_flow/tickets/<name>/plan_YYYY-MM-DD.md   # written by the planner as its first step; set the date to the launch day. A rerun gets a new date; the old record stays as history
red_run_file: dev_flow/tickets/<name>/tests_red.txt       # full test output at red state (Gate 3 auto)
gates:
  plan: manual                          # Gate 2: manual = stop for a person; auto = write plan record and continue (overnight mode; ticket must be at plan level)
  red_run: manual                       # Gate 3: manual = stop for a person; auto = save tests_red.txt and continue (overnight mode)
stage_entries:                          # which session / model runs which stage; a note to the owner, not a config
  planner:
  test_writer:
  implementer:
  reviewer:
---
# <name>: <title>

Status: see frontmatter. v1 <date> (Strategist draft, pre-Gate 1) · Approver: <owner>

**Why this ticket exists.** Two or three sentences: which milestone it serves, what is
already done, why this slice and not a bigger one.

## Context (read first)

Pointers only — the implementer reads these files, nothing else:

- `CLAUDE.md` § … — the constraints that bind this ticket.
- Design doc § … — the section this implements.
- `path/to/existing_module.py` — the function signatures the new code calls
  (quote them here so the plan does not have to rediscover them).
- `tests/test_existing.py` — the fixture pattern to reuse (say whether to
  import it or copy it).

## Scope

**In:** exact files (must match `scope_impl_files` / `scope_test_files`).
**Out:** explicit non-goals, especially the tempting adjacent ones.

## Locked decisions

Constraints the plan must not reopen. Each one a single line with the reason.

## Open decisions (for the plan phase)

Questions the Planner must answer with a recommendation; the owner decides at Gate 2.
An overnight ticket (`gates.plan: auto`) has none left: rule them at Gate 1 and move
each into Locked decisions with its reason.

- OD1 — …
- OD2 — …

## Test requirements

Minimum behaviours the tests must cover, as a list the Planner turns into
concrete test cases. Fixtures policy: synthetic only, new fixture files only,
existing fixtures read-only.

State the expected red state in numbers: `<N existing> pass / <M new> fail`. If
any new test is expected to pass already (because of something the owner did
before the run), name it and say why — the implementer notes a predicted pass in
the Gate log and continues; any other new test passing at red is a bad red run
and the run stops.

## Definition of Done

Objective checks: test count (before → after — the "before" is the number from
the pre-run baseline below, never a number remembered from a plan or a commit
message), commands that must pass, files that must exist, output that must match.

## Pre-run checklist (owner, after Gate 1, before launch)

0. Launch the session and run `/context`: the header should show the small
   footprint from the companion guide's context fix. If it shows the full
   built-in tool set, stop — the fixes are not loaded and the run will not
   survive.
1. Any edit the implementer is forbidden to make but the tests need (a
   `pyproject.toml` entry, a fixture directory) — do it by hand now, and predict
   its effect on the red state above.
2. Run `test_command` yourself: write the real green count into Definition of
   Done; `git diff --stat` shows only your own pre-run edits.
3. `ollama stop` any other resident model; `caffeinate -is`; lid open, on power.
4. `ulimit -n 4096` in the shell that launches the session (macOS defaults to
   256 open files; a suite that opens a database client per test exhausts it,
   and the child test runner inherits the limit).
5. Allowlist present in `.claude/settings.local.json`; hook wired in
   `.claude/settings.json`; `plan_record` date in the frontmatter = today.
6. Clean tree, on a branch — commit (step 1's edits included), so the
   morning's `git diff` is the run and nothing else.
7. Launch with `--permission-mode acceptEdits` and effort low; run
   `/start-developing <name>`.

## Forbidden

Files and behaviours out of bounds, named explicitly. Typical entries: no
changes outside `scope_impl_files`; no new dependencies; no git commit; do
not open `<directory containing real data>`.

## Gate log

Appended as the ticket moves. One line per gate: who, when, what changed. A rerun
adds a line for the failed run (numbers, what stopped it) before the new Gate 2
line, so the ticket carries the whole history.
