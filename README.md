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

## Final Project

Branch reviewed: final-project

### What this submission demonstrates

- Existing Task Tracker app still runs inside the intended course scope (verified: `pytest -q` → 18 passed; `GET /health` → 200).
- One small, documented frontend bug fix: the new-task modal rendered open on every page load instead of staying hidden (`frontend/styles.css`); see `docs/final-ai-review.md` for the diagnosis and fix.
- CI runs the pytest suite on push and pull request (`.github/workflows/ci.yml`).
- Docker image builds and runs with `/health` returning 200 (`Dockerfile`, `.dockerignore`) — see `docs/release-evidence.md` for one open item: this session's sandbox couldn't reach a container registry to run the build itself, so that step still needs to be run and recorded on a normally-networked machine before submission.
- AI code review, security review, and ownership evidence is in `docs/final-ai-review.md`; the personal AI playbook is in `docs/ai-playbook.md`.

### How to run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `frontend/index.html` in a browser (or `python -m http.server 5500 --directory frontend`).

### How to run tests

```bash
cd backend && pytest -q
```

### How to run with Docker

```bash
docker build -t task-tracker .
docker run --rm -p 8000:8000 task-tracker
curl -i http://localhost:8000/health
```

### Evidence files

- docs/release-evidence.md
- docs/final-ai-review.md
- docs/ai-playbook.md

### AI assistance summary

AI helped draft or review: CI workflow, Dockerfile, security scan follow-up (bandit/checkov), documentation, and the frontend bug diagnosis.
I verified the work by: running the real pytest suite, curling the live `/health` endpoint, headless-browser screenshots of the frontend before/after the fix, and re-running checkov after the Dockerfile change.
One AI suggestion I rejected or corrected: an earlier due-date validator draft accepted full ISO timestamps instead of plain calendar dates — tightened to a strict `YYYY-MM-DD` check (see `backend/app/models.py` and `docs/final-ai-review.md`).
