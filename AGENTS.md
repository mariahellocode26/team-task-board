<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

# Team Kanban — instructions for coding agents

Team Kanban is a single shared, real-time Kanban board for small teams. Read
[docs/specs.md](docs/specs.md) before making product decisions — it is the
authority on what is in and out of scope, and it is deliberately restrictive.

## Repository layout

```
/backend       backend application and its tests   (FastAPI, SQLAlchemy, SQLite by default)
/docs          supporting documentation
/frontend      frontend application                 (built, working)
AGENTS.md      this file
openapi.yaml   the API agreement between frontend and backend
```

There is no root `package.json`. Each application owns its own dependencies and
scripts, so run every command from inside its own directory.

## Frontend

TanStack Start + React 19 + Vite 8, Tailwind CSS v4, shadcn/ui (new-york style,
slate base) and TypeScript. The package manager is **bun** — `frontend/bun.lock`
is the lockfile that matters. A `frontend/package-lock.json` is also tracked,
committed by accident when someone ran `npm install`; treat it as stray rather
than as a second source of truth, and do not update it.

```sh
cd frontend
bun install
bun run dev      # dev server
bun run build    # production build
bun run lint     # eslint
bun run format   # prettier
```

Notable paths:

- [frontend/src/routes/index.tsx](frontend/src/routes/index.tsx) — the board page.
- [frontend/src/components/kanban/](frontend/src/components/kanban/) — board column, task card, task dialog, join dialog.
- [frontend/src/components/ui/](frontend/src/components/ui/) — generated shadcn/ui primitives. Prefer composing these over hand-rolling new ones, and avoid editing them directly.
- [frontend/src/lib/kanban.ts](frontend/src/lib/kanban.ts) — the `Task` model, the `TaskStore` storage interface, `localTaskStore`, and `httpTaskStore`.
- [frontend/src/hooks/use-board.ts](frontend/src/hooks/use-board.ts) — all board mutations, written against `TaskStore` rather than against a concrete store.

`@/` resolves to `frontend/src/`.

Do not edit `frontend/src/routeTree.gen.ts`; TanStack Router generates it.

[frontend/vite.config.ts](frontend/vite.config.ts) wraps
`@lovable.dev/vite-tanstack-config`, which already registers the TanStack, React,
Tailwind and Nitro plugins. Adding any of them again breaks the build.

`frontend/bunfig.toml` sets `minimumReleaseAge` to 24h as a supply-chain guard.
Confirm with the user before adding any package to the excludes list.

### The storage seam

The spec (§16–17) requires that the UI never depend on a storage
implementation, so that browser storage can be swapped for a database later:

```
Kanban UI  ->  useBoard()  ->  TaskStore  ->  httpTaskStore -> backend/ (default, today)
                                          ->  localTaskStore -> localStorage (fallback)
```

`useBoard(store)` takes a `TaskStore` and now **defaults to `httpTaskStore`**,
which talks to `backend/` over HTTP per [openapi.yaml](openapi.yaml). Because
HTTP calls aren't synchronous the way `localStorage` reads/writes are,
`TaskStore` is an async, CRUD-shaped interface (`loadTasks`, `createTask`,
`updateTask`, `deleteTask`, `moveTask`) rather than a "load/save the whole
array" one. `localTaskStore` still exists as an offline/fallback
implementation of the same interface — it isn't wired up anywhere by default,
but pass it to `useBoard(localTaskStore)` if you need the board to work
without the backend running.

`httpTaskStore` is also where the `in-progress` (frontend) / `in_progress`
(wire, per docs/specs.md §27) naming mismatch gets mapped — see
`TO_WIRE_STATUS`/`FROM_WIRE_STATUS` in kanban.ts. The API base URL comes from
`VITE_API_BASE_URL` (see [frontend/.env.example](frontend/.env.example)),
defaulting to `http://localhost:8000`.

Known gap: clearing an optional field (assignee/description/due date) to
empty in the edit modal does not clear it on the backend, because
`TaskDialog` omits empty fields from its payload entirely instead of sending
them as `null`. Pre-existing behavior, carried over unchanged when the store
switched from `localStorage` to HTTP.

## Backend

FastAPI, implementing [openapi.yaml](openapi.yaml). Storage is a database via
SQLAlchemy — SQLite by default, configured by the `DATABASE_URL` environment
variable — seeded with sample data on first run only. See
[backend/README.md](backend/README.md) for the full design notes, including
exactly what keeps this database-agnostic for adding Postgres later.

```sh
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload   # docs at /docs, schema at /openapi.json
DATABASE_URL=... uvicorn app.main:app --reload   # point at a different database
pytest
```

Layout: `app/main.py` (lifespan: create tables + seed if empty; router wiring;
error-shape normalization), `app/models.py` (Pydantic schemas mirroring
openapi.yaml's components), `app/database.py` (SQLAlchemy engine/session,
`DATABASE_URL`, the one SQLite-specific branch), `app/orm.py` (the `TaskRow`
table model), `app/store.py` (`TaskStore`, wrapping a `Session`, kept separate
from routing), `app/routers/tasks.py` (the endpoints). Tests live in
`backend/tests/`, each against its own isolated in-memory SQLite database.

Data now survives a server restart — it didn't with the earlier in-memory
version. The default SQLite file (`team_kanban.db`) is gitignored.

**No authentication.** Every endpoint has `security: []`, matching
docs/specs.md §5.2/§33, which explicitly exclude accounts, logins and
passwords from the MVP. This was a deliberate decision, not an oversight — see
"openapi.yaml" below before adding any auth.

**CORS is wide open** (`allow_origins=["*"]` in `app/main.py`), on the same
reasoning as no-auth: the board has no origin worth restricting to and no
credentials in play. Needed because the frontend and backend run on different
ports/origins in dev.

Wired up to the frontend: `frontend/src/lib/kanban.ts`'s `httpTaskStore` is
the default `TaskStore` `useBoard()` uses — see "The storage seam" under
Frontend above.

## openapi.yaml

The agreed HTTP contract between the two applications, implemented by
`backend/` and matching what `frontend/`'s existing `Task`/`TaskStore` shapes
need. Two of the three open questions this file used to block on are now
settled and implemented:

1. **Status naming** — resolved. The wire format uses
   [docs/specs.md](docs/specs.md) §27's `in_progress` (underscore).
   [frontend/src/lib/kanban.ts](frontend/src/lib/kanban.ts)'s `ColumnId` still
   spells it `in-progress` (hyphen) internally; `httpTaskStore` maps between
   the two at the boundary.
2. **Reordering** — resolved. `POST /tasks/{taskId}/move` takes a target
   column and a 0-based index, mirroring `moveTask()` in
   [frontend/src/hooks/use-board.ts](frontend/src/hooks/use-board.ts) exactly,
   down to only renumbering the destination column.

Still open:

3. **Real-time transport.** Spec §14 requires real-time collaboration but does
   not say how. SSE, WebSocket and polling are all still on the table, and
   openapi.yaml has no streaming endpoint yet — a client has to poll
   `GET /tasks` for now.

## Working on this repo

- Build only what [docs/specs.md](docs/specs.md) defines. §33 lists the excluded
  features explicitly, and "it would be easy to add" is not a reason to add it.
- The spec sections that mandate browser storage (§16.1) describe the MVP as it
  stands. A backend supersedes them; say so in `/docs` rather than leaving the
  two in silent contradiction.
- Conflicts resolve last-change-wins (§15). No merge UI.
