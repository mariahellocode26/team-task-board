# Backend

A FastAPI implementation of [openapi.yaml](../openapi.yaml), backed by an
in-memory store seeded with sample data. There is no authentication — see
"Scope" below.

## Run it

```sh
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

The server starts on `http://127.0.0.1:8000`. Interactive docs are at
`/docs`, the raw schema at `/openapi.json`, and a liveness check at
`/health`.

## Test it

```sh
cd backend
pytest
```

## Layout

```
app/
  main.py           FastAPI app: router wiring + error-shape normalization
  models.py         Pydantic schemas — mirrors openapi.yaml's components exactly
  store.py          In-memory TaskStore: seed data, ordering rules, thread-safety
  routers/
    tasks.py        The /tasks endpoints
tests/
  conftest.py       Fixtures: isolated store per test, dependency override
  test_tasks.py     Behavioral tests for every endpoint and error case
```

## Design notes

**Storage is in-memory and resets on restart.** `app/store.py`'s
`TaskStore` holds everything in a plain dict behind a lock — there is no
database yet. It exists as its own module specifically so it can be
swapped for a real database later without touching `app/routers/tasks.py`,
the same separation-of-concerns docs/specs.md §16-17 asks the frontend to
keep.

**Ordering mirrors the frontend exactly.** The frontend's own
localStorage-backed implementation
([frontend/src/hooks/use-board.ts](../frontend/src/hooks/use-board.ts))
already encodes the ordering rules docs/specs.md §12.2 requires: new tasks
append to the end of their column; changing a task's column via edit sends
it to the end of the new column; a drag-and-drop move renumbers only the
destination column's `order` values, leaving gaps in the source column
where a task was removed. `TaskStore` reproduces this rule-for-rule so the
board behaves identically regardless of which store is behind it.

**Error responses are normalized to match openapi.yaml.** FastAPI's
defaults don't match the contract on their own — a 404 nests its message
under a `"detail"` key, and body-validation failures return 422 rather than
400 — so `app/main.py` installs two exception handlers that reshape both
into the flat `{"message": string}` `Error` schema the contract defines.
Verified against the real, running server, not just inferred from FastAPI's
defaults.

**Seed data matches the frontend's own seed data.** `_seed_records()` in
`app/store.py` is the same four tasks as `seedTasks` in
[frontend/src/lib/kanban.ts](../frontend/src/lib/kanban.ts), so the board
looks identical whether it's reading from browser storage or this API.

## How this fits the frontend

```
Kanban UI  ->  useBoard()  ->  TaskStore  ->  localStorage (today)
                                          ->  this backend (next, via HTTP)
```

This backend is not yet wired up to the frontend — no HTTP-backed
`TaskStore` implementation exists on the frontend side yet. That adapter
should map the frontend's internal `ColumnId` spelling (`in-progress`,
hyphenated) to this API's `in_progress` (underscored, per
docs/specs.md §27) at the boundary; see openapi.yaml's info.description for
why that mapping exists.

This supersedes docs/specs.md §16.1, which describes browser storage as the
MVP storage layer — §16.2 anticipates exactly this replacement.

## Scope

Build only what [docs/specs.md](../docs/specs.md) defines. §33 lists the
excluded features explicitly. In particular:

- **No authentication.** §5.2 and §33 explicitly exclude accounts, logins,
  passwords and OAuth. Every endpoint in openapi.yaml has `security: []`.
  This was confirmed deliberately after considering the alternative — see
  the project's AGENTS.md if that decision needs revisiting.
- One board only, three fixed columns — there is no `/board` resource.
- Conflicts resolve last-change-wins (§15); there is no merge logic here,
  the store just accepts whichever write arrives.

## Not yet built

Real-time collaboration (specs.md §14) — the transport (SSE, WebSocket, or
polling) hasn't been decided, and openapi.yaml doesn't define a streaming
endpoint yet, so this backend has no push mechanism. A client has to poll
`GET /tasks` to see another user's changes.
