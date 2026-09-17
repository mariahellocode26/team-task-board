# Backend

A FastAPI implementation of [openapi.yaml](../openapi.yaml), backed by a
SQLAlchemy-managed database (SQLite by default) seeded with sample data on
first run. There is no authentication — see "Scope" below.

## Run it

```sh
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

The server starts on `http://127.0.0.1:8000`. Interactive docs are at
`/docs`, the raw schema at `/openapi.json`, and a liveness check at
`/health`.

## Database

The connection string comes from the `DATABASE_URL` environment variable:

```sh
DATABASE_URL=sqlite:///./team_kanban.db uvicorn app.main:app --reload   # default if unset
DATABASE_URL=postgresql+psycopg://user:pass@localhost/team_kanban uvicorn app.main:app --reload
```

With `make dev`, prefix the same way: `DATABASE_URL=... make dev`. If unset,
it defaults to a local SQLite file (`team_kanban.db`, gitignored) in whichever
directory the server is started from — nothing to configure for local dev.

Tables are created automatically on startup if they don't exist, and the
four sample tasks are inserted only if the table is empty — restarting
against a database that already has real data never re-adds them, and data
now survives a restart (unlike the earlier in-memory version).

**Database-agnostic by design**, so Postgres support later is a matter of
installing that dialect's driver (e.g. `psycopg`) and setting `DATABASE_URL`
— no code changes should be needed outside `app/database.py`:

- Every query goes through SQLAlchemy's ORM (`app/store.py`), never raw SQL.
- `app/orm.py`'s column types (`String`, `Text`, `Integer`) are plain and
  portable — priority/status are stored as strings, not a database-native
  enum type, since not every backend supports those the same way.
- The one SQLite-specific detail (`connect_args={"check_same_thread": False}`,
  needed because FastAPI's sync routes run in a thread pool) is isolated to a
  single conditional in `app/database.py`'s `_engine_kwargs()`. Nothing else
  in the codebase knows or cares which database is configured.
- Not done yet: schema changes currently rely on `create_all()` at startup,
  which only ever adds missing tables — it won't migrate an existing one. A
  real migration tool (e.g. Alembic) would be the next step before this schema
  needs to change against a database already holding real data.

## Test it

```sh
cd backend
pytest
```

## Layout

```
app/
  main.py           FastAPI app: lifespan (init + seed DB), router wiring, error-shape normalization
  models.py         Pydantic schemas — mirrors openapi.yaml's components exactly
  database.py       SQLAlchemy engine/session config; DATABASE_URL; the one SQLite-specific branch
  orm.py            SQLAlchemy TaskRow model — how a task is laid out in the database
  store.py          TaskStore: the operations the API needs, implemented against a Session
  routers/
    tasks.py        The /tasks endpoints
tests/
  conftest.py       Fixtures: isolated in-memory SQLite database per test, dependency override
  test_tasks.py     Behavioral tests for every endpoint and error case
```

## Design notes

**Storage is a database, kept behind its own module.** `app/store.py`'s
`TaskStore` wraps a SQLAlchemy `Session` and exposes exactly the operations
`app/routers/tasks.py` needs — the router never touches SQLAlchemy directly.
It exists as its own module specifically so the storage layer can keep
changing (in-memory → SQLite → possibly Postgres) without touching the
routing, the same separation-of-concerns docs/specs.md §16-17 asks the
frontend to keep. See "Database" above for how a different database gets
plugged in.

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

**Seed data matches the frontend's own seed data.** `seed_rows()` in
`app/store.py` is the same four tasks as `seedTasks` in
[frontend/src/lib/kanban.ts](../frontend/src/lib/kanban.ts), so the board
looks identical whether it's reading from browser storage or this API.

## How this fits the frontend

```
Kanban UI  ->  useBoard()  ->  TaskStore  ->  httpTaskStore -> this backend (default, today)
                                          ->  localTaskStore -> localStorage (fallback)
```

Wired up: `frontend/src/lib/kanban.ts`'s `httpTaskStore` is the `TaskStore`
`useBoard()` uses by default, talking to this API over HTTP. It maps the
frontend's internal `ColumnId` spelling (`in-progress`, hyphenated) to this
API's `in_progress` (underscored, per docs/specs.md §27) at the boundary;
see openapi.yaml's info.description for why that mapping exists.

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
