# Team Kanban

A single shared, real-time Kanban board for small teams. Open a shared URL, enter
a display name, and collaborate on one board with three fixed columns:

```
To Do  ->  In Progress  ->  Done
```

Tasks carry a title, description, assignee, priority (low/medium/high) and an
optional due date. Any member can create, edit, delete, assign, prioritise,
reorder and move any task.

The full product specification is in [docs/specs.md](docs/specs.md).

## Layout

| Path                         | What it is                                |
| ---------------------------- | ------------------------------------------ |
| [frontend/](frontend/)       | The web application — built and working    |
| [backend/](backend/)         | FastAPI + SQLAlchemy backend — built and working |
| [docs/](docs/)               | Specification and supporting documents     |
| [openapi.yaml](openapi.yaml) | The API agreement, implemented by both sides |
| [AGENTS.md](AGENTS.md)       | Instructions for coding agents             |

Each application owns its own dependencies; there is no root `package.json`.

## Running it locally

```sh
# terminal 1 — backend, http://localhost:8000 (docs at /docs)
cd backend
pip install -e ".[dev]"
make dev

# terminal 2 — frontend, http://localhost:8080
cd frontend
npm install   # or: bun install
npm run dev   # or: bun run dev
```

The frontend talks to the backend by default (`VITE_API_BASE_URL` defaults to
`http://localhost:8000`; see [frontend/.env.example](frontend/.env.example)).
The backend defaults to a local SQLite file (`DATABASE_URL`; see
[backend/.env.example](backend/.env.example)), seeded with sample tasks on
first run, and now persists across restarts.

## Testing

```sh
cd backend
make test   # or: pytest — 23 tests, each against its own isolated in-memory DB
```

```sh
cd frontend
npx tsc --noEmit   # type-check
npm run lint       # eslint
npm run build      # production build
```

There's no frontend test suite yet — verification so far has been type-checking,
linting, building, and manual/scripted checks against the running backend.

## Status

Both applications are built and wired together: the frontend's `httpTaskStore`
talks to the backend over HTTP per [openapi.yaml](openapi.yaml), which the
backend implements with FastAPI and a SQLAlchemy-managed database (SQLite by
default, database-agnostic by design — see [backend/README.md](backend/README.md)
for what that means concretely). There's no authentication, matching
docs/specs.md's explicit MVP scope.

Still open: real-time collaboration (docs/specs.md §14) doesn't have a
transport yet — SSE, WebSocket, and polling are all still on the table. See
[AGENTS.md](AGENTS.md) for details.

---

The frontend was originally generated with [Lovable](https://lovable.dev) from
the brief kept at [docs/frontend-brief.md](docs/frontend-brief.md).
