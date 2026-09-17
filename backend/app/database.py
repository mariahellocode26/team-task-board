"""Database engine and session configuration.

The connection string comes from the DATABASE_URL environment variable, so
which database the server talks to is a deployment-time choice, not a
code change. It defaults to a local SQLite file so the app runs with zero
setup; pointing it at Postgres later means installing that dialect's driver
and setting DATABASE_URL (see backend/README.md), not touching this file
except for the one isolated exception noted below.

Engine and session-factory creation is lazy (built on first use, not at
import time) so that importing this module — which happens just by
importing app.main — never has the side effect of opening a database
connection or creating a file on disk. Tests take advantage of this: they
build their own isolated engine and never call get_engine() here at all.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_DATABASE_URL = "sqlite:///./team_kanban.db"


class Base(DeclarativeBase):
    """Shared declarative base for every ORM model (see app/orm.py)."""


def _engine_kwargs(url: str) -> dict[str, Any]:
    """The one place that knows which database is in use.

    SQLite's default driver restricts a connection to the thread that
    created it; FastAPI's sync routes run in a thread pool, so a connection
    may be reused across threads over the app's lifetime. That relaxation
    is specific to SQLite — a Postgres URL needs no equivalent — which is
    exactly why it's isolated here instead of being a general engine
    setting: adding another database later means adding another branch
    here, not touching store.py, orm.py, or anything else.
    """

    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
        _engine = create_engine(url, **_engine_kwargs(url))
    return _engine


def get_sessionmaker() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)
    return _session_factory


def init_db() -> None:
    """Create every table that doesn't already exist. Safe to call on every
    startup — it's a no-op once the schema is in place."""

    from app import orm  # noqa: F401  (registers TaskRow on Base.metadata)

    Base.metadata.create_all(get_engine())


def get_session() -> Iterator[Session]:
    """FastAPI dependency: one Session per request, closed when it ends."""

    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.close()
