# Prompt Log — Mid-Course Project

AI assistant used: Claude (Cowork), working directly in the repo with file
read/edit/bash tools.

## Feature 1: Due dates + overdue filter

**Prompt 1 (weak → strong rewrite)**

- Weak: *"add due dates to tasks"*
- Why it's weak: no field format, no answer to "overdue computed how/where",
  no scope on frontend vs backend, nothing about validation or tests.
- Strong: *"Add an optional `due_date` field (YYYY-MM-DD) to the Task model,
  validated at the API layer with a 422 on bad format. Compute `overdue` as
  a read-time boolean (not a stored column) based on today's UTC date and
  whether status is 'done'. Add a `?overdue=true` filter to `GET /tasks`."*
- Result: AI produced the field, validator, and computed-property design in
  one pass instead of three follow-up corrections.

**Prompt 2:** *"Should overdue be a stored column or computed on read?"*
- AI response: recommended computed-on-read, explaining that a stored
  column goes stale as calendar days pass without a write to the row.
- Accepted as-is — this became the ADR decision.

**Prompt 3:** *"The date validator uses `datetime.fromisoformat`, which
accepts full datetimes like `2026-07-26T10:00:00`. Is that a problem for a
date-only field?"*
- AI response: agreed it was a gap, since a due date shouldn't carry a time
  component, and suggested a strict `^\d{4}-\d{2}-\d{2}$` regex check before
  `date.fromisoformat`, so both malformed strings and accidental datetimes
  are rejected the same way.
- Accepted and edited into `models.py` (`_validate_due_date`).

## Feature 2: Tags / labels

**Prompt 4:** *"Add tags to tasks — list or comma-separated field is fine
per the spec. Validate trimmed, non-empty tag values."*
- AI response: proposed a normalized many-to-many `tags` table with a join
  table as the "correct" relational design.
- Rejected as out of scope — noted in the mini-ADR. A join table adds
  migrations and cascade-delete handling for a feature that the assignment
  spec explicitly says a comma-separated field satisfies. Redirected the AI
  to the simpler CSV-column approach.

**Prompt 5:** *"Store tags as CSV internally, but should the API also
expose them as a raw CSV string, or as a list?"*
- AI response: initially returned `tags` as the raw CSV string in API
  responses (`"backend,urgent"`), matching the storage shape directly.
- Edited: changed the API contract so `tags` is always `list[str]` in both
  requests and responses, with CSV join/split fully internal to
  `main.py` (`_tags_to_csv` / `_tags_from_csv`). Raw CSV in the API would
  have pushed parsing onto the frontend and every future client.

**Prompt 6:** *"What happens if someone sends 40 one-character tags?"*
- AI response: pointed out there was no cap and suggested adding a max
  count and max length, defaulting to something reasonable since the spec
  only said "optional maximum count/length."
- Accepted: capped at 10 tags / 30 characters each, enforced in the same
  Pydantic validator as the blank-tag check, with a matching
  `test_create_task_rejects_too_many_tags` test added.
