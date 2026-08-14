# My AI Playbook

*Draft — Maria, this is a starting point built from what actually happened on this
project (mid-course reflection + the final-project evidence). Read it, cut anything
that doesn't sound like you, and add anything real it's missing before you submit it.*

## When I reach for AI first

- Turning a fuzzy plan ("add due dates and tags") into a concrete diff across
  backend, frontend, and tests at the same time — it's faster to get a full
  first draft to react to than to write each layer from scratch myself.
- A second pair of eyes on validation logic. The due-date bug (see
  `docs/final-ai-review.md`) is the clearest example: I wouldn't have thought
  to test `datetime.fromisoformat` against a full timestamp, but having it
  named out loud made the gap obvious.
- Running a first-pass static/security scan (bandit, checkov) so I'm not
  starting a security review from a blank page.
- Drafting docs and templates like this one, that I then edit rather than
  ship as-is.

## When I do not reach for AI first

- Deciding whether a linter finding is real. bandit flagged two "SQL
  injection" warnings this project; both were false positives once I traced
  the actual data flow myself. AI/tool output is a lead, not a verdict.
- Anything that touches the course's scope rules (no new features, limited
  `app/`/`frontend/` edits) — I decide what's in scope before asking AI to
  build it, not after.
- Verifying something actually works. I run the command myself; I don't
  accept "this should work now" as evidence. When I genuinely couldn't run
  something (Docker `/health` in a sandboxed, registry-blocked environment),
  I said so instead of asking AI to describe a run that didn't happen.

## My non-negotiables

- No real secrets, `.env` values, tokens, or real personal/customer data
  ever goes into a prompt or into this repo. This project only ever uses
  made-up task titles.
- No AI-suggested line ships if I can't explain what it does and why.
- Every "AI helped" claim in my docs points at a specific file, command, or
  test — not just a vague sentence.

## My review rules

- Read the actual diff, not a summary of it.
- Re-run whatever the change touches: tests for backend changes, a real
  browser check for frontend changes, a real `curl`/build for
  Docker/CI changes.
- For security or lint findings, trace the flagged line back to where its
  data actually comes from before grading it Valid or a False Positive —
  don't just trust the tool's label.
- Grade AI suggestions the same way I'd grade a teammate's PR comment:
  useful, noise, or wrong, with a one-line reason.

## What I am still figuring out

- Where the line is between a "small bug fix" (in scope) and a "new
  feature" (out of scope) when a fix reveals a real gap — e.g. the
  accessibility follow-up (`aria-hidden` on the modal) that the modal-bug
  fix surfaced but that I deliberately didn't apply this round.
- How much of a static-analysis run (bandit/checkov) I should treat as
  required due diligence for every change vs. something I reach for only
  when touching security-sensitive code.
- How to keep AI-assisted docs from sounding like an AI wrote them — this
  playbook itself is a case in point.

## Decision Card

| Situation | What I do |
|---|---|
| New feature | Decide scope and constraints myself first; use AI to draft the implementation against that scope, not to decide the scope. |
| Code review | Read the real diff myself before or alongside any AI review; grade each AI comment useful/noise/wrong with a reason, like `docs/final-ai-review.md`. |
| Debugging | Reproduce the bug myself first (a failing test, a screenshot, a curl) so I know what "fixed" looks like before asking AI for a fix. |
| Infrastructure (CI/Docker) | Run the actual command locally or in CI — never accept "this should build" without a real build/run log. |
| Never paste | Real secrets, tokens, `.env` contents, production data, or any real person's information. |
| One rule | If I can't explain it, it doesn't go in as final work. |
