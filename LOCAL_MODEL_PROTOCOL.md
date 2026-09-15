# LOCAL_MODEL_PROTOCOL — operating rules for implementer sessions on a local model

Operating rules for a Claude Code session on a local 27B model (Qwen 3.6 / 3.8 via Ollama; setup in [claude-code-ollama-guide](https://github.com/leonqi-io/claude-code-ollama-guide)). Cloud sessions do not need this file. Each rule but one exists because it prevents a failure that actually happened (the exception is named at the end); do not relax them ad hoc.

## 1. File edits

- Read files with the **Read** tool. Modify files ONLY with **Edit** or **Write**. Never write files via python/heredoc/sed/`>` — `.claude/hooks/no_script_writes.py` blocks the common shapes of that; the rule covers every shape.
- **Edit protocol** (every Edit, no exceptions):
  1. `old_string` starts at the first non-space character of the target — never include leading indentation (Edit is a substring match; leading whitespace is where transmission corrupts).
  2. `old_string` must include a unique anchor (the function's `def` line or another string that occurs exactly once in the file).
  3. Watch for non-ASCII: em-dashes (—), arrows (→), curly quotes must be copied exactly, never approximated with ASCII.
  4. One Edit at a time. After each successful Edit on a `.py` file, run the formatter and linter on that file (`uv run ruff format <file> && uv run ruff check <file>`, or your project's equivalent) before the next. Never fire a batch of Edits sharing one guess about whitespace.
  5. Two failures on the same target → change strategy, do not retry: if the file is under ~150 lines (or you authored it this session), rewrite it whole with **Write**; otherwise STOP and report the exact target and both error messages.
- Read-only `python3 -c` inspection is allowed and encouraged (print lines with `repr()` to see exact whitespace). It must contain **no `#` comment lines** (they trigger a manual approval prompt in Claude Code) and must not write.

## 2. Formatting is a tool job

- Never hand-fix whitespace, indentation, or line wrapping.
- After inserting any block into a `.py` file, immediately run the formatter and linter on it.
- The formatter and the linter's safe auto-fix (`ruff check --fix <file>`, import order and the like) may rewrite a file you are allowed to write. That is a tool-level change, not a plan deviation — mention it in the report, do not re-apply it by hand. Never run either on a file outside your scope.
- If the linter reports a **parse error** (unexpected indent / unindent mismatch): run `python3 scripts/fix_indent.py <file>` once, then the formatter again. If it still fails, STOP and report which lines are off — do not fix indentation line by line. (Known issue: inserted blocks can arrive shifted right by one space; the script repairs exactly that shape and nothing else.)

## 3. Context economy

- Read only the files listed in the ticket's Context section plus the files you will change. Do not read fixtures you will not modify. Do not re-read a file you already read unless you edited it since.
- Read with `offset` + `limit`, never more than ~150 lines per call. Read a file whole only when it is under 150 lines. The ticket's Context section gives the line ranges that matter — use them; do not page through the rest. Every line read stays in context until the next compaction.
- The plan record is the plan — whether a person approved it (Gate 2 manual) or you wrote it and continued (Gate 2 auto). Do not re-plan, re-derive, or second-guess it mid-run; execute step by step. If a step cannot work as written, STOP and explain — that is a gate decision, not yours.
- Maintain the task list: mark each step done the moment it finishes, before starting the next. After any context compaction, re-read the plan file and the task list before continuing.

## 4. Tests are the contract

- Tests-first: fixtures and tests before implementation; run the test command once to show the new tests failing; only then touch implementation.
- Never weaken a test to make it pass (changing test data, loosening an assertion). If a test you authored contains a bug, you may fix the test — but say so explicitly in the final report, with the reasoning.
- On any tool error: change something before retrying. Repeating an identical call is never correct.

## 5. Nothing waits for a person (overnight mode)

Applies when the ticket sets `gates.plan: auto` and/or `gates.red_run: auto`. The session is launched with `--permission-mode acceptEdits`; the only Bash commands that run without a prompt are the ones allowlisted in `.claude/settings.local.json`. A command that prompts stalls the run until morning, so:

- **Shell commands you may run, and nothing else:** `python3 -c …` (read-only, no `#` lines), `python3 scripts/fix_indent.py <file>`, the formatter and linter on a file in scope (`uv run ruff format <file>`, `uv run ruff check <file>`, `uv run ruff check --fix <file>`), and the ticket's `test_command`. No `ls`, `cat`, `date`, `mkdir`, `cp`, `git`, `pip`, `ollama`, or anything else — use the Read / Write / Edit tools for files, and `python3 -c "import datetime; print(datetime.datetime.now().isoformat(timespec='minutes'))"` for a timestamp.
- If the ticket sets `gates.plan: auto`, write the plan record to the path in the ticket's `plan_record` field with the Write tool before any code and continue; do not wait. The plan is an expansion of the ticket: every file, signature and test case traces to a ticket line. If it cannot, STOP and report.
- If the ticket sets `gates.red_run: auto`, do not stop after the red run: save the full output to the path in the ticket's `red_run_file` field with the Write tool, log one line in the plan record, and continue. If the red state is wrong — an existing test fails, or a new test already passes for a reason the ticket did not predict — STOP and report; never implement on a bad red run.
- Never `git commit`, `git add`, or edit any file outside `scope_impl_files` + `scope_test_files` + the plan record + `red_run_file` + the ticket's `status` line — and that line only ever changes to `in-progress`; `done` is the owner's.
- Every fixture a test references is created and complete before the red run.
- If a step cannot be completed as planned, STOP and write the reason into the report — a stopped run with a clear report is a good outcome; a run that improvises is not.

## 6. Report format (fixed)

Exact files-changed list (path + action) · full test transcript · formatter/linter results · every deviation from the plan, each with its reason. No git commit, ever — commits are the owner's.

## Why each rule is there

| Rule | Failure it prevents (observed) |
|---|---|
| 1.1 no leading indentation in `old_string` | A dozen consecutive Edit mismatches on whitespace |
| 1.4 one Edit, then format | Batches of Edits all wrong by the same one-space shift |
| 1.5 two failures → switch to Write | A burst of eight identical retries on one target |
| 2 formatter, never by hand | A 41-line block inserted with every line shifted right by one space; the model could not repair it line by line, the script did in one pass |
| 3 context economy | Usable context on a local 27B model is small; one run hit an auto-compaction mid-ticket, which is why the task list and plan file must survive a compaction |
| 3 read budget | A run that compacted nine times in two hours and produced only a plan record; every whole-file read was still in context at the next compaction |
| 2 / 5 auto-fix is not a deviation | A run reported a linter auto-fix as if it were a plan deviation; the reviewer had to decide after the fact whether that was allowed |
| 5 closed command list | A prompt for an unlisted command is the one thing that turns an overnight run into a stalled one |
| 4 never weaken a test | One run changed test data to pass, then reported "no tests modified" |
| 4 change something before retrying | A burst of eight identical retries on one Edit target |

Rule 3's "do not re-plan" is a design rule rather than a recorded failure: the plan is checked against the ticket by a person — at Gate 2 in day mode, at Gate 4 overnight — and a small model revising it mid-run is exactly what that check cannot catch.
