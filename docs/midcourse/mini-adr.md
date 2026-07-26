# Mini-ADR — Due Dates + Overdue Filter, and Tags

## Context

The baseline Task Tracker (Modules 1-3) is a FastAPI + SQLite backend with a
static HTML/JS Kanban frontend. It already exposes extension points for
exactly this kind of work: `cardExtras()`, `renderFeatureFields()`, and
`collectFeatureFields()` in `app.js` are no-op hooks meant to be overridden
by features, so the frontend integration was largely additive rather than
invasive.

## Decision

### Due dates

- Store `due_date` as a plain `TEXT` column (`YYYY-MM-DD` or `NULL`), validated
  at the API boundary with a regex + `date.fromisoformat`, rather than a SQL
  `DATE` type. SQLite has no real date type anyway, so this keeps the schema
  honest about what it actually stores.
- Compute `overdue` **on read**, not on write. Overdue is a function of
  "today," which changes independent of any write to the task, so storing it
  as a column would go stale the moment a day passes without an edit.
  `_to_task_dict()` in `main.py` computes it from `due_date`, `status`, and
  the current UTC date on every response.
- `overdue` is not stored, so filtering by it (`GET /tasks?overdue=true`)
  happens in Python after the SQL query, not in a `WHERE` clause.

### Tags

- Store tags as a normalized comma-separated `TEXT` column internally, but
  the **API contract** always uses `list[str]` — CSV is a storage detail,
  never exposed to clients. `_tags_to_csv` / `_tags_from_csv` in `main.py`
  are the only place that boundary is crossed.
- Validate tags in the Pydantic layer: trim, reject blank entries, cap at 10
  tags / 30 chars each. These limits are opinionated defaults, not something
  the spec mandated precisely, chosen to keep chips readable on a card.
- Tag filtering (`GET /tasks?tag=x`) is an exact, case-insensitive match
  against the parsed tag list, done in Python for the same reason as
  `overdue` — no derived column to index on.

## Alternatives considered and rejected

- **A real `tags` table with a join table (many-to-many).** This is the
  "correct" normalized design and is what the AI suggested first. Rejected
  as out of scope: it means new migrations, join queries, and cascade-delete
  handling for a feature whose spec explicitly calls out "list or normalized
  comma-separated field" as acceptable. A join table is the right call if
  tags need their own metadata (color, owner) later; today they don't.
- **Storing `overdue` as a computed/generated SQL column** using SQLite's
  `GENERATED ALWAYS AS`. Rejected because it still can't reference
  "today's date" at query time without a scalar function, and it would tie
  overdue status to whatever the column was computed at, not "now." Simpler
  to compute in the response layer.
- **A generic JSON blob column for extensibility** (storing `{"due_date":
  ..., "tags": [...]}` as one `TEXT` column instead of separate typed
  columns). Rejected: it loses the ability for SQLite to do anything useful
  with the data and pushes all validation into application code with no
  schema backstop at all — strictly worse than what we have.
- **Client-side-only overdue detection** (frontend compares `due_date` to
  `new Date()`). Rejected because the same `/tasks?overdue=true` filter is
  needed for the API/tests, and duplicating the "what counts as overdue"
  rule in two languages is exactly the kind of drift bugs come from.
