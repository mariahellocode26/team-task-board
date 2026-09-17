"""In-memory task store.

This plays the role docs/specs.md §16-17 assigns to a storage layer: a
concern kept separate from the HTTP routing so it can later be swapped for
a real database without changing the API contract. Data lives only in
process memory and resets whenever the server restarts.

The ordering rules below intentionally mirror the frontend's own
localStorage-backed implementation in frontend/src/hooks/use-board.ts, so
that a task's manually-chosen position (specs.md §12.2) behaves the same
way regardless of which store is behind the API.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, replace
from threading import Lock

from app.models import Priority, Status, Task, TaskCreate, TaskMove, TaskUpdate


@dataclass
class _Record:
    """Internal representation; identical shape to Task but mutable."""

    id: str
    title: str
    priority: Priority
    status: Status
    order: int
    description: str | None = None
    assignee: str | None = None
    dueDate: str | None = None

    def to_task(self) -> Task:
        return Task(
            id=self.id,
            title=self.title,
            description=self.description,
            assignee=self.assignee,
            priority=self.priority,
            dueDate=self.dueDate,
            status=self.status,
            order=self.order,
        )


def _seed_records() -> list[_Record]:
    """Sample data so the frontend has something to show immediately.

    Deliberately the same four tasks the frontend's own localStorage seed
    (frontend/src/lib/kanban.ts seedTasks) uses, so the board looks
    identical whether it's reading from browser storage or this API.
    """

    return [
        _Record(
            id="t1",
            title="Draft onboarding checklist",
            description="Outline the first-week steps for new teammates.",
            assignee="Maria",
            priority=Priority.HIGH,
            dueDate="2026-09-18",
            status=Status.TODO,
            order=0,
        ),
        _Record(
            id="t2",
            title="Collect feedback from pilot users",
            description="Summarise the five interviews into key themes.",
            assignee="Sam",
            priority=Priority.MEDIUM,
            status=Status.TODO,
            order=1,
        ),
        _Record(
            id="t3",
            title="Rework board empty states",
            description="Make them quieter and more helpful.",
            assignee="Ines",
            priority=Priority.LOW,
            status=Status.IN_PROGRESS,
            order=0,
        ),
        _Record(
            id="t4",
            title="Ship weekly release notes",
            description="Publish the summary to the team channel.",
            assignee="Theo",
            priority=Priority.MEDIUM,
            dueDate="2026-09-12",
            status=Status.DONE,
            order=0,
        ),
    ]


class TaskStore:
    """Thread-safe in-memory store for the board's tasks.

    One instance backs the whole shared board (docs/specs.md §3.1 — there
    is only ever one board), so every operation is serialized through a
    single lock rather than partitioned per-board or per-user.
    """

    def __init__(self, *, seed: bool = True) -> None:
        self._lock = Lock()
        self._tasks: dict[str, _Record] = {}
        if seed:
            for record in _seed_records():
                self._tasks[record.id] = record

    def list_tasks(self) -> list[Task]:
        with self._lock:
            return [r.to_task() for r in self._tasks.values()]

    def get_task(self, task_id: str) -> Task | None:
        with self._lock:
            record = self._tasks.get(task_id)
            return record.to_task() if record else None

    def create_task(self, payload: TaskCreate) -> Task:
        with self._lock:
            order = self._next_order(payload.status)
            record = _Record(
                id=str(uuid.uuid4()),
                title=payload.title,
                description=payload.description,
                assignee=payload.assignee,
                priority=payload.priority,
                dueDate=payload.dueDate,
                status=payload.status,
                order=order,
            )
            self._tasks[record.id] = record
            return record.to_task()

    def update_task(self, task_id: str, payload: TaskUpdate) -> Task | None:
        with self._lock:
            record = self._tasks.get(task_id)
            if record is None:
                return None

            changes = payload.model_dump(exclude_unset=True)
            status_changed = "status" in changes and changes["status"] != record.status

            updated = replace(record, **changes)
            if status_changed:
                # Same rule useBoard's upsertTask() uses: a task whose
                # column changed goes to the end of the new column rather
                # than keeping a position from the old one.
                updated.order = self._next_order(updated.status, exclude_id=task_id)

            self._tasks[task_id] = updated
            return updated.to_task()

    def delete_task(self, task_id: str) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None

    def move_task(self, task_id: str, payload: TaskMove) -> list[Task] | None:
        """Move `task_id` into `payload.status` at `payload.index`.

        Mirrors moveTask() in frontend/src/hooks/use-board.ts: only the
        tasks that end up in the destination column are renumbered
        (sequential from 0); tasks left behind in the source column keep
        their existing order values, gaps and all.
        """

        with self._lock:
            moving = self._tasks.get(task_id)
            if moving is None:
                return None

            column = sorted(
                (r for r in self._tasks.values() if r.status == payload.status and r.id != task_id),
                key=lambda r: r.order,
            )
            clamped = max(0, min(payload.index, len(column)))
            column.insert(clamped, replace(moving, status=payload.status))

            for position, record in enumerate(column):
                record.order = position
                self._tasks[record.id] = record

            return [r.to_task() for r in self._tasks.values()]

    def _next_order(self, status: Status, *, exclude_id: str | None = None) -> int:
        """One past the highest existing order in `status`, or 0 if empty —
        the same append-to-end rule use-board.ts's upsertTask() uses."""

        orders = [
            r.order
            for r in self._tasks.values()
            if r.status == status and r.id != exclude_id
        ]
        return max(orders, default=-1) + 1


# A single store instance shared by the whole process — there is only one
# board (docs/specs.md §3.1), so there is no per-request or per-board state
# to keep separate.
store = TaskStore()
