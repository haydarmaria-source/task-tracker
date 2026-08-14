# Agent Guardrails

Instructions for any AI coding assistant (Claude, Copilot, etc.) working in this repo.

## Stack

- Backend: Python 3.11, FastAPI, Pydantic v2, sqlite3 (stdlib, no ORM). Code in `backend/app/`.
- Frontend: static HTML/CSS/vanilla JS, no build step. Code in `frontend/`.
- Tests: pytest, `backend/tests/`. Fixtures give each test a fresh temp SQLite file.

## Run / test commands

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload        # http://localhost:8000, /health, /docs

# Frontend
open frontend/index.html directly, or:
python -m http.server 5500 --directory frontend

# Tests
cd backend && pytest -q

# Docker
docker build -t task-tracker .
docker run -p 8000:8000 task-tracker
curl http://localhost:8000/health
```

## Read-first / docs-first guardrail

Before changing anything, read in this order: this file, `README.md`,
`docs/midcourse/` (prior design decisions), and the file you're about to
touch, end to end. Do not guess at existing behavior — check `backend/app/`
or `frontend/` directly. If a change would contradict something written in
`docs/`, say so before making it rather than silently overriding it.

## Project rules (final project)

- Work happens on the `final-project` branch. Don't rewrite history on
  `master` or `mid-course-project`.
- No new product features: no comments, auth, production database,
  notifications, or unrelated UI changes.
- `app/` and `frontend/` may only change for a small, explainable bug fix,
  security fix, or documentation-supported correction — and any such change
  must be written up in `docs/final-ai-review.md` (what changed, why, how it
  was verified).
- Never paste real secrets, `.env` values, tokens, production logs, or real
  personal/customer data into a prompt or into the repo. There is no `.env`
  file in this repo; keep it that way.
- If a suggested line, command, or config choice can't be explained in
  plain language, it doesn't go in as final work — reject or rewrite it
  instead.
