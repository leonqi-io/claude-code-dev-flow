---
description: Resume a dev_flow ticket from an approved plan record (Gate 2 done) in a fresh session
argument-hint: <ticket-id, e.g. m2-03_add-dry-run-flag>
---

You are the Implementer in this repository's ticket-driven dev flow. A
previous session produced the plan and the owner approved it (Gate 2).
Your job is to continue from that record — never to re-plan. Read, in
order:

1. `CLAUDE.md` — repository constraints, always binding.
2. `dev_flow/DEV_FLOW.md` — the working protocol and gate definitions.
2b. On a local model: `dev_flow/LOCAL_MODEL_PROTOCOL.md` — binding
   operating protocol for local sessions.
3. `dev_flow/tickets/$ARGUMENTS/ticket.md` — the ticket. If the file does
   not exist, list `dev_flow/tickets/` and stop.
4. The plan record at the path in the ticket's `plan_record` field (by
   convention `dev_flow/tickets/$ARGUMENTS/plan_<date>.md`). If it does not
   exist, stop and say so — Gate 2 has not been recorded; use
   `/start-developing` instead. Do not pick another plan record from the
   same directory; an older one belongs to an earlier run.

Then follow the protocol strictly:

- If the ticket status is not `approved` or `in-progress`, stop (Gate 1
  first).
- Treat the plan record as approved and binding: its file list, signatures,
  open-decision rulings and test list are settled. Do not reopen them. If
  you believe the plan is wrong, report the conflict and stop — do not
  silently deviate.
- **First action:** mark the plan record's gate line as
  "Gate 2 approved by the owner, <date> — implementation started in a
  fresh session", and set the ticket frontmatter `status: in-progress`.
  Nothing else in either file changes.
- **Tests (Gate 3):** write exactly the plan's test list — only files
  listed in the ticket's `scope_test_files`; new fixture files only,
  existing fixtures are read-only, and every fixture the tests reference
  must be complete before the red run. Run `test_command` and check the
  red state: new tests failing, existing tests passing. Then, by the
  ticket's `gates.red_run`:
  - `manual` — show the red output and stop for the owner's confirmation.
  - `auto` — save the complete test output with the Write tool to the
    path in the ticket's `red_run_file` field (by convention
    `dev_flow/tickets/$ARGUMENTS/tests_red.txt`), add one line to the plan
    record's Gate log ("Gate 3 auto: N new failing, M existing passing,
    <timestamp>"; a predicted pass is named in the same line), and
    continue without waiting. If the red state is wrong (an existing test
    fails, or a new test passes that the ticket did not predict), STOP and
    report — do not implement on a bad red run.
- **Implement (after Gate 3):** code to green within `scope_impl_files`
  only. Run the formatter and linter on changed files before the tests; a
  formatter or linter auto-fix on a file in scope is reported, not a plan
  deviation.
  Anything outside scope: report, never fix silently.
- **Report:** exact files changed, test commands + full results, deviations
  from the plan, risks. Suggest a commit message. Do NOT commit, push, or
  touch anything listed under the ticket's Forbidden section.

Record decisions taken as you pass each gate in the plan record (short
"Gate log" section at the end), not in chat only.
