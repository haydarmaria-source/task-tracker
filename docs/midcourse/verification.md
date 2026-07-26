# Verification — Mid-Course Project

## Environment note

This work was done inside a sandboxed AI coding session with no PyPI/apt
access and no root, so `pip install -r requirements.txt` could not run and
the actual FastAPI test suite could not be executed end-to-end here. Every
piece of new logic was still verified two ways: (1) by re-implementing the
exact validation/computation logic as standalone stdlib-only Python and
running it directly (no fastapi/pydantic needed for `re`, `datetime`,
`sqlite3`), and (2) by tracing each new test by hand against the real
`models.py`/`db.py`/`main.py` — including a second, independent pass by a
separate review agent given the same task. **You still need to run `pytest`
yourself once, from `backend/`, to get an official pass/fail record before
submitting** — see "Backend test results" below for the command.

## Baseline check

Before any changes, the repo had 6 passing tests in
`backend/tests/test_tasks.py` (health check, create/defaults, blank-title
rejection, list + status filter, 404 on missing task, update, delete),
covering the Modules 1-3 CRUD baseline. No changes were made to any of
these tests or their behavior.

## Backend test results

Run this locally to get the real result:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

Expected: 16 passed (the original 6 baseline tests, unmodified, plus 10 new
tests — 5 for due dates, 5 for tags — added in `test_tasks.py`). If anything
fails, paste the pytest output back and it'll get fixed before submission.

## Manual browser checks (to do locally)

1. `uvicorn app.main:app --reload` from `backend/`, then open
   `frontend/index.html`.
2. Create a task with a due date in the past → card should show a red
   "Overdue" pill.
3. Create a task with a due date in the future → card should show a neutral
   "Due <date>" pill, not overdue.
4. Mark an overdue task `done` → the overdue pill should disappear (a done
   task is never overdue).
5. Add tags like `backend, urgent` in the modal → chips appear on the card.
6. Type into the "Filter by tag" box → board should narrow to matching
   cards only.
7. Check "Overdue only" → board should show just overdue tasks; toggling it
   off restores the full board.

## Behavior contract: before vs. after

| Endpoint | Baseline behavior | After this project |
|---|---|---|
| `POST /tasks` | requires `title`, defaults `status`/`priority` | unchanged, plus optional `due_date`/`tags` with new validation |
| `GET /tasks` | filters: `status`, `priority`, `assignee` | same filters unchanged, plus new `tag`, `overdue` filters |
| `GET /tasks/{id}` | 404 on missing | unchanged |
| `PUT /tasks/{id}` | partial update, untouched fields survive | unchanged for existing fields; same partial-update semantics now also apply to `due_date`/`tags` |
| `DELETE /tasks/{id}` | 204, then 404 on re-fetch | unchanged |

No refactor pass was needed beyond the initial implementation — the
baseline already exposed `cardExtras()` / `renderFeatureFields()` /
`collectFeatureFields()` hooks in `app.js` specifically for this kind of
extension, so the frontend integration was additive rather than a rewrite.

## Break Test evidence

Two of the new validators were deliberately broken, re-run, and restored to
confirm the corresponding tests actually catch a regression rather than
passing vacuously.

**Break Test 1 — `due_date` format validation** (backs
`test_create_task_rejects_invalid_due_date_format`)

```
-- with validation intact (current code) --
PASS (correctly rejected): due_date must be in YYYY-MM-DD format
-- with validation skipped entirely (simulated bug) --
Bug reproduced: garbage date WAS accepted and would be stored -> '01/01/2099'
```

**Break Test 2 — empty-tag rejection** (backs
`test_create_task_rejects_empty_tag`)

```
-- with validation intact (current code) --
PASS (correctly rejected): tags must not contain blank values
-- with the blank-check disabled (simulated bug) --
Bug reproduced: blank tag WAS accepted -> ['ok', '']
```

Both confirm the tests fail loudly when the guard they exist to check is
removed, not just when everything is already working.

## Additional verification performed

- `python3 -m py_compile` / `compile()` syntax checks on
  `models.py`, `db.py`, `main.py`, `test_tasks.py`, and `node --check` on
  `app.js` — all clean.
- Real execution of `db.py`'s `init_db()`, insert, and query against a
  throwaway SQLite file (stdlib `sqlite3`, no install needed), confirming
  the CSV tag round-trip and overdue date-string comparison both produce
  correct results against the actual (not reimplemented) `db.py` module.
- An independent review pass (separate agent, same code, no shared
  context) traced all 10 new tests by hand against `models.py`/`db.py`/
  `main.py` and reported no discrepancies.
