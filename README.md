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
| ---------------------------- | ----------------------------------------- |
| [frontend/](frontend/)       | The web application — built and working   |
| [backend/](backend/)         | The backend and its tests — not started   |
| [docs/](docs/)               | Specification and supporting documents    |
| [openapi.yaml](openapi.yaml) | The API agreement — empty placeholder     |
| [AGENTS.md](AGENTS.md)       | Instructions for coding agents            |

Each application owns its own dependencies; there is no root `package.json`.

## Running the frontend

TanStack Start + React 19 + Vite, Tailwind CSS v4 and shadcn/ui, managed with
[bun](https://bun.sh).

```sh
cd frontend
bun install
bun run dev
```

Other scripts: `bun run build`, `bun run lint`, `bun run format`.

## Status

The frontend is complete against the MVP spec and persists the board to browser
storage through a `TaskStore` interface, so the UI has no dependency on how tasks
are stored. The backend is the next step: it should arrive as a second
`TaskStore` implementation behind that same interface.

Before the backend can be built, three decisions are outstanding — the stack, the
real-time transport, and how reordering is expressed over the wire. They are
written up in [AGENTS.md](AGENTS.md).

---

The frontend was originally generated with [Lovable](https://lovable.dev) from
the brief kept at [docs/frontend-brief.md](docs/frontend-brief.md).
