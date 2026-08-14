# Release Evidence

## Baseline

- Branch: `final-project` (created from `mid-course-project`)
- Date: 2026-08-14
- Local app run command: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload`
- `/health` result: `curl -i http://localhost:8000/health` → `HTTP/1.1 200 OK`, body `{"status":"ok"}`. Also confirmed `POST /tasks` (201) and `GET /tasks` (200) against the running server.
- Frontend check: opened `frontend/index.html` (served locally with `python -m http.server 5500 --directory frontend`) in a headless Chromium session and screenshotted it. **Found a real bug during this check**: the "New task" modal rendered open on every page load, covering the whole board, instead of staying hidden until "+ New task" is clicked. Root cause and fix are in the AI security/code review log in `docs/final-ai-review.md`; after the one-line CSS fix, the board loads clean and the create/edit modal opens and closes correctly (verified with before/after screenshots).
- Test command: `cd backend && pytest -q`
- Test result: `18 passed, 1 warning in 0.26s` (warning is a non-fatal `httpx`/starlette deprecation notice, not a failure). No pre-existing or newly-introduced test failures.

## CI evidence

- Workflow file: `.github/workflows/ci.yml`
- Latest run link or note: not yet pushed to GitHub from this session — see the note in the "How to finish this" section below. The workflow was authored and its logic was exercised locally: the exact steps it runs (`pip install -r requirements.txt` then `pytest -q` from `backend/`) were run directly in this environment and produced the "18 passed" result above.
- Test command used by CI: `pytest -q` (working directory `backend`, Python 3.11 via `actions/setup-python@v5`)
- Shortcut check: no `continue-on-error`, no `|| true`, pytest is not skipped or conditional, Python version is pinned to `3.11` (not "latest"), dependency install (`pip install -r requirements.txt`) runs as its own step before tests.

## Docker evidence

- Build command: `docker build -t task-tracker .`
- Run command: `docker run --rm -p 8000:8000 task-tracker`
- `/health` check: **not executed in this session** — this cloud sandbox's Docker daemon has no route to any container registry (`docker pull python:3.11-slim` and even `docker pull hello-world` both fail with `403 Forbidden` from `registry-1.docker.io`; PyPI access works fine, registry access does not). Rather than fabricate a result, the Dockerfile was instead validated statically with `checkov` (a real static-analysis tool, not the app under test): it initially failed `CKV_DOCKER_2` (missing `HEALTHCHECK`), which was fixed by adding a `HEALTHCHECK` that curls `/health` via Python's `urllib`; after the fix, `checkov -f Dockerfile` reports zero failed checks. **Action needed before submission:** run the three commands above on a machine with normal internet access and confirm `curl http://localhost:8000/health` returns `200 {"status":"ok"}`, then replace this line with the actual result.
- Non-root check: yes — Dockerfile creates and switches to `appuser` (uid 1000) via `USER appuser`; confirmed by checkov (`CKV_DOCKER_3` / `CKV_DOCKER_8` both pass).
- No-baked-secrets check: yes — there is no `.env` file anywhere in this repo, and `.dockerignore` explicitly excludes `.env`, `.env.*`, and `*.db` in case one is ever added. The Dockerfile only `COPY`s `backend/requirements.txt` and `backend/app/`, so `docs/`, `tests/`, `.git`, and the frontend never enter the image.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README: "The API runs at http://localhost:8000 ... `GET /health`" | Ran the exact README command, then `curl -i http://localhost:8000/health` | Confirmed — `200`, `{"status":"ok"}` | None |
| README: "Open `frontend/index.html` ... talks to the API" (implies a working Kanban board) | Served `frontend/` and loaded it in headless Chromium | **False as shipped** — the new-task modal covered the board on load instead of staying hidden | Fixed one CSS rule in `frontend/styles.css` (`.modal-backdrop[hidden] { display: none; }`); re-verified with screenshots that the board now loads clean and the modal opens/closes on click |
| README: "Run the tests ... `pytest -q`" (implies the full suite currently passes) | Ran `cd backend && pytest -q` after installing `requirements.txt` | Confirmed — `18 passed` | None |
| Mid-course-project claim (docs/midcourse/mini-adr.md area): tags are exposed by the API as a list, not the CSV string used internally | Read `backend/app/main.py` (`_to_task_dict`) and hit `POST /tasks` with tags, then `GET /tasks` | Confirmed — API returns `"tags": ["backend","urgent"]`, not a CSV string | None |
| Dockerfile: image builds and runs, `/health` returns 200 | Attempted `docker build` in this session | **Could not verify here** — registry access is blocked in this sandbox (see Docker evidence above) | Statically checked with `checkov` instead; live build/run still needs to happen on a normally-networked machine before submission |

## How to finish this before submitting

Two things in this file are placeholders because this session's cloud sandbox has no route to a container registry:

1. Run `docker build -t task-tracker .`, then `docker run --rm -p 8000:8000 task-tracker`, then `curl -i http://localhost:8000/health` on your own machine (or in GitHub Actions), and paste the real `/health` result into the "Docker evidence" section above.
2. Push the `final-project` branch to GitHub, let the CI workflow run once, and paste the run link into "CI evidence" above.
