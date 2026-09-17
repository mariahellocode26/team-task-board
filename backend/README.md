# Backend

Not started.

This directory will hold the Team Kanban backend application and its tests.

## Before writing code here

The stack has not been chosen. [docs/specs.md](../docs/specs.md) §36 leaves the
backend technology deliberately open, so agree it with the project owner rather
than picking one.

The HTTP contract lives in [openapi.yaml](../openapi.yaml) at the repository
root. That file is currently empty on purpose — its content is undecided. Three
questions block it:

1. **Status naming** — the spec says `in_progress`, the frontend uses
   `in-progress`. One of them has to win on the wire.
2. **Real-time transport** — spec §14 requires real-time collaboration but does
   not specify a mechanism. SSE, WebSocket and polling are all open.
3. **Reordering** — spec §12.2 requires manual ordering to survive. Whether a
   drag becomes a move endpoint, a client-supplied `order` value, or a bulk
   per-column reorder is undecided.

## How this fits the frontend

The frontend already isolates storage behind a `TaskStore` interface in
[frontend/src/lib/kanban.ts](../frontend/src/lib/kanban.ts), consumed by
[frontend/src/hooks/use-board.ts](../frontend/src/hooks/use-board.ts):

```
Kanban UI  ->  useBoard()  ->  TaskStore  ->  localStorage (today)
                                          ->  this backend (next)
```

This backend should become a second `TaskStore` implementation passed into the
same hook. The UI itself should not need to change.

Note that this supersedes spec §16.1, which describes browser storage as the MVP
storage layer. §16.2 anticipates exactly this replacement.

## Scope

Build only what [docs/specs.md](../docs/specs.md) defines. §33 lists the excluded
features explicitly. In particular there is no authentication, no user accounts,
one board only, and three fixed columns. Conflicts resolve last-change-wins
(§15).
