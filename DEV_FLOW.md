# Dev Flow — ticket-driven, tests-first, human-gated development with Claude Code

The protocol the two slash commands follow. Three roles, one ticket at a time, gates with an objective pass/fail signal because the codebase is tests-first. No runner and no automation between sessions: the files are the state.

## Roles

- **Owner.** Writes or approves the ticket (Gate 1), reviews the result (Gate 4), owns every commit. No session ever commits or pushes on the owner's behalf.
- **Strategist** (the strongest model available, in a short evening session). Drafts tickets to plan level with the owner; audits accumulated diffs at milestone close. Does not implement.
- **Planner / Implementer** (the local model, one overnight session). Expands the ticket into a plan record, writes the tests, shows them red, implements to green, reports. `/start-developing` runs all of it; `/continue-developing` runs the implementation half from an existing plan record in a fresh session. It sets the ticket's `status` to `in-progress` when it starts and never to anything else; `done` is the owner's, at Gate 4.

## The flow

1. **Ticket.** Owner and Strategist write `dev_flow/tickets/<ID>/ticket.md` from [`tickets/TEMPLATE.md`](tickets/TEMPLATE.md), to plan level: new-file scope (or one exactly named edit), no open decision left (rule them and move them into Locked decisions), test requirements enumerated with the expected red state in numbers, signatures and line ranges quoted in Context. **Gate 1: the owner approves** (`status: approved`) and runs the template's pre-run checklist — the baseline test count in the ticket comes from a run the owner did that evening, not from memory or a commit message.
2. **Plan.** `/start-developing <ID>`. The session writes the plan record to the path in the ticket's `plan_record` field (`dev_flow/tickets/<ID>/plan_<date>.md`): file list equal to the ticket's scope, function signatures, a test list derived one-to-one from the test requirements. **Gate 2: the plan is an expansion of the ticket and nothing more.** With `gates.plan: auto` the session logs a Gate line and continues — nobody has approved that plan yet; the owner reads it against the ticket at Gate 4, and the session's rule in the meantime is to execute it, not to revise it. If it hits a decision the ticket does not settle, it stops and reports instead of guessing. (`gates.plan: manual` makes it stop for the owner — for a ticket that needs a real plan on a stronger model, approved in advance, then `/continue-developing` implements it.)
3. **Tests.** The session writes exactly the plan's test list, only into `scope_test_files`, new fixture files only, every fixture complete; runs `test_command`. **Gate 3: the red run matches the ticket** — new tests fail, existing tests pass, a new test passing at red is one the ticket predicted and explained. With `gates.red_run: auto` the full output is saved to `red_run_file` (`dev_flow/tickets/<ID>/tests_red.txt`), one Gate line logged, and the session continues; a wrong red state stops the run. (`manual` stops for the owner.)
4. **Implement.** Code to green inside `scope_impl_files` only. Formatter and linter on changed files before the tests; a formatter or linter auto-fix on a file in scope is reported, not a deviation. Anything outside scope is reported, never fixed along the way. No test is weakened.
5. **Report.** Files changed, test commands and full results, every deviation from the plan with its reason, risks, a suggested commit message — as the session's final message; the owner pastes it into the ticket's Gate log if it is to be kept. Never a commit.
6. **Gate 4 (owner, morning).** Plan record against the ticket, `tests_red.txt` against the plan, then `git diff` in full; tests and linter run by the owner, not trusted from the transcript. Commit, or reject and rerun. A second, stronger model reading the three files first — the auditor is never the implementer — is worth the ten minutes.
7. **Gate 5 (milestone).** Every few tickets, the Strategist audits the accumulated diffs against the milestone's definition of done.

## What each gate catches

| Gate | Catches |
|---|---|
| 1 — ticket | Vague scope, a decision left implicit, an open decision that is really the owner's to make, a baseline count copied from somewhere instead of measured, no forbidden list |
| 2 — plan | A plan that touches files outside scope, a test list that does not cover the requirements, a decision resolved by assumption |
| 3 — red run | Tests that pass before implementation, a test list that drifted, a broken existing suite blamed on the new work |
| 4 — diff | Weakened tests, silent scope creep, a report that does not match the diff, formatting done by hand |
| 5 — milestone | Tickets that each passed but together miss the definition of done |

Gates are policy, not tooling: nothing stops you skipping one, and nothing but the Bash allowlist, accept-edits mode and the script-write hook is enforced by machinery — the rest is instruction, and the gates are where you find out whether it was followed.

## Ticket layout and records

- One directory per ticket: `dev_flow/tickets/<milestone>-<seq>_<slug>/` containing `ticket.md`, the plan record `plan_<date>.md` and, in overnight mode, `tests_red.txt` — their paths are the ticket's `plan_record` and `red_run_file` fields. One `ls` of the directory shows how far the run got.
- The plan record ends with a **Gate log**: one line per gate as the run passes it, plus any deviation noted at Gate 3 or 4. The ticket's own Gate log carries the owner's lines (approval, amendments, the outcome of each run).
- A rerun of the same ticket gets a new plan record with a new date; the old one stays as history and the ticket's Forbidden section names it so the new run does not continue from it.
- Ticket frontmatter (`scope_test_files`, `scope_impl_files`, `test_command`, `plan_record`, `red_run_file`, `gates`, `depends_on`) is read by people and by the slash commands' prose only. Nothing parses or enforces it; it is structured so the owner can check at Gate 4 that the session stayed inside it. `status` moves `draft → approved` (owner, Gate 1) `→ in-progress` (session, Gate 2) `→ done` (owner, Gate 4).

## Standing rules

- `CLAUDE.md` always applies; a ticket narrows scope, it never widens permissions. Conflict → stop and flag.
- Synthetic fixtures only in tests; no real user data.
- A session that finishes reports exactly which files it changed; one that stops early reports why and what it had written so far.
- File edits go through `Edit` or `Write` so every change is a reviewable diff; the common shapes of a shell-scripted write are blocked by `.claude/hooks/no_script_writes.py`.
- Formatting is not a model job: formatter and linter on changed files before tests; their diffs are expected, reported, and not a deviation. Neither is ever run on a file outside scope.
- `Read` with `offset` and `limit`, at most ~150 lines per call; a file is read whole only when it is under 150 lines. This rule also lives in `CLAUDE.md`, because `CLAUDE.md` is what Claude Code re-injects after a context compaction.
- Never weaken a test to make it pass. A bug in a test the session authored may be fixed, and the fix is called out in the report with the reasoning.
- Local-model sessions additionally follow [`LOCAL_MODEL_PROTOCOL.md`](LOCAL_MODEL_PROTOCOL.md).
