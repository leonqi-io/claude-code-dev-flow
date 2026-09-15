# Claude Code on a local model — unattended workflow

Claude Code + a local 27B model (Qwen 3.8 via Ollama, set up per [claude-code-ollama-guide](https://github.com/leonqi-io/claude-code-ollama-guide)) turning one scoped ticket into a diff for you to review in the morning. You write and approve the ticket; the model plans, writes the tests, shows them red, implements to green and reports — or stops and says why — in one session, with no gate that waits for a person; you review in the morning.

This repo is the kit: two slash commands, a hook, a ticket template with a filled-in example, and the two protocol files the commands read. Copy them into your project, write a ticket, launch. It is not a runner or a framework — nothing here chains sessions or enforces the gates. Three things are mechanical: a Bash allowlist, accept-edits mode, and a hook that blocks the common shapes of file writes done through a script. Everything else is instruction the session follows and files you check in the morning.

Written from use on one Python project with a test suite, on "create these new files" tickets (§3). A feature is not a ticket; a feature is several tickets, one per night. Tickets that edit existing code in several places are not what it is for.

## Contents

1. [What a run looks like](#1-what-a-run-looks-like)
2. [Install](#2-install)
3. [Write the ticket](#3-write-the-ticket)
4. [Launch](#4-launch)
5. [The morning](#5-the-morning)
6. [What is enforced and what is not](#6-what-is-enforced-and-what-is-not)
7. [Where this goes](#7-where-this-goes)
8. [Files](#8-files)

## 1. What a run looks like

```
 EVENING (you, ~30–45 min)
   write dev_flow/tickets/<ID>/ticket.md to plan level ──► approve it (Gate 1) ──► pre-run checklist ──► /start-developing <ID>

 NIGHT (local model, one session, nobody watching)
   plan record → file  ──►  tests written  ──►  test run, red output → file  ──►  implement to green  ──►  report
   (Gate 2: auto)                                (Gate 3: auto)

 MORNING (you, ~20 min)
   read plan_<date>.md ──► read tests_red.txt ──► read git diff ──► run the tests and linter yourself ──► commit (Gate 4)
```

One ticket per night. What the run writes about itself lands in the ticket's directory — `plan_<date>.md` and `tests_red.txt` beside `ticket.md`; the code lands in the files the ticket names; the report is the session's last message (paste it into the ticket's Gate log if you want it kept). The full protocol is [`DEV_FLOW.md`](DEV_FLOW.md).

## 2. Install

Prerequisites: the companion guide's stack, including its §4.5 context budget (tool deny list + `CLAUDE_CODE_ENABLE_TASKS=0`) — without it the session compacts almost as soon as it starts reading files. A project with a test suite: Gate 3 has nothing to check without one.

1. Copy `.claude/commands/`, `.claude/hooks/`, `.claude/settings.json` and `scripts/fix_indent.py` into your project. The hook needs Python 3 on `PATH`.
2. Copy `DEV_FLOW.md`, `LOCAL_MODEL_PROTOCOL.md` and `tickets/TEMPLATE.md` into `dev_flow/` (the commands read them from there; change the paths in the command files if you use another location).
3. Add the per-machine Bash allowlist to `.claude/settings.local.json` (gitignored):

   ```json
   {"permissions": {"allow": ["Bash(python3:*)", "Bash(uv run *)", "Bash(uv run pytest:*)", "Bash(.venv/bin/python3:*)"]}}
   ```

   Substitute your interpreter and test runner. This is what lets the model run tests and the formatter without a prompt. The hook is what keeps a wide `python3` allowlist tolerable: it pattern-matches the usual shapes of a scripted write — `open(…, 'w')`, `.write*()`, `sed -i`, `tee`, `>` into a source or config file, heredocs, `shutil`/`os` file ops — and denies them with a recovery message, so changes go through `Edit`/`Write` and show up as a diff. It is a guard against a habit, not a sandbox: the session runs as your user, inside the allowlist, and can read anything in the tree. Keep secrets out of the repository, and know that whatever your test command touches — a database, the network — it touches unattended.
4. Put in your `CLAUDE.md`: how tests are run, any rule a ticket must never override, and the read budget (`Read` with `offset`/`limit`, ≤150 lines per call). `CLAUDE.md` is re-injected after a context compaction; the chat is not.

## 3. Write the ticket

Start from [`tickets/TEMPLATE.md`](tickets/TEMPLATE.md); [`tickets/EXAMPLE_add-dry-run-flag/ticket.md`](tickets/EXAMPLE_add-dry-run-flag/ticket.md) is one filled in.

**How big a ticket is.** One night, one session, one model — there is no parallelism on a local stack and no second agent to hand anything to. A ticket is one or two new files, on the order of a hundred to three hundred lines of implementation, around ten tests, every one of them enumerable in advance. "Build me a booking system" is not a ticket; it is a milestone, and a milestone is split by you (or by a cloud model with you) into tickets of this shape, run one per night in dependency order — the frontmatter's `depends_on` is the list you keep by hand. If you cannot write the test requirements as a finished list, the ticket is too big or not decided enough; either way the night would be spent inventing, and that is what a 27B model does badly.

A ticket the local model can run overnight is written to the point where planning is mechanical:

- **Scope is a list of files — new ones, or at most one existing file with an exactly described edit.** `scope_impl_files` and `scope_test_files` are the only files the model may write. "Create these two files, touch nothing that exists" is the shape that works best; if a one-line wiring edit to an existing file is needed, you make it before the run.
- **No open decisions.** Anything the plan would have to decide, you decide in Locked decisions, one line each with the reason.
- **Test requirements are enumerable**, one behaviour per line, and the expected red state is stated in numbers (`62 existing pass / 10 new fail`). If a new test will already pass — because of an edit you made before the run — name it and say why.
- **Context quotes the signatures** the new code calls, with the line ranges to read. The ticket tells the model to read those and nothing else; the plan record shows what it read.
- **`gates.plan: auto`, `gates.red_run: auto`.** The plan record and the red-run file are written instead of waiting for you.

A strong cloud model is good at drafting a ticket to this level; the point is that a 27B model then has few decisions left to make.

## 4. Launch

The template ends with this checklist; it is what makes "unattended" true.

0. Launch the local session and run `/context`: fixed footprint ~18K on a 131K window. If it shows ~69K / 100K, the companion guide's §4.5 is not loaded — stop.
1. Make any owner-side edit the tests need (a `pyproject.toml` entry, a fixture directory) now, and predict its effect on the red state in the ticket.
2. Run the test suite yourself; write the real green count into the ticket. `git diff --stat` shows only your own edits.
3. `ollama stop` other models; `caffeinate -is`; lid open, on power.
4. `ulimit -n 4096` in the shell that launches the session — macOS defaults to 256 open files and a suite that opens a database client per test exhausts it.
5. Allowlist and hook in place; `plan_record` date in the frontmatter is today.
6. Clean tree, on a branch: commit — your step-1 edits included — so the morning's `git diff` is the run and nothing else, and rejecting it is discarding the run's changes to tracked files (`git checkout -- .`, delete the new files) — whatever the test command did outside the tree is yours to undo.
7. Launch with `--permission-mode acceptEdits` and `CLAUDE_CODE_EFFORT_LEVEL=low` (the guide's wrapper sets the latter), then `/start-developing <ID>`. Go to bed. There is no ceiling on the run; if you want one, note the session's PID after launch and `kill` it from another tab after N hours.

`acceptEdits` plus the allowlist is what the flow needs; `--dangerously-skip-permissions` stays off.

## 5. The morning

In this order, before reading any code:

1. `plan_<date>.md` against `ticket.md` — every file, signature and test traces to a ticket line; nothing added.
2. `tests_red.txt` against the plan — the failing tests are exactly the plan's list, every pre-existing test passed, and any new test that passed at red is one the ticket predicted.
3. `git diff`, read in full. Then run the tests and the linter yourself; never trust the transcript's numbers.
4. Every deviation from the plan has a reason in the report; no test was weakened. Commit, or reject and rerun — a rerun costs a night and another review, not money.

If a stronger model is available, having it read steps 1–3 before you do is a second pair of eyes on the plan; it may catch drift you would read past. It runs nothing; the tests are yours to run.

If the session died mid-run: a plan record and nothing else written means `/continue-developing <ID>` in a fresh session picks up from the plan (it never re-plans); anything beyond that — a half-written test file, a partial implementation — is discarded and the ticket rerun from the top. Compaction is handled inside the run — the commands re-read the plan record and task list after one.

## 6. What is enforced and what is not

Enforced: the Bash allowlist (anything else prompts, and nothing answers), accept-edits mode, and the hook. Instructed, and checked by you in the morning: scope, locked decisions, tests-first, no weakened tests, the read budget, the closed command list. The ticket is written so that a 27B model has as little as possible to invent — files fixed, decisions made, signatures quoted, tests enumerated, a red run as the stopping condition — and [`LOCAL_MODEL_PROTOCOL.md`](LOCAL_MODEL_PROTOCOL.md) carries the operating rules for what such a model still gets wrong: how to write an `Edit` that matches, when to give up and `Write` the whole file, formatting by tool and never by hand, no command that could prompt, reads small enough to keep compaction rare. Each rule names the failure it prevents. When the model ignores one, the morning review is where it shows, which is why Gate 4 reads the plan and the red file before the code.

## 7. Where this goes

What this repo ships is the unit: one ticket, one unattended session, one diff. A night that gets through several tickets is a queue of these units plus a runner — a loop that picks the next approved ticket whose dependencies are done, opens a git worktree for it, launches the session, waits for it to exit, runs the tests itself, marks the ticket ready for review and takes the next one. On a local stack that loop is serial (one model resident, one session at a time), so a night is a handful of tickets, not a milestone; tickets that depend on each other stack unreviewed work on unreviewed work, and the morning review is of the stack; and every ticket needs a time limit or one stuck run eats the night. It is designed and not built, and it will not be published until it has run real tickets. The protocol does not change when it lands — the runner drives the same commands, reads the same files, and Gate 4 stays yours.

## 8. Files

| File | What it is |
|---|---|
| [`DEV_FLOW.md`](DEV_FLOW.md) | The protocol: roles, gates, ticket layout, standing rules |
| [`LOCAL_MODEL_PROTOCOL.md`](LOCAL_MODEL_PROTOCOL.md) | Binding rules for a local-model implementer session, each with the failure it prevents |
| [`tickets/TEMPLATE.md`](tickets/TEMPLATE.md) | Ticket template: frontmatter, required sections, pre-run checklist |
| [`tickets/EXAMPLE_add-dry-run-flag/ticket.md`](tickets/EXAMPLE_add-dry-run-flag/ticket.md) | A filled-in, synthetic overnight ticket |
| [`.claude/commands/start-developing.md`](.claude/commands/start-developing.md) | Slash command: plan, tests, implementation, report in one session — the overnight entry point |
| [`.claude/commands/continue-developing.md`](.claude/commands/continue-developing.md) | Slash command: resume from an existing plan record in a fresh session, never re-plan |
| [`.claude/hooks/no_script_writes.py`](.claude/hooks/no_script_writes.py) | PreToolUse hook on Bash: blocks file writes done via scripts |
| [`.claude/settings.json`](.claude/settings.json) | Wires the hook |
| [`scripts/fix_indent.py`](scripts/fix_indent.py) | The one sanctioned script write: repairs off-by-one indentation, ast-validated. Python only — in other languages the formatter does this |

MIT licensed. If one of these rules does not hold on your setup, that is worth an issue.
