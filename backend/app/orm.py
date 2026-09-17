"""SQLAlchemy ORM model: how a task is laid out in the database.

Deliberately separate from app/models.py (the API's Pydantic wire format)
and app/store.py (the operations the API needs) — this file only describes
table structure, using plain, portable column types so the same model
works unchanged against SQLite today and another database (e.g. Postgres)
later. In particular, priority and status are stored as plain strings
rather than a database-native enum type, which not every backend supports
the same way.
"""

from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TaskRow(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assignee: Mapped[str | None] = mapped_column(String(200), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    due_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
