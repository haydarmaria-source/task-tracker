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

- Workflow file: `.github/workflows/ci.yml` — two jobs, `test` (installs `backend/requirements.txt`, runs `pytest -q` on Python 3.11) and `docker` (builds the image, runs the container, waits for it to become healthy, then checks `/health` and the non-root user).
- Latest run: **green**, both jobs passed — [`Add CI workflow (pytest + Docker build/run/health check)` — run #1, commit `6fdbee4`](https://github.com/haydarmaria-source/task-tracker/actions/runs/33090091443), finished in 42s total.
- Test command used by CI: `pytest -q` (working directory `backend`, Python 3.11.16 via `actions/setup-python@v5`). CI output: `18 passed, 1 warning in 0.26s` — same result as the local run above.
- Shortcut check: no `continue-on-error`, no `|| true`, pytest is not skipped or conditional, Python version is pinned to `3.11` (not "latest"), dependency install (`pip install -r requirements.txt`) runs as its own step before tests.

## Docker evidence

- Build command: `docker build -t task-tracker .` — ran in the `docker` job of CI run [#1](https://github.com/haydarmaria-source/task-tracker/actions/runs/33090091443) (GitHub-hosted runner, which has normal registry access), completed in 19s with no errors.
- Run command: `docker run -d --name task-tracker -p 127.0.0.1:8000:8000 task-tracker` — container started successfully.
- `/health` check: **executed and passed**, in CI (this cloud sandbox's Docker daemon has no route to any container registry, so the build/run was verified on a GitHub Actions runner instead — see the run linked above for the full log). Actual output of `curl -i http://localhost:8000/health` inside the `Check /health` step:
  ```
  HTTP/1.1 200 OK
  date: Thu, 27 Aug 2026 15:51:47 GMT
  server: uvicorn
  content-length: 15
  content-type: application/json

  {"status":"ok"}
  ```
- Non-root check: yes — Dockerfile creates and switches to `appuser` (uid 1000) via `USER appuser`; confirmed both by the CI `Check non-root user` step (`docker exec task-tracker whoami` → `appuser`) and by `checkov` (`CKV_DOCKER_3` / `CKV_DOCKER_8` both pass).
- No-baked-secrets check: yes — there is no `.env` file anywhere in this repo, and `.dockerignore` explicitly excludes `.env`, `.env.*`, and `*.db` in case one is ever added. The Dockerfile only `COPY`s `backend/requirements.txt` and `backend/app/`, so `docs/`, `tests/`, `.git`, and the frontend never enter the image.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README: "The API runs at http://localhost:8000 ... `GET /health`" | Ran the exact README command, then `curl -i http://localhost:8000/health` | Confirmed — `200`, `{"status":"ok"}` | None |
| README: "Open `frontend/index.html` ... talks to the API" (implies a working Kanban board) | Served `frontend/` and loaded it in headless Chromium | **False as shipped** — the new-task modal covered the board on load instead of staying hidden | Fixed one CSS rule in `frontend/styles.css` (`.modal-backdrop[hidden] { display: none; }`); re-verified with screenshots that the board now loads clean and the modal opens/closes on click |
| README: "Run the tests ... `pytest -q`" (implies the full suite currently passes) | Ran `cd backend && pytest -q` after installing `requirements.txt` | Confirmed — `18 passed` | None |
| Mid-course-project claim (docs/midcourse/mini-adr.md area): tags are exposed by the API as a list, not the CSV string used internally | Read `backend/app/main.py` (`_to_task_dict`) and hit `POST /tasks` with tags, then `GET /tasks` | Confirmed — API returns `"tags": ["backend","urgent"]`, not a CSV string | None |
| Dockerfile: image builds and runs, `/health` returns 200 | Built and ran the image in GitHub Actions (CI run [#1](https://github.com/haydarmaria-source/task-tracker/actions/runs/33090091443)), since this session's local sandbox has no route to a container registry | Confirmed — build succeeded, container started, `/health` returned `200 {"status":"ok"}`, `whoami` inside the container returned `appuser` | None — the Dockerfile itself needed no changes, only the missing `HEALTHCHECK` added earlier (see Docker evidence) |
| README/docs: CI workflow exists and runs the suite on push/PR | Added `.github/workflows/ci.yml`, pushed to `final-project`, watched the run in the Actions tab | Confirmed — both `test` and `docker` jobs pass | Added `.github/workflows/ci.yml` |
