"""The /tasks endpoints — see openapi.yaml for the authoritative contract.

There is no authentication on any of these routes: docs/specs.md §5.2 and
§33 explicitly exclude accounts, logins and passwords from the MVP, and
openapi.yaml sets `security: []` accordingly.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Error, Task, TaskCreate, TaskMove, TaskUpdate
from app.store import TaskStore

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Documents the real error responses (openapi.yaml's ValidationError /
# NotFound) alongside FastAPI's own auto-added 422, which is never what a
# client actually receives — the handlers in app.main normalize every
# error to one of these two shapes before it leaves the process.
VALIDATION_ERROR = {400: {"model": Error, "description": "The request body failed validation."}}
NOT_FOUND = {404: {"model": Error, "description": "No task exists with that id."}}


def get_store(session: Session = Depends(get_session)) -> TaskStore:
    """FastAPI dependency: one TaskStore per request, wrapping one Session.

    Tests override this directly (via app.dependency_overrides) with a
    TaskStore built on their own isolated in-memory database, bypassing
    get_session and the app's real database entirely.
    """

    return TaskStore(session)


StoreDep = Annotated[TaskStore, Depends(get_store)]


@router.get("", response_model=list[Task], summary="List every task on the board")
def list_tasks(task_store: StoreDep) -> list[Task]:
    return task_store.list_tasks()


@router.post(
    "",
    response_model=Task,
    status_code=http_status.HTTP_201_CREATED,
    summary="Create a task",
    responses=VALIDATION_ERROR,
)
def create_task(payload: TaskCreate, task_store: StoreDep) -> Task:
    return task_store.create_task(payload)


@router.patch(
    "/{task_id}",
    response_model=Task,
    summary="Edit a task",
    responses={**VALIDATION_ERROR, **NOT_FOUND},
)
def update_task(task_id: str, payload: TaskUpdate, task_store: StoreDep) -> Task:
    task = task_store.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete(
    "/{task_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    responses=NOT_FOUND,
)
def delete_task(task_id: str, task_store: StoreDep) -> None:
    if not task_store.delete_task(task_id):
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.post(
    "/{task_id}/move",
    response_model=list[Task],
    summary="Move a task to a column and position",
    responses={**VALIDATION_ERROR, **NOT_FOUND},
)
def move_task(task_id: str, payload: TaskMove, task_store: StoreDep) -> list[Task]:
    tasks = task_store.move_task(task_id, payload)
    if tasks is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")
    return tasks
