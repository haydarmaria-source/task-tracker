# User Stories — Mid-Course Project

## Feature 1: Due dates + overdue filter

**US-1.1** As a user, I want to set an optional due date when creating a task, so I know when it's supposed to be finished.
- Acceptance: `POST /tasks` accepts `due_date` as `YYYY-MM-DD`. Omitting it leaves the task without a due date.
- Acceptance: a due date in any other shape (e.g. `01/01/2099`, or a full datetime) is rejected with `422`.

**US-1.2** As a user, I want to change or clear a task's due date later, so plans can shift without recreating the task.
- Acceptance: `PUT /tasks/{id}` with `due_date` updates just that field; other fields are untouched.
- Acceptance: sending `due_date: null` clears it.

**US-1.3** As a user, I want overdue tasks to be visually obvious on the board, so nothing slips through.
- Acceptance: a task card shows a red "Overdue" pill when `due_date` is in the past and the task isn't `done`.
- Acceptance: a `done` task with a past due date is never shown as overdue.

**US-1.4** As a user, I want to filter the board to just overdue tasks, so I can triage quickly.
- Acceptance: `GET /tasks?overdue=true` returns only tasks currently overdue.
- Acceptance: the frontend has an "Overdue only" toggle that applies this filter live.

**AI assumption corrected:** the first draft validated due dates with `datetime.fromisoformat`, which happily accepts full datetimes like `2026-07-26T10:00:00`. That's wrong for a date-only field — a task shouldn't have a due *time*. I tightened this to a strict `YYYY-MM-DD` regex checked before parsing, and rejected anything else, so the field stays a plain calendar date.

## Feature 2: Tags / labels

**US-2.1** As a user, I want to add tags to a task, so I can group related work (e.g. `backend`, `urgent`).
- Acceptance: `POST /tasks` accepts `tags` as a list of strings; each is trimmed.
- Acceptance: a blank/whitespace-only tag is rejected with `422`, not silently dropped.

**US-2.2** As a user, I want a sane limit on tags, so a task can't accumulate an unbounded, unreadable list.
- Acceptance: more than 10 tags on one task is rejected with `422`.
- Acceptance: a single tag longer than 30 characters is rejected with `422`.

**US-2.3** As a user, I want to edit a task's tags without affecting its other fields, so retagging is a lightweight action.
- Acceptance: `PUT /tasks/{id}` with only `tags` set leaves title/status/due date/etc. unchanged.
- Acceptance: updating an unrelated field (e.g. `status`) leaves existing tags untouched.

**US-2.4** As a user, I want to filter the board by tag, so I can see just one category of work.
- Acceptance: `GET /tasks?tag=backend` returns only tasks with that exact tag (case-insensitive).
- Acceptance: the frontend has a tag filter input that applies this live.

**US-2.5** As a user, I want tags displayed as chips on each card, so I don't have to open a task to see its labels.
- Acceptance: each tag renders as its own small chip in the card's meta row.

**AI assumption corrected:** the first draft stored tags as a raw comma-joined string and returned that same string from the API (`"backend,urgent"`), pushing parsing onto the frontend. I changed the API contract so `tags` is always a `list[str]` in requests and responses — CSV is purely an internal SQLite storage detail — because a raw string forces every consumer (frontend, tests, future API clients) to re-implement the same trim/split logic.
