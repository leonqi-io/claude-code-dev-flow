---
description: Develop a dev_flow ticket end to end (plan, tests-first, gated) — the overnight entry point
argument-hint: <ticket-id, e.g. m2-03_add-dry-run-flag>
---

You are the Planner and Implementer in this repository's ticket-driven dev
flow. Read, in order:

1. `CLAUDE.md` — repository constraints, always binding.
2. `dev_flow/DEV_FLOW.md` — the working protocol and gate definitions.
2b. On a local model: `dev_flow/LOCAL_MODEL_PROTOCOL.md` — binding
   operating protocol for local sessions.
3. `dev_flow/tickets/$ARGUMENTS/ticket.md` — the ticket for this session.
   If the file does not exist, list `dev_flow/tickets/` and stop.

Then follow the protocol strictly. Read only the files the ticket's Context
section lists plus the files you will change, with `offset`/`limit` and at
most ~150 lines per call (see `LOCAL_MODEL_PROTOCOL.md` §3).

- If the ticket status is not `approved`, stop and say so (Gate 1 first).
- **Plan (Gate 2).** Before touching any code, write the plan as a file with
  the Write tool at the path in the ticket's `plan_record` field (by
  convention `dev_flow/tickets/$ARGUMENTS/plan_<YYYY-MM-DD>.md`; never
  continue from an older plan record in that directory — it belongs to an
  earlier run and the ticket's Forbidden section names it), containing: the file list (must equal the ticket's `scope_impl_files` +
  `scope_test_files`), function signatures, the concrete test-case list
  derived one-to-one from the ticket's Test requirements, and a
  recommendation for each Open decision. Then, by the ticket's
  `gates.plan`:
  - `manual` — stop and wait for the owner's approval. (Use plan mode if
    the session offers it.)
  - `auto` — add a "Gate log" line to the plan record ("Gate 2 auto:
    plan written, <timestamp>"), set the ticket `status: in-progress`, and
    continue. If the ticket has an Open decision you cannot resolve from
    its Locked decisions and Context, STOP and report — do not guess.
- **Tests (Gate 3).** Write exactly the plan's test list — only files in
  `scope_test_files`; new fixture files only, existing fixtures read-only,
  every fixture complete before the red run. Run `test_command`. Check:
  new tests failing, existing tests passing. Then, by `gates.red_run`:
  - `manual` — show the red output and stop for confirmation.
  - `auto` — save the complete output with the Write tool to the path in
    the ticket's `red_run_file` field (by convention
    `dev_flow/tickets/$ARGUMENTS/tests_red.txt`), add a Gate log line
    ("Gate 3 auto: N new failing, M existing passing, <timestamp>"; if a
    new test passes because the ticket predicted it, say so in the same
    line), and continue. If the red state is wrong — an existing test
    fails, or a new test passes that the ticket did not predict — STOP and
    report; never implement on a bad red run.
- **Implement.** Code to green within `scope_impl_files` only. Run the
  formatter and linter on changed files before the tests; a formatter or
  linter auto-fix on a file in scope is reported, not treated as a plan
  deviation. Anything outside
  scope: report, never fix silently. Never weaken a test.
- **Report.** Exact files changed, test commands + full results,
  deviations from the plan with reasons, risks, a suggested commit
  message. Do NOT commit, push, or modify anything listed under Forbidden.

Record decisions taken as you pass each gate in the plan record's Gate log,
not in chat only.
