"""Pydantic models for the Team Kanban API.

These mirror the schemas in openapi.yaml at the repository root exactly —
that file is the source of truth for the contract; this module is its
Python implementation. See docs/specs.md §27 for the underlying data model.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class Priority(str, Enum):
    """One of three fixed priorities (specs.md §8). No custom priorities."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(str, Enum):
    """One of the three fixed columns (specs.md §4, §27)."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


def _clean_title(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("title must not be blank")
    return stripped


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class Task(BaseModel):
    """A task as returned by the API (openapi.yaml Task, specs.md §27)."""

    id: str
    title: str
    description: str | None = None
    assignee: str | None = None
    priority: Priority
    dueDate: str | None = None
    status: Status
    order: int


class TaskCreate(BaseModel):
    """Request body for POST /tasks. Only title is required (specs.md §9)."""

    title: str = Field(min_length=1)
    description: str | None = None
    assignee: str | None = None
    priority: Priority = Priority.MEDIUM
    dueDate: str | None = None
    status: Status = Status.TODO

    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str) -> str:
        return _clean_title(value)

    @field_validator("description", "assignee", "dueDate")
    @classmethod
    def _validate_optional_strings(cls, value: str | None) -> str | None:
        return _clean_optional(value)


class TaskUpdate(BaseModel):
    """Request body for PATCH /tasks/{taskId}. Every field optional; at
    least one must be present."""

    title: str | None = None
    description: str | None = None
    assignee: str | None = None
    priority: Priority | None = None
    dueDate: str | None = None
    status: Status | None = None

    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str | None) -> str | None:
        return None if value is None else _clean_title(value)

    @field_validator("description", "assignee", "dueDate")
    @classmethod
    def _validate_optional_strings(cls, value: str | None) -> str | None:
        return _clean_optional(value)

    @model_validator(mode="after")
    def _require_at_least_one_field(self) -> "TaskUpdate":
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        return self


class TaskMove(BaseModel):
    """Request body for POST /tasks/{taskId}/move."""

    status: Status
    index: int = Field(ge=0)


class Error(BaseModel):
    message: str
