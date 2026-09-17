"""Database-backed task store.

This plays the role docs/specs.md §16-17 assigns to a storage layer: a
concern kept separate from the HTTP routing so it can be swapped — first
from in-memory to SQLite, later from SQLite to something else — without
changing the API contract. One TaskStore wraps one request-scoped
SQLAlchemy Session (see app/database.py's get_session); there is only one
board (docs/specs.md §3.1), so there is no board-id to key queries on.

Every query here goes through SQLAlchemy's ORM/Core expression API rather
than raw SQL, and every column type in app/orm.py is a plain, portable one
— nothing in this file assumes SQLite. The ordering rules below
intentionally mirror the frontend's own localStorage-backed implementation
in frontend/src/hooks/use-board.ts, so that a task's manually-chosen
position (specs.md §12.2) behaves the same way regardless of which store —
or which database — is behind the API.
"""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Priority, Status, Task, TaskCreate, TaskMove, TaskUpdate
from app.orm import TaskRow


def _to_task(row: TaskRow) -> Task:
    return Task(
        id=row.id,
        title=row.title,
        description=row.description,
        assignee=row.assignee,
        priority=Priority(row.priority),
        dueDate=row.due_date,
        status=Status(row.status),
        order=row.order,
    )


def seed_rows() -> list[TaskRow]:
    """Sample data so the frontend has something to show immediately.

    Deliberately the same four tasks the frontend's own localStorage seed
    (frontend/src/lib/kanban.ts seedTasks) uses, so the board looks
    identical whether it's reading from browser storage or this API.
    Returns fresh ORM instances on every call, since a row object is tied
    to whichever session it gets added to.
    """

    return [
        TaskRow(
            id="t1",
            title="Draft onboarding checklist",
            description="Outline the first-week steps for new teammates.",
            assignee="Maria",
            priority=Priority.HIGH.value,
            due_date="2026-09-18",
            status=Status.TODO.value,
            order=0,
        ),
        TaskRow(
            id="t2",
            title="Collect feedback from pilot users",
            description="Summarise the five interviews into key themes.",
            assignee="Sam",
            priority=Priority.MEDIUM.value,
            status=Status.TODO.value,
            order=1,
        ),
        TaskRow(
            id="t3",
            title="Rework board empty states",
            description="Make them quieter and more helpful.",
            assignee="Ines",
            priority=Priority.LOW.value,
            status=Status.IN_PROGRESS.value,
            order=0,
        ),
        TaskRow(
            id="t4",
            title="Ship weekly release notes",
            description="Publish the summary to the team channel.",
            assignee="Theo",
            priority=Priority.MEDIUM.value,
            due_date="2026-09-12",
            status=Status.DONE.value,
            order=0,
        ),
    ]


def seed_if_empty(session: Session) -> None:
    """Populate the tasks table on first run only. Called on app startup;
    a restart against a database that already has data is a no-op."""

    count = session.execute(select(func.count()).select_from(TaskRow)).scalar_one()
    if count == 0:
        session.add_all(seed_rows())
        session.commit()


class TaskStore:
    """Operations the API needs, implemented against one Session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_tasks(self) -> list[Task]:
        rows = self._session.execute(select(TaskRow)).scalars().all()
        return [_to_task(r) for r in rows]

    def get_task(self, task_id: str) -> Task | None:
        row = self._session.get(TaskRow, task_id)
        return _to_task(row) if row else None

    def create_task(self, payload: TaskCreate) -> Task:
        row = TaskRow(
            id=str(uuid.uuid4()),
            title=payload.title,
            description=payload.description,
            assignee=payload.assignee,
            priority=payload.priority.value,
            due_date=payload.dueDate,
            status=payload.status.value,
            order=self._next_order(payload.status.value),
        )
        self._session.add(row)
        self._session.commit()
        return _to_task(row)

    def update_task(self, task_id: str, payload: TaskUpdate) -> Task | None:
        row = self._session.get(TaskRow, task_id)
        if row is None:
            return None

        changes = payload.model_dump(exclude_unset=True)
        new_status = changes.get("status")
        status_changed = new_status is not None and new_status.value != row.status

        for field, value in changes.items():
            if field == "dueDate":
                row.due_date = value
            elif field in ("priority", "status"):
                setattr(row, field, value.value)
            else:
                setattr(row, field, value)

        if status_changed:
            # Same rule useBoard's upsertTask() uses: a task whose column
            # changed goes to the end of the new column rather than
            # keeping a position from the old one.
            row.order = self._next_order(row.status, exclude_id=task_id)

        self._session.commit()
        return _to_task(row)

    def delete_task(self, task_id: str) -> bool:
        row = self._session.get(TaskRow, task_id)
        if row is None:
            return False
        self._session.delete(row)
        self._session.commit()
        return True

    def move_task(self, task_id: str, payload: TaskMove) -> list[Task] | None:
        """Move `task_id` into `payload.status` at `payload.index`.

        Mirrors moveTask() in frontend/src/hooks/use-board.ts: only the
        tasks that end up in the destination column are renumbered
        (sequential from 0); tasks left behind in the source column keep
        their existing order values, gaps and all.
        """

        moving = self._session.get(TaskRow, task_id)
        if moving is None:
            return None

        target_status = payload.status.value
        column = list(
            self._session.execute(
                select(TaskRow)
                .where(TaskRow.status == target_status, TaskRow.id != task_id)
                .order_by(TaskRow.order)
            )
            .scalars()
            .all()
        )
        clamped = max(0, min(payload.index, len(column)))
        column.insert(clamped, moving)
        moving.status = target_status

        for position, row in enumerate(column):
            row.order = position

        self._session.commit()
        return self.list_tasks()

    def _next_order(self, status: str, *, exclude_id: str | None = None) -> int:
        """One past the highest existing order in `status`, or 0 if empty —
        the same append-to-end rule use-board.ts's upsertTask() uses."""

        stmt = select(func.max(TaskRow.order)).where(TaskRow.status == status)
        if exclude_id is not None:
            stmt = stmt.where(TaskRow.id != exclude_id)
        highest = self._session.execute(stmt).scalar_one_or_none()
        return (highest if highest is not None else -1) + 1
