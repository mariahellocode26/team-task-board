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
/backend       backend application and its tests   (not started)
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
- [frontend/src/lib/kanban.ts](frontend/src/lib/kanban.ts) — the `Task` model and the `TaskStore` storage interface.
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
Kanban UI  ->  useBoard()  ->  TaskStore  ->  localStorage (today)
```

`useBoard(store)` takes a `TaskStore` and defaults to `localTaskStore`. When the
backend arrives it should land as a second `TaskStore` implementation passed into
that same hook — not as fetch calls sprinkled through the components.

## Backend

Not started. The stack has not been chosen yet; the spec (§36) leaves it open on
purpose. Confirm the choice with the user before scaffolding anything here.
Tests belong in `/backend` alongside the application.

## openapi.yaml

The agreed HTTP contract between the two applications. It is currently **empty**
— a deliberate placeholder. Its content has not been decided, so do not invent
endpoints; agree them with the user first.

Three questions are open and must be settled before it can be written:

1. **Status naming.** [docs/specs.md](docs/specs.md) §27 specifies `in_progress`,
   but [frontend/src/lib/kanban.ts](frontend/src/lib/kanban.ts) uses
   `in-progress`. The wire format has to pick one, and the other side maps to it.
2. **Real-time transport.** Spec §14 requires real-time collaboration but does
   not say how. SSE, WebSocket and polling are all still on the table.
3. **Reordering.** Spec §12.2 requires manual order to be preserved. How a drag
   is expressed over the wire — a move endpoint, a client-computed `order`, or a
   bulk per-column reorder — is undecided.

## Working on this repo

- Build only what [docs/specs.md](docs/specs.md) defines. §33 lists the excluded
  features explicitly, and "it would be easy to add" is not a reason to add it.
- The spec sections that mandate browser storage (§16.1) describe the MVP as it
  stands. A backend supersedes them; say so in `/docs` rather than leaving the
  two in silent contradiction.
- Conflicts resolve last-change-wins (§15). No merge UI.
