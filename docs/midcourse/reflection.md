# Reflection

I used Claude, working directly in the repo through Cowork, for the whole
sprint: planning the two features, writing the backend validation and
endpoint changes, wiring up the frontend hooks the baseline already exposed
for this purpose, writing the new pytest tests, and drafting these docs. I
reviewed and edited everything rather than accepting the first draft of
any file.

One place AI genuinely helped was catching a validation gap I wouldn't have
thought to test for on my own: the first draft of the due-date validator
used `datetime.fromisoformat`, which happily accepts a full timestamp like
`2026-07-26T10:00:00`. That's technically "valid ISO," but wrong for a field
that's supposed to be a plain calendar date. Naming that mismatch and
tightening it to a strict `YYYY-MM-DD` regex before parsing was a case where
having a second "pair of eyes" articulate the assumption out loud made the
bug obvious in a way that just staring at the code hadn't.

One place it slowed things down was the environment itself, not the model:
this sandbox has no PyPI or apt access and no root, so I couldn't actually
install FastAPI/pytest to run the real test suite here. Rather than
pretending a run happened, I fell back to re-implementing the exact
validation and overdue-computation logic in plain stdlib Python (no
framework needed) and running that directly, plus running the real `db.py`
module against a throwaway SQLite file, plus a second independent review
pass by a separate agent instance with no shared context. That's a
reasonable substitute for confidence, but it's not the same as a green
pytest run, and I was explicit about that gap in `verification.md` rather
than fabricating output — the actual `pytest -q` run still needs to happen
locally before this gets submitted.

The place my review changed the result the most was the tags API contract.
The AI's first instinct was to expose tags as the same raw comma-separated
string used for SQLite storage (`"backend,urgent"`) — technically correct
per the spec ("comma-separated field is acceptable"), but it would have
pushed trim/split parsing onto the frontend and every future API consumer.
I pushed back and set the boundary explicitly: CSV is a storage detail
internal to `main.py`; the API always speaks `list[str]`. Small change, but
it's the difference between one place owning the tag format and every
client having to reimplement it.
