# Task Tracker

A small Kanban task tracker: FastAPI + SQLite backend, static HTML/JS frontend.
Built across Modules 1-3 as a CRUD board, then extended in the mid-course
project with due dates and tags.

## Run the backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at http://localhost:8000 (interactive docs at `/docs`).

## Open the frontend

Open `frontend/index.html` in a browser (double-click, or serve the folder with
`python -m http.server` from `frontend/`). It talks to the API at
`http://localhost:8000`.

## Run the tests

```bash
cd backend
pytest -q
```

Tests use a fresh temporary SQLite database per test, so they never touch your
real `task_tracker.db`.

## Mid-course project: due dates + tags

Two features were added on top of the Modules 1-3 CRUD baseline:

- **Due dates + overdue filter** — optional `due_date` (`YYYY-MM-DD`) on a
  task. `overdue` is computed on every response (past due date, not
  `done`), not stored. Filter with `GET /tasks?overdue=true`.
- **Tags** — optional list of short tags per task, validated (non-blank,
  max 10 tags, 30 chars each). Filter with `GET /tasks?tag=<name>`.

Both are visible in the Kanban UI: the task modal has due date / tags
inputs, cards show a due-date or overdue pill plus tag chips, and the
toolbar has a tag filter box and an "Overdue only" toggle.

See `docs/midcourse/` for the user stories, design decisions (mini-ADR),
prompt log, verification evidence, and reflection for this project.
